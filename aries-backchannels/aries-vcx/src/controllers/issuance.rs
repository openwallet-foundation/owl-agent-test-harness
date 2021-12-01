use std::sync::Mutex;
use std::fs::File;
use actix_web::{web, Responder, post, get};
use crate::error::{HarnessError, HarnessErrorType, HarnessResult};
use aries_vcx::handlers::issuance::issuer::issuer::{Issuer, IssuerState};
use aries_vcx::handlers::issuance::holder::holder::{Holder, HolderState};
use aries_vcx::handlers::connection::connection::Connection;
use aries_vcx::messages::a2a::A2AMessage;
use aries_vcx::messages::issuance::credential_offer::{CredentialOffer as VcxCredentialOffer, OfferInfo};
use aries_vcx::messages::issuance::credential_proposal::CredentialProposalData;
use aries_vcx::messages::issuance::credential_proposal::CredentialProposal as VcxCredentialProposal;
use aries_vcx::messages::mime_type::MimeType;
use uuid;
use crate::{Agent, State};
use crate::controllers::Request;
use crate::controllers::credential_definition::CachedCredDef;
use crate::soft_assert_eq;

#[derive(Serialize, Deserialize, Default, Clone, Debug)]
pub struct CredentialPreview {
    #[serde(rename = "@type")]
    msg_type: String,
    attributes: Vec<serde_json::Value>
}

#[derive(Serialize, Deserialize, Default, Debug)]
pub struct CredentialOffer {
    cred_def_id: String,
    credential_preview: CredentialPreview,
    connection_id: String
}

#[derive(Serialize, Deserialize, Default, Clone)]
pub struct CredentialProposal {
        schema_issuer_did: String,
        issuer_did: String,
        schema_name: String,
        cred_def_id: String,
        schema_version: String,
        credential_proposal: CredentialPreview,
        connection_id: String,
        schema_id: String
}

#[derive(Serialize, Deserialize, Default)]
pub struct Credential {
    credential_preview: CredentialPreview,
    #[serde(default)]
    comment: Option<String>
}

#[derive(Serialize, Deserialize, Default)]
pub struct CredentialId {
    credential_id: String,
}

fn _get_state_issuer(issuer: &Issuer) -> State {
    match issuer.get_state() {
        IssuerState::Initial => State::Initial,
        IssuerState::ProposalReceived => State::ProposalReceived,
        IssuerState::OfferSent => State::OfferSent,
        IssuerState::RequestReceived => State::RequestReceived,
        IssuerState::CredentialSent => State::CredentialSent,
        IssuerState::Finished => State::Done,
        IssuerState::Failed => State::Failure,
    }
}

fn _get_state_holder(holder: &Holder) -> State {
    match holder.get_state() {
        HolderState::Initial => State::Initial,
        HolderState::ProposalSent => State::ProposalSent,
        HolderState::OfferReceived => State::OfferReceived,
        HolderState::RequestSent => State::RequestSent,
        HolderState::Finished => State::Done,
        HolderState::Failed => State::Failure,
    }
}

fn download_tails_file(tails_base_url: &str, rev_reg_id: &str, tails_hash: &str) -> HarnessResult<()> {
    let url = match tails_base_url.to_string().matches("/").count() {
        0 => format!("{}/{}", tails_base_url, rev_reg_id),
        1.. => tails_base_url.to_string(),
        _ => { return Err(HarnessError::from_msg(HarnessErrorType::InternalServerError, "Negative count"))}
    };
    let client = reqwest::Client::new();
    let tails_folder_path = std::env::current_dir().expect("Failed to obtain the current directory path").join("resource").join("tails");
    std::fs::create_dir_all(&tails_folder_path).map_err(|_| HarnessError::from_msg(HarnessErrorType::InternalServerError, "Failed to create tails folder"))?;
    let tails_file_path = tails_folder_path.join(tails_hash).to_str().unwrap().to_string();
    let mut res = client.get(&url).send().unwrap();
    soft_assert_eq!(res.status(), reqwest::StatusCode::OK);
    let mut out = File::create(tails_file_path).unwrap();
    std::io::copy(&mut res, &mut out).unwrap();
    Ok(())
}

fn get_proposal(connection: &Connection) -> HarnessResult<VcxCredentialProposal> {
     let mut proposals: Vec<VcxCredentialProposal> =
         connection.get_messages()?
             .into_iter()
             .filter_map(|(uid, message)| {
                 match message {
                     A2AMessage::CredentialProposal(proposal) => {
                        connection.update_message_status(uid).ok()?;
                        Some(proposal)
                     }
                     _ => None
                 }
             }).collect();
     soft_assert_eq!(proposals.len(), 1);
     proposals.pop()
        .ok_or(
            HarnessError::from_msg(HarnessErrorType::InternalServerError, &format!("Did not obtain presentation request message"))
        )
}

