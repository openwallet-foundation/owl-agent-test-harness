use std::sync::Mutex;
use actix_web::{web, Responder, post, get};
use actix_web::http::header::{CacheControl, CacheDirective};
use uuid;
use crate::{Agent, State};
use crate::error::{HarnessError, HarnessErrorType, HarnessResult};
use crate::controllers::Request;
use aries_vcx::messages::a2a::A2AMessage;
use aries_vcx::messages::connection::invite::{Invitation, PairwiseInvitation};
use aries_vcx::messages::connection::request::Request as VcxConnectionRequest;
use aries_vcx::handlers::connection::connection::{Connection, ConnectionState};
use aries_vcx::handlers::connection::invitee::state_machine::InviteeState;
use aries_vcx::handlers::connection::inviter::state_machine::InviterState;

#[allow(dead_code)]
#[derive(Deserialize, Default)]
pub struct ConnectionRequest {
    request: String
}

#[allow(dead_code)]
#[derive(Deserialize, Default)]
pub struct Comment {
    comment: String
}

fn _get_state(connection: &Connection) -> State {
    match connection.get_state() {
        ConnectionState::Invitee(state) => match state {
            InviteeState::Initial => State::Initial,
            InviteeState::Invited => State::Invited,
            InviteeState::Requested => State::Requested,
            InviteeState::Responded => State::Responded,
            InviteeState::Completed => State::Complete
        }
        ConnectionState::Inviter(state) => match state {
            InviterState::Initial => State::Initial,
            InviterState::Invited => State::Invited,
            InviterState::Requested => State::Requested,
            InviterState::Responded => State::Responded,
            InviterState::Completed => State::Complete
        }
    }
}

async fn get_requests(connection: &Connection) -> HarnessResult<Vec<VcxConnectionRequest>> {
     Ok(connection.get_messages_noauth()
        .await?
        .into_iter()
        .filter_map(|(_, message)| {
            match message {
                A2AMessage::ConnectionRequest(request) => Some(request),
                _ => None
            }
        }).collect())
}

impl Agent {
    pub async fn create_invitation(&mut self) -> HarnessResult<String> {
        let id = uuid::Uuid::new_v4().to_string();
        let mut connection = Connection::create(&id, false).await?;
        connection.connect().await?;
        let invite = connection.get_invite_details()
            .ok_or(HarnessError::from_msg(HarnessErrorType::InternalServerError, "Failed to get invite details"))?;
        let thread_id = connection.get_thread_id();
        self.dbs.connection.set(&id, &connection)?;
        self.dbs.connection.set(&thread_id, &connection)?;
        Ok(json!({ "connection_id": id, "invitation": invite }).to_string())
    }

    pub async fn receive_invitation(&mut self, invite: PairwiseInvitation) -> HarnessResult<String> {
        let id = uuid::Uuid::new_v4().to_string();
        let connection = Connection::create_with_invite(&id, Invitation::Pairwise(invite), false).await?;
        let thread_id = connection.get_thread_id();
        self.dbs.connection.set(&id, &connection)?;
        self.dbs.connection.set(&thread_id, &connection)?;
        Ok(json!({ "connection_id": id }).to_string())
    }

    pub async fn send_request(&mut self, id: &str) -> HarnessResult<String> {
        let mut connection: Connection = self.dbs.connection.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
        connection.connect().await?;
        connection.update_state().await?;
        let thread_id = connection.get_thread_id();
        self.dbs.connection.set(&id, &connection)?;
        self.dbs.connection.set(&thread_id, &connection)?;
        Ok(json!({ "connection_id": id }).to_string())
    }

    pub async fn accept_request(&mut self, id: &str) -> HarnessResult<String> {
        let mut connection: Connection = self.dbs.connection.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
        let requests = get_requests(&connection).await?;
        let curr_state = connection.get_state();
        if curr_state != ConnectionState::Inviter(InviterState::Invited) || requests.len() > 1 {
            return Err(HarnessError::from_msg(HarnessErrorType::RequestNotAcceptedError, &format!("Received state {:?}, expected requested state", curr_state)));
        }
        connection.update_state().await?;
        let thread_id = connection.get_thread_id();
        self.dbs.connection.set(&id, &connection)?;
        self.dbs.connection.set(&thread_id, &connection)?;
        Ok(json!({ "connection_id": id }).to_string()) 
    }

