//! Error types for ClawChain RPC client

use thiserror::Error;

/// ClawChain RPC errors
#[derive(Error, Debug)]
pub enum ClawChainError {
    #[error("RPC connection failed: {0}")]
    ConnectionError(String),

    #[error("Transaction failed: {0}")]
    TransactionError(String),

    #[error("Agent not found: {0}")]
    NotFound(String),

    #[error("Unauthorized: {0}")]
    Unauthorized(String),

    #[error("Invalid DID format: {0}")]
    InvalidDID(String),

    #[error("Chain error: {0}")]
    ChainError(String),

    #[error("Serialization error: {0}")]
    SerializationError(String),

    #[error("Deserialization error: {0}")]
    DeserializationError(String),

    #[error("Timeout after {0}s")]
    Timeout(u64),
}

/// Result type alias
pub type Result<T> = std::result::Result<T, ClawChainError>;
