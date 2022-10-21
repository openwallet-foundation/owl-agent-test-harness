use crate::controllers::credential_definition::CachedCredDef;
use crate::controllers::Request;
use crate::error::{HarnessError, HarnessErrorType, HarnessResult};
use crate::soft_assert_eq;
use crate::{Agent, State};
use actix_web::http::header::{CacheControl, CacheDirective};
use actix_web::{get, post, web, Responder};
use aries_vcx::agency_client::agency_client::AgencyClient;
use aries_vcx::handlers::connection::connection::Connection;
use aries_vcx::handlers::issuance::holder::Holder;
use aries_vcx::handlers::issuance::issuer::Issuer;
use aries_vcx::messages::a2a::A2AMessage;
use aries_vcx::messages::issuance::credential_offer::{
    CredentialOffer as VcxCredentialOffer, OfferInfo,
};
use aries_vcx::messages::issuance::credential_proposal::CredentialProposal as VcxCredentialProposal;
use aries_vcx::messages::issuance::credential_proposal::CredentialProposalData;
use aries_vcx::messages::mime_type::MimeType;
use aries_vcx::messages::issuance::CredentialPreviewData;
use aries_vcx::protocols::issuance::holder::state_machine::HolderState;
use aries_vcx::protocols::issuance::issuer::state_machine::IssuerState;
use std::sync::Mutex;
use uuid;

#[derive(Serialize, Deserialize, Default, Debug)]
pub struct CredentialOffer {
    cred_def_id: String,
    credential_preview: CredentialPreviewData,
    connection_id: String,
}

#[derive(Serialize, Deserialize, Default, Clone)]
pub struct CredentialProposal {
    schema_issuer_did: String,
    issuer_did: String,
    schema_name: String,
    cred_def_id: String,
    schema_version: String,
    credential_proposal: CredentialPreviewData,
    connection_id: String,
    schema_id: String,
}

#[derive(Serialize, Deserialize, Default)]
pub struct Credential {
    credential_preview: CredentialPreviewData,
    #[serde(default)]
    comment: Option<String>,
}

#[derive(Serialize, Deserialize, Default)]
pub struct CredentialId {
    credential_id: String,
}

fn _get_state_issuer(issuer: &Issuer) -> State {
    match issuer.get_state() {
        IssuerState::Initial => State::Initial,
        IssuerState::ProposalReceived | IssuerState::OfferSet => State::ProposalReceived,
        IssuerState::OfferSent => State::OfferSent,
        IssuerState::RequestReceived => State::RequestReceived,
        IssuerState::CredentialSent => State::CredentialSent,
        IssuerState::Finished => State::Done,
        IssuerState::Failed => State::Failure,
    }
}

fn _get_state_holder(holder: &Holder) -> State {
    match holder.get_state() {
        HolderState::Initial => State::Initial,
        HolderState::ProposalSent => State::ProposalSent,
        HolderState::OfferReceived => State::OfferReceived,
        HolderState::RequestSent => State::RequestSent,
        HolderState::Finished => State::Done,
        HolderState::Failed => State::Failure,
    }
}

async fn download_tails_file(
    tails_base_url: &str,
    rev_reg_id: &str,
    tails_hash: &str,
) -> HarnessResult<()> {
    let url = match tails_base_url.to_string().matches('/').count() {
        0 => format!("{}/{}", tails_base_url, rev_reg_id),
        1.. => tails_base_url.to_string(),
        _ => {
            return Err(HarnessError::from_msg(
                HarnessErrorType::InternalServerError,
                "Negative count",
            ))
        }
    };
    let client = reqwest::Client::new();
    let tails_folder_path = std::env::current_dir()
        .expect("Failed to obtain the current directory path")
        .join("resource")
        .join("tails");
    std::fs::create_dir_all(&tails_folder_path).map_err(|_| {
        HarnessError::from_msg(
            HarnessErrorType::InternalServerError,
            "Failed to create tails folder",
        )
    })?;
    let tails_file_path = tails_folder_path
        .join(tails_hash)
        .to_str()
        .ok_or(HarnessError::from_msg(
            HarnessErrorType::InternalServerError,
            "Failed to convert tails hash to str",
        ))?
        .to_string();
    let res = client.get(&url).send().await?;
    soft_assert_eq!(res.status(), reqwest::StatusCode::OK);
    std::fs::write(tails_file_path, res.bytes().await?)?;
    Ok(())
}

