use std::sync::Mutex;
use std::collections::HashMap;
use actix_web::{web, Responder, post, get};
use uuid;
use crate::error::{HarnessError, HarnessErrorType, HarnessResult};
use crate::{Agent, State};
use crate::controllers::Request;
use aries_vcx::messages::proof_presentation::presentation_request::PresentationRequest as VcxPresentationRequest;
use aries_vcx::messages::a2a::A2AMessage;
use aries_vcx::messages::status::Status;
use aries_vcx::handlers::proof_presentation::verifier::verifier::{Verifier, VerifierState};
use aries_vcx::handlers::proof_presentation::prover::prover::{Prover, ProverState};
use aries_vcx::messages::proof_presentation::presentation_proposal::{PresentationProposalData, Attribute, Predicate};
use aries_vcx::handlers::connection::connection::Connection;
use crate::soft_assert_eq;

#[derive(Serialize, Deserialize, Default, Debug)]
pub struct PresentationRequestWrapper {
    connection_id: String,
    presentation_request: PresentationRequest
}

#[derive(Serialize, Deserialize, Default, Debug)]
pub struct PresentationProposalWrapper {
    connection_id: String,
    presentation_proposal: PresentationProposal
}

#[derive(Debug, Deserialize, Serialize, Clone, PartialEq, Default)]
pub struct PresentationRequest {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub comment: Option<String>,
    pub proof_request: ProofRequestData
}

#[derive(Serialize, Deserialize, Default, Debug)]
pub struct PresentationProposal {
    comment: String,
    attributes: Vec<Attribute>,
    predicates: Vec<Predicate>
}

#[derive(Serialize, Deserialize, Debug, PartialEq, Clone, Default)]
pub struct ProofRequestData {
    pub data: serde_json::Value,
}

fn _get_state_prover(prover: &Prover) -> State {
    match prover.get_state() {
        ProverState::Initial => State::Initial,
        ProverState::PresentationRequestReceived => State::RequestReceived,
        ProverState::PresentationProposalSent => State::ProposalSent,
        ProverState::PresentationSent => State::PresentationSent,
        ProverState::PresentationPreparationFailed | ProverState::Finished | ProverState::Failed => State::Done,
        _ => State::Unknown
    }
}

fn _get_state_verifier(verifier: &Verifier) -> State {
    match verifier.get_state() {
        VerifierState::Initial => State::Initial,
        VerifierState::PresentationRequestSet => State::RequestSet,
        VerifierState::PresentationProposalReceived => State::ProposalReceived,
        VerifierState::PresentationRequestSent => State::OfferSent,
        VerifierState::Finished => State::Done,
        _ => State::Unknown
    }
}

fn _select_credentials(resolved_creds: &str, secondary_required: bool) -> HarnessResult<String> {
    let resolved_creds: HashMap<String, HashMap<String, serde_json::Value>> = serde_json::from_str(resolved_creds)?;
    let resolved_creds: HashMap<String, serde_json::Value> = resolved_creds.get("attrs")
        .ok_or(HarnessError::from_msg(HarnessErrorType::InternalServerError, &format!("No attrs in resolved_creds: {:?}", resolved_creds)))?.clone();
    let mut selected_creds: HashMap<String, HashMap<String, serde_json::Value>> = HashMap::new();
    selected_creds.insert(String::from("attrs"), HashMap::new());
    // TODO: Discard revoked selected credentials
    for (attr_name, attr_cred_info) in resolved_creds.iter() {
        match attr_cred_info {
            serde_json::Value::Array(attr_cred_info) => {
                let to_insert = if secondary_required {
                    json!({
                        "credential": attr_cred_info.last().unwrap(),
                        "tails_file": std::env::current_dir().unwrap().join("resource").join("tails").to_str().unwrap().to_string()
                    })
                } else {
                    json!({
                        "credential": attr_cred_info.first().unwrap(),
                    })
                };
                if attr_cred_info.len() > 0 {
                    selected_creds.get_mut("attrs").unwrap().insert(String::from(attr_name), to_insert);
                }
            }
            _ => return Err(HarnessError::from_msg(HarnessErrorType::InternalServerError, &format!("Unexpected data, expected attr_cred_info to be an array, but got {:?}.", attr_cred_info)))
        }
    }
    serde_json::to_string(&selected_creds).map_err(|err| HarnessError::from(err))
}

