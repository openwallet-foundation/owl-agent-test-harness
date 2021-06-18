use serde::Deserialize;
use actix_web::{web, dev, App, Error, HttpRequest, FromRequest};
use actix_web::error::ErrorBadRequest;
use futures_util::future::{ok, err, Ready};
use futures::executor::block_on;

pub mod connection;
pub mod general;
pub mod credential_definition;
pub mod schema;
pub mod issuance;
pub mod presentation;

#[derive(Deserialize)]
struct Request<T> {
    #[serde(default)]
    pub id: String, // TODO: Maybe Option<String> is better
    #[serde(default)]
    pub cred_ex_id: String,
    #[serde(default)]
    pub data: T,
}
