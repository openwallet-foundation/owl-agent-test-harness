use aries_vcx::agency_client::agency_client::AgencyClient;
use aries_vcx::indy::wallet::{IssuerConfig, WalletConfig, close_wallet, create_wallet_with_master_secret, delete_wallet, open_wallet, wallet_configure_issuer};
use aries_vcx::indy::ledger::pool::{create_pool_ledger_config, open_pool_ledger};
use aries_vcx::indy::ledger::pool::PoolConfigBuilder;
use aries_vcx::indy::wallet::WalletConfigBuilder;
use aries_vcx::agency_client::configuration::AgentProvisionConfig;
use aries_vcx::global::settings::init_issuer_config;
use aries_vcx::utils::provision::provision_cloud_agent;
use std::io::prelude::*;
use crate::AgentConfig;
use rand::{thread_rng, Rng};
use uuid;

#[derive(Debug, Deserialize)]
struct SeedResponse {
    seed: String,
}

async fn get_trustee_seed() -> String {
    if let Some(ledger_url) = std::env::var("LEDGER_URL").ok() {
        let url = format!("{}/register", ledger_url);
        let mut rng = thread_rng();
        let client = reqwest::Client::new();
        let body = json!({
            "role": "TRUST_ANCHOR",
            "seed": format!("my_seed_000000000000000000{}", rng.gen_range(100000, 1000000))
        }).to_string();
        client.post(&url).body(body).send().await.expect("Failed to send message").json::<SeedResponse>().await.expect("Failed to deserialize response").seed
    } else {
        "000000000000000000000000Trustee1".to_string()
    }
}

async fn download_genesis_file() -> std::result::Result<String, String> {
    match std::env::var("GENESIS_FILE").ok() {
        Some(genesis_file) => {
            if !std::path::Path::new(&genesis_file).exists() {
                Err(format!("The file {} does not exist", genesis_file))
            } else {
                info!("Using genesis file {}", genesis_file);
                Ok(genesis_file)
            }
        }
        None => match std::env::var("LEDGER_URL").ok() {
            Some(ledger_url) => {
                info!("Downloading genesis file from {}", ledger_url);
                let genesis_url = format!("{}/genesis", ledger_url);
                let body = reqwest::get(&genesis_url)
                    .await
                    .expect("Failed to get genesis file from ledger")
                    .text()
                    .await
                    .expect("Failed to get the response text");
                let path = std::env::current_dir().expect("Failed to obtain the current directory path").join("resource").join("genesis_file.txn");
                info!("Storing genesis file to {:?}", path);
                let mut f = std::fs::OpenOptions::new()
                    .write(true)
                    .create(true)
                    .open(path.clone())
                    .expect("Unable to open file");
                f.write_all(body.as_bytes()).expect("Unable to write data");
                debug!("Genesis file downloaded and saved to {:?}", path);
                path.to_str().map(|s| s.to_string()).ok_or("Failed to convert genesis file path to string".to_string())
            }
            None => {
                std::env::current_dir().expect("Failed to obtain the current directory path").join("resource").join("indypool.txn").to_str().map(|s| s.to_string()).ok_or("Failed to convert genesis file path to string".to_string())
            }
        }
    }
}

pub async fn initialize() -> AgentConfig {
    info!("Initializing vcx");
    let genesis_path = download_genesis_file().await.expect("Failed to download the genesis file");
    let agency_endpoint = std::env::var("CLOUD_AGENCY_URL").unwrap_or("http://localhost:8080".to_string());
    let pool_config = serde_json::to_string(&PoolConfigBuilder::default()
        .genesis_path(&genesis_path)
        .build()
        .expect("Failed to build pool config")
    ).unwrap();
    let agency_config = AgentProvisionConfig {
        agency_did: "VsKV7grR1BUE29mG2Fm2kX".to_string(),
        agency_verkey: "Hezce2UWMZ3wUhVkh2LfKSs8nDzWwzs2Win7EzNN3YaR".to_string(),
        agency_endpoint,
        agent_seed: None,
    };
    let wallet_config = WalletConfigBuilder::default()
        .wallet_name(format!("rust_agent_{}", uuid::Uuid::new_v4()))
        .wallet_key("8dvfYSt5d1taSd6yJdpjq4emkwsPDDLYxkNFysFD2cZY")
        .wallet_key_derivation("RAW")
        .build()
        .expect("Failed to build wallet config");
    create_wallet_with_master_secret(&wallet_config).await.expect("Failed to create wallet");
    let wallet_handle = open_wallet(&wallet_config).await.expect("Failed to open wallet");
    create_pool_ledger_config("aries-vcx-pool", &genesis_path).await.unwrap();
    let pool_handle = open_pool_ledger("aries-vcx-pool", Some(&pool_config)).await.unwrap();

    let issuer_config = wallet_configure_issuer(wallet_handle, &get_trustee_seed().await).await.expect("Failed to configure the issuer wallet");
    init_issuer_config(&issuer_config).expect("Failed to init issuer config");
    let mut agency_client = AgencyClient::new();
    provision_cloud_agent(&mut agency_client, wallet_handle, &agency_config).await.expect("Failed to provision the cloud agent");

    debug!("Initialization finished");
    AgentConfig { did: issuer_config.institution_did, wallet_handle, pool_handle, agency_client }
}

pub fn shutdown() {
}
