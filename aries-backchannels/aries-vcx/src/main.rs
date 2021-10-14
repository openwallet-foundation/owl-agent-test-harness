mod controllers;
mod setup;
mod error;

use std::sync::Mutex;

use actix_web::{App, HttpServer, web, middleware};
use pickledb::{PickleDb, PickleDbDumpPolicy, SerializationMethod};
use crate::controllers::{general, connection, credential_definition, issuance, schema, presentation};
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

use clap::{AppSettings, Clap};

#[derive(Clap)]
#[clap(version = "1.0")]
#[clap(setting = AppSettings::ColoredHelp)]
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
    CredentialReceived,
    PresentationSent,
    PresentationReceived,
    Done
}

#[derive(Copy, Clone, Serialize)]
#[serde(rename_all = "lowercase")]
enum Status {
    Active,
    Inactive
}

#[derive(Clone, Serialize)]
struct AgentConfig {
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

struct Agent {
    id: String,
    dbs: Storage,
    state: State,
    status: Status,
    config: AgentConfig,
    last_connection: Option<Connection>
}

impl Agent {
    fn get_state(&self) -> State {
        self.state
    }

    fn set_state(&mut self, state: State) {
        self.state = state;
    }

    fn get_status(&self) -> Status {
        self.status
    }

    fn set_status(&mut self, status: Status) {
        self.status = status;
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("trace"));
    let opts: Opts = Opts::parse();

    ctrlc::set_handler(move || {
        setup::shutdown();
    }).expect("Error setting Ctrl-C handler");

    let config = setup::initialize().await.unwrap();

    HttpServer::new(move || {
        App::new()
            .wrap(middleware::Logger::default())
            .wrap(middleware::NormalizePath::new(middleware::normalize::TrailingSlash::Trim))
            .data(Mutex::new(Agent {
                id: String::from("aries-vcx"),
                dbs: Storage::new(),
                state: State::Initial,
                status: Status::Active,
                config: config.clone(),
                last_connection: None
            }))
            .service(
                web::scope("/agent")
                    .configure(connection::config)
                    .configure(schema::config)
                    .configure(credential_definition::config)
                    .configure(issuance::config)
                    .configure(presentation::config)
                    .configure(general::config)
            )
    })
        .workers(1)
        .bind(format!("0.0.0.0:{}", opts.port))?
        .run()
        .await
}
