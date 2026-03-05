//! JSON-RPC Server for SmithNode
//!
//! Exposes APIs for AI agents to:
//! - Subscribe to new blocks
//! - Get current challenge
//! - Submit validation proofs
//! - Query state

use std::sync::Arc;
use std::collections::HashMap;
use std::time::{Duration, Instant};
use jsonrpsee::server::{Server, ServerHandle};
use jsonrpsee::core::{async_trait, RpcResult, SubscriptionResult};
use jsonrpsee::types::ErrorObjectOwned;
use jsonrpsee::proc_macros::rpc;
use jsonrpsee::PendingSubscriptionSink;
use serde::{Deserialize, Serialize};
use tokio::sync::{Mutex, broadcast, RwLock};
use tower_http::cors::{CorsLayer, Any};

use crate::stf::{SmithNodeState, NodeTx, TxResult, ChallengeResponse as StfChallengeResponse, TxRecord};
use crate::p2p::{NetworkHandle, get_version_tracker, SMITH_VERSION};

// ============ RATE LIMITING ============

/// Rate limiter configuration
const RATE_LIMIT_WINDOW_SECS: u64 = 60;           // 1 minute window
// Registration spam protection: duplicate keys rejected by state layer, general RPC rate limiting handles the rest
const CHALLENGE_RATE_LIMIT: usize = 500;           // Max 500 challenge requests per minute (global)
const TRANSFER_RATE_LIMIT: usize = 50;             // Max 50 transfers per minute per sender

/// Rate limit entry tracking request counts
#[derive(Clone, Debug)]
struct RateLimitEntry {
    count: usize,
    window_start: Instant,
}

impl RateLimitEntry {
    fn new() -> Self {
        Self {
            count: 0,
            window_start: Instant::now(),
        }
    }
    
    /// Check if rate limit is exceeded, and increment counter if not
    fn check_and_increment(&mut self, limit: usize) -> bool {
        let now = Instant::now();
        
        // Reset if window has passed
        if now.duration_since(self.window_start) > Duration::from_secs(RATE_LIMIT_WINDOW_SECS) {
            self.count = 0;
            self.window_start = now;
        }
        
        // Check limit
        if self.count >= limit {
            return false; // Rate limited
        }
        
        self.count += 1;
        true // Allowed
    }
}

/// Rate limiter for RPC requests
#[derive(Clone)]
pub struct RateLimiter {
    /// Tracks: (operation_type, key) -> RateLimitEntry
    /// key can be validator pubkey or IP address
    entries: Arc<RwLock<HashMap<(String, String), RateLimitEntry>>>,
}

impl RateLimiter {
    pub fn new() -> Self {
        Self {
            entries: Arc::new(RwLock::new(HashMap::new())),
        }
    }
    
    /// Check if an operation is rate limited
    /// Returns Ok(()) if allowed, Err(message) if rate limited
    pub async fn check(&self, operation: &str, key: &str, limit: usize) -> Result<(), String> {
        let mut entries = self.entries.write().await;
        let cache_key = (operation.to_string(), key.to_string());
        
        let entry = entries.entry(cache_key).or_insert_with(RateLimitEntry::new);
        
        if entry.check_and_increment(limit) {
            // Prune stale entries to prevent unbounded growth.
            // Trigger at 500 entries (was 1000) and use shorter expiry.
            if entries.len() > 500 {
                let now = std::time::Instant::now();
                entries.retain(|_, v| {
                    now.duration_since(v.window_start) < Duration::from_secs(RATE_LIMIT_WINDOW_SECS * 2)
                });
                if entries.len() > 1000 {
                    tracing::warn!("⚠️ Rate limiter has {} entries after pruning, possible abuse", entries.len());
                }
            }
            Ok(())
        } else {
            Err(format!(
                "Rate limit exceeded for {}: max {} requests per {} seconds",
                operation, limit, RATE_LIMIT_WINDOW_SECS
            ))
        }
    }
}

impl Default for RateLimiter {
    fn default() -> Self {
        Self::new()
    }
}

/// Cognitive puzzle data sent to agents so they can solve it
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct PuzzleResponse {
    pub puzzle_type: String,
    pub prompt: String,
    pub code_snippet: Option<String>,
    pub sequence: Option<Vec<String>>,
    pub input_text: Option<String>,
    pub time_limit_ms: u64,
    // expected_answer_hash omitted from response
}

