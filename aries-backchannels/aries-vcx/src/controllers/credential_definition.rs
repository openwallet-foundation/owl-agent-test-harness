use std::sync::Mutex;
use actix_web::{web, Responder, post, get};
use actix_web::http::header::{CacheControl, CacheDirective};
use crate::error::{HarnessError, HarnessErrorType, HarnessResult};
use aries_vcx::handlers::issuance::credential_def::{CredentialDef, CredentialDefConfigBuilder, RevocationDetailsBuilder};
use reqwest::multipart;
use aries_vcx::libindy::utils::anoncreds::RevocationRegistryDefinition;

use uuid;
use crate::Agent;
use crate::controllers::Request;
use crate::soft_assert_eq;

#[derive(Serialize, Deserialize, Default, Debug)]
pub struct CredentialDefinition {
    support_revocation: bool,
    schema_id: String,
    tag: String
}

#[derive(Serialize, Deserialize, Debug)]
pub struct CachedCredDef {
    cred_def_id: String,
    cred_def_json: String,
    pub tails_file: Option<String>,
    pub rev_reg_id: Option<String>
}

fn get_tails_hash(cred_def: &CredentialDef) -> HarnessResult<String> {
    let err = HarnessError::from_msg(HarnessErrorType::InternalServerError, "Failed to retrieve credential definition from credential definition");
    let rev_reg_def: String = cred_def.get_rev_reg_def().map_err(|_| err.clone())?.ok_or(err)?;
    let rev_reg_def: RevocationRegistryDefinition = serde_json::from_str(&rev_reg_def)?;
    Ok(rev_reg_def.value.tails_hash)
}

async fn upload_tails_file(tails_url: &str, tails_file: &str) -> HarnessResult<()> {
    info!("Going to upload tails file");
    let client = reqwest::Client::new();
    let genesis_file = std::env::var("GENESIS_FILE").unwrap_or(
        std::env::current_dir().expect("Failed to obtain the current directory path").join("resource").join("genesis_file.txn").to_str()
        .ok_or(HarnessError::from_msg(HarnessErrorType::InternalServerError, "Failed to convert path to str"))?.to_string());
    let genesis_file_data = std::fs::read(genesis_file)?;
    let tails_file_data = std::fs::read(tails_file)?;
    let genesis_part = multipart::Part::bytes(genesis_file_data);
    let tails_part = multipart::Part::bytes(tails_file_data);
    let form = multipart::Form::new()
        .part("genesis", genesis_part).part("tails", tails_part);
    let res = client.put(tails_url).multipart(form).send().await?;
    soft_assert_eq!(res.status(), reqwest::StatusCode::OK);
    Ok(())
}

impl Agent {
    pub async fn create_credential_definition(&mut self, cred_def: &CredentialDefinition) -> HarnessResult<String> {
        let id = uuid::Uuid::new_v4().to_string();
        let did = self.config.did.to_string();
        let tails_base_url = std::env::var("TAILS_SERVER_URL").unwrap_or("https://tails-server-test.pathfinder.gov.bc.ca".to_string());
        let tails_base_path = "/tmp".to_string();
        let cred_def_id  = match self.dbs.cred_def.get::<CachedCredDef>(&cred_def.schema_id) {
            None => {
                let config = CredentialDefConfigBuilder::default()
                    .issuer_did(did)
                    .schema_id(&cred_def.schema_id)
                    .tag(&id)
                    .build()?;
                let revocation_details = if cred_def.support_revocation {
                    RevocationDetailsBuilder::default()
                        .support_revocation(cred_def.support_revocation)
                        .tails_file(&tails_base_path)
                        .max_creds(50 as u32)
                        .build()?
                } else {
                    RevocationDetailsBuilder::default()
                        .support_revocation(cred_def.support_revocation)
                        .build()?
                };
                let cd = CredentialDef::create_and_store(id.to_string(), config, revocation_details)?;
                let (rev_reg_id, tails_url) = match cred_def.support_revocation {
                    true => {
                        let rev_reg_id = cd.get_rev_reg_id().ok_or(HarnessError::from_msg(HarnessErrorType::InternalServerError, "Failed to retrieve revocation registry id from credential definition"))?;
                        let tails_url = format!("{}/{}", tails_base_url, rev_reg_id);
                        (Some(rev_reg_id), Some(tails_url))
                    }
                    false => (None, None)
                };
                let cd = cd.publish(tails_url.as_deref())?;
                let tails_file = match tails_url {
                    Some(tails_url) => {
                        let tails_hash = get_tails_hash(&cd)?;
                        let tails_file = format!("{}/{}", tails_base_path, tails_hash);
                        upload_tails_file(&tails_url, &tails_file).await?;
                        Some(tails_base_path)
                    }
                    None => None
                };
                let cred_def_id = cd.get_cred_def_id();
                let cred_def_json: serde_json::Value = serde_json::from_str(&cd.to_string()?)?;
                let cred_def_json = cred_def_json["data"]["cred_def_json"].as_str().ok_or(HarnessError::from_msg(HarnessErrorType::InternalServerError, "Failed to convert cred def json Value to str"))?;
                self.dbs.cred_def.set(&cred_def.schema_id, &CachedCredDef { cred_def_id: cred_def_id.to_string(), cred_def_json: cred_def_json.to_string(), tails_file: tails_file.clone(), rev_reg_id: rev_reg_id.clone() })?;
                self.dbs.cred_def.set(&cred_def_id, &CachedCredDef { cred_def_id: cred_def_id.to_string(), cred_def_json: cred_def_json.to_string(), tails_file: tails_file.clone(), rev_reg_id: rev_reg_id.clone() })?;
                cred_def_id
            }
            Some(cached_cred_def) => {
                cached_cred_def.cred_def_id.to_string()
            }
        };
        Ok(json!({ "credential_definition_id": cred_def_id }).to_string())
    }

    pub fn get_credential_definition(&self, id: &str) -> HarnessResult<String> {
        let cred_def: CachedCredDef = self.dbs.cred_def.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Credential definition with id {} not found", id)))?;
        Ok(cred_def.cred_def_json)
    }
}

#[post("")]
pub async fn create_credential_definition(req: web::Json<Request<CredentialDefinition>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().create_credential_definition(&req.data).await
        .customize()
        .append_header(CacheControl(vec![CacheDirective::Private, CacheDirective::NoStore, CacheDirective::MustRevalidate]))
}

#[get("/{cred_def_id}")]
pub async fn get_credential_definition(agent: web::Data<Mutex<Agent>>, path: web::Path<String>) -> impl Responder {
    agent.lock().unwrap().get_credential_definition(&path.into_inner())
        .customize()
        .append_header(CacheControl(vec![CacheDirective::Private, CacheDirective::NoStore, CacheDirective::MustRevalidate]))
}

pub fn config(cfg: &mut web::ServiceConfig) {
    cfg
        .service(
            web::scope("/command/credential-definition")
                .service(create_credential_definition)
                .service(get_credential_definition)
        );
}
