use crate::controllers::Request;
use crate::error::{HarnessError, HarnessErrorType, HarnessResult};
use crate::Agent;
use actix_web::http::header::{CacheControl, CacheDirective};
use actix_web::{get, post, web, Responder};
use aries_vcx::handlers::issuance::issuer::Issuer;
use aries_vcx::indy::primitives::revocation_registry::publish_local_revocations;
use std::sync::Mutex;

#[derive(Serialize, Deserialize, Default, Clone, Debug)]
pub struct CredentialRevocationData {
    cred_rev_id: String,
    rev_registry_id: String,
    publish_immediately: bool,
}

impl Agent {
    pub async fn revoke_credential(
        &mut self,
        revocation_data: &CredentialRevocationData,
    ) -> HarnessResult<String> {
        let issuer: Issuer = self
            .dbs
            .issuer
            .get(&revocation_data.rev_registry_id)
            .ok_or(HarnessError::from_msg(
                HarnessErrorType::NotFoundError,
                &format!(
                    "Issuer with id {} not found",
                    &revocation_data.rev_registry_id
                ),
            ))?;
        issuer
            .revoke_credential_local(self.config.wallet_handle)
            .await?;
        publish_local_revocations(self.config.wallet_handle, self.config.pool_handle, &self.config.did, &revocation_data.rev_registry_id).await?;
        self.dbs.issuer.set(&issuer.get_source_id()?, &issuer)?;
        Ok("OK".to_string())
    }

    pub fn get_revocation_registry(&mut self, id: &str) -> HarnessResult<String> {
        let issuer: Issuer = self.dbs.issuer.get(id).ok_or(HarnessError::from_msg(
            HarnessErrorType::NotFoundError,
            &format!("Credential definition with id {} not found", id),
        ))?;
        let rev_reg_id = issuer.get_rev_reg_id()?;
        self.dbs.issuer.set(&rev_reg_id, &issuer)?;
        Ok(json!({ "revocation_id": rev_reg_id, "revoc_reg_id": rev_reg_id }).to_string())
    }
}

#[post("/revoke")]
pub async fn revoke_credential(
    agent: web::Data<Mutex<Agent>>,
    req: web::Json<Request<CredentialRevocationData>>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .revoke_credential(&req.data)
        .await
        .customize()
        .append_header(CacheControl(vec![
            CacheDirective::Private,
            CacheDirective::NoStore,
            CacheDirective::MustRevalidate,
        ]))
}

#[get("/{cred_id}")]
pub async fn get_revocation_registry(
    agent: web::Data<Mutex<Agent>>,
    path: web::Path<String>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .get_revocation_registry(&path.into_inner())
        .customize()
        .append_header(CacheControl(vec![
            CacheDirective::Private,
            CacheDirective::NoStore,
            CacheDirective::MustRevalidate,
        ]))
}

pub fn config(cfg: &mut web::ServiceConfig) {
    cfg.service(web::scope("/response/revocation-registry").service(get_revocation_registry))
        .service(web::scope("/command/revocation").service(revoke_credential));
}
