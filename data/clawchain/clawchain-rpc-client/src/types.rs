//! Type definitions for ClawChain

use serde::{Deserialize, Serialize};

/// Agent DID format: did:claw:<hash>
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentDID(String);

impl AgentDID {
    /// Parse a DID string
    pub fn parse(did: &str) -> Result<Self> {
        if !did.starts_with("did:claw:") {
            return Err(ClawChainError::InvalidDID(format!(
                "Expected 'did:claw:' prefix, got: {}", did
            )));
        }
        let hash = did[9..].to_string();
        if hash.len() != 64 {
            return Err(ClawChainError::InvalidDID(format!(
                "Expected 64-char hash, got {} chars", hash.len()
            )));
        }
        Ok(AgentDID(did.to_string()))
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// Agent information from AgentRegistry pallet
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentInfo {
    pub did: String,
    pub owner: String,
    pub metadata: String,
    pub reputation: u64,
    pub verifications: u32,
    pub registered_at_block: u64,
}

/// Governance proposal
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Proposal {
    pub id: u64,
    pub proposer: String,
    pub title: String,
    pub description: String,
    pub yes_votes: u64,
    pub no_votes: u64,
    pub status: ProposalStatus,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ProposalStatus {
    Pending,
    Active,
    Passed,
    Rejected,
    Executed,
}

/// Chain events for subscription
#[derive(Debug, Clone)]
pub enum ChainEvent {
    Block { number: u64, hash: String },
    AgentRegistered { did: String },
    AgentVerified { did: String, by: String },
    ProposalCreated { id: u64 },
    ProposalPassed { id: u64 },
    ProposalRejected { id: u64 },
    TokenTransfer { from: String, to: String, amount: u128 },
}

use crate::error::{ClawChainError, Result};

impl AgentDID {
    /// Generate DID from metadata and owner
    pub fn generate(metadata: &str, owner: &str) -> Self {
        use sha2::{Sha256, Digest};
        
        let mut hasher = Sha256::new();
        hasher.update(metadata.as_bytes());
        hasher.update(owner.as_bytes());
        let hash = hasher.finalize();
        
        AgentDID(format!("did:claw:{:064x}", hash))
    }
}
