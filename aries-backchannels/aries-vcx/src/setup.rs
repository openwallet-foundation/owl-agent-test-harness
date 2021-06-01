use vcx::init::{open_main_pool, PoolConfig, open_as_main_wallet, init_issuer_config}; // TODO: Should we move all Config arguments to a single module?
use vcx::libindy::utils::wallet::{create_wallet, configure_issuer_wallet, close_main_wallet, WalletConfig, IssuerConfig};
use vcx::utils::provision::{provision_cloud_agent, AgentProvisionConfig};
use vcx::libindy::utils::pool;
use vcx::utils::plugins::init_plugin;
use vcx::settings;
use std::io::prelude::*;
use crate::AgentConfig;
use pickledb::{PickleDb, PickleDbDumpPolicy, SerializationMethod};
use serde_json::Value;
use uuid;

async fn download_tails() -> std::io::Result<String> {
    info!("Downloading tails file");
    // let body = reqwest::get("http://127.0.0.1:9000/genesis")
    //     .await.unwrap()
    //     .text()
    //     .await.unwrap();
    let path = std::env::current_dir()?.join("resource").join("indypool.txn").to_str().unwrap().to_string();
    // let path = std::env::current_dir()?.join("resource").join("von.txn");
    // let mut f = std::fs::OpenOptions::new()
    //     .write(true)
    //     .create(true)
    //     .open(path.clone())
    //     .expect("Unable to open file");
    // f.write_all(body.as_bytes()).expect("Unable to write data");
    debug!("Tails file downloaded");
    Ok(path)
}

pub async fn initialize() -> std::io::Result<AgentConfig> {
    info!("Initializing vcx");
    let genesis_path = download_tails().await.unwrap();
    init_plugin(settings::DEFAULT_PAYMENT_PLUGIN, settings::DEFAULT_PAYMENT_INIT_FUNCTION); // TODO: Remove payments
    // TODO: Builder methods for these configs
    let pool_config = PoolConfig {
        genesis_path,
        pool_config: None,
        pool_name: None
    };
    let agency_config = AgentProvisionConfig {
        agency_endpoint: "http://localhost:8080".to_string(),
        agency_did: "VsKV7grR1BUE29mG2Fm2kX".to_string(),
        agency_verkey: "Hezce2UWMZ3wUhVkh2LfKSs8nDzWwzs2Win7EzNN3YaR".to_string(),
        agent_seed: None
    };
    let wallet_config = WalletConfig {
        wallet_name: format!("rust_agent_{}", uuid::Uuid::new_v4().to_string()),
        wallet_key: "8dvfYSt5d1taSd6yJdpjq4emkwsPDDLYxkNFysFD2cZY".to_string(),
        wallet_key_derivation: "RAW".to_string(),
        rekey: None,
        storage_config: None,
        rekey_derivation_method: None,
        storage_credentials: None,
        wallet_type: None
    };
    
    create_wallet(&wallet_config).unwrap();
    let _wh = open_as_main_wallet(&wallet_config).unwrap();
    let _ph = open_main_pool(&pool_config).unwrap();

    let enterprise_seed = "000000000000000000000000Trustee1";
    let issuer_config = configure_issuer_wallet(enterprise_seed).unwrap();
    init_issuer_config(&issuer_config).unwrap();
    let agency_config = provision_cloud_agent(&agency_config).unwrap();

    debug!("Initialization finished");
    Ok(AgentConfig { did: issuer_config.institution_did })
}

pub fn shutdown() {
    close_main_wallet();
    pool::close();
}