async fn get_proposal(
    connection: &Connection,
    agency_client: &AgencyClient,
) -> HarnessResult<VcxCredentialProposal> {
    let mut proposals = Vec::<VcxCredentialProposal>::new();
    for (uid, message) in connection.get_messages(agency_client).await?.into_iter() {
        match message {
            A2AMessage::CredentialProposal(proposal) => {
                connection
                    .update_message_status(&uid, agency_client)
                    .await
                    .ok();
                proposals.push(proposal);
            }
            _ => {}
        }
    }
    soft_assert_eq!(proposals.len(), 1);
    proposals.pop().ok_or(HarnessError::from_msg(
        HarnessErrorType::InternalServerError,
        "Did not obtain presentation request message",
    ))
}

async fn get_offer(
    connection: &Connection,
    agency_client: &AgencyClient,
    thread_id: &str,
) -> HarnessResult<VcxCredentialOffer> {
    let mut offers = Vec::<VcxCredentialOffer>::new();
    for (uid, message) in connection.get_messages(agency_client).await?.into_iter() {
        match message {
            A2AMessage::CredentialOffer(offer) if offer.get_thread_id() == *thread_id => {
                connection
                    .update_message_status(&uid, agency_client)
                    .await
                    .ok();
                offers.push(offer);
            }
            _ => {}
        }
    }
    soft_assert_eq!(offers.len(), 1);
    offers.pop().ok_or(HarnessError::from_msg(
        HarnessErrorType::InternalServerError,
        "Did not obtain presentation request message",
    ))
}

impl Agent {
    pub async fn send_credential_proposal(
        &mut self,
        cred_proposal: &CredentialProposal,
    ) -> HarnessResult<String> {
        let id = uuid::Uuid::new_v4().to_string();
        let connection: Connection = self
            .dbs
            .connection
            .get(&cred_proposal.connection_id)
            .ok_or(HarnessError::from_msg(
                HarnessErrorType::NotFoundError,
                &format!(
                    "Connection with id {} not found",
                    cred_proposal.connection_id
                ),
            ))?;
        let mut holder = Holder::create(&id)?;
        let mut proposal_data = CredentialProposalData::create()
            .set_schema_id(cred_proposal.schema_id.clone())
            .set_cred_def_id(cred_proposal.cred_def_id.clone());
        for attr in cred_proposal
            .credential_proposal
            .attributes
            .clone()
            .into_iter()
        {
            proposal_data = proposal_data.add_credential_preview_data(&attr.name, &attr.value, MimeType::Plain);
        }
        holder
            .send_proposal(
                self.config.wallet_handle,
                self.config.pool_handle,
                proposal_data.clone(),
                connection
                    .send_message_closure(self.config.wallet_handle)
                    .await?,
            )
            .await?;
        let thread_id = holder.get_thread_id()?;
        self.dbs.holder.set(&thread_id, &holder)?;
        self.dbs.connection.set(&thread_id, &connection)?;
        Ok(json!({ "state": _get_state_holder(&holder), "thread_id": thread_id }).to_string())
    }

    pub async fn send_credential_request(&mut self, id: &str) -> HarnessResult<String> {
        let connection: Connection = self.dbs.connection.get(id).ok_or(HarnessError::from_msg(
            HarnessErrorType::NotFoundError,
            &format!("Connection with id {} not found", id),
        ))?;
        let mut holder: Holder = self.dbs.holder.get(id).unwrap_or(Holder::create(&id)?);
        holder
            .send_request(
                self.config.wallet_handle,
                self.config.pool_handle,
                connection.pairwise_info().pw_did.to_string(),
                connection
                    .send_message_closure(self.config.wallet_handle)
                    .await?,
            )
            .await?;
        let thread_id = holder.get_thread_id()?;
        self.dbs.holder.set(&thread_id, &holder)?;
        Ok(json!({ "state": _get_state_holder(&holder), "thread_id": thread_id }).to_string())
    }

