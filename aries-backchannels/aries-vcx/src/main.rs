mod controllers;
mod setup;
mod error;

use std::sync::Mutex;

use actix_web::{App, HttpServer, web, middleware};
use pickledb::{PickleDb, PickleDbDumpPolicy, SerializationMethod};
use crate::controllers::{general, connection, credential_definition, issuance, schema, presentation, revocation};
use clap::Parser;
use aries_vcx::handlers::connection::connection::Connection;
 
extern crate serde;
#[macro_use]
extern crate serde_derive;
#[macro_use]
extern crate serde_json;
#[macro_use]
extern crate log;
extern crate ctrlc;
extern crate uuid;
extern crate futures_util;
extern crate clap;
extern crate reqwest;
extern crate derive_builder;


#[derive(Parser)]
#[clap(version = "1.0")]
struct Opts {
    #[clap(short, long, default_value = "9020")]
    port: u32,
    #[clap(short, long, default_value = "false")]
    interactive: String,
}

#[derive(Copy, Clone, Debug, Serialize)]
#[serde(rename_all = "kebab-case")]
enum State {
    Initial,
    Invited,
    Requested,
    RequestSet,
    Responded,
    Complete,
    Failure,
    Unknown,
    ProposalSent,
    ProposalReceived,
    OfferSent,
    RequestReceived,
    CredentialSent,
    OfferReceived,
    RequestSent,
    PresentationSent,
    Done
}

#[derive(Copy, Clone, Serialize)]
#[serde(rename_all = "lowercase")]
enum Status {
    Active,
}

#[derive(Clone, Serialize)]
pub struct AgentConfig {
    did: String
}

struct Storage {
    schema: PickleDb,
    cred_def: PickleDb,
    connection: PickleDb,
    holder: PickleDb,
    issuer: PickleDb,
    verifier: PickleDb,
    prover: PickleDb,
}

impl Storage {
    pub fn new() -> Self {
        Self {
            schema: PickleDb::new("storage-schema.db", PickleDbDumpPolicy::AutoDump, SerializationMethod::Json),
            cred_def: PickleDb::new("storage-cred-def.db", PickleDbDumpPolicy::AutoDump, SerializationMethod::Json),
            connection: PickleDb::new("storage-connection.db", PickleDbDumpPolicy::AutoDump, SerializationMethod::Json),
            holder: PickleDb::new("storage-holder.db", PickleDbDumpPolicy::AutoDump, SerializationMethod::Json),
            issuer: PickleDb::new("storage-issuer.db", PickleDbDumpPolicy::AutoDump, SerializationMethod::Json),
            verifier: PickleDb::new("storage-verifier.db", PickleDbDumpPolicy::AutoDump, SerializationMethod::Json),
            prover: PickleDb::new("storage-prover.db", PickleDbDumpPolicy::AutoDump, SerializationMethod::Json),
        }
    }
}

pub struct Agent {
    dbs: Storage,
    status: Status,
    config: AgentConfig,
    last_connection: Option<Connection>
}

#[macro_export]
macro_rules! soft_assert_eq {
    ($left:expr, $right:expr) => ({
        match (&$left, &$right) {
            (left_val, right_val) => {
                if !(*left_val == *right_val) {
                    return Err(HarnessError::from_msg(HarnessErrorType::InternalServerError, &format!(r#"assertion failed: `(left == right)`
  left: `{:?}`,
 right: `{:?}`"#, left_val, right_val)));
                }
            }
        }
    });
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("trace"));
    let opts: Opts = Opts::parse();

    ctrlc::set_handler(move || {
        setup::shutdown();
    }).expect("Error setting Ctrl-C handler");

    let host = std::env::var("HOST").unwrap_or("0.0.0.0".to_string());

    let config = setup::initialize().await;

    HttpServer::new(move || {
        App::new()
            .wrap(middleware::Logger::default())
            .wrap(middleware::NormalizePath::new(middleware::TrailingSlash::Trim))
            .app_data(web::Data::new(Mutex::new(Agent {
                dbs: Storage::new(),
                status: Status::Active,
                config: config.clone(),
                last_connection: None
            })))
            .service(
                web::scope("/agent")
                    .configure(connection::config)
                    .configure(schema::config)
                    .configure(credential_definition::config)
                    .configure(issuance::config)
                    .configure(revocation::config)
                    .configure(presentation::config)
                    .configure(general::config)
            )
    })
        .keep_alive(30)
        .client_timeout(30000)
        .workers(1)
        .bind(format!("{}:{}", host, opts.port))?
        .run()
        .await
}
