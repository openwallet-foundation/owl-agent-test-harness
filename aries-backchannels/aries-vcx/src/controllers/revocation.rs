use crate::controllers::Request;
use crate::error::HarnessResult;
use crate::HarnessAgent;

use actix_web::{get, post, web, Responder};

use std::sync::Mutex;

#[derive(Serialize, Deserialize, Default, Clone, Debug)]
pub struct CredentialRevocationData {
    cred_rev_id: String,
    rev_registry_id: String,
    publish_immediately: bool,
    notify_connection_id: String
}

impl HarnessAgent {
    pub async fn revoke_credential(
        &mut self,
        revocation_data: &CredentialRevocationData,
    ) -> HarnessResult<String> {
        let CredentialRevocationData {
            rev_registry_id,
            cred_rev_id,
            publish_immediately,
            ..
        } = revocation_data;
        self.aries_agent.rev_regs().revoke_credential_locally(rev_registry_id, cred_rev_id).await?;
        if *publish_immediately {
            self.aries_agent.rev_regs().publish_local_revocations(rev_registry_id).await?;
        };
        Ok("".to_string())
    }

    pub fn get_revocation_registry(&mut self, id: &str) -> HarnessResult<String> {
        let rev_reg_id = self.aries_agent.issuer().get_rev_reg_id(id)?;
        Ok(json!({ "revoc_reg_id": rev_reg_id }).to_string())
    }
}

#[post("/revoke")]
pub async fn revoke_credential(
    agent: web::Data<Mutex<HarnessAgent>>,
    req: web::Json<Request<CredentialRevocationData>>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .revoke_credential(&req.data)
        .await
}

#[get("/{cred_id}")]
pub async fn get_revocation_registry(
    agent: web::Data<Mutex<HarnessAgent>>,
    path: web::Path<String>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .get_revocation_registry(&path.into_inner())
}

pub fn config(cfg: &mut web::ServiceConfig) {
    cfg.service(web::scope("/response/revocation-registry").service(get_revocation_registry))
        .service(web::scope("/command/revocation").service(revoke_credential));
}