    pub async fn send_credential_offer(
        &mut self,
        cred_offer: &CredentialOffer,
        id: &str,
    ) -> HarnessResult<String> {
        let connection: Connection =
            match cred_offer.connection_id.is_empty() {
                false => self.dbs.connection.get(&cred_offer.connection_id).ok_or(
                    HarnessError::from_msg(
                        HarnessErrorType::NotFoundError,
                        &format!("Connection with id {} not found", cred_offer.connection_id),
                    ),
                )?,
                true => self.last_connection.clone().ok_or(HarnessError::from_msg(
                    HarnessErrorType::InternalServerError,
                    "No connection established",
                ))?,
            };
        let issuer = match id.is_empty() {
            true => {
                let cred_def: CachedCredDef =
                    self.dbs.cred_def.get(&cred_offer.cred_def_id).ok_or(
                        HarnessError::from_msg(
                            HarnessErrorType::NotFoundError,
                            &format!("Cred def with id {} not found", cred_offer.cred_def_id),
                        ),
                    )?;
                let id = uuid::Uuid::new_v4().to_string();
                let credential_preview =
                    serde_json::to_string(&cred_offer.credential_preview.attributes)?;
                let offer_info = OfferInfo {
                    credential_json: credential_preview,
                    cred_def_id: cred_offer.cred_def_id.clone(),
                    rev_reg_id: cred_def.rev_reg_id.clone(),
                    tails_file: cred_def.tails_file.clone(),
                };
                let mut issuer = Issuer::create(&id)?;
                issuer
                    .build_credential_offer_msg(self.config.wallet_handle, offer_info, None)
                    .await?;
                issuer
                    .send_credential_offer(
                        connection
                            .send_message_closure(self.config.wallet_handle)
                            .await?,
                    )
                    .await?;
                issuer
            }
            false => {
                let mut agency_client =
                    AgencyClient::new().configure(&self.config.agency_client_config)?;
                agency_client.set_wallet_handle(self.config.wallet_handle);
                let proposal = get_proposal(&connection, &agency_client).await?;
                let cred_def: CachedCredDef =
                    self.dbs
                        .cred_def
                        .get(&proposal.cred_def_id)
                        .ok_or(HarnessError::from_msg(
                            HarnessErrorType::NotFoundError,
                            &format!("Cred def with id {} not found", cred_offer.cred_def_id),
                        ))?;
                let offer_info = OfferInfo {
                    credential_json: proposal.credential_proposal.to_string().unwrap(),
                    cred_def_id: proposal.cred_def_id.clone(),
                    rev_reg_id: cred_def.rev_reg_id.clone(),
                    tails_file: cred_def.tails_file.clone(),
                };
                let mut issuer = Issuer::create_from_proposal(id, &proposal)?;
                issuer
                    .build_credential_offer_msg(self.config.wallet_handle, offer_info, None)
                    .await?;
                issuer
                    .send_credential_offer(
                        connection
                            .send_message_closure(self.config.wallet_handle)
                            .await?,
                    )
                    .await?;
                issuer
            }
        };
        let thread_id = issuer.get_thread_id()?;
        self.dbs.issuer.set(&thread_id, &issuer)?;
        self.dbs.connection.set(&thread_id, &connection)?;
        Ok(json!({ "state": _get_state_issuer(&issuer), "thread_id": thread_id }).to_string())
    }

