mod api;
mod controllers;
mod setup;
mod error;

use std::boxed::Box;
use std::cell::{Cell, RefCell};
use std::sync::{RwLock, RwLockReadGuard, RwLockWriteGuard, Mutex, Arc};

use actix_web::{App, get, HttpResponse, HttpServer, post, Responder, web, guard, middleware};
use pickledb::{PickleDb, PickleDbDumpPolicy, SerializationMethod};
use crate::controllers::general;
use crate::controllers::connection;
 
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
    Rejected,
    AwaitReponse,
    ReceiveResponse,
    Failure
}

#[derive(Copy, Clone, Serialize)]
#[serde(rename_all = "lowercase")]
enum Status {
    Active,
    Inactive
}

struct Agent {
    id: String,
    db: PickleDb,
    state: State,
    status: Status
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
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("info"));
    let opts: Opts = Opts::parse();

    ctrlc::set_handler(move || {
        setup::shutdown();
    }).expect("Error setting Ctrl-C handler");

    setup::initialize().await.unwrap();

    HttpServer::new(|| {
        App::new()
            .wrap(middleware::Logger::default())
            .wrap(middleware::NormalizePath::new(middleware::normalize::TrailingSlash::Trim))
            .data(Mutex::new(Agent {
                id: String::from("aries-vcx"),
                db: PickleDb::new("storage.db", PickleDbDumpPolicy::AutoDump, SerializationMethod::Json),
                state: State::Initial,
                status: Status::Active
            }))
            .service(
                web::scope("/agent")
                    .configure(connection::config)
                    .configure(general::config)
            )
    })
        .workers(1)
        .bind(format!("127.0.0.1:{}", opts.port))?
        .run()
        .await
}

