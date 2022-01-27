use std::sync::Mutex;
use std::collections::HashMap;
use actix_web::{web, Responder, post, get};
use actix_web::http::header::{CacheControl, CacheDirective};
use uuid;
use crate::error::{HarnessError, HarnessErrorType, HarnessResult};
use crate::{Agent, State};
use crate::controllers::Request;
use aries_vcx::messages::proof_presentation::presentation_request::PresentationRequest as VcxPresentationRequest;
use aries_vcx::messages::a2a::A2AMessage;
use aries_vcx::messages::status::Status;
use aries_vcx::messages::proof_presentation::presentation_proposal::{PresentationProposalData, Attribute, Predicate};
use aries_vcx::handlers::proof_presentation::verifier::verifier::{Verifier, VerifierState};
use aries_vcx::handlers::proof_presentation::prover::prover::{Prover, ProverState};
use aries_vcx::handlers::connection::connection::Connection;
use aries_vcx::libindy::proofs::proof_request_internal::{AttrInfo, PredicateInfo, NonRevokedInterval};
use aries_vcx::libindy::proofs::proof_request::ProofRequestDataBuilder;
use aries_vcx::libindy::utils::anoncreds;
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
    pub proof_request: ProofRequestDataWrapper
}

#[derive(Serialize, Deserialize, Default, Debug)]
pub struct PresentationProposal {
    comment: String,
    attributes: Vec<Attribute>,
    predicates: Vec<Predicate>
}

#[derive(Serialize, Deserialize, Debug, PartialEq, Clone, Default)]
pub struct ProofRequestData {
    pub requested_attributes: Option<HashMap<String, AttrInfo>>,
    pub requested_predicates: Option<HashMap<String, PredicateInfo>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub non_revoked: Option<NonRevokedInterval>,
}

#[derive(Serialize, Deserialize, Debug, PartialEq, Clone, Default)]
pub struct ProofRequestDataWrapper {
    pub data: ProofRequestData
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
    let attach: serde_json::Value = serde_json::from_str(&attach)?;
    Ok(!attach["non_revoked"].is_null())
}

impl Agent {
    pub async fn send_proof_request(&mut self, presentation_request: &PresentationRequestWrapper) -> HarnessResult<String> {
        let id = uuid::Uuid::new_v4().to_string();
        let connection: Connection = self.dbs.connection.get(&presentation_request.connection_id)
            .unwrap_or(self.last_connection.clone().ok_or(HarnessError::from_msg(HarnessErrorType::InternalServerError, &format!("No connection established")))?);
        for (uid, message) in connection.get_messages().await?.into_iter() {
            match message {
                A2AMessage::PresentationProposal(_) => {
                    connection.update_message_status(&uid).await.ok();
                }
                _ => {}
            }
        };
        let req_data = presentation_request.presentation_request.proof_request.data.clone();
        let presentation_request = ProofRequestDataBuilder::default()
            .name("test proof")
            .requested_attributes(req_data.requested_attributes.unwrap_or_default())
            .requested_predicates(req_data.requested_predicates.unwrap_or_default())
            .non_revoked(req_data.non_revoked)
            .nonce(anoncreds::generate_nonce()?)
            .build()?;
        let mut verifier = Verifier::create_from_request(id.to_string(), &presentation_request)?;
        verifier.send_presentation_request(connection.send_message_closure()?).await?;
        soft_assert_eq!(verifier.get_state(), VerifierState::PresentationRequestSent);
        let thread_id = verifier.get_thread_id()?;
        self.dbs.verifier.set(&thread_id, &verifier)?;
        self.dbs.connection.set(&thread_id, &connection)?;
        Ok(json!({"state": _get_state_verifier(&verifier), "thread_id": thread_id}).to_string())
    }

    pub async fn send_proof_proposal(&mut self, presentation_proposal: &PresentationProposalWrapper) -> HarnessResult<String> {
        let id = uuid::Uuid::new_v4().to_string();
        let connection: Connection = self.dbs.connection.get(&presentation_proposal.connection_id)
            .unwrap_or(self.last_connection.clone().ok_or(HarnessError::from_msg(HarnessErrorType::InternalServerError, &format!("No connection established")))?);
        let mut proposal_data = PresentationProposalData::create();
        for attr in presentation_proposal.presentation_proposal.attributes.clone().into_iter() {
            proposal_data = proposal_data.add_attribute(attr.clone());
        };
        let mut prover = Prover::create(&id)?;
        prover.send_proposal(proposal_data, connection.send_message_closure()?).await?;
        soft_assert_eq!(prover.get_state(), ProverState::PresentationProposalSent);
        let thread_id = prover.get_thread_id()?;
        self.dbs.prover.set(&thread_id, &prover)?;
        Ok(json!({ "state": _get_state_prover(&prover), "thread_id": thread_id }).to_string())
    }

