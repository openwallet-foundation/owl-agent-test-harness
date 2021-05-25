use vcx::init::{open_pool, init_issuer_config, init_agency_client, open_pool_directly};
use vcx::libindy::utils::wallet::{create_wallet_from_config, configure_issuer_wallet, open_wallet_directly, close_main_wallet};
use vcx::utils::provision::provision_cloud_agent;
use vcx::libindy::utils::pool;
use std::io::prelude::*;
use uuid;

async fn download_tails() -> std::io::Result<std::path::PathBuf> {
    info!("Downloading tails file");
    let body = reqwest::get("http://127.0.0.1:9000/genesis")
        .await.unwrap()
        .text()
        .await.unwrap();

    let path = std::env::current_dir()?.join("resource").join("von.txn");
    let mut f = std::fs::OpenOptions::new()
        .write(true)
        .create(true)
        .open(path.clone())
        .expect("Unable to open file");
    f.write_all(body.as_bytes()).expect("Unable to write data");
    debug!("Tails file downloaded");
    Ok(path)
}

pub async fn initialize() -> std::io::Result<()> {
    info!("Initializing vcx");
    let genesis_path = download_tails().await.unwrap();
    let agency_config = json!({
        "agency_endpoint": "http://localhost:8080",
        "agency_did": "VsKV7grR1BUE29mG2Fm2kX",
        "agency_verkey": "Hezce2UWMZ3wUhVkh2LfKSs8nDzWwzs2Win7EzNN3YaR",
    }).to_string();
    let wallet_config = json!({
        "wallet_name": format!("rust_agent_{}", uuid::Uuid::new_v4().to_string()),
        "wallet_key": "8dvfYSt5d1taSd6yJdpjq4emkwsPDDLYxkNFysFD2cZY",
        "wallet_key_derivation": "RAW",
    }).to_string();
    
    create_wallet_from_config(&wallet_config).unwrap();
    let _wh = open_wallet_directly(&wallet_config).unwrap();
    let _ph = open_pool_directly(&json!({ "genesis_path": genesis_path.to_str() }).to_string()).unwrap();

    let enterprise_seed = "000000000000000000000000Trustee1";
    let _issuer_config = configure_issuer_wallet(enterprise_seed).unwrap();
    let agency_config = provision_cloud_agent(&agency_config).unwrap();

    debug!("Initialization finished");
    Ok(())
}

pub fn shutdown() {
    close_main_wallet();
    pool::close();
}
