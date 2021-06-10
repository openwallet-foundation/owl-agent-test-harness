use std::sync::Mutex;
use actix_web::{web, Responder, post, get};
use crate::error::{HarnessError, HarnessErrorType, HarnessResult};
use vcx::schema::{create_and_publish_schema, get_schema_id};
use vcx::schema;
use vcx::libindy::utils::anoncreds;
use uuid;
use crate::Agent;
use crate::controllers::Request;

#[derive(Serialize, Deserialize, Default)]
struct Schema {
    schema_name: String,
    schema_version: String,
    attributes: Vec<String>
}

impl Agent {
    pub fn create_schema(&mut self, schema: &Schema) -> HarnessResult<String> {
        let id = uuid::Uuid::new_v4().to_string();
        let did = self.config.did.to_string();
        let attrs = serde_json::to_string(&schema.attributes).map_err(|err| HarnessError::from(err))?;
        let (schema_id, schema_json) = match create_and_publish_schema(&id, did, schema.schema_name.to_string(), schema.schema_version.to_string(), attrs.to_string()) {
            Err(err) => {
                warn!("Error: {:?}, schema probably exists on ledger, skipping schema publish", err);
                anoncreds::create_schema(&schema.schema_name.to_string(), &schema.schema_version.to_string(), &attrs).map_err(|err| HarnessError::from(err))?
            }
            Ok(sh) => (get_schema_id(sh).map_err(|err| HarnessError::from(err))?, schema::to_string(sh)?)
        };
        self.db.set(&schema_id, &schema_json).map_err(|err| HarnessError::from(err))?;
        Ok(json!({ "schema_id": schema_id }).to_string())
    }

    pub fn get_schema(&mut self, id: &str) -> HarnessResult<String> {
        let schema: String = self.db.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Schema with id {} not found", id)))?;
        let schema: serde_json::Value = serde_json::from_str(&schema).map_err(|err| HarnessError::from(err))?;
        Ok(schema["data"].to_string())
    }
}

#[post("")]
pub async fn create_schema(req: web::Json<Request<Schema>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().create_schema(&req.data)
}

#[get("/{schema_id}")]
pub async fn get_schema(agent: web::Data<Mutex<Agent>>, path: web::Path<String>) -> impl Responder {
    agent.lock().unwrap().get_schema(&path.into_inner())
}

pub fn config(cfg: &mut web::ServiceConfig) {
    cfg
        .service(
            web::scope("/command/schema")
                .service(create_schema)
                .service(get_schema)
        );
}
