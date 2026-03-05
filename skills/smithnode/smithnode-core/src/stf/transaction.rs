//! Transaction types for SmithNode

use serde::{Deserialize, Serialize};
use sha2::{Sha256, Digest};

/// Transaction types supported by SmithNode
#[derive(Clone, Debug)]
pub enum NodeTx {
    /// Submit a validation proof (from AI agent)
    SubmitProof {
        validator_pubkey: [u8; 32],
        challenge_hash: [u8; 32],
        signature: [u8; 64],
        /// Merkle root of flagged transaction IDs (verdict)
        verdict_digest: [u8; 32],
        /// AI's answer to the cognitive puzzle (if puzzle was present)
        puzzle_answer: Option<String>,
    },
    
    /// Transfer tokens between accounts
    Transfer {
        from: [u8; 32],
        to: [u8; 32],
        amount: u64,
        nonce: u64,
        signature: [u8; 64],
    },
    
    /// Register as a new validator
    RegisterValidator {
        public_key: [u8; 32],
    },
    
    /// AI-to-AI message (verifiable P2P communication)
    AIMessage {
        /// Sender validator public key
        from: [u8; 32],
        /// Target validator (or all zeros for broadcast)
        to: [u8; 32],
        /// Message content hash
        content_hash: [u8; 32],
        /// AI response hash (if this is a response)
        response_hash: Option<[u8; 32]>,
        /// Timestamp
        timestamp: u64,
        /// Signature over message
        signature: [u8; 64],
        /// Message type: 0=query, 1=response, 2=broadcast
        message_type: u8,
    },
    
    /// Create a governance proposal
    CreateProposal {
        proposer: [u8; 32],
        /// Proposal type encoded: 0=reward, 1=committee, 2=minstake, 3=slash, 4=blocktime, 5=ratelimit, 6=maxval, 7=emergency
        proposal_type: u8,
        /// New value for the parameter
        new_value: u64,
        /// Description hash
        description_hash: [u8; 32],
        signature: [u8; 64],
    },
    
    /// Vote on a governance proposal
    VoteProposal {
        voter: [u8; 32],
        proposal_id: u64,
        vote: bool,  // true = approve, false = reject
        signature: [u8; 64],
        /// AI-generated reasoning for the vote
        reason: Option<String>,
    },
    
    /// Execute a passed proposal
    ExecuteProposal {
        executor: [u8; 32],
        proposal_id: u64,
        signature: [u8; 64],
    },
}

impl NodeTx {
    /// Compute the hash of this transaction
    pub fn hash(&self) -> [u8; 32] {
        let mut hasher = Sha256::new();
        
        match self {
            NodeTx::SubmitProof {
                validator_pubkey,
                challenge_hash,
                signature,
                verdict_digest,
                puzzle_answer,
            } => {
                hasher.update(b"submit_proof");
                hasher.update(validator_pubkey);
                hasher.update(challenge_hash);
                hasher.update(signature);
                hasher.update(verdict_digest);
                if let Some(ref answer) = puzzle_answer {
                    hasher.update(answer.as_bytes());
                }
            }
            NodeTx::Transfer {
                from,
                to,
                amount,
                nonce,
                signature,
            } => {
                hasher.update(b"transfer");
                hasher.update(from);
                hasher.update(to);
                hasher.update(&amount.to_le_bytes());
                hasher.update(&nonce.to_le_bytes());
                hasher.update(signature);
            }
            NodeTx::RegisterValidator { public_key } => {
                hasher.update(b"register_validator");
                hasher.update(public_key);
            }
            NodeTx::AIMessage {
                from,
                to,
                content_hash,
                response_hash,
                timestamp,
                signature,
                message_type,
            } => {
                hasher.update(b"ai_message");
                hasher.update(from);
                hasher.update(to);
                hasher.update(content_hash);
                if let Some(resp) = response_hash {
                    hasher.update(resp);
                }
                hasher.update(&timestamp.to_le_bytes());
                hasher.update(signature);
                hasher.update(&[*message_type]);
            }
            NodeTx::CreateProposal {
                proposer,
                proposal_type,
                new_value,
                description_hash,
                signature,
            } => {
                hasher.update(b"create_proposal");
                hasher.update(proposer);
                hasher.update(&[*proposal_type]);
                hasher.update(&new_value.to_le_bytes());
                hasher.update(description_hash);
                hasher.update(signature);
            }
            NodeTx::VoteProposal {
                voter,
                proposal_id,
                vote,
                signature,
                reason,
            } => {
                hasher.update(b"vote_proposal");
                hasher.update(voter);
                hasher.update(&proposal_id.to_le_bytes());
                hasher.update(&[if *vote { 1 } else { 0 }]);
                hasher.update(signature);
                if let Some(ref r) = reason {
                    hasher.update(r.as_bytes());
                }
            }
            NodeTx::ExecuteProposal {
                executor,
                proposal_id,
                signature,
            } => {
                hasher.update(b"execute_proposal");
                hasher.update(executor);
                hasher.update(&proposal_id.to_le_bytes());
                hasher.update(signature);
            }
        }
        
        hasher.finalize().into()
    }
}

/// Result of applying a transaction
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum TxResult {
    Success {
        reward: u64,
        new_balance: u64,
    },
    /// Block was finalized after this proof
    BlockFinalized {
        reward: u64,
        new_balance: u64,
        block_height: u64,
        state_root: [u8; 32],
    },
    Registered {
        public_key: String,
    },
    /// Governance proposal created
    ProposalCreated {
        proposal_id: u64,
    },
    /// Vote recorded
    VoteRecorded {
        proposal_id: u64,
        vote: bool,
    },
    /// Proposal executed
    ProposalExecuted {
        proposal_id: u64,
        param_changed: String,
    },
    Error(String),
}

impl TxResult {
    pub fn is_success(&self) -> bool {
        matches!(self, 
            TxResult::Success { .. } | 
            TxResult::BlockFinalized { .. } |
            TxResult::Registered { .. } |
            TxResult::ProposalCreated { .. } |
            TxResult::VoteRecorded { .. } |
            TxResult::ProposalExecuted { .. }
        )
    }
}
