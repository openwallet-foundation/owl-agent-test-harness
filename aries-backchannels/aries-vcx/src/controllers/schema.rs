use crate::controllers::Request;
use crate::error::{HarnessError, HarnessErrorType, HarnessResult};
use crate::{HarnessAgent, soft_assert_eq};
use actix_web::{get, post, web, Responder};
use std::sync::Mutex;

#[derive(Serialize, Deserialize, Default)]
pub struct Schema {
    schema_name: String,
    schema_version: String,
    attributes: Vec<String>,
}

impl HarnessAgent {
    fn schema_id(&self, schema: &Schema) -> String {
        let did = self.aries_agent.issuer_did();
        let &Schema { schema_name, schema_version, .. } = &schema;
        format!("{}:2:{}:{}", did, schema_name, schema_version)
    }

    async fn schema_published(&self, id: &str) -> bool {
        self.aries_agent.schemas().schema_json(id).await.is_ok()
    }

    pub async fn create_schema(&mut self, schema: &Schema) -> HarnessResult<String> {
        let id = self.aries_agent
                    .schemas()
                    .create_schema(
                        &schema.schema_name,
                        &schema.schema_version,
                        &schema.attributes,
                    )
                    .await?;
        if !self.schema_published(&id).await {
            soft_assert_eq!(
                self
                    .aries_agent
                    .schemas()
                    .create_schema(
                        &schema.schema_name,
                        &schema.schema_version,
                        &schema.attributes,
                    )
                    .await?,
                id);
            self.aries_agent.schemas().publish_schema(&id).await?;
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
