use std::sync::Mutex;
use actix_web::{web, Responder, post, get};
use crate::error::{HarnessError, HarnessErrorType, HarnessResult};
use aries_vcx::handlers::issuance::credential_def::CredentialDef;
use aries_vcx::libindy::utils::anoncreds;
use uuid;
use crate::Agent;
use crate::controllers::Request;

#[derive(Serialize, Deserialize, Default)]
struct CredentialDefinition {
    support_revocation: bool,
    schema_id: String,
    tag: String
}

#[derive(Serialize, Deserialize)]
struct CachedCredDef {
    cred_def_id: String,
    cred_def_json: String
}

impl Agent {
    pub fn create_credential_definition(&mut self, cred_def: &CredentialDefinition) -> HarnessResult<String> {
        let id = uuid::Uuid::new_v4().to_string();
        let did = self.config.did.to_string();
        let revocation_details = json!({ "support_revocation": cred_def.support_revocation }).to_string();
        let cred_def_id  = match self.dbs.cred_def.get::<CachedCredDef>(&cred_def.schema_id) {
            None => {
                let cd = CredentialDef::create(id.to_string(), id.to_string(), did.to_string(), cred_def.schema_id.to_string(), cred_def.tag.to_string(), revocation_details).map_err(|err| HarnessError::from(err))?;
                let cred_def_id = cd.get_cred_def_id();
                let cred_def_json: serde_json::Value = serde_json::from_str(&cd.to_string()?).map_err(|err| HarnessError::from(err))?;
                let cred_def_json = cred_def_json["data"].to_string();
                self.dbs.cred_def.set(&cred_def.schema_id, &CachedCredDef { cred_def_id: cred_def_id.to_string(), cred_def_json: cred_def_json.to_string() }).map_err(|err| HarnessError::from(err))?;
                self.dbs.cred_def.set(&cred_def_id, &CachedCredDef { cred_def_id: cred_def_id.to_string(), cred_def_json: cred_def_json.to_string() }).map_err(|err| HarnessError::from(err))?;
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
        Ok(cred_def.cred_def_json.to_string())
    }
}

#[post("")]
pub async fn create_credential_definition(req: web::Json<Request<CredentialDefinition>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().create_credential_definition(&req.data)
}

#[get("/{cred_def_id}")]
pub async fn get_credential_definition(agent: web::Data<Mutex<Agent>>, path: web::Path<String>) -> impl Responder {
    agent.lock().unwrap().get_credential_definition(&path.into_inner())
}

pub fn config(cfg: &mut web::ServiceConfig) {
    cfg
        .service(
            web::scope("/command/credential-definition")
                .service(create_credential_definition)
                .service(get_credential_definition)
        );
}
