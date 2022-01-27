use std::sync::Mutex;
use actix_web::{web, Responder, post, get};
use actix_web::http::header::{CacheControl, CacheDirective};
use crate::error::{HarnessError, HarnessErrorType, HarnessResult};
use aries_vcx::handlers::issuance::credential_def::PublicEntityStateType;
use aries_vcx::handlers::issuance::schema::schema::Schema as VcxSchema;
use aries_vcx::libindy::utils::anoncreds;
use uuid;
use crate::Agent;
use crate::controllers::Request;

#[derive(Serialize, Deserialize, Default)]
pub struct Schema {
    schema_name: String,
    schema_version: String,
    attributes: Vec<String>
}

#[derive(Serialize, Deserialize)]
pub struct CachedSchema {
    schema_id: String,
    schema_json: String
}

fn create_and_publish_schema(source_id: &str,
                             name: String,
                             version: String,
                             data: String) -> HarnessResult<(String, String)> {
    let (schema_id, schema) = anoncreds::create_schema(&name, &version, &data)?;
    anoncreds::publish_schema(&schema)?;
    let schema_json = VcxSchema {
        source_id: source_id.to_string(),
        name,
        data: serde_json::from_str(&data).unwrap_or_default(),
        version,
        schema_id: schema_id.to_string(),
        state: PublicEntityStateType::Built
    }.to_string()?;
    let schema_json: serde_json::Value = serde_json::from_str(&schema_json).map_err(|err| HarnessError::from(err))?;
    let mut schema_json = schema_json["data"].clone();
    schema_json.as_object_mut().ok_or(HarnessError::from_msg(HarnessErrorType::InternalServerError, "Failed to convert schema json Value to Map"))?.insert("id".to_string(), serde_json::Value::String(schema_id.to_string()));
    Ok((schema_id, schema_json.to_string()))
}

impl Agent {
    pub fn create_schema(&mut self, schema: &Schema) -> HarnessResult<String> {
        let id = uuid::Uuid::new_v4().to_string();
        let attrs = serde_json::to_string(&schema.attributes).map_err(|err| HarnessError::from(err))?;
        let (schema_id, schema_json) = match create_and_publish_schema(&id, schema.schema_name.to_string(), schema.schema_version.to_string(), attrs.to_string()) {
            Err(err) => {
                warn!("Error: {:?}, schema probably exists on ledger, skipping schema publish", err);
                anoncreds::create_schema(&schema.schema_name.to_string(), &schema.schema_version.to_string(), &attrs)?
            }
            Ok((schema_id, schema_json)) => (schema_id, schema_json)
        };
        self.dbs.schema.set(&schema_id, &schema_json)?;
        Ok(json!({ "schema_id": schema_id }).to_string())
    }

    pub fn get_schema(&mut self, id: &str) -> HarnessResult<String> {
        let schema: String = self.dbs.schema.get(id)
            .ok_or(HarnessError::from_msg(HarnessErrorType::NotFoundError, &format!("Schema with id {} not found", id)))?;
        let schema: serde_json::Value = serde_json::from_str(&schema).map_err(|err| HarnessError::from(err))?;
        Ok(schema.to_string())
    }
}

#[post("")]
pub async fn create_schema(req: web::Json<Request<Schema>>, agent: web::Data<Mutex<Agent>>) -> impl Responder {
    agent.lock().unwrap().create_schema(&req.data)
        .customize()
        .append_header(CacheControl(vec![CacheDirective::Private, CacheDirective::NoStore, CacheDirective::MustRevalidate]))
}

#[get("/{schema_id}")]
pub async fn get_schema(agent: web::Data<Mutex<Agent>>, path: web::Path<String>) -> impl Responder {
    agent.lock().unwrap().get_schema(&path.into_inner())
        .customize()
        .append_header(CacheControl(vec![CacheDirective::Private, CacheDirective::NoStore, CacheDirective::MustRevalidate]))
}

pub fn config(cfg: &mut web::ServiceConfig) {
    cfg
        .service(
            web::scope("/command/schema")
                .service(create_schema)
                .service(get_schema)
        );
}
