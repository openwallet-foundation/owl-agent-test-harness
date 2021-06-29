use vcx::init::{open_main_pool, PoolConfig, open_as_main_wallet, init_issuer_config}; // TODO: Should we move all Config arguments to a single module?
use vcx::utils::logger::LibvcxDefaultLogger;
use vcx::libindy::utils::wallet::{create_wallet, configure_issuer_wallet, close_main_wallet, WalletConfig};
use vcx::utils::provision::{provision_cloud_agent, AgentProvisionConfig};
use vcx::libindy::utils::pool;
use vcx::utils::plugins::init_plugin;
use vcx::settings;
use std::io::prelude::*;
use crate::AgentConfig;
use hyper::Client;
use uuid;

async fn download_tails() -> std::result::Result<String, String> {
    match std::env::var("TAILS_FILE").ok() {
        Some(tails_file) => {
            if !std::path::Path::new(&tails_file).exists() {
                Err(format!("The file {} does not exist", tails_file))
            } else {
                info!("Using tails file {}", tails_file);
                Ok(tails_file)
            }
        }
        None => match std::env::var("LEDGER_URL").ok() {
            Some(ledger_url) => {
                info!("Downloading tails file");
                let genesis_url = format!("{}/genesis", ledger_url);
                let body = Client::new().get(genesis_url.parse::<hyper::Uri>().unwrap()).await.expect(&format!("Failed to get genesis file from url {}", genesis_url));
                let path = std::env::current_dir().expect("Failed to obtain the current directory path").join("resource").join("genesis_file.txn");
                let mut f = std::fs::OpenOptions::new()
                    .write(true)
                    .create(true)
                    .open(path.clone())
                    .expect("Unable to open file");
                f.write_all(&hyper::body::to_bytes(body).await.expect("Failed to convert retrieved genesis file to bytes")).expect("Unable to write data");
                debug!("Tails file downloaded and saved to {:?}", path);
                path.to_str().map(|s| s.to_string()).ok_or("Failed to convert genesis file path to string".to_string())
            }
            None => {
                std::env::current_dir().expect("Failed to obtain the current directory path").join("resource").join("indypool.txn").to_str().map(|s| s.to_string()).ok_or("Failed to convert genesis file path to string".to_string())
            }
        }
    }
}

// TODO: Remove unwraps
pub async fn initialize() -> std::io::Result<AgentConfig> {
    info!("Initializing vcx");
    let genesis_path = download_tails().await.unwrap();
    let agency_endpoint = std::env::var("CLOUD_AGENCY_URL").unwrap_or("http://localhost:8080".to_string());
    init_plugin(settings::DEFAULT_PAYMENT_PLUGIN, settings::DEFAULT_PAYMENT_INIT_FUNCTION); // TODO: Remove payments
    // TODO: Builder methods for these configs
    let pool_config = PoolConfig {
        genesis_path,
        pool_config: None,
        pool_name: None
    };
    let agency_config = AgentProvisionConfig {
        agency_endpoint,
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
