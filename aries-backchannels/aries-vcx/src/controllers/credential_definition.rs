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

impl Agent {
    pub fn create_credential_definition(&mut self, cred_def: &CredentialDefinition) -> HarnessResult<String> {
        let id = uuid::Uuid::new_v4().to_string();
        let did = self.config.did.to_string();
        let revocation_details = json!({ "support_revocation": cred_def.support_revocation }).to_string();
        let schema_json: String = self.db.get(&cred_def.schema_id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Cannot create credential definition - schema with id {} not found", id)))?;
        let (cred_def_id, cred_def_json) = match CredentialDef::create(id.to_string(), id.to_string(), did.to_string(), cred_def.schema_id.to_string(), cred_def.tag.to_string(), revocation_details) {
            Err(err) => {
                warn!("Error: {:?}, cred def probably exists on ledger, skipping cred def publish", err);
                anoncreds::generate_cred_def(&did, &schema_json, &cred_def.tag.to_string(), None, Some(cred_def.support_revocation))?
            }
            Ok(cd) => (cd.id.to_string(), cd.to_string()?)
        };
        self.db.set(&cred_def_id, &cred_def_json).map_err(|err| HarnessError::from(err))?;
        Ok(json!({ "credential_definition_id": cred_def_id }).to_string())
    }

    pub fn get_credential_definition(&self, id: &str) -> HarnessResult<String> {
        let cred_def: String = self.db.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Credential definition with id {} not found", id)))?;
        let cred_def: serde_json::Value = serde_json::from_str(&cred_def).map_err(|err| HarnessError::from(err))?;
        Ok(cred_def["data"].to_string())
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