    pub async fn send_presentation(&mut self, id: &str) -> HarnessResult<String> {
        let mut prover: Prover = self.dbs.prover.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Prover with id {} not found", id)))?;
        let connection: Connection = self.dbs.connection.get(id)
            .unwrap_or(self.last_connection.clone().ok_or(HarnessError::from_msg(HarnessErrorType::InternalServerError, &format!("No connection established")))?);
        prover.update_state(&connection).await?;
        soft_assert_eq!(prover.get_state(), ProverState::PresentationRequestReceived);
        let credentials = prover.retrieve_credentials()?;
        let secondary_required = _secondary_proof_required(&prover)?;
        let credentials = _select_credentials(&credentials, secondary_required)?;
        prover.generate_presentation(credentials, "{}".to_string()).await?;
        prover.send_presentation(connection.send_message_closure()?).await?;
        soft_assert_eq!(prover.get_state(), ProverState::PresentationSent);
        let thread_id = prover.get_thread_id()?;
        self.dbs.prover.set(&thread_id, &prover)?;
        Ok(json!({"state": _get_state_prover(&prover), "thread_id": thread_id}).to_string())
    }

    pub async fn verify_presentation(&mut self, id: &str) -> HarnessResult<String> {
        let mut verifier: Verifier = self.dbs.verifier.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Verifier with id {} not found", id)))?;
        let connection: Connection = self.dbs.connection.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
        soft_assert_eq!(verifier.get_state(), VerifierState::PresentationRequestSent);
        verifier.update_state(&connection).await?;
        if !vec![VerifierState::Finished, VerifierState::Failed].contains(&verifier.get_state()) {
            return Err(HarnessError::from_msg(HarnessErrorType::ProtocolError, "Presentation not received"));
        }
        self.dbs.verifier.set(&verifier.get_thread_id()?, &verifier)?;
        verifier.send_ack(connection.send_message_closure()?).await?;
        let verified = match Status::from_u32(verifier.get_presentation_status()) {
            Status::Success => {
                soft_assert_eq!(verifier.get_state(), VerifierState::Finished);
                "true"
            },
            _ => "false"
        };
        Ok(json!({ "state": State::Done, "verified": verified }).to_string())
    }

    pub async fn get_proof(&mut self, id: &str) -> HarnessResult<String> {
        let connection_ids = self.dbs.connection.get_all();
        match self.dbs.prover.get::<Prover>(id) {
            Some(mut prover) => {
               let connection: Connection = self.dbs.connection.get(id)
                   .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
                prover.update_state(&connection).await?;
                self.dbs.prover.set(&prover.get_thread_id()?, &prover)?;
                let state = _get_state_prover(&prover);
                Ok(json!({ "state": state }).to_string())
            }
            None => match self.dbs.verifier.get::<Verifier>(id) {
                None => {
                    let mut presentation_requests: Vec<VcxPresentationRequest> = Vec::new();
                    for cid in connection_ids.into_iter() {
                        let connection = self.dbs.connection.get::<Connection>(&cid)
                            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
                        let mut _presentation_requests = Vec::<VcxPresentationRequest>::new();
                        for (uid, message) in connection.get_messages_noauth().await?.into_iter() {
                            match message {
                                A2AMessage::PresentationRequest(presentation_request) => {
                                    connection.update_message_status(&uid).await.ok();
                                    self.dbs.connection.set(&id, &connection)?;
                                    _presentation_requests.push(presentation_request);
                                }
                                _ => {}
                            }
                        }
                        presentation_requests.append(&mut _presentation_requests);
                    }
                    soft_assert_eq!(presentation_requests.len(), 1);
                    let presentation_request = presentation_requests.first()
                       .ok_or(
                           HarnessError::from_msg(HarnessErrorType::InternalServerError, &format!("Did not obtain presentation request message"))
                       )?;
                    let prover = Prover::create_from_request(id, presentation_request.clone())?;
                    self.dbs.prover.set(&prover.get_thread_id()?, &prover)?;
                    let state = _get_state_prover(&prover);
                    Ok(json!({ "state": state }).to_string())
               }
               Some(mut verifier) => {
                   let connection: Connection = self.dbs.connection.get(id)
                       .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
                    verifier.update_state(&connection).await?;
                    self.dbs.verifier.set(&verifier.get_thread_id()?, &verifier)?;
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
        .await
        .customize()
        .append_header(CacheControl(vec![CacheDirective::Private, CacheDirective::NoStore, CacheDirective::MustRevalidate]))
}

#[post("/send-proposal")]
pub async fn send_proof_proposal(req: web::Json<Request<PresentationProposalWrapper>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().send_proof_proposal(&req.data)
        .await
        .customize()
        .append_header(CacheControl(vec![CacheDirective::Private, CacheDirective::NoStore, CacheDirective::MustRevalidate]))
}

#[post("/send-presentation")]
pub async fn send_presentation(req: web::Json<Request<serde_json::Value>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().send_presentation(&req.id)
        .await
        .customize()
        .append_header(CacheControl(vec![CacheDirective::Private, CacheDirective::NoStore, CacheDirective::MustRevalidate]))
}

#[post("/verify-presentation")]
pub async fn verify_presentation(req: web::Json<Request<serde_json::Value>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().verify_presentation(&req.id)
        .await
        .customize()
        .append_header(CacheControl(vec![CacheDirective::Private, CacheDirective::NoStore, CacheDirective::MustRevalidate]))
}

#[get("/{proof_id}")]
pub async fn get_proof(agent: web::Data<Mutex<Agent>>, path: web::Path<String>) -> impl Responder {
    agent.lock().unwrap().get_proof(&path.into_inner())
        .await
        .customize()
        .append_header(CacheControl(vec![CacheDirective::Private, CacheDirective::NoStore, CacheDirective::MustRevalidate]))
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
