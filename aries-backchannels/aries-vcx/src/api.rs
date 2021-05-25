use std::env;

use actix_web::{App, get, HttpResponse, HttpServer, post, Responder, web};
use once_cell::sync::OnceCell;

use vcx::init::{open_pool, init_threadpool, init_issuer_config, init_agency_client, open_pool_directly};
use vcx::libindy::utils::wallet::{create_wallet_from_config, configure_issuer_wallet, open_wallet_directly, close_main_wallet};
use vcx::utils::provision::provision_cloud_agent;

static AGENT_PROVISION: OnceCell<String> = OnceCell::new();

#[post("/agent")]
pub async fn provision_agent() -> impl Responder {
    info!("POST /agent");

    init_threadpool("{}").unwrap();
    let genesis_path = env::var("GENESIS_PATH").unwrap_or(String::from("./resource/docker.txn"));
    let agency_config = json!({
        "agency_url": "http://localhost:8080",
        "agency_did": "VsKV7grR1BUE29mG2Fm2kX",
        "agency_verkey": "Hezce2UWMZ3wUhVkh2LfKSs8nDzWwzs2Win7EzNN3YaR",
    }).to_string();
    let wallet_config = json!({
        "wallet_name": "rust_agent",
        "wallet_key": "8dvfYSt5d1taSd6yJdpjq4emkwsPDDLYxkNFysFD2cZY",
        "wallet_key_derivation": "RAW",
    }).to_string();
    let enterprise_seed = "000000000000000000000000Trustee1";
    let _issuer_config = configure_issuer_wallet(enterprise_seed).unwrap();
    let agency_config = provision_cloud_agent(&agency_config).unwrap();

    create_wallet_from_config(&wallet_config).unwrap();
    let _wh = open_wallet_directly(&wallet_config).unwrap();
    let _ph = open_pool_directly(&json!({ "genesis_path": genesis_path }).to_string()).unwrap();
    let _agency_config = provision_cloud_agent(&agency_config).unwrap();
    close_main_wallet().unwrap();

    HttpResponse::Ok().body("success")
}

#[get("/agent")]
pub async fn get_agent_provision() -> impl Responder {
    info!("GET /agent");
    let provision = AGENT_PROVISION.get().unwrap();
    info!("Retrieved provision {}", provision);
    HttpResponse::Ok().body(provision)
}