fn _secondary_proof_required(prover: &Prover) -> HarnessResult<bool> {
    let attach = prover.get_proof_request_attachment()?;
    let attach: serde_json::Value = serde_json::from_str(&attach).unwrap();
    Ok(!attach["non_revoked"].is_null())
}

impl Agent {
    pub fn send_proof_request(&mut self, presentation_request: &PresentationRequestWrapper) -> HarnessResult<String> {
        let id = uuid::Uuid::new_v4().to_string();
        let connection: Connection = self.dbs.connection.get(&presentation_request.connection_id).unwrap();
        connection.get_messages()?
            .into_iter()
            .for_each(|(uid, message)| {
                match message {
                    A2AMessage::PresentationProposal(_) => {
                        connection.update_message_status(uid).ok();
                    }
                    _ => {}
                }
            });
        let req_data = presentation_request.presentation_request.proof_request.data.clone();
        let requested_attrs = req_data["requested_attributes"].to_string();
        let revoc_interval = req_data["non_revoked"].clone(); 
        let revoc_interval = match revoc_interval.is_null() {
            true => "{}".to_string(),
            false => revoc_interval.to_string()
        };
        let mut verifier = Verifier::create_from_request(id.to_string(), requested_attrs, "[]".to_string(), revoc_interval, id.to_string())?;
        verifier.send_presentation_request(connection.send_message_closure()?, None)?;
        soft_assert_eq!(verifier.get_state(), VerifierState::PresentationRequestSent);
        self.dbs.verifier.set(&id, &verifier)?;
        self.dbs.connection.set(&id, &connection)?;
        Ok(json!({"state": _get_state_verifier(&verifier), "thread_id": id}).to_string())
    }

    pub fn send_proof_proposal(&mut self, presentation_proposal: &PresentationProposalWrapper) -> HarnessResult<String> {
        let id = uuid::Uuid::new_v4().to_string();
        let connection: Connection = self.dbs.connection.get(&presentation_proposal.connection_id).unwrap();
        let mut proposal_data = PresentationProposalData::create();
        for attr in presentation_proposal.presentation_proposal.attributes.clone().into_iter() {
            proposal_data = proposal_data.add_attribute(attr.clone());
        };
        let mut prover = Prover::create(&id)?;
        prover.send_proposal(proposal_data, &connection.send_message_closure()?)?;
        soft_assert_eq!(prover.get_state(), ProverState::PresentationProposalSent);
        self.dbs.prover.set(&id, &prover)?;
        Ok(json!({ "state": _get_state_prover(&prover), "thread_id": id }).to_string())
    }

    pub fn send_presentation(&mut self, id: &str) -> HarnessResult<String> {
        let mut prover: Prover = self.dbs.prover.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Prover with id {} not found", id)))?;
        let connection: Connection = self.dbs.connection.get(id).unwrap();
        prover.update_state(&connection)?;
        soft_assert_eq!(prover.get_state(), ProverState::PresentationRequestReceived);
        let credentials = prover.retrieve_credentials()?;
        let secondary_required = _secondary_proof_required(&prover)?;
        let credentials = _select_credentials(&credentials, secondary_required)?;
        prover.generate_presentation(credentials, "{}".to_string())?;
        prover.send_presentation(&connection.send_message_closure()?)?;
        soft_assert_eq!(prover.get_state(), ProverState::PresentationSent);
        self.dbs.prover.set(&id, &prover)?;
        Ok(json!({"state": _get_state_prover(&prover), "thread_id": id}).to_string())
    }

