use actix_web::{
    dev::HttpResponseBuilder, error, get, http::header, http::StatusCode, App, HttpResponse,
};
use derive_more::{Display, Error};

pub type HarnessResult<T> = Result<T, HarnessError>;

#[derive(Debug, Display, Error)]
pub enum HarnessErrorType {
    #[display(fmt = "Internal server error")]
    InternalServerError,
    #[display(fmt = "Request not accepted")]
    RequestNotAcceptedError,
    #[display(fmt = "Not found")]
    NotFoundError,
}

#[derive(Debug, Display, Error)]
#[display(fmt = "Error: {}", message)]
pub struct HarnessError {
    pub message: String,
    pub kind: HarnessErrorType
}

impl error::ResponseError for HarnessError {
    fn error_response(&self) -> HttpResponse {
        HttpResponseBuilder::new(self.status_code())
            .set_header(header::CONTENT_TYPE, "text/html; charset=utf-8")
            .body(self.to_string())
    }

    fn status_code(&self) -> StatusCode {
        match self.kind {
            HarnessErrorType::InternalServerError => StatusCode::INTERNAL_SERVER_ERROR,
            HarnessErrorType::RequestNotAcceptedError => StatusCode::NOT_ACCEPTABLE,
            HarnessErrorType::NotFoundError => StatusCode::NOT_FOUND,
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
