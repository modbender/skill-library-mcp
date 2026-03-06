//! ClawChain RPC client for EvoClaw agents
//!
//! This skill enables EvoClaw agents to:
//! - Query their on-chain reputation
//! - Check token balances
//! - Vote on governance proposals
//! - Register new agents
//! - Submit transactions
//!
//! Usage:
//! ```rust
//! use clawchain::ClawChainClient;
//!
//! let client = ClawChainClient::new("ws://localhost:9944").await?;
//! let reputation = client.get_agent_reputation("did:claw:...").await?;
//! ```

pub mod client;
pub mod types;
pub mod error;

pub use client::ClawChainClient;
pub use error::{ClawChainError, Result};
pub use types::{AgentInfo, ChainEvent, Proposal};

// Re-exports for convenience
pub use client::{
    register_agent,
    get_agent,
    get_token_balance,
    vote,
    submit_extrinsic,
    subscribe_events,
};
