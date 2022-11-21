use actix_web::{error, http::StatusCode, HttpResponse, HttpResponseBuilder};
use aries_vcx_agent::aries_vcx;
use aries_vcx_agent::aries_vcx::indy::primitives::credential_definition::{
    CredentialDefConfigBuilderError, RevocationDetailsBuilderError,
};
use aries_vcx_agent::aries_vcx::indy::proofs::proof_request::ProofRequestDataBuilderError;
use aries_vcx_agent::aries_vcx::messages::error::MessagesError;
use aries_vcx_agent::AgentError;
use derive_more::{Display, Error};

pub type HarnessResult<T> = Result<T, HarnessError>;

#[derive(Debug, Display, Error, Clone)]
pub enum HarnessErrorType {
    #[display(fmt = "Internal server error")]
    InternalServerError,
    #[display(fmt = "Request not accepted")]
    RequestNotAcceptedError,
    #[display(fmt = "Request not received")]
    RequestNotReceived,
    #[display(fmt = "Not found")]
    NotFoundError,
    #[display(fmt = "Invalid JSON")]
    InvalidJson,
    #[display(fmt = "Protocol error")]
    ProtocolError,
    #[display(fmt = "Invalid state for requested operation")]
    InvalidState,
    #[display(fmt = "Encryption error")]
    EncryptionError,
    #[display(fmt = "Multiple credential definitions found")]
    MultipleCredDefinitions,
}

#[derive(Debug, Display, Error, Clone)]
#[display(fmt = "Error: {}", message)]
pub struct HarnessError {
    pub message: String,
    pub kind: HarnessErrorType,
}

impl error::ResponseError for HarnessError {
    fn error_response(&self) -> HttpResponse {
        error!("{}", self.to_string());
        HttpResponseBuilder::new(self.status_code()).body(self.to_string())
    }

    fn status_code(&self) -> StatusCode {
        match self.kind {
            HarnessErrorType::RequestNotAcceptedError
            | HarnessErrorType::RequestNotReceived
            | HarnessErrorType::InvalidJson => StatusCode::NOT_ACCEPTABLE,
            HarnessErrorType::NotFoundError => StatusCode::NOT_FOUND,
            _ => StatusCode::INTERNAL_SERVER_ERROR,
        }
    }
}

impl HarnessError {
    pub fn from_msg(kind: HarnessErrorType, msg: &str) -> Self {
        HarnessError {
            kind,
            message: msg.to_string(),
        }
    }

    pub fn from_kind(kind: HarnessErrorType) -> Self {
        let message = kind.to_string();
        HarnessError { kind, message }
    }
}

impl std::convert::From<aries_vcx::error::VcxError> for HarnessError {
    fn from(vcx_err: aries_vcx::error::VcxError) -> HarnessError {
        let kind = HarnessErrorType::InternalServerError;
        HarnessError {
            message: vcx_err.to_string(),
            kind,
        }
    }
}

impl std::convert::From<aries_vcx::agency_client::error::AgencyClientError> for HarnessError {
    fn from(
        agency_client_error: aries_vcx::agency_client::error::AgencyClientError,
    ) -> HarnessError {
        let kind = HarnessErrorType::InternalServerError;
        HarnessError {
            message: agency_client_error.to_string(),
            kind,
        }
    }
}

impl std::convert::From<serde_json::Error> for HarnessError {
    fn from(serde_err: serde_json::Error) -> HarnessError {
        let kind = HarnessErrorType::InternalServerError;
        let message = format!("(De)serialization failed; err: {:?}", serde_err.to_string());
        HarnessError { message, kind }
    }
}

impl std::convert::From<std::io::Error> for HarnessError {
    fn from(io_err: std::io::Error) -> HarnessError {
        let kind = HarnessErrorType::InternalServerError;
        let message = format!("I/O error: {:?}", io_err.to_string());
        HarnessError { message, kind }
    }
}

impl std::convert::From<reqwest::Error> for HarnessError {
    fn from(rw_err: reqwest::Error) -> HarnessError {
        let kind = HarnessErrorType::InternalServerError;
        let message = format!("Reqwest error: {:?}", rw_err.to_string());
        HarnessError { message, kind }
    }
}

impl std::convert::From<RevocationDetailsBuilderError> for HarnessError {
    fn from(err: RevocationDetailsBuilderError) -> HarnessError {
        let kind = HarnessErrorType::InternalServerError;
        let message = format!("RevocationDetailsBuilderError: {:?}", err.to_string());
        HarnessError { message, kind }
    }
}

impl std::convert::From<CredentialDefConfigBuilderError> for HarnessError {
    fn from(err: CredentialDefConfigBuilderError) -> HarnessError {
        let kind = HarnessErrorType::InternalServerError;
        let message = format!("CredentialDefConfigBuilderError: {:?}", err.to_string());
        HarnessError { message, kind }
    }
}

impl std::convert::From<ProofRequestDataBuilderError> for HarnessError {
    fn from(err: ProofRequestDataBuilderError) -> HarnessError {
        let kind = HarnessErrorType::InternalServerError;
        let message = format!("ProofRequestDataBuilderError: {:?}", err.to_string());
        HarnessError { message, kind }
    }
}

impl std::convert::From<AgentError> for HarnessError {
    fn from(err: AgentError) -> HarnessError {
        let kind = HarnessErrorType::InternalServerError;
        let message = format!("AgentError: {:?}", err.to_string());
        HarnessError { message, kind }
    }
}

impl std::convert::From<MessagesError> for HarnessError {
    fn from(err: MessagesError) -> HarnessError {
        let kind = HarnessErrorType::InternalServerError;
        let message = format!("MessagesError: {:?}", err.to_string());
        HarnessError { message, kind }
    }
}
