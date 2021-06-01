use std::sync::Mutex;
use actix_web::{web, Responder, post, get};
use uuid;
use crate::{Agent, State};
use crate::error::{HarnessError, HarnessErrorType, HarnessResult};
use crate::controllers::Request;
use vcx::aries::messages::connection::invite::Invitation;
use vcx::aries::handlers::connection::connection::Connection;
use vcx::api::VcxStateType;

// Unsupported test cases:
// @T005-RFC0160 - public did

#[derive(Deserialize, Default)]
struct ConnectionRequest {
    request: String
}

#[derive(Deserialize, Default)]
struct Comment {
    comment: String
}

fn _get_state(connection: &Connection) -> State {
    match VcxStateType::from_u32(connection.state()) {
        VcxStateType::VcxStateNone => State::Initial,
        VcxStateType::VcxStateInitialized => State::Invited,
        VcxStateType::VcxStateOfferSent => State::Requested,
        VcxStateType::VcxStateRequestReceived => State::Responded,
        VcxStateType::VcxStateAccepted => State::Complete,
        _ => State::Unknown
    }
}

impl Agent {
    pub fn create_invitation(&mut self) -> HarnessResult<String> {
        let id = uuid::Uuid::new_v4().to_string();
        let mut connection = Connection::create(&id, false);
        connection.connect().map_err(|err| HarnessError::from(err))?;
        let invite = connection.get_invite_details()
            .ok_or(HarnessError::from_msg(HarnessErrorType::InternalServerError, "Failed to get invite details"))?;
        self.db.set(&id, &connection).map_err(|err| HarnessError::from(err))?;
        Ok(json!({ "connection_id": id, "invitation": invite }).to_string())
    }

    pub fn receive_invitation(&mut self, invite: &str) -> HarnessResult<String> {
        let id = uuid::Uuid::new_v4().to_string();
        let invite: Invitation = serde_json::from_str(invite).map_err(|err| HarnessError::from(err))?;
        let connection = Connection::create_with_invite(&id, invite, false).map_err(|err| HarnessError::from(err))?;
        self.db.set(&id, &connection).map_err(|err| HarnessError::from(err))?;
        Ok(json!({ "connection_id": id }).to_string())
    }

    pub fn send_request(&mut self, id: &str) -> HarnessResult<String> {
        let mut connection: Connection = self.db.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
        connection.connect().map_err(|err| HarnessError::from(err))?;
        connection.update_state().map_err(|err| HarnessError::from(err))?;
        self.db.set(&id, &connection).map_err(|err| HarnessError::from(err))?;
        Ok(json!({ "connection_id": id }).to_string())
    }

    pub fn accept_request(&mut self, id: &str) -> HarnessResult<String> {
        let mut connection: Connection = self.db.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
        if connection.state() != VcxStateType::VcxStateOfferSent as u32 {
            return Err(HarnessError::from_kind(HarnessErrorType::RequestNotAcceptedError));
        }
        connection.update_state().map_err(|err| HarnessError::from(err))?;
        self.db.set(&id, &connection).map_err(|err| HarnessError::from(err))?;
        Ok(json!({ "connection_id": id }).to_string()) 
    }

    pub fn send_ping(&mut self, id: &str) -> HarnessResult<String> {
        let mut connection: Connection = self.db.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
        connection.update_state().map_err(|err| HarnessError::from(err))?;

        self.db.set(&id, &connection).map_err(|err| HarnessError::from(err))?;
        Ok(json!({ "connection_id": id }).to_string()) 
    }

    pub fn get_connection_state(&mut self, id: &str) -> HarnessResult<String> {
        let mut connection: Connection = self.db.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Connection with id {} not found", id)))?;
        if connection.needs_message() {
            connection.update_state().map_err(|err| HarnessError::from(err))?;
        }
        let state = _get_state(&connection);
        self.db.set(&id, &connection).map_err(|err| HarnessError::from(err))?;
        self.last_connection = Some(connection);
        Ok(json!({ "state": state }).to_string())
    }
}

#[post("/create-invitation")]
pub async fn create_invitation(agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().create_invitation()
}

#[post("/receive-invitation")]
pub async fn receive_invitation(req: web::Json<Request<String>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().receive_invitation(&req.data)
}

#[post("/accept-invitation")]
pub async fn send_request(req: web::Json<Request<()>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().send_request(&req.id)
}

#[post("/accept-request")]
pub async fn accept_request(req: web::Json<Request<()>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().accept_request(&req.id)
}

#[get("/{connection_id}")]
pub async fn get_connection_state(agent: web::Data<Mutex<Agent>>, path: web::Path<String>) -> impl Responder {
    agent.lock().unwrap().get_connection_state(&path.into_inner())
        .with_header("Cache-Control", "private, no-store, must-revalidate")
}

#[post("/send-ping")]
pub async fn send_ping(req: web::Json<Request<Comment>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().send_ping(&req.id)
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
        );
}
