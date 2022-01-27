use actix_web::{
    HttpResponseBuilder, error, http::StatusCode, HttpResponse,
};
use derive_more::{Display, Error};
use aries_vcx::handlers::issuance::credential_def::{RevocationDetailsBuilderError, CredentialDefConfigBuilderError};
use aries_vcx::libindy::proofs::proof_request::ProofRequestDataBuilderError;

pub type HarnessResult<T> = Result<T, HarnessError>;

#[derive(Debug, Display, Error, Clone)]
pub enum HarnessErrorType {
    #[display(fmt = "Internal server error")]
    InternalServerError,
    #[display(fmt = "Request not accepted")]
    RequestNotAcceptedError,
    #[display(fmt = "Not found")]
    NotFoundError,
    #[display(fmt = "Invalid JSON")]
    InvalidJson,
    #[display(fmt = "Protocol error")]
    ProtocolError,
}

#[derive(Debug, Display, Error, Clone)]
#[display(fmt = "Error: {}", message)]
pub struct HarnessError {
    pub message: String,
    pub kind: HarnessErrorType
}

impl error::ResponseError for HarnessError {
    fn error_response(&self) -> HttpResponse {
        HttpResponseBuilder::new(self.status_code())
            .body(self.to_string())
    }

    fn status_code(&self) -> StatusCode {
        match self.kind {
            HarnessErrorType::InternalServerError => StatusCode::INTERNAL_SERVER_ERROR,
            HarnessErrorType::RequestNotAcceptedError |
                HarnessErrorType::InvalidJson => StatusCode::NOT_ACCEPTABLE,
            HarnessErrorType::NotFoundError => StatusCode::NOT_FOUND,
            HarnessErrorType::ProtocolError => StatusCode::INTERNAL_SERVER_ERROR,
        }
    }
}

impl HarnessError {
    pub fn from_msg(kind: HarnessErrorType, msg: &str) -> Self {
        HarnessError { kind, message: msg.to_string() }
    }

    pub fn from_kind(kind: HarnessErrorType) -> Self {
        let message = kind.to_string();
        HarnessError { kind, message }
    }
}

impl std::convert::From<aries_vcx::error::VcxError> for HarnessError {
    fn from(vcx_err: aries_vcx::error::VcxError) -> HarnessError {
        let kind = HarnessErrorType::InternalServerError;
        HarnessError { message: vcx_err.to_string(), kind }
    }
}

impl std::convert::From<pickledb::error::Error> for HarnessError {
    fn from(pickle_err: pickledb::error::Error) -> HarnessError {
        let kind = HarnessErrorType::NotFoundError;
        let message = format!(
            "Failed to load / save object from memory; err: {:?}", pickle_err.to_string()
        );
        HarnessError { message: message.to_string(), kind }
    }
}

impl std::convert::From<serde_json::Error> for HarnessError {
    fn from(serde_err: serde_json::Error) -> HarnessError {
        let kind = HarnessErrorType::InternalServerError;
        let message = format!(
            "(De)serialization failed; err: {:?}", serde_err.to_string()
        );
        HarnessError { message: message.to_string(), kind }
    }
}

impl std::convert::From<std::io::Error> for HarnessError {
    fn from(io_err: std::io::Error) -> HarnessError {
        let kind = HarnessErrorType::InternalServerError;
        let message = format!(
            "I/O error: {:?}", io_err.to_string()
        );
        HarnessError { message, kind }
    }
}

impl std::convert::From<reqwest::Error> for HarnessError {
    fn from(rw_err: reqwest::Error) -> HarnessError {
        let kind = HarnessErrorType::InternalServerError;
        let message = format!(
            "Reqwest error: {:?}", rw_err.to_string()
        );
        HarnessError { message, kind }
    }
}

impl std::convert::From<RevocationDetailsBuilderError> for HarnessError {
    fn from(err: RevocationDetailsBuilderError) -> HarnessError {
        let kind = HarnessErrorType::InternalServerError;
        let message = format!(
            "RevocationDetailsBuilderError: {:?}", err.to_string()
        );
        HarnessError { message, kind }
    }
}

impl std::convert::From<CredentialDefConfigBuilderError> for HarnessError {
    fn from(err: CredentialDefConfigBuilderError) -> HarnessError {
        let kind = HarnessErrorType::InternalServerError;
        let message = format!(
            "CredentialDefConfigBuilderError: {:?}", err.to_string()
        );
        HarnessError { message, kind }
    }
}

impl std::convert::From<ProofRequestDataBuilderError> for HarnessError {
    fn from(err: ProofRequestDataBuilderError) -> HarnessError {
        let kind = HarnessErrorType::InternalServerError;
        let message = format!(
            "ProofRequestDataBuilderError: {:?}", err.to_string()
        );
        HarnessError { message, kind }
    }
}
