//! State Transition Function (STF) for SmithNode
//!
//! This module defines the core state machine that:
//! - Accepts AI validation proofs
//! - Rewards validators with tokens
//! - Manages the cognitive challenge system
//! - Handles governance proposals and voting

mod state;
mod transaction;
mod challenge;
mod governance;

pub use state::{SmithNodeState, ValidatorInfo, BlockHeader, TxRecord};
pub use transaction::{NodeTx, TxResult};
pub use challenge::{CognitiveChallenge, ChallengeResponse, CognitivePuzzle, PuzzleType};
// Governance types - used by RPC and state
pub use governance::{GovernanceState, NetworkParams, Proposal, ProposalType, ProposalStatus, Vote, ProposalStats};
