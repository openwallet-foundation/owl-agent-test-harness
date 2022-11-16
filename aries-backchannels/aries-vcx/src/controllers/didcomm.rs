use crate::error::{HarnessResult, HarnessError, HarnessErrorType};
use crate::HarnessAgent;
use actix_web::{web, HttpResponse, Responder};
use aries_vcx_agent::aries_vcx::{
    messages::a2a::A2AMessage, utils::encryption_envelope::EncryptionEnvelope,
};
use std::sync::RwLock;

impl HarnessAgent {
    pub async fn receive_message(&self, payload: Vec<u8>) -> HarnessResult<HttpResponse> {
        let (message, sender_vk) =
            EncryptionEnvelope::anon_unpack(self.aries_agent.wallet_handle(), payload).await?;
        let sender_vk = sender_vk.ok_or_else(|| {
            HarnessError::from_msg(
                HarnessErrorType::EncryptionError,
                "Received anoncrypted message",
            )
        })?;
        info!("Received message: {:?}", message);
        let connection_ids = self.aries_agent.connections().get_by_their_vk(&sender_vk)?;
        let connection_id = connection_ids.last();
        match message {
            A2AMessage::ConnectionRequest(request) => {
                self.aries_agent
                    .connections()
                    .accept_request(&request.get_thread_id(), request)
                    .await?;
            }
            A2AMessage::ConnectionResponse(response) => {
                self.aries_agent
                    .connections()
                    .accept_response(&response.get_thread_id(), response)
                    .await?;
            }
            A2AMessage::CredentialProposal(proposal) => {
                if connection_ids.len() == 1 {
                    self.aries_agent
                        .issuer()
                        .accept_proposal(connection_id.unwrap(), &proposal)
                        .await?;
                } else {
                    return Err(HarnessError::from_msg(HarnessErrorType::InvalidState, &format!("Found multiple or no connections by verkey {}", sender_vk)));
                }
            }
            A2AMessage::CredentialOffer(offer) => {
                if connection_ids.len() == 1 {
                    self.aries_agent
                        .holder()
                        .create_from_offer(connection_id.unwrap(), offer)?;
                } else {
                    return Err(HarnessError::from_msg(HarnessErrorType::InvalidState, &format!("Found multiple or no connections by verkey {}", sender_vk)));
                }
            }
            A2AMessage::CredentialRequest(request) => {
                self.aries_agent
                    .issuer()
                    .process_credential_request(&request.get_thread_id(), request)?;
            }
            A2AMessage::Credential(credential) => {
                self.aries_agent
                    .holder()
                    .process_credential(&credential.get_thread_id(), credential).await?;
            }
            A2AMessage::PresentationRequest(request) => {
                if connection_ids.len() == 1 {
                    self.aries_agent
                        .prover()
                        .create_from_request(connection_id.unwrap(), request)?;
                } else {
                    return Err(HarnessError::from_msg(HarnessErrorType::InvalidState, &format!("Found multiple or no connections by verkey {}", sender_vk)));
                }
            }
            A2AMessage::Presentation(presentation) => {
                self.aries_agent
                    .verifier()
                    .verify_presentation(&presentation.get_thread_id(), presentation)
                    .await?;
            }
            A2AMessage::PresentationAck(ack) => {
                self.aries_agent
                    .prover()
                    .process_presentation_ack(&ack.get_thread_id(), ack)?;
            }
            m @ _ => {
                warn!("Received message of unexpected type: {:?}", m);
            }
        }
        Ok(HttpResponse::Ok().finish())
    }
}

pub async fn receive_message(
    req: web::Bytes,
    agent: web::Data<RwLock<HarnessAgent>>,
) -> impl Responder {
    agent.read().unwrap().receive_message(req.to_vec()).await
}
