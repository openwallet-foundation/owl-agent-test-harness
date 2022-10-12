use crate::controllers::Request;
use crate::error::{HarnessError, HarnessErrorType, HarnessResult};
use crate::HarnessAgent;
use actix_web::http::header::{CacheControl, CacheDirective};
use actix_web::{get, post, web, Responder};
use aries_vcx_agent::aries_vcx::indy::primitives::credential_definition::PublicEntityStateType;
use aries_vcx_agent::aries_vcx::indy::primitives::credential_schema;
use aries_vcx_agent::aries_vcx::indy::primitives::credential_schema::Schema as VcxSchema;
use aries_vcx_agent::aries_vcx::vdrtools_sys::{PoolHandle, WalletHandle};
use std::sync::Mutex;
use uuid;

#[derive(Serialize, Deserialize, Default)]
pub struct Schema {
    schema_name: String,
    schema_version: String,
    attributes: Vec<String>,
}

#[derive(Serialize, Deserialize)]
pub struct CachedSchema {
    schema_id: String,
    schema_json: String,
}

impl HarnessAgent {
    pub async fn create_schema(&mut self, schema: &Schema) -> HarnessResult<String> {
        let ids = self
            .aries_agent
            .schemas()
            .find_by_name_and_version(&schema.schema_name, &schema.schema_version)?;
        let id = if let Some(id) = ids.get(0) {
            id.to_string()
        } else {
            let id = self
                .aries_agent
                .schemas()
                .create_schema(
                    &schema.schema_name,
                    &schema.schema_version,
                    &schema.attributes,
                )
                .await?;
            self.aries_agent.schemas().publish_schema(&id).await?;
            id
        };
        Ok(json!({ "schema_id": id }).to_string())
    }

    pub async fn get_schema(&mut self, id: &str) -> HarnessResult<String> {
        self.aries_agent
            .schemas()
            .schema_json(&id)
            .await
            .map_err(|err| err.into())
    }
}

#[post("")]
pub async fn create_schema(
    req: web::Json<Request<Schema>>,
    agent: web::Data<Mutex<HarnessAgent>>,
) -> impl Responder {
    agent.lock().unwrap().create_schema(&req.data).await
}

#[get("/{schema_id}")]
pub async fn get_schema(
    agent: web::Data<Mutex<HarnessAgent>>,
    path: web::Path<String>,
) -> impl Responder {
    agent.lock().unwrap().get_schema(&path.into_inner()).await
}

pub fn config(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::scope("/command/schema")
            .service(create_schema)
            .service(get_schema),
    );
}
