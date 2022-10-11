use crate::controllers::Request;
use crate::error::{HarnessError, HarnessErrorType, HarnessResult};
use crate::{State, HarnessAgent};
use actix_web::http::header::{CacheControl, CacheDirective};
use actix_web::{get, post, web, Responder};
use aries_vcx_agent::aries_vcx::agency_client::agency_client::AgencyClient;
use aries_vcx_agent::aries_vcx::handlers::connection::connection::{Connection, ConnectionState};
use aries_vcx_agent::aries_vcx::indy::ledger::transactions::into_did_doc;
use aries_vcx_agent::aries_vcx::messages::a2a::A2AMessage;
use aries_vcx_agent::aries_vcx::messages::connection::invite::{Invitation, PairwiseInvitation};
use aries_vcx_agent::aries_vcx::messages::connection::request::Request as VcxConnectionRequest;
use aries_vcx_agent::aries_vcx::protocols::connection::invitee::state_machine::InviteeState;
use aries_vcx_agent::aries_vcx::protocols::connection::inviter::state_machine::InviterState;
use std::sync::Mutex;
use uuid;

#[allow(dead_code)]
#[derive(Deserialize, Default)]
pub struct ConnectionRequest {
    request: String,
}

#[allow(dead_code)]
#[derive(Deserialize, Default)]
pub struct Comment {
    comment: String,
}

fn to_backchannel_state(state: ConnectionState) -> State {
    match state {
        ConnectionState::Invitee(state) => match state {
            InviteeState::Initial => State::Initial,
            InviteeState::Invited => State::Invited,
            InviteeState::Requested => State::Requested,
            InviteeState::Responded => State::Responded,
            InviteeState::Completed => State::Complete,
        },
        ConnectionState::Inviter(state) => match state {
            InviterState::Initial => State::Initial,
            InviterState::Invited => State::Invited,
            InviterState::Requested => State::Requested,
            InviterState::Responded => State::Responded,
            InviterState::Completed => State::Complete,
        },
    }
}

impl HarnessAgent {
    pub async fn create_invitation(&mut self) -> HarnessResult<String> {
        let invitation = self.aries_agent.connections().create_invitation().await?;
        let id = invitation.get_id()?;
        Ok(json!({ "connection_id": id, "invitation": invitation }).to_string())
    }

    pub async fn receive_invitation(
        &mut self,
        invite: PairwiseInvitation,
    ) -> HarnessResult<String> {
        let id = self.aries_agent.connections().receive_invitation(Invitation::Pairwise(invite)).await?;
        Ok(json!({ "connection_id": id }).to_string())

    }

    pub async fn send_request(&mut self, id: &str) -> HarnessResult<String> {
        self.aries_agent.connections().send_request(id).await?;
        Ok(json!({ "connection_id": id }).to_string()) 
    }

    pub async fn accept_request(&mut self, id: &str) -> HarnessResult<String> {
        let mut requests = self.aries_agent.connections().get_requests(id).await?;
        if self.aries_agent.connections().get_state(id)? != ConnectionState::Inviter(InviterState::Invited) || requests.len() > 1 {
            return Err(HarnessError::from_kind(HarnessErrorType::RequestNotReceived));
        }
        self.aries_agent.connections().accept_request(id, requests.pop().unwrap()).await?;
        Ok(json!({ "connection_id": id }).to_string()) 
    }

    pub async fn send_ping(&mut self, id: &str) -> HarnessResult<String> {
        // self.aries_agent.connections().send_ping(id).await?;
        self.aries_agent.connections().update_state(id).await?;
        Ok(json!({ "connection_id": id }).to_string()) 
    }

    pub async fn get_connection_state(&mut self, id: &str) -> HarnessResult<String> {
        let state = to_backchannel_state(self.aries_agent.connections().update_state(id).await?);
        Ok(json!({ "state": state }).to_string())
    }

    pub async fn get_connection(&mut self, id: &str) -> HarnessResult<String> {
        self.aries_agent.connections().get_by_id(id)?;
        Ok(json!({ "connection_id": id }).to_string()) 
    }
}

#[post("/create-invitation")]
pub async fn create_invitation(agent: web::Data<Mutex<HarnessAgent>>) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .create_invitation()
        .await
}

#[post("/receive-invitation")]
pub async fn receive_invitation(
    req: web::Json<Request<PairwiseInvitation>>,
    agent: web::Data<Mutex<HarnessAgent>>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .receive_invitation(req.data.clone())
        .await
}

#[post("/accept-invitation")]
pub async fn send_request(
    req: web::Json<Request<()>>,
    agent: web::Data<Mutex<HarnessAgent>>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .send_request(&req.id)
        .await
}

#[post("/accept-request")]
pub async fn accept_request(
    req: web::Json<Request<()>>,
    agent: web::Data<Mutex<HarnessAgent>>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .accept_request(&req.id)
        .await
}

#[get("/{connection_id}")]
pub async fn get_connection_state(
    agent: web::Data<Mutex<HarnessAgent>>,
    path: web::Path<String>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .get_connection_state(&path.into_inner())
        .await
}

#[get("/{thread_id}")]
pub async fn get_connection(
    agent: web::Data<Mutex<HarnessAgent>>,
    path: web::Path<String>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .get_connection(&path.into_inner())
        .await
}

#[post("/send-ping")]
pub async fn send_ping(
    req: web::Json<Request<Comment>>,
    agent: web::Data<Mutex<HarnessAgent>>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .send_ping(&req.id)
        .await
}

pub fn config(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::scope("/command/connection")
            .service(create_invitation)
            .service(receive_invitation)
            .service(send_request)
            .service(accept_request)
            .service(send_ping)
            .service(get_connection_state),
    )
    .service(web::scope("/response/connection").service(get_connection));
}
