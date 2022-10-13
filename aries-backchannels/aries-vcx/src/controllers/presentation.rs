use crate::controllers::Request;
use crate::error::{HarnessError, HarnessErrorType, HarnessResult};
use crate::soft_assert_eq;
use crate::{HarnessAgent, State};
use actix_web::http::header::{CacheControl, CacheDirective};
use actix_web::{get, post, web, Responder};
use aries_vcx_agent::aries_vcx::agency_client::agency_client::AgencyClient;
use aries_vcx_agent::aries_vcx::handlers::connection::connection::Connection;
use aries_vcx_agent::aries_vcx::handlers::proof_presentation::prover::Prover;
use aries_vcx_agent::aries_vcx::handlers::proof_presentation::verifier::Verifier;
use aries_vcx_agent::aries_vcx::indy::anoncreds;
use aries_vcx_agent::aries_vcx::indy::proofs::proof_request::ProofRequestDataBuilder;
use aries_vcx_agent::aries_vcx::indy::proofs::proof_request_internal::{
    AttrInfo, NonRevokedInterval, PredicateInfo,
};
use aries_vcx_agent::aries_vcx::messages::a2a::A2AMessage;
use aries_vcx_agent::aries_vcx::messages::proof_presentation::presentation_proposal::{
    Attribute, Predicate, PresentationProposalData,
};
use aries_vcx_agent::aries_vcx::messages::proof_presentation::presentation_request::PresentationRequest as VcxPresentationRequest;
use aries_vcx_agent::aries_vcx::messages::status::Status;
use aries_vcx_agent::aries_vcx::protocols::proof_presentation::prover::state_machine::ProverState;
use aries_vcx_agent::aries_vcx::protocols::proof_presentation::verifier::state_machine::VerifierState;
use std::collections::HashMap;
use std::sync::Mutex;
use uuid;

#[derive(Serialize, Deserialize, Default, Debug)]
pub struct PresentationRequestWrapper {
    connection_id: String,
    presentation_request: PresentationRequest,
}

#[derive(Serialize, Deserialize, Default, Debug)]
pub struct PresentationProposalWrapper {
    connection_id: String,
    presentation_proposal: PresentationProposal,
}

#[derive(Debug, Deserialize, Serialize, Clone, PartialEq, Default)]
pub struct PresentationRequest {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub comment: Option<String>,
    pub proof_request: ProofRequestDataWrapper,
}

#[derive(Serialize, Deserialize, Default, Debug)]
pub struct PresentationProposal {
    comment: String,
    attributes: Vec<Attribute>,
    predicates: Vec<Predicate>,
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
    pub data: ProofRequestData,
}

fn to_backchannel_state_prover(state: ProverState) -> State {
    match state {
        ProverState::Initial => State::Initial,
        ProverState::PresentationRequestReceived => State::RequestReceived,
        ProverState::PresentationProposalSent => State::ProposalSent,
        ProverState::PresentationSent => State::PresentationSent,
        ProverState::PresentationPreparationFailed
        | ProverState::Finished
        | ProverState::Failed => State::Done,
        _ => State::Unknown,
    }
}

fn to_backchannel_state_verifier(state: VerifierState) -> State {
    match state {
        VerifierState::Initial => State::Initial,
        VerifierState::PresentationRequestSet => State::RequestSet,
        VerifierState::PresentationProposalReceived => State::ProposalReceived,
        VerifierState::PresentationRequestSent => State::OfferSent,
        VerifierState::Finished => State::Done,
        _ => State::Unknown,
    }
}

fn _select_credentials(resolved_creds: &str, secondary_required: bool) -> HarnessResult<String> {
    let resolved_creds: HashMap<String, HashMap<String, serde_json::Value>> =
        serde_json::from_str(resolved_creds)?;
    let resolved_creds: HashMap<String, serde_json::Value> = resolved_creds
        .get("attrs")
        .ok_or(HarnessError::from_msg(
            HarnessErrorType::InternalServerError,
            &format!("No attrs in resolved_creds: {:?}", resolved_creds),
        ))?
        .clone();
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
                if !attr_cred_info.is_empty() {
                    selected_creds
                        .get_mut("attrs")
                        .unwrap()
                        .insert(String::from(attr_name), to_insert);
                }
            }
            _ => {
                return Err(HarnessError::from_msg(
                    HarnessErrorType::InternalServerError,
                    &format!(
                        "Unexpected data, expected attr_cred_info to be an array, but got {:?}.",
                        attr_cred_info
                    ),
                ))
            }
        }
    }
    serde_json::to_string(&selected_creds).map_err(HarnessError::from)
}

fn _secondary_proof_required(prover: &Prover) -> HarnessResult<bool> {
    let attach = prover.get_proof_request_attachment()?;
    let attach: serde_json::Value = serde_json::from_str(&attach)?;
    Ok(!attach["non_revoked"].is_null())
}

