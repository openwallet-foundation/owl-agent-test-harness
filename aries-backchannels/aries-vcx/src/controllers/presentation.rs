use crate::controllers::Request;
use crate::error::{HarnessError, HarnessErrorType, HarnessResult};
use crate::soft_assert_eq;
use crate::{HarnessAgent, State};
use actix_web::{get, post, web, Responder};
use aries_vcx_agent::aries_vcx::indy::anoncreds;
use aries_vcx_agent::aries_vcx::indy::proofs::proof_request::ProofRequestDataBuilder;
use aries_vcx_agent::aries_vcx::indy::proofs::proof_request_internal::{
    AttrInfo, NonRevokedInterval, PredicateInfo,
};
use aries_vcx_agent::aries_vcx::messages::proof_presentation::presentation_proposal::{
    Attribute, Predicate, PresentationProposalData,
};
use aries_vcx_agent::aries_vcx::messages::status::Status;
use aries_vcx_agent::aries_vcx::protocols::proof_presentation::prover::state_machine::ProverState;
use aries_vcx_agent::aries_vcx::protocols::proof_presentation::verifier::state_machine::VerifierState;
use std::collections::HashMap;
use std::sync::Mutex;

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
        VerifierState::PresentationRequestSent => State::RequestSent,
        VerifierState::Finished => State::Done,
        _ => State::Unknown,
    }
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
        let id = self
            .aries_agent
            .verifier()
            .send_proof_request(
                &presentation_request.connection_id,
                presentation_request_data,
            )
            .await?;
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
        let id = self
            .aries_agent
            .prover()
            .send_proof_proposal(&presentation_proposal.connection_id, proposal_data)
            .await?;
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
        soft_assert_eq!(
            self.aries_agent.verifier().get_state(id)?,
            VerifierState::PresentationRequestSent
        );
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
        } else {
            let requests = self
                .aries_agent
                .connections()
                .get_all_proof_requests()
                .await?;
            soft_assert_eq!(requests.len(), 1);
            let id = self
                .aries_agent
                .prover()
                .create_from_request(&requests.last().unwrap().1, requests.last().unwrap().0.clone())?;
            to_backchannel_state_prover(self.aries_agent.prover().get_state(&id)?)
        };
        Ok(json!({ "state": state }).to_string())
    }
}

#[post("/send-request")]
pub async fn send_proof_request(
    req: web::Json<Request<PresentationRequestWrapper>>,
    agent: web::Data<Mutex<HarnessAgent>>,
) -> impl Responder {
    agent.lock().unwrap().send_proof_request(&req.data).await
}

#[post("/send-proposal")]
pub async fn send_proof_proposal(
    req: web::Json<Request<PresentationProposalWrapper>>,
    agent: web::Data<Mutex<HarnessAgent>>,
) -> impl Responder {
    agent.lock().unwrap().send_proof_proposal(&req.data).await
}

#[post("/send-presentation")]
pub async fn send_presentation(
    req: web::Json<Request<serde_json::Value>>,
    agent: web::Data<Mutex<HarnessAgent>>,
) -> impl Responder {
    agent.lock().unwrap().send_presentation(&req.id).await
}

#[post("/verify-presentation")]
pub async fn verify_presentation(
    req: web::Json<Request<serde_json::Value>>,
    agent: web::Data<Mutex<HarnessAgent>>,
) -> impl Responder {
    agent.lock().unwrap().verify_presentation(&req.id).await
}

#[get("/{proof_id}")]
pub async fn get_proof_state(
    agent: web::Data<Mutex<HarnessAgent>>,
    path: web::Path<String>,
) -> impl Responder {
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