fn get_offer(connection: &Connection, thread_id: &str) -> HarnessResult<VcxCredentialOffer> {
    let mut offers: Vec<VcxCredentialOffer> = connection.get_messages()?
        .into_iter()
        .filter_map(|(uid, a2a_message)| {
            match a2a_message {
                A2AMessage::CredentialOffer(offer) if offer.get_thread_id() == thread_id.to_string() => {
                    connection.update_message_status(uid).ok()?;
                    Some(offer)
                }
                _ => None
            }
        })
    .collect();
    soft_assert_eq!(offers.len(), 1);
    offers.pop()
       .ok_or(
           HarnessError::from_msg(HarnessErrorType::InternalServerError, &format!("Did not obtain presentation request message"))
       )
}

impl Agent {
    pub fn send_credential_proposal(&mut self, cred_proposal: &CredentialProposal) -> HarnessResult<String> {
        let id = uuid::Uuid::new_v4().to_string();
        let connection: Connection = self.dbs.connection.get(&cred_proposal.connection_id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", cred_proposal.connection_id)))?;
        let mut holder = Holder::create(&id)?;
        let mut proposal_data = CredentialProposalData::create()
            .set_schema_id(cred_proposal.schema_id.clone())
            .set_cred_def_id(cred_proposal.cred_def_id.clone());
        for attr in cred_proposal.credential_proposal.attributes.clone().into_iter() {
            let name = attr["name"].as_str().ok_or(HarnessError::from_msg(HarnessErrorType::InvalidJson, "No 'name' field in attributes"))?;
            let value = attr["value"].as_str().ok_or(HarnessError::from_msg(HarnessErrorType::InvalidJson, "No 'value' field in attributes"))?;
            proposal_data = proposal_data.add_credential_preview_data(&name, &value, MimeType::Plain)?;
        }
        holder.send_proposal(proposal_data.clone(), connection.send_message_closure()?)?;
        let thread_id = holder.get_thread_id()?;
        self.dbs.holder.set(&thread_id, &holder)?;
        self.dbs.connection.set(&thread_id, &connection)?;
        Ok(json!({ "state": _get_state_holder(&holder), "thread_id": thread_id }).to_string())
    }

    pub fn send_credential_request(&mut self, id: &str) -> HarnessResult<String> {
        let mut holder: Holder = self.dbs.holder.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Holder with id {} not found", id)))?;
        let connection: Connection = self.dbs.connection.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
        holder.send_request(connection.pairwise_info().pw_did.to_string(), connection.send_message_closure()?)?;
        let thread_id = holder.get_thread_id()?;
        self.dbs.holder.set(&thread_id, &holder)?;
        Ok(json!({ "state": _get_state_holder(&holder), "thread_id": thread_id }).to_string())
    }

    pub fn send_credential_offer(&mut self, cred_offer: &CredentialOffer, id: &str) -> HarnessResult<String> {
        let connection: Connection = match cred_offer.connection_id.is_empty() {
            false => self.dbs.connection.get(&cred_offer.connection_id)
                        .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", cred_offer.connection_id)))?,
            true => self.last_connection.clone()
                        .ok_or(HarnessError::from_msg(HarnessErrorType::InternalServerError, &format!("No connection established")))?
        };
        let issuer = match id.is_empty() {
            true => {
                let cred_def: CachedCredDef = self.dbs.cred_def.get(&cred_offer.cred_def_id)
                    .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Cred def with id {} not found", cred_offer.cred_def_id)))?;
                let id = uuid::Uuid::new_v4().to_string();
                let credential_preview = serde_json::to_string(&cred_offer.credential_preview.attributes)?;
                let offer_info = OfferInfo {
                    credential_json: credential_preview,
                    cred_def_id: cred_offer.cred_def_id.clone(),
                    rev_reg_id: cred_def.rev_reg_id.clone(),
                    tails_file: cred_def.tails_file.clone()
                };
                let mut issuer = Issuer::create(&id)?;
                issuer.send_credential_offer(offer_info, None, connection.send_message_closure()?)?;
                issuer
            }
            false => {
                let proposal = get_proposal(&connection)?;
                let cred_def: CachedCredDef = self.dbs.cred_def.get(&proposal.cred_def_id)
                    .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Cred def with id {} not found", cred_offer.cred_def_id)))?;
                let offer_info = OfferInfo {
                    credential_json: proposal.credential_proposal.to_string()?,
                    cred_def_id: proposal.cred_def_id.clone(),
                    rev_reg_id: cred_def.rev_reg_id.clone(),
                    tails_file: cred_def.tails_file.clone()
                };
                let mut issuer = Issuer::create_from_proposal(&id, &proposal)?;
                issuer.send_credential_offer(offer_info, None, connection.send_message_closure()?)?;
                issuer
            }
        };
        let thread_id = issuer.get_thread_id()?;
        self.dbs.issuer.set(&thread_id, &issuer)?;
        self.dbs.connection.set(&thread_id, &connection)?;
        Ok(json!({ "state": _get_state_issuer(&issuer), "thread_id": thread_id }).to_string())
    }

    pub fn issue_credetial(&mut self, id: &str, _credential: &Credential) -> HarnessResult<String> {
        let mut issuer: Issuer = self.dbs.issuer.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Issuer with id {} not found", id)))?;
        let connection: Connection = self.dbs.connection.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
        issuer.update_state(&connection)?;
        issuer.send_credential(connection.send_message_closure()?)?;
        self.dbs.issuer.set(&id, &issuer)?;
        Ok(json!({ "state": _get_state_issuer(&issuer) }).to_string())
    }

    pub fn send_ack(&mut self, id: &str) -> HarnessResult<String> {
        let mut holder: Holder = self.dbs.holder.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Holder with id {} not found", id)))?;
        let connection: Connection = self.dbs.connection.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
        holder.update_state(&connection)?;
        if holder.is_revokable()? {
            let rev_reg_id = holder.get_rev_reg_id()?;
            let tails_hash = holder.get_tails_hash()?;
            let tails_location = holder.get_tails_location()?;
            download_tails_file(&tails_location, &rev_reg_id, &tails_hash)?;
        };
        self.dbs.holder.set(&id, &holder)?;
        Ok(json!({ "state": _get_state_holder(&holder), "credential_id": id }).to_string())
    }

    pub fn get_issuer_state(&mut self, id: &str) -> HarnessResult<String> {
        let connection: Connection = self.dbs.connection.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
        match self.dbs.issuer.get::<Issuer>(id) {
            Some(mut issuer) => {
                issuer.update_state(&connection)?;
                self.dbs.issuer.set(&id, &issuer)?;
                Ok(json!({ "state": _get_state_issuer(&issuer) }).to_string())
            }
            None => {
                match self.dbs.holder.get::<Holder>(id) {
                    Some(mut holder) => {
                        let connection: Connection = self.dbs.connection.get(id)
                            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
                        holder.update_state(&connection)?;
                        self.dbs.holder.set(&id, &holder)?;
                        Ok(json!({ "state": _get_state_holder(&holder) }).to_string())
                    }
                    None => {
                        let offer = get_offer(&connection, id)?;
                        let holder = Holder::create_from_offer(id, offer)?;
                        self.dbs.holder.set(&id, &holder)?;
                        Ok(json!({ "state": _get_state_holder(&holder) }).to_string())
                    }
                }
            }
        }
    }

    pub fn get_credential(&mut self, id: &str) -> HarnessResult<String> {
        let mut holder: Holder = self.dbs.holder.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Holder with id {} not found", id)))?;
        let connection: Connection = self.dbs.connection.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
        holder.update_state(&connection)?;
        let attach = holder.get_attachment()?;
        let attach: serde_json::Value = serde_json::from_str(&attach)?;
        let mut attach = attach.as_object().unwrap().clone();
        attach.insert("referent".to_string(), serde_json::Value::String(id.to_string()));
        Ok(serde_json::to_string(&attach).unwrap())
    }
}

#[post("/send-proposal")]
pub async fn send_credential_proposal(req: web::Json<Request<CredentialProposal>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().send_credential_proposal(&req.data)
        .with_header("Cache-Control", "private, no-store, must-revalidate")
}

#[post("/send-offer")]
pub async fn send_credential_offer(req: web::Json<Request<CredentialOffer>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().send_credential_offer(&req.data, &req.id)
        .with_header("Cache-Control", "private, no-store, must-revalidate")
}

#[post("/send-request")]
pub async fn send_credential_request(req: web::Json<Request<String>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().send_credential_request(&req.id)
        .with_header("Cache-Control", "private, no-store, must-revalidate")
}

#[get("/{issuer_id}")]
pub async fn get_issuer_state(agent: web::Data<Mutex<Agent>>, path: web::Path<String>) -> impl Responder {
    agent.lock().unwrap().get_issuer_state(&path.into_inner())
        .with_header("Cache-Control", "private, no-store, must-revalidate")
}

#[post("/issue")]
pub async fn issue_credential(req: web::Json<Request<Credential>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().issue_credetial(&req.id, &req.data)
        .with_header("Cache-Control", "private, no-store, must-revalidate")
}

#[post("/store")]
pub async fn send_ack(req: web::Json<Request<CredentialId>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().send_ack(&req.id)
        .with_header("Cache-Control", "private, no-store, must-revalidate")
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
                .service(send_credential_proposal)
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