    pub async fn send_ping(&mut self, id: &str) -> HarnessResult<String> {
        let mut connection: Connection = self.dbs.connection.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
        connection.update_state().await?;
        let thread_id = connection.get_thread_id();
        self.dbs.connection.set(&id, &connection)?;
        self.dbs.connection.set(&thread_id, &connection)?;
        Ok(json!({ "connection_id": id }).to_string()) 
    }

    pub async fn get_connection_state(&mut self, id: &str) -> HarnessResult<String> {
        let mut connection: Connection = self.dbs.connection.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
        if connection.needs_message() {
            connection.update_state().await?;
        }
        let state = _get_state(&connection);
        let thread_id = connection.get_thread_id();
        self.dbs.connection.set(&id, &connection)?;
        self.dbs.connection.set(&thread_id, &connection)?;
        self.last_connection = Some(connection);
        Ok(json!({ "state": state }).to_string())
    }

    pub async fn get_connection(&mut self, thread_id: &str) -> HarnessResult<String> {
        let connection: Connection = self.dbs.connection.get(thread_id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with thread id {} not found", thread_id)))?;
        let connection_id = connection.get_source_id();
        Ok(json!({ "connection_id": connection_id }).to_string())
    }
}

#[post("/create-invitation")]
pub async fn create_invitation(agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().create_invitation()
        .await
        .customize()
        .append_header(CacheControl(vec![CacheDirective::Private, CacheDirective::NoStore, CacheDirective::MustRevalidate]))
}

#[post("/receive-invitation")]
pub async fn receive_invitation(req: web::Json<Request<PairwiseInvitation>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().receive_invitation(req.data.clone())
        .await
        .customize()
        .append_header(CacheControl(vec![CacheDirective::Private, CacheDirective::NoStore, CacheDirective::MustRevalidate]))
}

#[post("/accept-invitation")]
pub async fn send_request(req: web::Json<Request<()>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().send_request(&req.id)
        .await
        .customize()
        .append_header(CacheControl(vec![CacheDirective::Private, CacheDirective::NoStore, CacheDirective::MustRevalidate]))
}

#[post("/accept-request")]
pub async fn accept_request(req: web::Json<Request<()>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().accept_request(&req.id)
        .await
        .customize()
        .append_header(CacheControl(vec![CacheDirective::Private, CacheDirective::NoStore, CacheDirective::MustRevalidate]))
}

#[get("/{connection_id}")]
pub async fn get_connection_state(agent: web::Data<Mutex<Agent>>, path: web::Path<String>) -> impl Responder {
    agent.lock().unwrap().get_connection_state(&path.into_inner())
        .await
        .customize()
        .append_header(CacheControl(vec![CacheDirective::Private, CacheDirective::NoStore, CacheDirective::MustRevalidate]))
}

#[get("/{thread_id}")]
pub async fn get_connection(agent: web::Data<Mutex<Agent>>, path: web::Path<String>) -> impl Responder {
    agent.lock().unwrap().get_connection(&path.into_inner())
        .await
        .customize()
        .append_header(CacheControl(vec![CacheDirective::Private, CacheDirective::NoStore, CacheDirective::MustRevalidate]))
}

#[post("/send-ping")]
pub async fn send_ping(req: web::Json<Request<Comment>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().send_ping(&req.id)
        .await
        .customize()
        .append_header(CacheControl(vec![CacheDirective::Private, CacheDirective::NoStore, CacheDirective::MustRevalidate]))
}
 
pub fn config(cfg: &mut web::ServiceConfig) {
    cfg
        .service(
            web::scope("/command/connection")
                .service(create_invitation)
                .service(receive_invitation)
                .service(send_request)
                .service(accept_request)
                .service(send_ping)
                .service(get_connection_state)
        )
        .service(
            web::scope("/response/connection")
                .service(get_connection)
        );
}
