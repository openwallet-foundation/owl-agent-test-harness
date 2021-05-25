use std::sync::Mutex;
use actix_web::{web, HttpResponse, HttpRequest, Responder, post, get};
use crate::{Agent, State};
use crate::controllers::Request;

impl Agent {
    pub fn get_status_json(&self) -> std::io::Result<String> {
        Ok(json!({ "status": self.status }).to_string())
    }

    pub fn get_state_json(&self) -> std::io::Result<String> {
        Ok(json!({ "state": self.state }).to_string())
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

pub fn config(cfg: &mut web::ServiceConfig) {
    cfg
        .service(
            web::scope("/command")
                .service(get_status)
                .service(get_version)
        );
}
