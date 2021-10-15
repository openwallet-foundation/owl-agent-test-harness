use std::sync::Mutex;
use actix_web::{web, HttpResponse, Responder, get};
use crate::Agent;
use crate::error::HarnessResult;

impl Agent {
    pub fn get_status_json(&self) -> HarnessResult<String> {
        Ok(json!({ "status": self.status }).to_string())
    }

    pub fn get_state_json(&self) -> HarnessResult<String> {
        Ok(json!({ "state": self.state }).to_string())
    }

    pub fn get_public_did(&self) -> HarnessResult<String> {
        Ok(json!({ "did": self.config.did.to_string() }).to_string())
    }
}

#[get("/status")]
pub async fn get_status(agent: web::Data<Mutex<Agent>>) -> impl Responder {
    HttpResponse::Ok()
        .body(
            agent.lock().unwrap().get_status_json().unwrap()
        )
}

#[get("/version")]
pub async fn get_version() -> impl Responder {
    HttpResponse::Ok().body("1.0.0")
}

#[get("/did")]
pub async fn get_public_did(agent: web::Data<Mutex<Agent>>) -> impl Responder {
    HttpResponse::Ok()
        .body(
            agent.lock().unwrap().get_public_did().unwrap()
        )
}

pub fn config(cfg: &mut web::ServiceConfig) {
    cfg
        .service(
            web::scope("/command")
                .service(get_status)
                .service(get_version)
                .service(get_public_did)
        );
}