    pub async fn issue_credetial(
        &mut self,
        id: &str,
        _credential: &Credential,
    ) -> HarnessResult<String> {
        let mut issuer: Issuer = self.dbs.issuer.get(id).ok_or(HarnessError::from_msg(
            HarnessErrorType::NotFoundError,
            &format!("Issuer with id {} not found", id),
        ))?;
        let connection: Connection = self.dbs.connection.get(id).ok_or(HarnessError::from_msg(
            HarnessErrorType::NotFoundError,
            &format!("Connection with id {} not found", id),
        ))?;
        let mut agency_client = AgencyClient::new().configure(&self.config.agency_client_config)?;
        agency_client.set_wallet_handle(self.config.wallet_handle);
        issuer
            .update_state(self.config.wallet_handle, &agency_client, &connection)
            .await?;
        issuer
            .send_credential(
                self.config.wallet_handle,
                connection
                    .send_message_closure(self.config.wallet_handle)
                    .await?,
            )
            .await?;
        self.dbs.issuer.set(id, &issuer)?;
        Ok(json!({ "state": _get_state_issuer(&issuer) }).to_string())
    }

    pub async fn send_ack(&mut self, id: &str) -> HarnessResult<String> {
        let mut holder: Holder = self.dbs.holder.get(id).ok_or(HarnessError::from_msg(
            HarnessErrorType::NotFoundError,
            &format!("Holder with id {} not found", id),
        ))?;
        let connection: Connection = self.dbs.connection.get(id).ok_or(HarnessError::from_msg(
            HarnessErrorType::NotFoundError,
            &format!("Connection with id {} not found", id),
        ))?;
        let mut agency_client = AgencyClient::new().configure(&self.config.agency_client_config)?;
        agency_client.set_wallet_handle(self.config.wallet_handle);
        holder
            .update_state(
                self.config.wallet_handle,
                self.config.pool_handle,
                &agency_client,
                &connection,
            )
            .await?;
        if holder
            .is_revokable(self.config.wallet_handle, self.config.pool_handle)
            .await?
        {
            let rev_reg_id = holder.get_rev_reg_id()?;
            let tails_hash = holder.get_tails_hash()?;
            let tails_location = holder.get_tails_location()?;
            download_tails_file(&tails_location, &rev_reg_id, &tails_hash).await?;
        };
        self.dbs.holder.set(id, &holder)?;
        Ok(json!({ "state": _get_state_holder(&holder), "credential_id": id }).to_string())
    }

    pub async fn get_issuer_state(&mut self, id: &str) -> HarnessResult<String> {
        let connection: Connection =
            self.dbs
                .connection
                .get(id)
                .unwrap_or(self.last_connection.clone().ok_or(HarnessError::from_msg(
                    HarnessErrorType::InternalServerError,
                    "No connection established",
                ))?);
        let mut agency_client = AgencyClient::new().configure(&self.config.agency_client_config)?;
        agency_client.set_wallet_handle(self.config.wallet_handle);
        match self.dbs.issuer.get::<Issuer>(id) {
            Some(mut issuer) => {
                issuer
                    .update_state(self.config.wallet_handle, &agency_client, &connection)
                    .await?;
                self.dbs.issuer.set(id, &issuer)?;
                self.dbs.connection.set(id, &issuer)?;
                Ok(json!({ "state": _get_state_issuer(&issuer) }).to_string())
            }
            None => match self.dbs.holder.get::<Holder>(id) {
                Some(mut holder) => {
                    holder
                        .update_state(
                            self.config.wallet_handle,
                            self.config.pool_handle,
                            &agency_client,
                            &connection,
                        )
                        .await?;
                    self.dbs.holder.set(id, &holder)?;
                    self.dbs.connection.set(id, &connection)?;
                    Ok(json!({ "state": _get_state_holder(&holder) }).to_string())
                }
                None => {
                    let offer = get_offer(&connection, &agency_client, id).await?;
                    let holder = Holder::create_from_offer(id, offer)?;
                    self.dbs.holder.set(id, &holder)?;
                    self.dbs.connection.set(id, &connection)?;
                    Ok(json!({ "state": _get_state_holder(&holder) }).to_string())
                }
            },
        }
    }