/// RPC request/response types
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ChallengeResponse {
    pub challenge_hash: String,
    pub challenge_type: String,
    pub height: u64,
    pub difficulty: u8,
    pub pending_tx_count: usize,
    pub expires_at: u64,
    pub remaining_seconds: u64,
    /// The cognitive puzzle the validator must solve (AI Proof of Cognition)
    pub cognitive_puzzle: Option<PuzzleResponse>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SubmitProofRequest {
    pub validator_pubkey: String,
    pub challenge_hash: String,
    pub signature: String,
    pub verdict_digest: String,
    /// AI's answer to the cognitive puzzle (optional)
    pub puzzle_answer: Option<String>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SubmitProofResponse {
    pub success: bool,
    pub reward: Option<u64>,
    pub new_balance: Option<u64>,
    pub error: Option<String>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ValidatorInfoResponse {
    pub public_key: String,
    pub balance: u64,
    pub validations_count: u64,
    pub reputation_score: u64,
    pub last_active_timestamp: u64,
    pub is_online: bool,
    pub nonce: u64,                   // Current nonce for transfers (to prevent replay)
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct NodeStatusResponse {
    pub height: u64,
    pub state_root: String,
    pub total_supply: u64,
    pub validator_count: usize,
    pub active_validator_count: usize, // Online in last 5 minutes
    pub has_active_challenge: bool,
    pub node_version: String,
    /// P2P peer ID for this node (for connecting as peer)
    pub peer_id: Option<String>,
    /// All known multiaddrs for connecting to this node (dynamically discovered)
    pub p2p_multiaddrs: Vec<String>,
    /// Known bootstrap peers (other nodes you can connect to)
    pub bootstrap_peers: Vec<String>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RegisterValidatorRequest {
    pub public_key: String,
}

/// Heartbeat/presence request - validators announce they're online
/// MUST include signature to prevent impersonation
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct PresenceRequest {
    pub validator_pubkey: String,
    /// Signature over (pubkey || height || timestamp) for authentication
    /// If not provided, presence will only update local state (not P2P broadcast)
    pub signature: Option<String>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct PresenceResponse {
    pub success: bool,
    pub active_validators: usize,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TransferRequest {
    pub from: String,
    pub to: String,
    pub amount: u64,
    pub nonce: u64,             // Sequence number to prevent replay attacks
    pub signature: String,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TransferResponse {
    pub success: bool,
    pub tx_hash: Option<String>,
    pub error: Option<String>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct PaginatedTransactionsResponse {
    pub transactions: Vec<TxRecord>,
    pub total: usize,
    pub page: usize,
    pub per_page: usize,
    pub total_pages: usize,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CommitteeMemberResponse {
    pub pubkey: String,
    pub submitted_proof: bool,
    pub proof_valid: bool,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CommitteeResponse {
    pub block_height: u64,
    pub members: Vec<CommitteeMemberResponse>,
    pub challenge_hash: String,
    pub expires_at: u64,
    pub approvals: usize,
    pub threshold: usize,
    pub finalized: bool,
}

/// Full state snapshot for subscriptions
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct StateSnapshot {
    pub status: NodeStatusResponse,
    pub validators: Vec<ValidatorInfoResponse>,
    pub challenge: Option<ChallengeResponse>,
    pub timestamp: u64,
}

/// Full state export for P2P sync
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct FullStateExport {
    pub height: u64,
    pub state_root: String,
    pub total_supply: u64,
    pub validators: Vec<ValidatorInfoResponse>,
    pub node_version: String,
}

/// Update check response - used by agents to check if update is available
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct UpdateCheckResponse {
    pub current_version: String,
    pub newest_version: Option<String>,
    pub update_available: bool,
    pub network_versions: std::collections::HashMap<String, usize>,
    /// Verified download URL from trusted operator (if available)
    pub download_url: Option<String>,
    /// SHA256 checksum for this platform (if available)
    pub checksum: Option<String>,
    /// Is this a mandatory upgrade?
    pub mandatory: bool,
    /// Release notes
    pub release_notes: Option<String>,
    /// Whether the upgrade was verified by trusted operator signature
    pub verified: bool,
}

/// P2P-verified validators response
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct P2PValidatorsResponse {
    /// Total validators known (from state)
    pub total_validators: usize,
    /// Validators verified via P2P gossipsub (true P2P peers)
    pub p2p_verified_count: usize,
    /// Validators currently online (seen in last 2 minutes)
    pub online_p2p_count: usize,
    /// List of P2P-verified validators
    pub validators: Vec<P2PValidatorDetail>,
}

/// Detail of a P2P-verified validator
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct P2PValidatorDetail {
    pub public_key: String,
    pub is_online: bool,
    pub last_seen_timestamp: u64,
    pub last_height: u64,
    pub version: String,
    pub presence_count: u64,
    pub first_seen: u64,
    /// "p2p" = true P2P peer, "rpc" = only seen via RPC, "unknown" = never seen
    pub peer_type: String,
}

/// P2P verification result for a single validator
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct P2PVerificationResult {
    pub public_key: String,
    /// Whether this validator has been seen via P2P gossipsub
    pub is_p2p_verified: bool,
    /// Whether currently online (seen in last 2 minutes)
    pub is_online: bool,
    /// Number of valid presence messages received
    pub presence_count: u64,
    /// "p2p", "rpc", or "unknown"
    pub peer_type: String,
    /// Additional info if registered
    pub balance: Option<u64>,
    pub validations_count: Option<u64>,
}

/// Allowed topics for validator AI communication
pub const ALLOWED_AI_TOPICS: &[&str] = &[
    "upgrade",      // Protocol upgrades and improvements
    "marketing",    // Marketing strategies and outreach
    "dev",          // Development discussions
    "code",         // Code reviews and updates
    "governance",   // Governance proposals
    "security",     // Security discussions
    "performance", // Performance optimizations
    "consensus",    // Consensus mechanism discussions
];

/// Rate limiting for AI messages
/// - Questions: 1 per validator per 10 minutes (6 per hour max)
/// - Responses: Handled by committee selection (max 3 per question)
pub const AI_MESSAGE_COOLDOWN_SECS: u64 = 600; // 10 minutes between questions

/// Track last message time per validator for rate limiting
static AI_RATE_LIMITER: std::sync::OnceLock<std::sync::RwLock<HashMap<String, u64>>> = std::sync::OnceLock::new();

fn get_rate_limiter() -> &'static std::sync::RwLock<HashMap<String, u64>> {
    AI_RATE_LIMITER.get_or_init(|| std::sync::RwLock::new(HashMap::new()))
}

fn check_rate_limit(validator_pubkey: &str) -> Result<(), String> {
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();
    
    let limiter = get_rate_limiter();
    let last_time = limiter.read().unwrap_or_else(|p| p.into_inner()).get(validator_pubkey).copied();
    
    if let Some(last) = last_time {
        let elapsed = now - last;
        if elapsed < AI_MESSAGE_COOLDOWN_SECS {
            let remaining = AI_MESSAGE_COOLDOWN_SECS - elapsed;
            return Err(format!(
                "Rate limited. Wait {} minutes {} seconds before sending another message.",
                remaining / 60,
                remaining % 60
            ));
        }
    }
    
    // Update last message time
    limiter.write().unwrap_or_else(|p| p.into_inner()).insert(validator_pubkey.to_string(), now);
    Ok(())
}

/// AI message request for sending via P2P
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AIMessageRequest {
    /// Sender's public key (must be a registered validator)
    pub from: String,
    /// Recipient's public key (or "broadcast" for all validators)
    pub to: String,
    /// Topic of discussion (must be one of: upgrade, marketing, dev, code, governance, security, performance, consensus)
    pub topic: String,
    /// The message/question content
    pub content: String,
    /// AI provider to use (groq or together - both FREE)
    pub ai_provider: String,
    /// Model to use (default: llama-3.1-70b)
    pub model: Option<String>,
    /// Optional: if this is a reply to another message
    pub in_reply_to: Option<String>,
    /// Signature of the message (ed25519 hex)
    pub signature: String,
}

/// AI message response after sending
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AIMessageResponse {
    /// Unique message ID (hash of content + timestamp)
    pub message_id: String,
    /// Whether the message was broadcast successfully
    pub success: bool,
    /// Transaction hash if recorded on chain
    pub tx_hash: Option<String>,
    /// Error message if failed
    pub error: Option<String>,
}

/// AI message record from storage
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AIMessageRecord {
    pub message_id: String,
    pub from: String,
    pub to: String,
    /// Topic: upgrade, marketing, dev, code, governance, security, performance, consensus
    pub topic: String,
    pub content: String,
    pub response: Option<String>,
    pub ai_provider: String,
    pub model: String,
    pub timestamp: u64,
    pub signature: String,
    pub in_reply_to: Option<String>,
    /// "query", "response", "chat", "broadcast"
    pub message_type: String,
    /// Block height when recorded (if on-chain)
    pub block_height: Option<u64>,
    /// On-chain transaction hash
    pub tx_hash: Option<String>,
}

/// Request to query the node's AI
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AIQueryRequest {
    /// The prompt/question to ask the AI
    pub prompt: String,
    /// Optional system prompt/context
    pub system: Option<String>,
    /// Max tokens to generate
    pub max_tokens: Option<u32>,
    /// Temperature (0.0 - 2.0)
    pub temperature: Option<f32>,
    /// Which AI provider to use (if node has multiple configured)
    pub provider: Option<String>,
}

/// Response from AI query
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AIQueryResponse {
    /// The AI's response
    pub response: String,
    /// Which provider was used
    pub provider: String,
    /// Which model was used
    pub model: String,
    /// Tokens consumed
    pub tokens_used: u32,
    /// Response latency in ms
    pub latency_ms: u64,
    /// Error message if failed
    pub error: Option<String>,
}

// ============ GOVERNANCE RPC TYPES (M2 FIX) ============

/// Request to create a governance proposal
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CreateProposalRpcRequest {
    /// Proposer's public key (hex)
    pub proposer: String,
    /// Proposal type: 0=ChangeReward, 1=ChangeCommitteeSize, 2=ChangeMinStake,
    /// 3=ChangeSlashPenalty, 4=ChangeBlockTime, 5=ChangeAIRateLimit, 6=ChangeMaxValidators
    pub proposal_type: u8,
    /// New value for the parameter
    pub new_value: u64,
    /// SHA256 hash of the description text (hex)
    pub description_hash: String,
    /// ed25519 signature over (proposal_type || new_value || description_hash) (hex)
    pub signature: String,
}

/// Request to vote on a proposal
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct VoteProposalRpcRequest {
    /// Voter's public key (hex)
    pub voter: String,
    /// Proposal ID to vote on
    pub proposal_id: u64,
    /// true = approve, false = reject
    pub vote: bool,
    /// ed25519 signature over (proposal_id || vote_byte) (hex)
    pub signature: String,
    /// AI-generated reasoning for the vote (why the validator decided yes/no)
    #[serde(default)]
    pub reason: Option<String>,
}

/// Request to execute an approved proposal
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ExecuteProposalRpcRequest {
    /// Executor's public key (hex)
    pub executor: String,
    /// Proposal ID to execute
    pub proposal_id: u64,
    /// ed25519 signature over (proposal_id) (hex)
    pub signature: String,
}

/// Response for governance operations
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct GovernanceRpcResponse {
    pub success: bool,
    pub message: String,
    pub proposal_id: Option<u64>,
}

/// Summary of a governance proposal
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct GovernanceProposalResponse {
    pub id: u64,
    pub proposer: String,
    pub proposal_type: String,
    pub description: String,
    pub status: String,
    pub votes_for: u64,
    pub votes_against: u64,
    pub created_at: u64,
    pub expires_at: u64,
    /// Transaction hash of proposal creation
    #[serde(skip_serializing_if = "Option::is_none")]
    pub tx_hash: Option<String>,
    /// Transaction hash of execution (if executed)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub execution_tx_hash: Option<String>,
    /// Individual votes with AI reasoning
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub votes: Vec<VoteDetail>,
}

/// Individual vote detail with AI reasoning
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct VoteDetail {
    pub voter: String,
    pub vote: bool,
    pub stake_weight: u64,
    /// AI-generated reasoning for why the validator voted this way
    pub reason: Option<String>,
    /// Transaction hash for this vote
    #[serde(skip_serializing_if = "Option::is_none")]
    pub tx_hash: Option<String>,
}

/// Current network parameters (governed values)
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct NetworkParamsResponse {
    pub reward_per_proof: u64,
    pub committee_size: usize,
    pub min_validator_stake: u64,
    pub slash_percentage: u8,
    pub ai_rate_limit_secs: u64,
    pub max_validators: usize,
    pub challenge_timeout_secs: u64,
}

/// Comprehensive agent dashboard - everything an agent needs for governance decisions
/// Single RPC call to get: status, own validator info, rewards, committee, governance, params
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AgentDashboardResponse {
    // ── Network state ──
    pub height: u64,
    pub state_root: String,
    pub total_supply: u64,
    pub validator_count: usize,
    pub active_validator_count: usize,
    pub node_version: String,
    
    // ── My validator info (if pubkey provided) ──
    pub my_validator: Option<ValidatorInfoResponse>,
    
    // ── Current challenge & puzzle ──
    pub current_challenge: Option<ChallengeResponse>,
    
    // ── Current committee ──
    pub current_committee: Option<CommitteeResponse>,
    
    // ── Governance: current parameters ──
    pub network_params: NetworkParamsResponse,
    
    // ── Governance: active proposals ──
    pub active_proposals: Vec<GovernanceProposalResponse>,
    
    // ── Recent rewards (last N blocks mined by this validator) ──
    pub recent_rewards: Vec<RewardEntry>,
    
    // ── Network health ──
    pub peer_count: usize,
    pub p2p_verified_validators: usize,
}

/// A single reward entry for the agent dashboard
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RewardEntry {
    pub block_height: u64,
    pub reward: u64,
    pub timestamp: u64,
    pub puzzle_bonus: bool,
}

/// Event types for subscriptions
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(tag = "type", content = "data")]
pub enum StateEvent {
    #[serde(rename = "snapshot")]
    Snapshot(StateSnapshot),
    #[serde(rename = "block")]
    NewBlock { height: u64, state_root: String },
    #[serde(rename = "challenge")]
    NewChallenge(ChallengeResponse),
    #[serde(rename = "transaction")]
    NewTransaction(TxRecord),
}

/// RPC trait definition
#[rpc(server)]
pub trait SmithNodeRpcApi {
    /// Get current node status
    #[method(name = "smithnode_status")]
    async fn status(&self) -> RpcResult<NodeStatusResponse>;
    
    /// Get current cognitive challenge
    #[method(name = "smithnode_getChallenge")]
    async fn get_challenge(&self) -> RpcResult<Option<ChallengeResponse>>;
    
    /// Generate a new challenge (triggers block building)
    #[method(name = "smithnode_newChallenge")]
    async fn new_challenge(&self) -> RpcResult<ChallengeResponse>;
    
    /// Submit a validation proof
    #[method(name = "smithnode_submitProof")]
    async fn submit_proof(&self, req: SubmitProofRequest) -> RpcResult<SubmitProofResponse>;
    
    /// Register as a validator
    #[method(name = "smithnode_registerValidator")]
    async fn register_validator(&self, req: RegisterValidatorRequest) -> RpcResult<SubmitProofResponse>;
    
    /// Send presence/heartbeat (announces validator is online)
    #[method(name = "smithnode_presence")]
    async fn presence(&self, req: PresenceRequest) -> RpcResult<PresenceResponse>;
    
    /// Get validator info
    #[method(name = "smithnode_getValidator")]
    async fn get_validator(&self, pubkey: String) -> RpcResult<Option<ValidatorInfoResponse>>;
    
    /// Get all validators
    #[method(name = "smithnode_getValidators")]
    async fn get_validators(&self) -> RpcResult<Vec<ValidatorInfoResponse>>;

    /// Transfer SMITH tokens
    #[method(name = "smithnode_transfer")]
    async fn transfer(&self, req: TransferRequest) -> RpcResult<TransferResponse>;

    /// Get recent transactions (paginated, optionally filtered by type)
    #[method(name = "smithnode_getTransactions")]
    async fn get_transactions(&self, page: Option<usize>, per_page: Option<usize>, tx_type: Option<String>) -> RpcResult<PaginatedTransactionsResponse>;

    /// Get block/transaction by hash
    #[method(name = "smithnode_getBlock")]
    async fn get_block(&self, hash: String) -> RpcResult<Option<TxRecord>>;

    /// Get current committee info
    #[method(name = "smithnode_getCommittee")]
    async fn get_committee(&self) -> RpcResult<Option<CommitteeResponse>>;

    /// Get full state snapshot (for efficient polling or initial subscription state)
    #[method(name = "smithnode_getState")]
    async fn get_state(&self) -> RpcResult<StateSnapshot>;

    /// Get full state export for P2P sync (validators + balances)
    #[method(name = "smithnode_exportState")]
    async fn export_state(&self) -> RpcResult<FullStateExport>;

    /// Import state from another node (for initial sync)
    #[method(name = "smithnode_importState")]
    async fn import_state(&self, state: FullStateExport) -> RpcResult<SubmitProofResponse>;

    /// Subscribe to state updates
    #[subscription(name = "smithnode_subscribeState" => "smithnode_stateUpdate", unsubscribe = "smithnode_unsubscribeState", item = StateEvent)]
    async fn subscribe_state(&self) -> SubscriptionResult;

    /// Check for available updates (for release management)
    #[method(name = "smithnode_checkUpdate")]
    async fn check_update(&self) -> RpcResult<UpdateCheckResponse>;

    /// Announce a new upgrade to the network (operator only)
    #[method(name = "smithnode_AnnounceNode")]
    async fn announce_upgrade(&self, announcement: crate::p2p::UpgradeAnnouncement) -> RpcResult<serde_json::Value>;

    /// Get P2P-verified validators (only validators seen via gossipsub, not just RPC)
    /// This is the TRUSTWORTHY list - these validators are running true P2P nodes
    #[method(name = "smithnode_getP2PValidators")]
    async fn get_p2p_validators(&self) -> RpcResult<P2PValidatorsResponse>;

    /// Check if a specific validator is P2P-verified
    #[method(name = "smithnode_isP2PVerified")]
    async fn is_p2p_verified(&self, pubkey: String) -> RpcResult<P2PVerificationResult>;
    
    /// Send an AI message to the P2P network
    #[method(name = "smithnode_sendAIMessage")]
    async fn send_ai_message(&self, req: AIMessageRequest) -> RpcResult<AIMessageResponse>;
    
    /// Get AI messages for a validator
    #[method(name = "smithnode_getAIMessages")]
    async fn get_ai_messages(&self, pubkey: String, limit: Option<usize>) -> RpcResult<Vec<AIMessageRecord>>;
    
    /// Query this node's AI directly (requires API key configured)
    #[method(name = "smithnode_queryAI")]
    async fn query_ai(&self, req: AIQueryRequest) -> RpcResult<AIQueryResponse>;

    // SECURITY (M2): Governance RPC endpoints - allows on-chain proposals and voting
    
    /// Create a governance proposal
    #[method(name = "smithnode_createProposal")]
    async fn create_proposal(&self, req: CreateProposalRpcRequest) -> RpcResult<GovernanceRpcResponse>;
    
    /// Vote on a governance proposal
    #[method(name = "smithnode_voteProposal")]
    async fn vote_proposal(&self, req: VoteProposalRpcRequest) -> RpcResult<GovernanceRpcResponse>;
    
    /// Execute an approved governance proposal
    #[method(name = "smithnode_executeProposal")]
    async fn execute_proposal(&self, req: ExecuteProposalRpcRequest) -> RpcResult<GovernanceRpcResponse>;
    
    /// Get all governance proposals
    #[method(name = "smithnode_getProposals")]
    async fn get_proposals(&self) -> RpcResult<Vec<GovernanceProposalResponse>>;
    
    /// Get current network parameters (governed values)
    #[method(name = "smithnode_getNetworkParams")]
    async fn get_network_params(&self) -> RpcResult<NetworkParamsResponse>;
    
    /// Get comprehensive agent dashboard (all state needed for governance decisions)
    /// Pass your validator pubkey to get personalized info (balance, rewards, committee membership)
    #[method(name = "smithnode_getAgentDashboard")]
    async fn get_agent_dashboard(&self, pubkey: Option<String>) -> RpcResult<AgentDashboardResponse>;
    
    /// Get the full signed upgrade announcement (for P2P fallback polling)
    /// Returns the raw UpgradeAnnouncement with operator signature so validators can verify it
    #[method(name = "smithnode_getUpgradeAnnouncement")]
    async fn get_upgrade_announcement(&self) -> RpcResult<Option<crate::p2p::UpgradeAnnouncement>>;
}

/// Event broadcaster for real-time updates
pub type EventSender = broadcast::Sender<StateEvent>;

/// RPC server implementation with rate limiting
pub struct SmithNodeRpcServerImpl {
    state: Arc<SmithNodeState>,
    network: Option<Arc<Mutex<NetworkHandle>>>,
    event_tx: EventSender,
    rate_limiter: RateLimiter,
}

/// Convert a CognitivePuzzle to a PuzzleResponse (strips the answer hash for security)
pub fn puzzle_to_response(puzzle: &crate::stf::CognitivePuzzle) -> PuzzleResponse {
    PuzzleResponse {
        puzzle_type: format!("{:?}", puzzle.puzzle_type),
        prompt: puzzle.prompt.clone(),
        code_snippet: puzzle.code_snippet.clone(),
        sequence: puzzle.sequence.clone(),
        input_text: puzzle.input_text.clone(),
        time_limit_ms: puzzle.time_limit_ms,
    }
}

impl SmithNodeRpcServerImpl {
    pub fn new(state: SmithNodeState, network: Option<NetworkHandle>, event_tx: EventSender) -> Self {
        Self {
            state: Arc::new(state),
            network: network.map(|n| Arc::new(Mutex::new(n))),
            event_tx,
            rate_limiter: RateLimiter::new(),
        }
    }

    fn build_snapshot(&self) -> StateSnapshot {
        let peer_info = crate::p2p::get_local_peer_info();
        
        let status = NodeStatusResponse {
            height: self.state.get_height(),
            state_root: hex::encode(self.state.get_state_root()),
            total_supply: self.state.get_total_supply(),
            validator_count: self.state.get_all_validators().len(),
            active_validator_count: self.state.get_active_validator_count(),
            has_active_challenge: self.state.get_current_challenge().is_some(),
            node_version: crate::p2p::SMITH_VERSION.to_string(),
            peer_id: peer_info.map(|p| p.peer_id.clone()),
            p2p_multiaddrs: peer_info.map(|p| p.get_multiaddrs()).unwrap_or_default(),
            bootstrap_peers: crate::p2p::get_bootstrap_peers(),
        };

        let validators: Vec<ValidatorInfoResponse> = self.state.get_all_validators()
            .into_iter()
            .map(|v| ValidatorInfoResponse {
                public_key: hex::encode(v.public_key),
                balance: v.balance,
                validations_count: v.validations_count,
                reputation_score: v.reputation_score,
                last_active_timestamp: v.last_active_timestamp,
                is_online: v.is_online,
                nonce: v.nonce,
            })
            .collect();

        let challenge = self.state.get_current_challenge().map(|c| ChallengeResponse {
            challenge_hash: hex::encode(c.challenge_hash),
            challenge_type: format!("{:?}", c.challenge_type),
            height: c.height,
            difficulty: c.difficulty,
            pending_tx_count: c.pending_tx_hashes.len(),
            expires_at: c.expires_at,
            remaining_seconds: c.remaining_time(),
            cognitive_puzzle: c.cognitive_puzzle.as_ref().map(puzzle_to_response),
        });

        StateSnapshot {
            status,
            validators,
            challenge,
            timestamp: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_secs(),
        }
    }
}

#[async_trait]
impl SmithNodeRpcApiServer for SmithNodeRpcServerImpl {
    async fn status(&self) -> RpcResult<NodeStatusResponse> {
        // Get P2P peer info if available
        let peer_info = crate::p2p::get_local_peer_info();
        
        Ok(NodeStatusResponse {
            height: self.state.get_height(),
            state_root: hex::encode(self.state.get_state_root()),
            total_supply: self.state.get_total_supply(),
            validator_count: self.state.get_all_validators().len(),
            active_validator_count: self.state.get_active_validator_count(),
            has_active_challenge: self.state.get_current_challenge().is_some(),
            node_version: crate::p2p::SMITH_VERSION.to_string(),
            peer_id: peer_info.map(|p| p.peer_id.clone()),
            p2p_multiaddrs: peer_info.map(|p| p.get_multiaddrs()).unwrap_or_default(),
            bootstrap_peers: crate::p2p::get_bootstrap_peers(),
        })
    }
    
    async fn get_challenge(&self) -> RpcResult<Option<ChallengeResponse>> {
        Ok(self.state.get_current_challenge().map(|c| ChallengeResponse {
            challenge_hash: hex::encode(c.challenge_hash),
            challenge_type: format!("{:?}", c.challenge_type),
            height: c.height,
            difficulty: c.difficulty,
            pending_tx_count: c.pending_tx_hashes.len(),
            expires_at: c.expires_at,
            remaining_seconds: c.remaining_time(),
            cognitive_puzzle: c.cognitive_puzzle.as_ref().map(puzzle_to_response),
        }))
    }
    
    async fn new_challenge(&self) -> RpcResult<ChallengeResponse> {
        // Rate limit challenge generation to prevent spam
        if let Err(e) = self.rate_limiter.check("new_challenge", "global", CHALLENGE_RATE_LIMIT).await {
            return Err(ErrorObjectOwned::owned(-32000, e, None::<()>));
        }
        
        let c = self.state.generate_challenge();
        
        // Broadcast challenge over P2P if network is available
        if let Some(network) = &self.network {
            let network = network.lock().await;
            if let Err(e) = network.broadcast_challenge(c.clone()).await {
                tracing::warn!("Failed to broadcast challenge over P2P: {}", e);
            }
        }
        
        Ok(ChallengeResponse {
            challenge_hash: hex::encode(c.challenge_hash),
            challenge_type: format!("{:?}", c.challenge_type),
            height: c.height,
            difficulty: c.difficulty,
            pending_tx_count: c.pending_tx_hashes.len(),
            expires_at: c.expires_at,
            remaining_seconds: c.remaining_time(),
            cognitive_puzzle: c.cognitive_puzzle.as_ref().map(puzzle_to_response),
        })
    }
    
    async fn submit_proof(&self, req: SubmitProofRequest) -> RpcResult<SubmitProofResponse> {
        // Parse hex inputs
        let validator_pubkey: [u8; 32] = match hex::decode(&req.validator_pubkey) {
            Ok(bytes) if bytes.len() == 32 => bytes.try_into().unwrap(),
            _ => return Ok(SubmitProofResponse {
                success: false,
                reward: None,
                new_balance: None,
                error: Some("Invalid validator pubkey (must be 32 bytes hex)".into()),
            }),
        };
        
        let challenge_hash: [u8; 32] = match hex::decode(&req.challenge_hash) {
            Ok(bytes) if bytes.len() == 32 => bytes.try_into().unwrap(),
            _ => return Ok(SubmitProofResponse {
                success: false,
                reward: None,
                new_balance: None,
                error: Some("Invalid challenge hash (must be 32 bytes hex)".into()),
            }),
        };
        
        let signature: [u8; 64] = match hex::decode(&req.signature) {
            Ok(bytes) if bytes.len() == 64 => bytes.try_into().unwrap(),
            _ => return Ok(SubmitProofResponse {
                success: false,
                reward: None,
                new_balance: None,
                error: Some("Invalid signature (must be 64 bytes hex)".into()),
            }),
        };
        
        let verdict_digest: [u8; 32] = match hex::decode(&req.verdict_digest) {
            Ok(bytes) if bytes.len() == 32 => bytes.try_into().unwrap(),
            _ => return Ok(SubmitProofResponse {
                success: false,
                reward: None,
                new_balance: None,
                error: Some("Invalid verdict digest (must be 32 bytes hex)".into()),
            }),
        };
        
        // Capture state root BEFORE applying proof (needed for block broadcast)
        let pre_block_state_root = self.state.get_state_root();
        
        // Apply the transaction
        let tx = NodeTx::SubmitProof {
            validator_pubkey,
            challenge_hash,
            signature,
            verdict_digest,
            puzzle_answer: req.puzzle_answer.clone(),
        };
        
        match self.state.apply_tx(tx) {
            TxResult::Success { reward, new_balance } => {
                // Broadcast proof over P2P if network is available
                if let Some(network) = &self.network {
                    let proof_response = StfChallengeResponse {
                        challenge_hash: req.challenge_hash.clone(),
                        validator_pubkey: req.validator_pubkey.clone(),
                        signature: req.signature.clone(),
                        verdict_digest: req.verdict_digest.clone(),
                        tx_verdicts: None,
                        puzzle_answer: req.puzzle_answer.clone(),
                        submitted_at_ms: None,
                    };
                    let network = network.lock().await;
                    if let Err(e) = network.broadcast_proof(proof_response).await {
                        tracing::warn!("Failed to broadcast proof over P2P: {}", e);
                    }
                }
                
                Ok(SubmitProofResponse {
                    success: true,
                    reward: Some(reward),
                    new_balance: Some(new_balance),
                    error: None,
                })
            },
            TxResult::BlockFinalized { reward, new_balance, block_height, state_root } => {
                // Broadcast proof AND block over P2P
                if let Some(network) = &self.network {
                    let proof_response = StfChallengeResponse {
                        challenge_hash: req.challenge_hash.clone(),
                        validator_pubkey: req.validator_pubkey.clone(),
                        signature: req.signature.clone(),
                        verdict_digest: req.verdict_digest.clone(),
                        tx_verdicts: None,
                        puzzle_answer: req.puzzle_answer.clone(),
                        submitted_at_ms: None,
                    };
                    
                    let network = network.lock().await;
                    
                    // Broadcast the proof
                    if let Err(e) = network.broadcast_proof(proof_response).await {
                        tracing::warn!("Failed to broadcast proof over P2P: {}", e);
                    }
                    
                    // Broadcast the finalized block
                    let tx_root = {
                        use sha2::{Sha256, Digest};
                        let mut hasher = Sha256::new();
                        hasher.update(&challenge_hash);
                        let result: [u8; 32] = hasher.finalize().into();
                        result
                    };
                    let block_header = crate::stf::BlockHeader {
                        height: block_height,
                        prev_state_root: pre_block_state_root,
                        tx_root,
                        timestamp: std::time::SystemTime::now()
                            .duration_since(std::time::UNIX_EPOCH)
                            .unwrap_or_default()
                            .as_secs(),
                        challenge_hash: challenge_hash,
                    };
                    
                    if let Err(e) = network.broadcast_block(block_header, None).await {
                        tracing::warn!("Failed to broadcast block over P2P: {}", e);
                    } else {
                        tracing::info!("📢 Block {} broadcasted to P2P network", block_height);
                    }
                }
                
                Ok(SubmitProofResponse {
                    success: true,
                    reward: Some(reward),
                    new_balance: Some(new_balance),
                    error: None,
                })
            },
            TxResult::Registered { .. } | TxResult::ProposalCreated { .. } | 
            TxResult::VoteRecorded { .. } | TxResult::ProposalExecuted { .. } => Ok(SubmitProofResponse {
                success: false,
                reward: None,
                new_balance: None,
                error: Some("Unexpected result type".into()),
            }),
            TxResult::Error(e) => Ok(SubmitProofResponse {
                success: false,
                reward: None,
                new_balance: None,
                error: Some(e),
            }),
        }
    }
    
    async fn register_validator(&self, req: RegisterValidatorRequest) -> RpcResult<SubmitProofResponse> {
        let public_key: [u8; 32] = match hex::decode(&req.public_key) {
            Ok(bytes) if bytes.len() == 32 => bytes.try_into().unwrap(),
            _ => return Ok(SubmitProofResponse {
                success: false,
                reward: None,
                new_balance: None,
                error: Some("Invalid public key (must be 32 bytes hex)".into()),
            }),
        };
        
        let tx = NodeTx::RegisterValidator { public_key };
        
        match self.state.apply_tx(tx) {
            TxResult::Success { reward, new_balance } => Ok(SubmitProofResponse {
                success: true,
                reward: Some(reward),
                new_balance: Some(new_balance),
                error: None,
            }),
            TxResult::BlockFinalized { reward, new_balance, .. } => Ok(SubmitProofResponse {
                success: true,
                reward: Some(reward),
                new_balance: Some(new_balance),
                error: None,
            }),
            TxResult::Registered { public_key: _ } => Ok(SubmitProofResponse {
                success: true,
                reward: Some(0),
                new_balance: Some(0),
                error: None,
            }),
            TxResult::ProposalCreated { .. } | TxResult::VoteRecorded { .. } | 
            TxResult::ProposalExecuted { .. } => Ok(SubmitProofResponse {
                success: false,
                reward: None,
                new_balance: None,
                error: Some("Unexpected result type".into()),
            }),
            TxResult::Error(e) => Ok(SubmitProofResponse {
                success: false,
                reward: None,
                new_balance: None,
                error: Some(e),
            }),
        }
    }
    
    async fn presence(&self, req: PresenceRequest) -> RpcResult<PresenceResponse> {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        
        let height = self.state.get_height();
        
        // Update validator's presence in local state (always works)
        self.state.update_validator_presence(
            &req.validator_pubkey,
            now,
            height,
        );
        
        // Broadcast presence over P2P only if signature is provided
        if let (Some(network), Some(signature)) = (&self.network, req.signature) {
            // Verify signature before broadcasting
            let presence_msg = crate::p2p::PresenceMessage {
                validator_pubkey: req.validator_pubkey.clone(),
                height,
                timestamp: now,
                version: crate::p2p::SMITH_VERSION.to_string(),
                signature,
            };
            
            // Only broadcast if signature is valid
            if presence_msg.verify_signature() {
                let network = network.lock().await;
                if let Err(e) = network.broadcast_presence(presence_msg).await {
                    tracing::debug!("Failed to broadcast presence: {}", e);
                }
            } else {
                tracing::warn!(
                    "⚠️ Invalid presence signature from {}...",
                    &req.validator_pubkey[..16.min(req.validator_pubkey.len())]
                );
            }
        }
        
        Ok(PresenceResponse {
            success: true,
            active_validators: self.state.get_active_validator_count(),
        })
    }
    
    async fn get_validator(&self, pubkey: String) -> RpcResult<Option<ValidatorInfoResponse>> {
        Ok(self.state.get_validator(&pubkey).map(|v| ValidatorInfoResponse {
            public_key: hex::encode(v.public_key),
            balance: v.balance,
            validations_count: v.validations_count,
            reputation_score: v.reputation_score,
            last_active_timestamp: v.last_active_timestamp,
            is_online: v.is_online,
            nonce: v.nonce,
        }))
    }
    
    async fn get_validators(&self) -> RpcResult<Vec<ValidatorInfoResponse>> {
        Ok(self.state.get_all_validators().into_iter().map(|v| ValidatorInfoResponse {
            public_key: hex::encode(v.public_key),
            balance: v.balance,
            validations_count: v.validations_count,
            reputation_score: v.reputation_score,
            last_active_timestamp: v.last_active_timestamp,
            is_online: v.is_online,
            nonce: v.nonce,
        }).collect())
    }

    async fn transfer(&self, req: TransferRequest) -> RpcResult<TransferResponse> {
        // Rate limit transfers per sender
        if let Err(e) = self.rate_limiter.check("transfer", &req.from, TRANSFER_RATE_LIMIT).await {
            return Ok(TransferResponse {
                success: false,
                tx_hash: None,
                error: Some(e),
            });
        }
        
        // Parse hex inputs
        let from: [u8; 32] = match hex::decode(&req.from) {
            Ok(bytes) if bytes.len() == 32 => bytes.try_into().unwrap(),
            _ => return Ok(TransferResponse {
                success: false,
                tx_hash: None,
                error: Some("Invalid 'from' address (must be 32 bytes hex)".into()),
            }),
        };

        let to: [u8; 32] = match hex::decode(&req.to) {
            Ok(bytes) if bytes.len() == 32 => bytes.try_into().unwrap(),
            _ => return Ok(TransferResponse {
                success: false,
                tx_hash: None,
                error: Some("Invalid 'to' address (must be 32 bytes hex)".into()),
            }),
        };

        let signature: [u8; 64] = match hex::decode(&req.signature) {
            Ok(bytes) if bytes.len() == 64 => bytes.try_into().unwrap(),
            _ => return Ok(TransferResponse {
                success: false,
                tx_hash: None,
                error: Some("Invalid signature (must be 64 bytes hex)".into()),
            }),
        };

        // Create and apply the transfer transaction
        let tx = NodeTx::Transfer {
            from,
            to,
            amount: req.amount,
            nonce: req.nonce,
            signature,
        };

        let tx_hash = hex::encode(tx.hash());

        match self.state.apply_tx(tx) {
            TxResult::Success { .. } => {
                tracing::info!(
                    "💸 Transfer: {} SMITH from {}... to {}...",
                    req.amount,
                    &req.from[..16],
                    &req.to[..16]
                );
                // Broadcast transfer via P2P so other nodes apply it
                if let Some(network) = &self.network {
                    let transfer_msg = crate::p2p::TransferGossipMessage {
                        from: req.from.clone(),
                        to: req.to.clone(),
                        amount: req.amount,
                        nonce: req.nonce,
                        signature: req.signature.clone(),
                    };
                    let network = network.lock().await;
                    if let Err(e) = network.broadcast_transfer(transfer_msg).await {
                        tracing::warn!("Failed to broadcast transfer via P2P: {}", e);
                    }
                }
                Ok(TransferResponse {
                    success: true,
                    tx_hash: Some(tx_hash),
                    error: None,
                })
            }
            TxResult::BlockFinalized { .. } => Ok(TransferResponse {
                success: false,
                tx_hash: None,
                error: Some("Unexpected block finalization from transfer".into()),
            }),
            TxResult::Registered { .. } | TxResult::ProposalCreated { .. } |
            TxResult::VoteRecorded { .. } | TxResult::ProposalExecuted { .. } => Ok(TransferResponse {
                success: false,
                tx_hash: None,
                error: Some("Unexpected result type".into()),
            }),
            TxResult::Error(e) => Ok(TransferResponse {
                success: false,
                tx_hash: None,
                error: Some(e),
            }),
        }
    }

    async fn get_transactions(&self, page: Option<usize>, per_page: Option<usize>, tx_type: Option<String>) -> RpcResult<PaginatedTransactionsResponse> {
        let page = page.unwrap_or(1).max(1);
        let per_page = per_page.unwrap_or(20).min(100).max(1);
        let filter = tx_type.filter(|t| t != "all");
        let (transactions, total) = self.state.get_transactions_paginated(page, per_page, filter);
        let total_pages = (total + per_page - 1) / per_page.max(1);
        
        Ok(PaginatedTransactionsResponse {
            transactions,
            total,
            page,
            per_page,
            total_pages,
        })
    }

    async fn get_block(&self, hash: String) -> RpcResult<Option<TxRecord>> {
        Ok(self.state.get_transaction_by_hash(&hash))
    }

    async fn get_committee(&self) -> RpcResult<Option<CommitteeResponse>> {
        Ok(self.state.get_committee().map(|c| CommitteeResponse {
            block_height: c.block_height,
            members: c.members.into_iter().map(|m| CommitteeMemberResponse {
                pubkey: m.pubkey,
                submitted_proof: m.submitted_proof,
                proof_valid: m.proof_valid,
            }).collect(),
            challenge_hash: hex::encode(c.challenge_hash),
            expires_at: c.expires_at,
            approvals: c.approvals,
            threshold: c.threshold,
            finalized: c.finalized,
        }))
    }

    async fn get_state(&self) -> RpcResult<StateSnapshot> {
        Ok(self.build_snapshot())
    }

    async fn export_state(&self) -> RpcResult<FullStateExport> {
        let validators: Vec<ValidatorInfoResponse> = self.state.get_all_validators()
            .into_iter()
            .map(|v| ValidatorInfoResponse {
                public_key: hex::encode(v.public_key),
                balance: v.balance,
                validations_count: v.validations_count,
                reputation_score: v.reputation_score,
                last_active_timestamp: v.last_active_timestamp,
                is_online: v.is_online,
                nonce: v.nonce,
            })
            .collect();
        
        Ok(FullStateExport {
            height: self.state.get_height(),
            state_root: hex::encode(self.state.get_state_root()),
            total_supply: self.state.get_total_supply(),
            validators,
            node_version: env!("CARGO_PKG_VERSION").to_string(),
        })
    }

    async fn import_state(&self, _state_export: FullStateExport) -> RpcResult<SubmitProofResponse> {
        // SECURITY: importState via RPC is DISABLED.
        // State sync happens ONLY through P2P with cryptographic verification.
        // This endpoint was a critical vulnerability (C2) - any HTTP client could overwrite chain state.
        tracing::warn!("⚠️ importState RPC called but is DISABLED for security");
        Ok(SubmitProofResponse {
            success: false,
            reward: None,
            new_balance: None,
            error: Some("importState is disabled. State sync is handled via P2P only.".into()),
        })
    }

    async fn subscribe_state(&self, pending: PendingSubscriptionSink) -> SubscriptionResult {
        let sink = pending.accept().await?;
        let mut rx = self.event_tx.subscribe();
        
        // Send initial snapshot
        let snapshot = self.build_snapshot();
        let _ = sink.send(jsonrpsee::SubscriptionMessage::from_json(&StateEvent::Snapshot(snapshot))?);
        
        // Forward events to subscriber
        tokio::spawn(async move {
            loop {
                match rx.recv().await {
                    Ok(event) => {
                        if let Ok(msg) = jsonrpsee::SubscriptionMessage::from_json(&event) {
                            if sink.send(msg).await.is_err() {
                                break;
                            }
                        }
                    }
                    Err(broadcast::error::RecvError::Lagged(_)) => continue,
                    Err(broadcast::error::RecvError::Closed) => break,
                }
            }
        });
        
        Ok(())
    }

    async fn check_update(&self) -> RpcResult<UpdateCheckResponse> {
        let tracker = get_version_tracker();
        let newest_version = tracker.needs_update();
        let version_stats = tracker.get_version_stats();
        
        // Convert stats to just count by version (drop timestamp)
        let network_versions: std::collections::HashMap<String, usize> = version_stats
            .into_iter()
            .map(|(v, (count, _))| (v, count))
            .collect();
        
        // Get verified upgrade from trusted operator (if any)
        let verified_upgrade = tracker.get_latest_upgrade();
        
        // Extract platform-specific URL and checksum
        let (download_url, checksum) = if let Some(ref upgrade) = verified_upgrade {
            let platform = std::env::consts::OS;
            let arch = std::env::consts::ARCH;
            
            let url = match (platform, arch) {
                ("macos", "aarch64") => upgrade.download_urls.darwin_arm64.clone(),
                ("macos", "x86_64") => upgrade.download_urls.darwin_x64.clone(),
                ("linux", "x86_64") => upgrade.download_urls.linux_x64.clone(),
                ("linux", "aarch64") => upgrade.download_urls.linux_arm64.clone(),
                ("windows", _) => upgrade.download_urls.windows_x64.clone(),
                _ => None,
            };
            
            let sum = match (platform, arch) {
                ("macos", "aarch64") => upgrade.checksums.darwin_arm64.clone(),
                ("macos", "x86_64") => upgrade.checksums.darwin_x64.clone(),
                ("linux", "x86_64") => upgrade.checksums.linux_x64.clone(),
                ("linux", "aarch64") => upgrade.checksums.linux_arm64.clone(),
                ("windows", _) => upgrade.checksums.windows_x64.clone(),
                _ => None,
            };
            
            (url, sum)
        } else {
            (None, None)
        };
        
        Ok(UpdateCheckResponse {
            current_version: SMITH_VERSION.to_string(),
            update_available: newest_version.is_some() || verified_upgrade.is_some(),
            newest_version: verified_upgrade.as_ref().map(|u| u.version.clone()).or(newest_version),
            network_versions,
            download_url,
            checksum,
            mandatory: verified_upgrade.as_ref().map(|u| u.mandatory).unwrap_or(false),
            release_notes: verified_upgrade.as_ref().and_then(|u| u.release_notes.clone()),
            verified: verified_upgrade.is_some(),
        })
    }

    async fn announce_upgrade(&self, announcement: crate::p2p::UpgradeAnnouncement) -> RpcResult<serde_json::Value> {
        tracing::info!("📦 Received upgrade announcement via RPC: v{}", announcement.version);
        
        // Verify the announcement signature and operator key
        if !announcement.verify() {
            return Err(jsonrpsee::types::ErrorObjectOwned::owned(
                -32001,
                "Invalid upgrade announcement: signature verification failed or untrusted operator key",
                None::<()>,
            ));
        }
        
        // Record in version tracker
        let tracker = get_version_tracker();
        tracker.record_upgrade(announcement.clone());
        
        // Broadcast via P2P network if available
        let mut broadcast_ok = false;
        if let Some(ref network) = self.network {
            let net = network.lock().await.clone();
            if let Err(e) = net.broadcast_upgrade(announcement.clone()).await {
                tracing::warn!("Failed to broadcast upgrade via P2P: {}", e);
            } else {
                broadcast_ok = true;
                tracing::info!("✅ Upgrade v{} broadcast to P2P network", announcement.version);
            }
        }
        
        Ok(serde_json::json!({
            "status": "ok",
            "version": announcement.version,
            "broadcast": broadcast_ok,
        }))
    }

    async fn get_p2p_validators(&self) -> RpcResult<P2PValidatorsResponse> {
        use crate::p2p::get_p2p_validator_tracker;
        
        let p2p_tracker = get_p2p_validator_tracker();
        let p2p_verified = p2p_tracker.get_verified_validators();
        let online_p2p = p2p_tracker.get_online_p2p_validators();
        
        // Get all validators from state
        let all_validators = self.state.get_all_validators();
        
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        
        // Build detail list with peer type classification
        let validators: Vec<P2PValidatorDetail> = all_validators.iter().map(|v| {
            let pubkey_hex = hex::encode(&v.public_key);
            let p2p_info = p2p_verified.iter().find(|p| p.public_key == pubkey_hex);
            
            let (is_p2p_verified, is_online, presence_count, last_seen, first_seen, last_height, version) = 
                if let Some(info) = p2p_info {
                    let online = info.last_seen_timestamp > now.saturating_sub(120);
                    (true, online, info.presence_count, info.last_seen_timestamp, info.first_seen, info.last_height, info.version.clone())
                } else {
                    (false, false, 0, 0, 0, 0, String::new())
                };
            
            let peer_type = if is_p2p_verified {
                "p2p".to_string()
            } else if v.last_active_timestamp > 0 {
                "rpc".to_string()  // Only seen via RPC submissions
            } else {
                "unknown".to_string()
            };
            
            P2PValidatorDetail {
                public_key: pubkey_hex,
                is_online,
                last_seen_timestamp: if is_p2p_verified { last_seen } else { v.last_active_timestamp },
                last_height,
                version,
                presence_count,
                first_seen,
                peer_type,
            }
        }).collect();
        
        Ok(P2PValidatorsResponse {
            total_validators: all_validators.len(),
            p2p_verified_count: p2p_verified.len(),
            online_p2p_count: online_p2p.len(),
            validators,
        })
    }

    async fn is_p2p_verified(&self, pubkey: String) -> RpcResult<P2PVerificationResult> {
        use crate::p2p::get_p2p_validator_tracker;
        
        let p2p_tracker = get_p2p_validator_tracker();
        let p2p_verified = p2p_tracker.get_verified_validators();
        let p2p_info = p2p_verified.iter().find(|p| p.public_key == pubkey);
        
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        
        // Get validator info from state
        let state_info = self.state.get_validator(&pubkey);
        
        let (is_p2p_verified, is_online, presence_count, peer_type) = if let Some(info) = p2p_info {
            let online = info.last_seen_timestamp > now.saturating_sub(120);
            (true, online, info.presence_count, "p2p".to_string())
        } else if state_info.is_some() {
            (false, false, 0, "rpc".to_string())
        } else {
            (false, false, 0, "unknown".to_string())
        };
        
        Ok(P2PVerificationResult {
            public_key: pubkey,
            is_p2p_verified,
            is_online,
            presence_count,
            peer_type,
            balance: state_info.as_ref().map(|v| v.balance),
            validations_count: state_info.as_ref().map(|v| v.validations_count),
        })
    }
    
    async fn send_ai_message(&self, req: AIMessageRequest) -> RpcResult<AIMessageResponse> {
        use sha2::{Sha256, Digest};
        
        // Validate topic is allowed
        let topic_lower = req.topic.to_lowercase();
        if !ALLOWED_AI_TOPICS.contains(&topic_lower.as_str()) {
            return Ok(AIMessageResponse {
                message_id: String::new(),
                success: false,
                tx_hash: None,
                error: Some(format!(
                    "Invalid topic '{}'. Allowed topics: upgrade, marketing, dev, code, governance, security, performance, consensus",
                    req.topic
                )),
            });
        }
        
        // Validate sender is a registered validator
        let sender = self.state.get_validator(&req.from);
        if sender.is_none() {
            return Ok(AIMessageResponse {
                message_id: String::new(),
                success: false,
                tx_hash: None,
                error: Some("Sender is not a registered validator".to_string()),
            });
        }
        
        // RATE LIMITING: 1 message per 10 minutes per validator
        if let Err(rate_error) = check_rate_limit(&req.from) {
            return Ok(AIMessageResponse {
                message_id: String::new(),
                success: false,
                tx_hash: None,
                error: Some(rate_error),
            });
        }
        
        // Generate message ID and timestamp
        let timestamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        
        let mut hasher = Sha256::new();
        hasher.update(format!("{}:{}:{}:{}:{}", req.from, req.to, req.topic, req.content, timestamp));
        let message_id = hex::encode(hasher.finalize());
        
        // Parse from/to public keys to bytes for on-chain transaction
        let from_bytes: [u8; 32] = match hex::decode(&req.from) {
            Ok(bytes) if bytes.len() == 32 => {
                let mut arr = [0u8; 32];
                arr.copy_from_slice(&bytes);
                arr
            }
            _ => {
                return Ok(AIMessageResponse {
                    message_id: String::new(),
                    success: false,
                    tx_hash: None,
                    error: Some("Invalid 'from' public key (must be 64 hex chars)".to_string()),
                });
            }
        };
        
        // For 'to': use zeros for broadcast, otherwise parse the pubkey
        let to_bytes: [u8; 32] = if req.to == "broadcast" {
            [0u8; 32]  // All zeros = broadcast
        } else {
            match hex::decode(&req.to) {
                Ok(bytes) if bytes.len() == 32 => {
                    let mut arr = [0u8; 32];
                    arr.copy_from_slice(&bytes);
                    arr
                }
                _ => {
                    return Ok(AIMessageResponse {
                        message_id: String::new(),
                        success: false,
                        tx_hash: None,
                        error: Some("Invalid 'to' public key (must be 64 hex chars or 'broadcast')".to_string()),
                    });
                }
            }
        };
        
        // Compute content hash
        let mut content_hasher = Sha256::new();
        content_hasher.update(format!("[{}] {}", req.topic, req.content));
        let content_hash_bytes: [u8; 32] = content_hasher.finalize().into();
        
        // Parse signature (64 bytes = 128 hex chars)
        let signature_bytes: [u8; 64] = match hex::decode(&req.signature) {
            Ok(bytes) if bytes.len() == 64 => {
                let mut arr = [0u8; 64];
                arr.copy_from_slice(&bytes);
                arr
            }
            _ => {
                // SECURITY: Reject invalid signatures (H4 fix)
                return Ok(AIMessageResponse {
                    message_id: String::new(),
                    success: false,
                    tx_hash: None,
                    error: Some("Invalid signature (must be 128 hex chars / 64 bytes)".to_string()),
                });
            }
        };
        
        // SECURITY (M3): Verify ed25519 signature over content hash
        {
            use ed25519_dalek::{Signature, Verifier, VerifyingKey};
            let verifying_key = VerifyingKey::from_bytes(&from_bytes)
                .map_err(|_| jsonrpsee::types::ErrorObjectOwned::owned(
                    -32602, "Invalid sender public key", None::<()>
                ))?;
            let signature = Signature::from_bytes(&signature_bytes);
            if verifying_key.verify(&content_hash_bytes, &signature).is_err() {
                return Ok(AIMessageResponse {
                    message_id: String::new(),
                    success: false,
                    tx_hash: None,
                    error: Some("Signature verification failed: message not signed by sender".to_string()),
                });
            }
        }
        
        // Message type: 0=query, 1=response, 2=broadcast
        let message_type: u8 = if req.to == "broadcast" { 2 } else { 0 };
        
        // Create on-chain transaction
        let ai_tx = crate::stf::NodeTx::AIMessage {
            from: from_bytes,
            to: to_bytes,
            content_hash: content_hash_bytes,
            response_hash: None,
            timestamp,
            signature: signature_bytes,
            message_type,
        };
        
        let tx_hash = ai_tx.hash();
        let tx_hash_hex = hex::encode(tx_hash);
        
        // Apply transaction to state
        let _result = self.state.apply_tx(ai_tx);
        
        // Create the AI network message for P2P broadcast
        let ai_message = crate::p2p::AINetworkMessage {
            from_validator: req.from.clone(),
            to_validator: req.to.clone(),
            topic: Some(req.topic.clone()),
            content: format!("[{}] {}", req.topic, req.content),
            response: None,
            ai_provider: Some(req.ai_provider.clone()),
            model: Some(req.model.clone().unwrap_or_else(|| "llama-3.1-70b".to_string())),
            timestamp,
            signature: req.signature.clone(),
            message_hash: message_id.clone(),
            in_reply_to: req.in_reply_to.clone(),
            message_type: if req.to == "broadcast" { "broadcast".to_string() } else { "query".to_string() },
            tx_hash: Some(tx_hash_hex.clone()),
        };
        
        // Broadcast via P2P if network is available
        if let Some(ref network) = self.network {
            let net = network.lock().await;
            if let Err(e) = net.broadcast_ai_message(ai_message).await {
                tracing::warn!("Failed to broadcast AI message via P2P: {}", e);
                // Don't fail - the on-chain tx was already recorded
            }
        }
        
        // Store in AI message tracker
        let is_broadcast = req.to == "broadcast";
        crate::p2p::store_ai_message(AIMessageRecord {
            message_id: message_id.clone(),
            from: req.from,
            to: req.to,
            topic: req.topic,
            content: req.content,
            response: None,
            ai_provider: req.ai_provider,
            model: req.model.unwrap_or_else(|| "llama-3.1-70b".to_string()),
            timestamp,
            signature: req.signature,
            in_reply_to: req.in_reply_to,
            message_type: if is_broadcast { "broadcast".to_string() } else { "query".to_string() },
            block_height: Some(self.state.get_height()),
            tx_hash: Some(tx_hash_hex.clone()),
        });
        
        tracing::info!("📨 AI message recorded on-chain: topic={}, tx={}", topic_lower, &tx_hash_hex[..16]);
        
        Ok(AIMessageResponse {
            message_id,
            success: true,
            tx_hash: Some(tx_hash_hex),
            error: None,
        })
    }
    
    async fn get_ai_messages(&self, pubkey: String, limit: Option<usize>) -> RpcResult<Vec<AIMessageRecord>> {
        let messages = crate::p2p::get_ai_messages(&pubkey, limit.unwrap_or(100));
        Ok(messages)
    }
    
    async fn query_ai(&self, req: AIQueryRequest) -> RpcResult<AIQueryResponse> {
        use crate::ai::{AIClient, AIConfig, AIProvider, AIQuery};
        
        // Check for configured AI provider via environment variables
        let (provider, api_key, model) = if let Ok(key) = std::env::var("OPENAI_API_KEY") {
            (AIProvider::OpenAI, Some(key), req.provider.clone().unwrap_or_else(|| "gpt-4".to_string()))
        } else if let Ok(key) = std::env::var("ANTHROPIC_API_KEY") {
            (AIProvider::Anthropic, Some(key), req.provider.clone().unwrap_or_else(|| "claude-3-opus-20240229".to_string()))
        } else if let Ok(key) = std::env::var("GROQ_API_KEY") {
            (AIProvider::Groq, Some(key), req.provider.clone().unwrap_or_else(|| "llama-3.1-70b-versatile".to_string()))
        } else if let Ok(key) = std::env::var("TOGETHER_API_KEY") {
            (AIProvider::Together, Some(key), req.provider.clone().unwrap_or_else(|| "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo".to_string()))
        } else if std::env::var("OLLAMA_HOST").is_ok() || std::env::var("OLLAMA_ENABLED").is_ok() {
            (AIProvider::Ollama, None, req.provider.clone().unwrap_or_else(|| "llama3.1".to_string()))
        } else {
            return Ok(AIQueryResponse {
                response: String::new(),
                provider: "none".to_string(),
                model: String::new(),
                tokens_used: 0,
                latency_ms: 0,
                error: Some("No AI provider configured. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY, or TOGETHER_API_KEY environment variable.".to_string()),
            });
        };
        
        let config = AIConfig {
            provider: provider.clone(),
            api_key,
            model: model.clone(),
            endpoint: std::env::var("OLLAMA_HOST").ok(),
            max_tokens: req.max_tokens.unwrap_or(1024),
            temperature: req.temperature.unwrap_or(0.7),
        };
        
        let client = AIClient::new(config);
        
        let query = AIQuery {
            prompt: req.prompt,
            system_prompt: req.system,
            max_tokens: req.max_tokens,
            temperature: req.temperature,
        };
        
        match client.query(&query).await {
            Ok(response) => {
                Ok(AIQueryResponse {
                    response: response.content,
                    provider: format!("{:?}", provider).to_lowercase(),
                    model: response.model,
                    tokens_used: response.tokens_used,
                    latency_ms: response.latency_ms,
                    error: None,
                })
            }
            Err(e) => {
                Ok(AIQueryResponse {
                    response: String::new(),
                    provider: format!("{:?}", provider).to_lowercase(),
                    model,
                    tokens_used: 0,
                    latency_ms: 0,
                    error: Some(e),
                })
            }
        }
    }

    // ============ GOVERNANCE RPC IMPLEMENTATIONS (M2 FIX) ============
    
    async fn create_proposal(&self, req: CreateProposalRpcRequest) -> RpcResult<GovernanceRpcResponse> {
        if let Err(e) = self.rate_limiter.check("governance", "global", 20).await {
            return Err(jsonrpsee::types::ErrorObjectOwned::owned(-32000, e, None::<String>));
        }
        
        let proposer_bytes = hex::decode(&req.proposer)
            .map_err(|_| jsonrpsee::types::ErrorObjectOwned::owned(-32602, "Invalid proposer hex", None::<String>))?;
        if proposer_bytes.len() != 32 {
            return Err(jsonrpsee::types::ErrorObjectOwned::owned(-32602, "Proposer must be 32 bytes", None::<String>));
        }
        let mut proposer = [0u8; 32];
        proposer.copy_from_slice(&proposer_bytes);
        
        let desc_hash_bytes = hex::decode(&req.description_hash)
            .map_err(|_| jsonrpsee::types::ErrorObjectOwned::owned(-32602, "Invalid description_hash hex", None::<String>))?;
        if desc_hash_bytes.len() != 32 {
            return Err(jsonrpsee::types::ErrorObjectOwned::owned(-32602, "Description hash must be 32 bytes", None::<String>));
        }
        let mut desc_hash = [0u8; 32];
        desc_hash.copy_from_slice(&desc_hash_bytes);
        
        let sig_bytes = hex::decode(&req.signature)
            .map_err(|_| jsonrpsee::types::ErrorObjectOwned::owned(-32602, "Invalid signature hex", None::<String>))?;
        if sig_bytes.len() != 64 {
            return Err(jsonrpsee::types::ErrorObjectOwned::owned(-32602, "Signature must be 64 bytes", None::<String>));
        }
        let mut signature = [0u8; 64];
        signature.copy_from_slice(&sig_bytes);
        
        let tx = crate::stf::NodeTx::CreateProposal {
            proposer,
            proposal_type: req.proposal_type,
            new_value: req.new_value,
            description_hash: desc_hash,
            signature,
        };
        
        let result = self.state.apply_tx(tx);
        match result {
            crate::stf::TxResult::ProposalCreated { proposal_id } => {
                // Broadcast governance action via P2P
                if let Some(network) = &self.network {
                    let gov_msg = crate::p2p::GovernanceGossipMessage {
                        action: crate::p2p::GovernanceAction::CreateProposal {
                            proposer: req.proposer.clone(),
                            proposal_type: req.proposal_type,
                            new_value: req.new_value,
                            description_hash: req.description_hash.clone(),
                            signature: req.signature.clone(),
                        },
                        timestamp: std::time::SystemTime::now()
                            .duration_since(std::time::UNIX_EPOCH)
                            .unwrap_or_default()
                            .as_secs(),
                    };
                    let network = network.lock().await;
                    if let Err(e) = network.broadcast_governance(gov_msg).await {
                        tracing::warn!("Failed to broadcast proposal via P2P: {}", e);
                    }
                }
                Ok(GovernanceRpcResponse {
                    success: true,
                    message: format!("Proposal #{} created", proposal_id),
                    proposal_id: Some(proposal_id),
                })
            }
            crate::stf::TxResult::Error(e) => Ok(GovernanceRpcResponse {
                success: false,
                message: e,
                proposal_id: None,
            }),
            _ => Ok(GovernanceRpcResponse {
                success: false,
                message: "Unexpected result".to_string(),
                proposal_id: None,
            }),
        }
    }
    
    async fn vote_proposal(&self, req: VoteProposalRpcRequest) -> RpcResult<GovernanceRpcResponse> {
        if let Err(e) = self.rate_limiter.check("governance", "global", 20).await {
            return Err(jsonrpsee::types::ErrorObjectOwned::owned(-32000, e, None::<String>));
        }
        
        let voter_bytes = hex::decode(&req.voter)
            .map_err(|_| jsonrpsee::types::ErrorObjectOwned::owned(-32602, "Invalid voter hex", None::<String>))?;
        if voter_bytes.len() != 32 {
            return Err(jsonrpsee::types::ErrorObjectOwned::owned(-32602, "Voter must be 32 bytes", None::<String>));
        }
        let mut voter = [0u8; 32];
        voter.copy_from_slice(&voter_bytes);
        
        let sig_bytes = hex::decode(&req.signature)
            .map_err(|_| jsonrpsee::types::ErrorObjectOwned::owned(-32602, "Invalid signature hex", None::<String>))?;
        if sig_bytes.len() != 64 {
            return Err(jsonrpsee::types::ErrorObjectOwned::owned(-32602, "Signature must be 64 bytes", None::<String>));
        }
        let mut signature = [0u8; 64];
        signature.copy_from_slice(&sig_bytes);
        
        let tx = crate::stf::NodeTx::VoteProposal {
            voter,
            proposal_id: req.proposal_id,
            vote: req.vote,
            signature,
            reason: req.reason.clone(),
        };
        
        let result = self.state.apply_tx(tx);
        match result {
            crate::stf::TxResult::VoteRecorded { proposal_id, .. } => {
                // Broadcast vote via P2P
                if let Some(network) = &self.network {
                    let gov_msg = crate::p2p::GovernanceGossipMessage {
                        action: crate::p2p::GovernanceAction::CastVote {
                            voter: req.voter.clone(),
                            proposal_id: req.proposal_id,
                            vote: req.vote,
                            signature: req.signature.clone(),
                            reason: req.reason.clone(),
                        },
                        timestamp: std::time::SystemTime::now()
                            .duration_since(std::time::UNIX_EPOCH)
                            .unwrap_or_default()
                            .as_secs(),
                    };
                    let network = network.lock().await;
                    if let Err(e) = network.broadcast_governance(gov_msg).await {
                        tracing::warn!("Failed to broadcast vote via P2P: {}", e);
                    }
                }
                Ok(GovernanceRpcResponse {
                    success: true,
                    message: format!("Vote recorded on proposal #{}", req.proposal_id),
                    proposal_id: Some(req.proposal_id),
                })
            }
            crate::stf::TxResult::Error(e) => Ok(GovernanceRpcResponse {
                success: false,
                message: e,
                proposal_id: None,
            }),
            _ => Ok(GovernanceRpcResponse {
                success: false,
                message: "Unexpected result".to_string(),
                proposal_id: None,
            }),
        }
    }
    
    async fn execute_proposal(&self, req: ExecuteProposalRpcRequest) -> RpcResult<GovernanceRpcResponse> {
        if let Err(e) = self.rate_limiter.check("governance", "global", 20).await {
            return Err(jsonrpsee::types::ErrorObjectOwned::owned(-32000, e, None::<String>));
        }
        
        let executor_bytes = hex::decode(&req.executor)
            .map_err(|_| jsonrpsee::types::ErrorObjectOwned::owned(-32602, "Invalid executor hex", None::<String>))?;
        if executor_bytes.len() != 32 {
            return Err(jsonrpsee::types::ErrorObjectOwned::owned(-32602, "Executor must be 32 bytes", None::<String>));
        }
        let mut executor = [0u8; 32];
        executor.copy_from_slice(&executor_bytes);
        
        let sig_bytes = hex::decode(&req.signature)
            .map_err(|_| jsonrpsee::types::ErrorObjectOwned::owned(-32602, "Invalid signature hex", None::<String>))?;
        if sig_bytes.len() != 64 {
            return Err(jsonrpsee::types::ErrorObjectOwned::owned(-32602, "Signature must be 64 bytes", None::<String>));
        }
        let mut signature = [0u8; 64];
        signature.copy_from_slice(&sig_bytes);
        
        let tx = crate::stf::NodeTx::ExecuteProposal {
            executor,
            proposal_id: req.proposal_id,
            signature,
        };
        
        let result = self.state.apply_tx(tx);
        match result {
            crate::stf::TxResult::ProposalExecuted { proposal_id, .. } => {
                // Broadcast execution via P2P
                if let Some(network) = &self.network {
                    let gov_msg = crate::p2p::GovernanceGossipMessage {
                        action: crate::p2p::GovernanceAction::ExecuteProposal {
                            executor: req.executor.clone(),
                            proposal_id: req.proposal_id,
                            signature: req.signature.clone(),
                        },
                        timestamp: std::time::SystemTime::now()
                            .duration_since(std::time::UNIX_EPOCH)
                            .unwrap_or_default()
                            .as_secs(),
                    };
                    let network = network.lock().await;
                    if let Err(e) = network.broadcast_governance(gov_msg).await {
                        tracing::warn!("Failed to broadcast proposal execution via P2P: {}", e);
                    }
                }
                Ok(GovernanceRpcResponse {
                    success: true,
                    message: format!("Proposal #{} executed", proposal_id),
                    proposal_id: Some(proposal_id),
                })
            }
            crate::stf::TxResult::Error(e) => Ok(GovernanceRpcResponse {
                success: false,
                message: e,
                proposal_id: None,
            }),
            _ => Ok(GovernanceRpcResponse {
                success: false,
                message: "Unexpected result".to_string(),
                proposal_id: None,
            }),
        }
    }
    
    async fn get_proposals(&self) -> RpcResult<Vec<GovernanceProposalResponse>> {
        let proposals = self.state.get_governance_proposals();
        Ok(proposals.iter().map(|p| {
            GovernanceProposalResponse {
                id: p.id,
                proposer: p.proposer.clone(),
                proposal_type: format!("{:?}", p.proposal_type),
                description: p.description.clone(),
                status: format!("{:?}", p.status),
                votes_for: p.yes_stake,
                votes_against: p.no_stake,
                created_at: p.created_at,
                expires_at: p.voting_ends_at,
                tx_hash: p.tx_hash.clone(),
                execution_tx_hash: p.execution_tx_hash.clone(),
                votes: p.votes.iter().map(|v| VoteDetail {
                    voter: v.voter.clone(),
                    vote: v.vote,
                    stake_weight: v.stake_weight,
                    reason: v.reason.clone(),
                    tx_hash: v.tx_hash.clone(),
                }).collect(),
            }
        }).collect())
    }
    
    async fn get_network_params(&self) -> RpcResult<NetworkParamsResponse> {
        let params = self.state.get_network_params();
        Ok(NetworkParamsResponse {
            reward_per_proof: params.reward_per_proof,
            committee_size: params.committee_size,
            min_validator_stake: params.min_validator_stake,
            slash_percentage: params.slash_percentage,
            ai_rate_limit_secs: params.ai_rate_limit_secs,
            max_validators: params.max_validators,
            challenge_timeout_secs: params.challenge_timeout_secs,
        })
    }
    
    async fn get_agent_dashboard(&self, pubkey: Option<String>) -> RpcResult<AgentDashboardResponse> {
        let height = self.state.get_height();
        let state_root = hex::encode(self.state.get_state_root());
        let total_supply = self.state.get_total_supply();
        let all_validators = self.state.get_all_validators();
        let validator_count = all_validators.len();
        let active_validator_count = self.state.get_active_validator_count();
        let params = self.state.get_network_params();
        
        // My validator info
        let my_validator = pubkey.as_ref().and_then(|pk| {
            all_validators.iter().find(|v| hex::encode(v.public_key) == *pk).map(|v| ValidatorInfoResponse {
                public_key: hex::encode(v.public_key),
                balance: v.balance,
                validations_count: v.validations_count,
                reputation_score: v.reputation_score,
                last_active_timestamp: v.last_active_timestamp,
                is_online: v.is_online,
                nonce: v.nonce,
            })
        });
        
        // Current challenge with puzzle
        let current_challenge = self.state.get_current_challenge().map(|c| ChallengeResponse {
            challenge_hash: hex::encode(c.challenge_hash),
            challenge_type: format!("{:?}", c.challenge_type),
            height: c.height,
            difficulty: c.difficulty,
            pending_tx_count: c.pending_tx_hashes.len(),
            expires_at: c.expires_at,
            remaining_seconds: c.remaining_time(),
            cognitive_puzzle: c.cognitive_puzzle.as_ref().map(puzzle_to_response),
        });
        
        // Current committee
        let current_committee = self.state.get_committee().map(|c| CommitteeResponse {
            block_height: c.block_height,
            members: c.members.iter().map(|m| CommitteeMemberResponse {
                pubkey: m.pubkey.clone(),
                submitted_proof: m.submitted_proof,
                proof_valid: m.proof_valid,
            }).collect(),
            challenge_hash: hex::encode(c.challenge_hash),
            expires_at: c.expires_at,
            approvals: c.approvals,
            threshold: c.threshold,
            finalized: c.finalized,
        });
        
        // Active governance proposals
        let active_proposals = self.state.get_active_proposals().iter().map(|p| {
            GovernanceProposalResponse {
                id: p.id,
                proposer: p.proposer.clone(),
                proposal_type: format!("{:?}", p.proposal_type),
                description: p.description.clone(),
                status: format!("{:?}", p.status),
                votes_for: p.yes_stake,
                votes_against: p.no_stake,
                created_at: p.created_at,
                expires_at: p.voting_ends_at,
                tx_hash: p.tx_hash.clone(),
                execution_tx_hash: p.execution_tx_hash.clone(),
                votes: p.votes.iter().map(|v| VoteDetail {
                    voter: v.voter.clone(),
                    vote: v.vote,
                    stake_weight: v.stake_weight,
                    reason: v.reason.clone(),
                    tx_hash: v.tx_hash.clone(),
                }).collect(),
            }
        }).collect();
        
        // Recent rewards — scan last 50 tx records for rewards to this validator
        let recent_rewards = if let Some(pk) = &pubkey {
            let (records, _) = self.state.get_transactions_paginated(1, 200, Some("block".to_string()));
            records.iter()
                .filter(|r| {
                    r.tx_type == "block" && 
                    r.validators.as_ref().map_or(false, |vs| vs.contains(pk))
                })
                .take(20)
                .map(|r| RewardEntry {
                    block_height: r.height,
                    reward: r.amount,
                    timestamp: r.timestamp,
                    puzzle_bonus: false, // Would need extra tracking to know; informational
                })
                .collect()
        } else {
            vec![]
        };
        
        // P2P health
        let p2p_tracker = crate::p2p::get_p2p_validator_tracker();
        let p2p_verified_validators = p2p_tracker.count();
        let online_peers = p2p_tracker.get_online_p2p_validators().len();
        
        Ok(AgentDashboardResponse {
            height,
            state_root,
            total_supply,
            validator_count,
            active_validator_count,
            node_version: crate::p2p::SMITH_VERSION.to_string(),
            my_validator,
            current_challenge,
            current_committee,
            network_params: NetworkParamsResponse {
                reward_per_proof: params.reward_per_proof,
                committee_size: params.committee_size,
                min_validator_stake: params.min_validator_stake,
                slash_percentage: params.slash_percentage,
                ai_rate_limit_secs: params.ai_rate_limit_secs,
                max_validators: params.max_validators,
                challenge_timeout_secs: params.challenge_timeout_secs,
            },
            active_proposals,
            recent_rewards,
            peer_count: online_peers,
            p2p_verified_validators,
        })
    }
    
    async fn get_upgrade_announcement(&self) -> RpcResult<Option<crate::p2p::UpgradeAnnouncement>> {
        let tracker = get_version_tracker();
        Ok(tracker.get_latest_upgrade())
    }
}

/// Start the RPC server with event broadcasting
pub async fn start_rpc_server(
    state: SmithNodeState, 
    addr: std::net::SocketAddr,
    network: Option<NetworkHandle>,
) -> anyhow::Result<(ServerHandle, EventSender)> {
    // Create event broadcast channel
    let (event_tx, _) = broadcast::channel::<StateEvent>(100);
    
    // Configure CORS — default allows any origin for devnet convenience.
    // SECURITY: In production, set SMITHNODE_CORS_ORIGINS env var to restrict.
    // Example: SMITHNODE_CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
    if std::env::var("SMITHNODE_CORS_ORIGINS").is_err() {
        tracing::warn!("⚠️ CORS allows ANY origin (devnet default). Set SMITHNODE_CORS_ORIGINS to restrict in production.");
    }
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let middleware = tower::ServiceBuilder::new().layer(cors);

    let server = Server::builder()
        .set_middleware(middleware)
        .build(addr)
        .await?;
    
    let rpc_module = SmithNodeRpcServerImpl::new(state, network, event_tx.clone()).into_rpc();
    
    let handle = server.start(rpc_module);
    
    tracing::info!("🌐 JSON-RPC server started on http://{}", addr);
    tracing::info!("📡 WebSocket subscriptions available at ws://{}", addr);
    
    Ok((handle, event_tx))
}