impl HarnessAgent {
    pub async fn send_proof_request(
        &mut self,
        presentation_request: &PresentationRequestWrapper,
    ) -> HarnessResult<String> {
        let req_data = presentation_request
            .presentation_request
            .proof_request
            .data
            .clone();
        let presentation_request_data = ProofRequestDataBuilder::default()
            .name("test proof")
            .requested_attributes(req_data.requested_attributes.unwrap_or_default())
            .requested_predicates(req_data.requested_predicates.unwrap_or_default())
            .non_revoked(req_data.non_revoked)
            .nonce(anoncreds::generate_nonce().await?)
            .build()?;
        let id = self.aries_agent.verifier().send_proof_request(&presentation_request.connection_id, presentation_request_data).await?;
        let state = self.aries_agent.verifier().get_state(&id)?;
        Ok(json!({"state": to_backchannel_state_verifier(state), "thread_id": id}).to_string())
    }

    pub async fn send_proof_proposal(
        &mut self,
        presentation_proposal: &PresentationProposalWrapper,
    ) -> HarnessResult<String> {
        let mut proposal_data = PresentationProposalData::create();
        for attr in presentation_proposal
            .presentation_proposal
            .attributes
            .clone()
            .into_iter()
        {
            proposal_data = proposal_data.add_attribute(attr.clone());
        }
        let id = self.aries_agent.prover().send_proof_proposal(&presentation_proposal.connection_id, proposal_data).await?; 
        let state = self.aries_agent.prover().get_state(&id)?;
        Ok(json!({ "state": to_backchannel_state_prover(state), "thread_id": id }).to_string())
    }

    pub async fn send_presentation(&mut self, id: &str) -> HarnessResult<String> {
        let state = self.aries_agent.prover().update_state(id).await?;
        soft_assert_eq!(state, ProverState::PresentationRequestReceived);
        self.aries_agent.prover().send_proof_prentation(id).await?;
        let state = self.aries_agent.prover().get_state(id)?;
        Ok(json!({"state": to_backchannel_state_prover(state), "thread_id": id}).to_string())
    }

    pub async fn verify_presentation(&mut self, id: &str) -> HarnessResult<String> {
        soft_assert_eq!(self.aries_agent.verifier().get_state(id)?, VerifierState::PresentationRequestSent);
        let state = self.aries_agent.verifier().update_state(id).await?;
        soft_assert_eq!(state, VerifierState::Finished);
        let verified = self.aries_agent.verifier().verify_presentation(id)? == Status::Success;
        Ok(json!({ "state": State::Done, "verified": verified }).to_string())
    }

    pub async fn get_proof_state(&mut self, id: &str) -> HarnessResult<String> {
        let state = if self.aries_agent.verifier().exists_by_id(&id) {
            to_backchannel_state_verifier(self.aries_agent.verifier().update_state(&id).await?)
        } else if self.aries_agent.prover().exists_by_id(&id) {
            to_backchannel_state_prover(self.aries_agent.prover().update_state(&id).await?)
        } else if self.aries_agent.verifier().exists_by_id(&id) {
            to_backchannel_state_verifier(self.aries_agent.verifier().update_state(&id).await?)
        } else if let Some(connection_id) = &self.last_connection_id {
            let mut requests = self.aries_agent.connections().get_proof_requests(connection_id).await?;
            soft_assert_eq!(requests.len(), 1);
            let id = self.aries_agent.prover().create_from_request(connection_id, requests.pop().unwrap())?;
            to_backchannel_state_prover(self.aries_agent.prover().get_state(&id)?)
        } else {
            return Err(HarnessError::from_kind(HarnessErrorType::NotFoundError));
        };
        Ok(json!({ "state": state }).to_string())
    }
}

#[post("/send-request")]
pub async fn send_proof_request(
    req: web::Json<Request<PresentationRequestWrapper>>,
    agent: web::Data<Mutex<HarnessAgent>>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .send_proof_request(&req.data)
        .await
}

#[post("/send-proposal")]
pub async fn send_proof_proposal(
    req: web::Json<Request<PresentationProposalWrapper>>,
    agent: web::Data<Mutex<HarnessAgent>>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .send_proof_proposal(&req.data)
        .await
}

#[post("/send-presentation")]
pub async fn send_presentation(
    req: web::Json<Request<serde_json::Value>>,
    agent: web::Data<Mutex<HarnessAgent>>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .send_presentation(&req.id)
        .await
}

#[post("/verify-presentation")]
pub async fn verify_presentation(
    req: web::Json<Request<serde_json::Value>>,
    agent: web::Data<Mutex<HarnessAgent>>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .verify_presentation(&req.id)
        .await
}

#[get("/{proof_id}")]
pub async fn get_proof_state(agent: web::Data<Mutex<HarnessAgent>>, path: web::Path<String>) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .get_proof_state(&path.into_inner())
        .await
}

pub fn config(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::scope("/command/proof")
            .service(send_proof_request)
            .service(send_proof_proposal)
            .service(send_presentation)
            .service(verify_presentation)
            .service(get_proof_state),
    );
}
