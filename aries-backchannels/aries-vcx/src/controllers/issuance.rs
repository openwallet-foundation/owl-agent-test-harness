use std::sync::Mutex;
use actix_web::{web, Responder, post, get};
use crate::error::{HarnessError, HarnessErrorType, HarnessResult};
use vcx::issuer_credential;
use vcx::libindy::utils::anoncreds;
use vcx::aries::handlers::issuance::issuer::issuer::{Issuer, IssuerConfig};
use vcx::aries::handlers::issuance::holder::holder::Holder;
use vcx::aries::handlers::connection::connection::Connection;
use vcx::api::VcxStateType;
use uuid;
use crate::{Agent, State};
use crate::controllers::Request;

#[derive(Serialize, Deserialize, Default)]
struct CredentialPreview {
    #[serde(rename = "@type")]
    msg_type: String,
    attributes: Vec<serde_json::Value>
}

#[derive(Serialize, Deserialize, Default)]
struct CredentialOffer {
    cred_def_id: String,
    credential_preview: CredentialPreview,
    connection_id: String
}

fn _get_state(issuer: &Issuer) -> State {
    match VcxStateType::from_u32(issuer.get_state().unwrap()) {
        VcxStateType::VcxStateInitialized => State::Initial,
        VcxStateType::VcxStateOfferSent => State::OfferSent,
        VcxStateType::VcxStateRequestReceived => State::RequestReceived,
        VcxStateType::VcxStateAccepted => State::CredentialSent,
        _ => State::Unknown
    }
}

impl Agent {
    pub fn send_credential_offer(&mut self, cred_offer: &CredentialOffer) -> HarnessResult<String> {
        let id = uuid::Uuid::new_v4().to_string();
        let connection: Connection = self.db.get(&cred_offer.connection_id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
        let issuer_config = IssuerConfig {
            cred_def_id: cred_offer.cred_def_id.clone(),
            rev_reg_id: None,
            tails_file: None
        };
        let credential_preview = serde_json::to_string(&cred_offer.credential_preview).map_err(|err| HarnessError::from(err))?;
        let mut issuer = Issuer::create(&issuer_config, &credential_preview, &id).map_err(|err| HarnessError::from(err))?;
        issuer.send_credential_offer(connection.send_message_closure().map_err(|err| HarnessError::from(err))?, None).map_err(|err| HarnessError::from(err))?;
        self.db.set(&id, &issuer).map_err(|err| HarnessError::from(err))?;
        Ok(json!({ "state": "offer-sent", "thread_id": id }).to_string()) // TODO: This must really be a thread id
    }

    pub fn get_issuer_state(&mut self, id: &str) -> HarnessResult<String> {
        // TODO: We need to get messages and if receive cred offer with thread id == id, create a
        // holder in offer-received state, but we don't know connection

        let mut issuer: Issuer = self.db.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Issuer with id {} not found", id)))?;
        let state = _get_state(&issuer);
        self.db.set(&id, &issuer).map_err(|err| HarnessError::from(err))?;
        Ok(json!({ "state": state }).to_string())
    }
}

#[post("/send-offer")]
pub async fn send_credential_offer(req: web::Json<Request<CredentialOffer>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().send_credential_offer(&req.data)
}

#[get("/{issuer_id}")]
pub async fn get_issuer_state(agent: web::Data<Mutex<Agent>>, path: web::Path<String>) -> impl Responder {
    agent.lock().unwrap().get_issuer_state(&path.into_inner())
        .with_header("Cache-Control", "private, no-store, must-revalidate")
}

pub fn config(cfg: &mut web::ServiceConfig) {
    cfg
        .service(
            web::scope("/command/issue-credential")
                .service(send_credential_offer)
                .service(get_issuer_state)
        );
}
