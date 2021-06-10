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
use vcx::aries::messages::a2a::A2AMessage;
use vcx::aries::messages::issuance::credential_offer::CredentialOffer as VcxCredentialOffer;

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

#[derive(Serialize, Deserialize, Default)]
struct Credential {
    credential_preview: CredentialPreview,
    #[serde(default)]
    comment: Option<String>
}

#[derive(Serialize, Deserialize, Default)]
struct CredentialId {
    credential_id: String,
}

fn _get_state_issuer(issuer: &Issuer) -> State {
    match VcxStateType::from_u32(issuer.get_state().unwrap()) {
        VcxStateType::VcxStateInitialized => State::Initial,
        VcxStateType::VcxStateOfferSent => State::OfferSent,
        VcxStateType::VcxStateRequestReceived => State::RequestReceived,
        VcxStateType::VcxStateAccepted => State::CredentialSent,
        _ => State::Unknown
    }
}

fn _get_state_holder(holder: &Holder) -> State {
    match VcxStateType::from_u32(holder.get_state()) {
        VcxStateType::VcxStateRequestReceived => State::OfferReceived,
        VcxStateType::VcxStateOfferSent => State::RequestSent,
        VcxStateType::VcxStateAccepted => State::CredentialReceived,
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
        let credential_preview = serde_json::to_string(&cred_offer.credential_preview.attributes).map_err(|err| HarnessError::from(err))?;
        let mut issuer = Issuer::create(&issuer_config, &credential_preview, &id).map_err(|err| HarnessError::from(err))?;
        issuer.send_credential_offer(connection.send_message_closure().map_err(|err| HarnessError::from(err))?, None).map_err(|err| HarnessError::from(err))?;
        self.db.set(&id, &issuer).map_err(|err| HarnessError::from(err))?;
        Ok(json!({ "state": "offer-sent", "thread_id": id }).to_string()) // TODO: This must really be a thread id
    }

    pub fn send_credential_request(&mut self, id: &str) -> HarnessResult<String> {
        let mut holder: Holder = self.db.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Holder with id {} not found", id)))?;
        let connection = self.last_connection.as_ref()
            .ok_or(HarnessError::from_msg(HarnessErrorType::InternalServerError, &format!("No connection established")))?;
        // TODO: Maybe just take Connection
        holder.send_request(connection.agent_info().pw_did.to_string(), connection.send_message_closure().map_err(|err| HarnessError::from(err))?).map_err(|err| HarnessError::from(err))?;
        let state = _get_state_holder(&holder);
        self.db.set(&id, &holder).map_err(|err| HarnessError::from(err))?;
        Ok(json!({ "state": state }).to_string())
    }

    pub fn issue_credetial(&mut self, id: &str, credential: &Credential) -> HarnessResult<String> {
        let mut issuer: Issuer = self.db.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Issuer with id {} not found", id)))?;
        let connection = self.last_connection.as_ref()
            .ok_or(HarnessError::from_msg(HarnessErrorType::InternalServerError, &format!("No connection established")))?;
        issuer.update_state(connection).map_err(|err| HarnessError::from(err))?;
        issuer.send_credential(connection.send_message_closure()?).map_err(|err| HarnessError::from(err))?;
        self.db.set(&id, &issuer).map_err(|err| HarnessError::from(err))?;
        Ok(json!({ "state": "credential-issued" }).to_string())
    }

    pub fn get_issuer_state(&mut self, id: &str) -> HarnessResult<String> {
        let connection = self.last_connection.as_ref()
            .ok_or(HarnessError::from_msg(HarnessErrorType::InternalServerError, &format!("No connection established")))?;
        match self.db.get::<Issuer>(id) {
            Some(mut issuer) => {
                issuer.update_state(connection).map_err(|err| HarnessError::from(err))?;
                self.db.set(&id, &issuer).map_err(|err| HarnessError::from(err))?;
                let state = _get_state_issuer(&issuer);
                Ok(json!({ "state": state }).to_string())
            }
            None => {
                match self.db.get::<Holder>(id) {
                    Some(mut holder) => {
                        holder.update_state(connection).map_err(|err| HarnessError::from(err))?;
                        self.db.set(&id, &holder).map_err(|err| HarnessError::from(err))?;
                        let state = _get_state_holder(&holder);
                        Ok(json!({ "state": state }).to_string())
                    }
                    None => {
                        let credential_offers: Vec<VcxCredentialOffer> = connection.get_messages()?
                            .into_iter()
                            .filter_map(|(_, a2a_message)| {
                                match a2a_message {
                                    A2AMessage::CredentialOffer(cred_offer) => Some(cred_offer),
                                    _ => None
                                }
                            })
                            .collect();
                        let holder = Holder::create(credential_offers.last().unwrap().clone(), id).map_err(|err| HarnessError::from(err))?;
                        self.db.set(&id, &holder).map_err(|err| HarnessError::from(err))?;
                        Ok(json!({ "state": "offer-received" }).to_string())
                    }
                }
            }
        }
    }

    pub fn send_ack(&mut self, id: &str) -> HarnessResult<String> {
        let mut holder: Holder = self.db.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Holder with id {} not found", id)))?;
        let connection = self.last_connection.as_ref()
            .ok_or(HarnessError::from_msg(HarnessErrorType::InternalServerError, &format!("No connection established")))?;
        holder.update_state(connection).map_err(|err| HarnessError::from(err))?;
        Ok(json!({ "state": "done", "credential_id": id }).to_string()) // TODO: Test we are in Finished state
    }

    pub fn get_credential(&mut self, id: &str) -> HarnessResult<String> {
        let mut holder: Holder = self.db.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Holder with id {} not found", id)))?;
        let attach = holder.get_attachment().map_err(|err| HarnessError::from(err))?;
        let attach: serde_json::Value = serde_json::from_str(&attach).map_err(|err| HarnessError::from(err))?;
        let mut attach = attach.as_object().unwrap().clone();
        attach.insert("referent".to_string(), serde_json::Value::String(id.to_string()));
        Ok(serde_json::to_string(&attach).unwrap())
    }
}

#[post("/send-offer")]
pub async fn send_credential_offer(req: web::Json<Request<CredentialOffer>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().send_credential_offer(&req.data)
}

#[post("/send-request")]
pub async fn send_credential_request(req: web::Json<Request<String>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().send_credential_request(&req.id)
}

#[get("/{issuer_id}")]
pub async fn get_issuer_state(agent: web::Data<Mutex<Agent>>, path: web::Path<String>) -> impl Responder {
    agent.lock().unwrap().get_issuer_state(&path.into_inner())
        .with_header("Cache-Control", "private, no-store, must-revalidate")
}

#[post("/issue")]
pub async fn issue_credential(req: web::Json<Request<Credential>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().issue_credetial(&req.id, &req.data)
}

#[post("/store")]
pub async fn send_ack(req: web::Json<Request<CredentialId>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().send_ack(&req.id)
}

#[get("/{cred_id}")]
pub async fn get_credential(agent: web::Data<Mutex<Agent>>, path: web::Path<String>) -> impl Responder {
    agent.lock().unwrap().get_credential(&path.into_inner())
        .with_header("Cache-Control", "private, no-store, must-revalidate")
}

pub fn config(cfg: &mut web::ServiceConfig) {
    cfg
        .service(
            web::scope("/command/issue-credential")
                .service(send_credential_offer)
                .service(get_issuer_state)
                .service(send_credential_request)
                .service(issue_credential)
                .service(send_ack)
        )
        .service(
            web::scope("/command/credential")
                .service(get_credential)
        );
}
