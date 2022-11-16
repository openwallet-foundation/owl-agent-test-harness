use crate::controllers::Request;
use crate::error::{HarnessError, HarnessErrorType, HarnessResult};
use crate::{soft_assert_eq, HarnessAgent, State};
use actix_web::{get, post, web, Responder};
use aries_vcx_agent::aries_vcx::handlers::connection::connection::ConnectionState;
use aries_vcx_agent::aries_vcx::messages::ack::Ack;
use aries_vcx_agent::aries_vcx::messages::connection::invite::{Invitation, PairwiseInvitation};
use aries_vcx_agent::aries_vcx::protocols::connection::invitee::state_machine::InviteeState;
use aries_vcx_agent::aries_vcx::protocols::connection::inviter::state_machine::InviterState;
use std::sync::RwLock;

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
    pub async fn create_invitation(&self) -> HarnessResult<String> {
        let invitation = self.aries_agent.connections().create_invitation().await?;
        let id = invitation.get_id()?;
        Ok(json!({ "connection_id": id, "invitation": invitation }).to_string())
    }

    pub async fn receive_invitation(
        &self,
        invite: PairwiseInvitation,
    ) -> HarnessResult<String> {
        let id = self
            .aries_agent
            .connections()
            .receive_invitation(Invitation::Pairwise(invite))
            .await?;
        Ok(json!({ "connection_id": id }).to_string())
    }

    pub async fn send_request(&self, id: &str) -> HarnessResult<String> {
        self.aries_agent.connections().send_request(id).await?;
        Ok(json!({ "connection_id": id }).to_string())
    }

    pub async fn accept_request(&self, id: &str) -> HarnessResult<String> {
        // TODO: Handle case of multiple requests received
        if self.aries_agent.connections().get_state(id)?
            != ConnectionState::Inviter(InviterState::Requested)
        {
            return Err(HarnessError::from_kind(
                HarnessErrorType::RequestNotReceived,
            ));
        }
        self.aries_agent.connections().send_response(id).await?;
        Ok(json!({ "connection_id": id }).to_string())
    }

    pub async fn send_ack(&self, id: &str) -> HarnessResult<String> {
        self.aries_agent.connections().send_ack(id).await?;
        Ok(json!({ "connection_id": id }).to_string())
    }

    pub async fn process_ack(&self, ack: Ack) -> HarnessResult<String> {
        let id = ack.get_thread_id();
        self.aries_agent.connections().process_ack(&id, ack).await?;
        Ok(json!({ "connection_id": id }).to_string())
    }

    pub async fn get_connection_state(&self, id: &str) -> HarnessResult<String> {
        let state = to_backchannel_state(self.aries_agent.connections().get_state(id)?);
        Ok(json!({ "state": state }).to_string())
    }

    pub async fn get_connection(&self, id: &str) -> HarnessResult<String> {
        soft_assert_eq!(self.aries_agent.connections().exists_by_id(id), true);
        Ok(json!({ "connection_id": id }).to_string())
    }
}

#[post("/create-invitation")]
pub async fn create_invitation(agent: web::Data<RwLock<HarnessAgent>>) -> impl Responder {
    agent.read().unwrap().create_invitation().await
}

#[post("/receive-invitation")]
pub async fn receive_invitation(
    req: web::Json<Request<PairwiseInvitation>>,
    agent: web::Data<RwLock<HarnessAgent>>,
) -> impl Responder {
    agent
        .read()
        .unwrap()
        .receive_invitation(req.data.clone())
        .await
}

#[post("/accept-invitation")]
pub async fn send_request(
    req: web::Json<Request<()>>,
    agent: web::Data<RwLock<HarnessAgent>>,
) -> impl Responder {
    agent.read().unwrap().send_request(&req.id).await
}

#[post("/accept-request")]
pub async fn accept_request(
    req: web::Json<Request<()>>,
    agent: web::Data<RwLock<HarnessAgent>>,
) -> impl Responder {
    agent.read().unwrap().accept_request(&req.id).await
}

#[get("/{connection_id}")]
pub async fn get_connection_state(
    agent: web::Data<RwLock<HarnessAgent>>,
    path: web::Path<String>,
) -> impl Responder {
    agent
        .read()
        .unwrap()
        .get_connection_state(&path.into_inner())
        .await
}

#[get("/{thread_id}")]
pub async fn get_connection(
    agent: web::Data<RwLock<HarnessAgent>>,
    path: web::Path<String>,
) -> impl Responder {
    agent
        .read()
        .unwrap()
        .get_connection(&path.into_inner())
        .await
}

#[post("/send-ping")]
pub async fn send_ack(
    req: web::Json<Request<Comment>>,
    agent: web::Data<RwLock<HarnessAgent>>,
) -> impl Responder {
    agent.read().unwrap().send_ack(&req.id).await
}

pub fn config(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::scope("/command/connection")
            .service(create_invitation)
            .service(receive_invitation)
            .service(send_request)
            .service(accept_request)
            .service(send_ack)
            .service(get_connection_state),
    )
    .service(web::scope("/response/connection").service(get_connection));
}
