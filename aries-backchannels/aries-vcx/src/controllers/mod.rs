use serde::Deserialize;

pub mod connection;
pub mod general;
pub mod credential_definition;
pub mod schema;
pub mod issuance;
pub mod presentation;
pub mod revocation;

#[derive(Deserialize)]
pub struct Request<T> {
    #[serde(default)]
    pub id: String, // TODO: Maybe Option<String> is better
    #[serde(default)]
    pub cred_ex_id: String,
    #[serde(default)]
    pub data: T,
}