    pub fn verify_presentation(&mut self, id: &str) -> HarnessResult<String> {
        let mut verifier: Verifier = self.dbs.verifier.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Verifier with id {} not found", id)))?;
        let connection: Connection = self.dbs.connection.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
        soft_assert_eq!(verifier.get_state(), VerifierState::PresentationRequestSent);
        verifier.update_state(&connection)?;
        self.dbs.verifier.set(&id, &verifier)?;
        let verified = match Status::from_u32(verifier.presentation_status()) {
            Status::Success => "true",
            _ => "false"
        };
        Ok(json!({ "state": State::Done, "verified": verified }).to_string())
    }

    pub fn get_proof(&mut self, id: &str) -> HarnessResult<String> {
        let connection_ids = self.dbs.connection.get_all();
        match self.dbs.prover.get::<Prover>(id) {
            Some(mut prover) => {
               let connection: Connection = self.dbs.connection.get(id)
                   .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
                prover.update_state(&connection)?;
                self.dbs.prover.set(&id, &prover)?;
                let state = _get_state_prover(&prover);
                Ok(json!({ "state": state }).to_string())
            }
            None => match self.dbs.verifier.get::<Verifier>(id) {
                None => {
                    let mut presentation_requests: Vec<VcxPresentationRequest> = Vec::new();
                    for cid in connection_ids.into_iter() {
                        let connection = self.dbs.connection.get::<Connection>(&cid).unwrap();
                        let mut _presentation_requests: Vec<VcxPresentationRequest> = connection.get_messages_noauth()?
                            .into_iter()
                            .filter_map(|(uid, message)| {
                                match message {
                                    A2AMessage::PresentationRequest(presentation_request) => {
                                        connection.update_message_status(uid).ok()?;
                                        self.dbs.connection.set(&id, &connection).unwrap();
                                        Some(presentation_request)
                                    }
                                    _ => None
                                }
                            }).collect();
                        presentation_requests.append(&mut _presentation_requests);
                    }
                    soft_assert_eq!(presentation_requests.len(), 1);
                    let presentation_request = presentation_requests.first()
                       .ok_or(
                           HarnessError::from_msg(HarnessErrorType::InternalServerError, &format!("Did not obtain presentation request message"))
                       )?;
                    let prover = Prover::create_from_request(id, presentation_request.clone())?;
                    self.dbs.prover.set(&id, &prover)?;
                    let state = _get_state_prover(&prover);
                    Ok(json!({ "state": state }).to_string())
               }
               Some(mut verifier) => {
                   let connection: Connection = self.dbs.connection.get(id)
                       .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
                    verifier.update_state(&connection)?;
                    self.dbs.verifier.set(&id, &verifier)?;
                    let state = _get_state_verifier(&verifier);
                    Ok(json!({ "state": state }).to_string())
               }
            }
        }
    } 
}

#[post("/send-request")]
pub async fn send_proof_request(req: web::Json<Request<PresentationRequestWrapper>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().send_proof_request(&req.data)
        .with_header("Cache-Control", "private, no-store, must-revalidate")
}

#[post("/send-proposal")]
pub async fn send_proof_proposal(req: web::Json<Request<PresentationProposalWrapper>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().send_proof_proposal(&req.data)
        .with_header("Cache-Control", "private, no-store, must-revalidate")
}

#[post("/send-presentation")]
pub async fn send_presentation(req: web::Json<Request<serde_json::Value>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().send_presentation(&req.id)
        .with_header("Cache-Control", "private, no-store, must-revalidate")
}

#[post("/verify-presentation")]
pub async fn verify_presentation(req: web::Json<Request<serde_json::Value>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().verify_presentation(&req.id)
        .with_header("Cache-Control", "private, no-store, must-revalidate")
}

#[get("/{proof_id}")]
pub async fn get_proof(agent: web::Data<Mutex<Agent>>, path: web::Path<String>) -> impl Responder {
    agent.lock().unwrap().get_proof(&path.into_inner())
        .with_header("Cache-Control", "private, no-store, must-revalidate")
}
pub fn config(cfg: &mut web::ServiceConfig) {
    cfg
        .service(
            web::scope("/command/proof")
                .service(send_proof_request)
                .service(send_proof_proposal)
                .service(send_presentation)
                .service(verify_presentation)
                .service(get_proof)
        );
}