    pub async fn get_credential(&mut self, id: &str) -> HarnessResult<String> {
        let mut holder: Holder = self.dbs.holder.get(id).ok_or(HarnessError::from_msg(
            HarnessErrorType::NotFoundError,
            &format!("Holder with id {} not found", id),
        ))?;
        let connection: Connection = self.dbs.connection.get(id).ok_or(HarnessError::from_msg(
            HarnessErrorType::NotFoundError,
            &format!("Connection with id {} not found", id),
        ))?;
        let mut agency_client = AgencyClient::new().configure(&self.config.agency_client_config)?;
        agency_client.set_wallet_handle(self.config.wallet_handle);
        holder
            .update_state(
                self.config.wallet_handle,
                self.config.pool_handle,
                &agency_client,
                &connection,
            )
            .await?;
        let attach = holder.get_attachment()?;
        let attach: serde_json::Value = serde_json::from_str(&attach)?;
        let mut attach = attach
            .as_object()
            .ok_or(HarnessError::from_msg(
                HarnessErrorType::InternalServerError,
                "Failed to convert attach Value to Map",
            ))?
            .clone();
        attach.insert(
            "referent".to_string(),
            serde_json::Value::String(id.to_string()),
        );
        Ok(serde_json::to_string(&attach)?)
    }
}

#[post("/send-proposal")]
pub async fn send_credential_proposal(
    req: web::Json<Request<CredentialProposal>>,
    agent: web::Data<Mutex<Agent>>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .send_credential_proposal(&req.data)
        .await
        .customize()
        .append_header(CacheControl(vec![
            CacheDirective::Private,
            CacheDirective::NoStore,
            CacheDirective::MustRevalidate,
        ]))
}

#[post("/send-offer")]
pub async fn send_credential_offer(
    req: web::Json<Request<CredentialOffer>>,
    agent: web::Data<Mutex<Agent>>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .send_credential_offer(&req.data, &req.id)
        .await
        .customize()
        .append_header(CacheControl(vec![
            CacheDirective::Private,
            CacheDirective::NoStore,
            CacheDirective::MustRevalidate,
        ]))
}

#[post("/send-request")]
pub async fn send_credential_request(
    req: web::Json<Request<String>>,
    agent: web::Data<Mutex<Agent>>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .send_credential_request(&req.id)
        .await
        .customize()
        .append_header(CacheControl(vec![
            CacheDirective::Private,
            CacheDirective::NoStore,
            CacheDirective::MustRevalidate,
        ]))
}

#[get("/{issuer_id}")]
pub async fn get_issuer_state(
    agent: web::Data<Mutex<Agent>>,
    path: web::Path<String>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .get_issuer_state(&path.into_inner())
        .await
        .customize()
        .append_header(CacheControl(vec![
            CacheDirective::Private,
            CacheDirective::NoStore,
            CacheDirective::MustRevalidate,
        ]))
}

#[post("/issue")]
pub async fn issue_credential(
    req: web::Json<Request<Credential>>,
    agent: web::Data<Mutex<Agent>>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .issue_credetial(&req.id, &req.data)
        .await
        .customize()
        .append_header(CacheControl(vec![
            CacheDirective::Private,
            CacheDirective::NoStore,
            CacheDirective::MustRevalidate,
        ]))
}

#[post("/store")]
pub async fn send_ack(
    req: web::Json<Request<CredentialId>>,
    agent: web::Data<Mutex<Agent>>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .send_ack(&req.id)
        .await
        .customize()
        .append_header(CacheControl(vec![
            CacheDirective::Private,
            CacheDirective::NoStore,
            CacheDirective::MustRevalidate,
        ]))
}

#[get("/{cred_id}")]
pub async fn get_credential(
    agent: web::Data<Mutex<Agent>>,
    path: web::Path<String>,
) -> impl Responder {
    agent
        .lock()
        .unwrap()
        .get_credential(&path.into_inner())
        .await
        .customize()
        .append_header(CacheControl(vec![
            CacheDirective::Private,
            CacheDirective::NoStore,
            CacheDirective::MustRevalidate,
        ]))
}

pub fn config(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::scope("/command/issue-credential")
            .service(send_credential_proposal)
            .service(send_credential_offer)
            .service(get_issuer_state)
            .service(send_credential_request)
            .service(issue_credential)
            .service(send_ack),
    )
    .service(web::scope("/command/credential").service(get_credential));
}
