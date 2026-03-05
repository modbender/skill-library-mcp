//! SmithNode State Management
//!
//! Core state structure holding balances, challenges, and validator info.

use std::collections::HashMap;
use std::sync::{Arc, RwLock, RwLockReadGuard, RwLockWriteGuard};
use std::sync::atomic::{AtomicBool, Ordering};
use std::path::PathBuf;
use ed25519_dalek::{Signature, Verifier, VerifyingKey};
use serde::{Deserialize, Serialize};
use sha2::{Sha256, Digest};

use super::transaction::{NodeTx, TxResult};
use super::challenge::{CognitiveChallenge, ChallengeType, CognitivePuzzle};
use super::governance::{GovernanceState, ProposalType, Vote, ProposalStatus};
use crate::storage::{Storage, PersistedState};

/// Global tainted flag — set when a poisoned RwLock is recovered.
/// Once tainted, state-mutating operations refuse to proceed to prevent
/// operating on partially-corrupted state after a thread panic.
static STATE_TAINTED: AtomicBool = AtomicBool::new(false);

/// Check if state has been tainted by a lock poisoning event.
pub fn is_state_tainted() -> bool {
    STATE_TAINTED.load(Ordering::SeqCst)
}

/// Extension trait that recovers from poisoned RwLocks gracefully,
/// but marks the state as TAINTED to prevent further mutations.
trait PoisonRecover<T> {
    fn read_or_recover(&self) -> RwLockReadGuard<'_, T>;
    fn write_or_recover(&self) -> RwLockWriteGuard<'_, T>;
}

impl<T> PoisonRecover<T> for RwLock<T> {
    fn read_or_recover(&self) -> RwLockReadGuard<'_, T> {
        self.read().unwrap_or_else(|poisoned| {
            tracing::error!("🚨 RwLock was poisoned (read) — state is TAINTED, node should be restarted");
            STATE_TAINTED.store(true, Ordering::SeqCst);
            poisoned.into_inner()
        })
    }
    fn write_or_recover(&self) -> RwLockWriteGuard<'_, T> {
        self.write().unwrap_or_else(|poisoned| {
            tracing::error!("🚨 RwLock was poisoned (write) — state is TAINTED, node should be restarted");
            STATE_TAINTED.store(true, Ordering::SeqCst);
            poisoned.into_inner()
        })
    }
}

/// Active validator threshold - validators must have been active within this time to be considered online
/// For P2P nodes: 90 seconds (3 missed heartbeats)
/// For RPC-only: 5 minutes (backwards compatible)
const ACTIVE_THRESHOLD_SECS: u64 = 90; // Reduced from 300 for better P2P presence tracking

// Registration rate limiting is handled per-key in the RPC layer (rpc/mod.rs)
// to avoid a global counter that attackers could exhaust to block legitimate users.

/// Validator information
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ValidatorInfo {
    pub public_key: [u8; 32],
    pub balance: u64,
    pub validations_count: u64,
    pub reputation_score: u64,
    pub last_validation_height: u64,
    #[serde(default)]
    pub last_active_timestamp: u64, // Unix timestamp of last activity
    #[serde(default)]
    pub is_online: bool,            // Considered online if active within ACTIVE_THRESHOLD_SECS (90s)
    #[serde(default)]
    pub nonce: u64,                 // Transaction sequence number to prevent replay attacks
}

/// Transaction record for history
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TxRecord {
    pub hash: String,
    pub tx_type: String,
    pub from: String,
    pub to: Option<String>,
    pub amount: u64,
    pub status: String,
    pub timestamp: u64,
    pub height: u64,
    /// For block type: list of validators who participated
    #[serde(skip_serializing_if = "Option::is_none")]
    pub validators: Option<Vec<String>>,
    /// Challenge hash for this block
    #[serde(skip_serializing_if = "Option::is_none")]
    pub challenge_hash: Option<String>,
}

/// Block header for the rollup
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BlockHeader {
    pub height: u64,
    pub prev_state_root: [u8; 32],
    pub tx_root: [u8; 32],
    pub timestamp: u64,
    pub challenge_hash: [u8; 32],
}

/// Committee member for block validation
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CommitteeMember {
    pub pubkey: String,
    pub submitted_proof: bool,
    pub proof_valid: bool,
    pub puzzle_correct: bool,
}

/// Block committee - validators selected to validate a block
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BlockCommittee {
    pub block_height: u64,
    pub members: Vec<CommitteeMember>,
    pub challenge_hash: [u8; 32],
    pub created_at: u64,
    pub expires_at: u64,
    pub finalized: bool,
    pub approvals: usize,
    pub threshold: usize, // 2/3 of committee must approve
}

/// The core state of SmithNode
#[derive(Clone)]
pub struct SmithNodeState {
    inner: Arc<RwLock<StateInner>>,
    storage: Arc<Storage>,
}

struct StateInner {
    /// Mapping: public_key_hex -> ValidatorInfo
    validators: HashMap<String, ValidatorInfo>,
    
    /// Current block height
    height: u64,
    
    /// Current state root (Merkle root of state)
    state_root: [u8; 32],
    
    /// Genesis hash - unique per chain instance, changes on reset
    genesis_hash: [u8; 32],
    
    /// Current active challenge
    current_challenge: Option<CognitiveChallenge>,
    
    /// Current block committee
    current_committee: Option<BlockCommittee>,
    
    /// Transaction records with metadata
    tx_records: Vec<TxRecord>,
    
    /// Pending transactions for next block
    pending_txs: Vec<NodeTx>,
    
    /// Total token supply
    total_supply: u64,
    
    /// Reward per valid proof submission
    reward_per_proof: u64,
    
    /// Committee size (how many validators per block)
    committee_size: usize,
    
    /// Equivocation detection: (block_height, validator_pubkey) -> verdict_digest
    /// Used to detect double-voting (submitting different verdicts for same block)
    submitted_verdicts: HashMap<(u64, String), [u8; 32]>,
    
    /// Governance state for proposals and voting
    governance: GovernanceState,
}

/// Maximum pending transactions per block (prevents mempool flooding)
const MAX_PENDING_TXS: usize = 1000;

/// Compute a commitment hash over the validator set (sorted by pubkey for determinism).
/// Included in state root so the root actually commits to balances and nonces.
pub fn validator_set_hash(validators: &HashMap<String, ValidatorInfo>) -> [u8; 32] {
    let mut sorted_keys: Vec<&String> = validators.keys().collect();
    sorted_keys.sort();
    let mut hasher = Sha256::new();
    for k in &sorted_keys {
        if let Some(v) = validators.get(*k) {
            hasher.update(k.as_bytes());
            hasher.update(&v.balance.to_le_bytes());
            hasher.update(&v.nonce.to_le_bytes());
        }
    }
    hasher.finalize().into()
}

/// Compute the canonical state root hash. ALL nodes must use this identical formula.
/// Includes a validator commitment so the root actually verifies balances, not just height/supply.
pub fn compute_state_root_hash(
    prev_state_root: &[u8; 32],
    height: u64,
    total_supply: u64,
    challenge_hash: &[u8; 32],
    validator_commitment: &[u8; 32],
) -> [u8; 32] {
    let mut hasher = Sha256::new();
    hasher.update(prev_state_root);
    hasher.update(&height.to_le_bytes());
    hasher.update(&total_supply.to_le_bytes());
    hasher.update(challenge_hash);
    hasher.update(validator_commitment);
    hasher.finalize().into()
}

impl SmithNodeState {
    pub fn new() -> Self {
        Self::with_data_dir(Storage::default_data_dir())
    }

    pub fn with_data_dir(data_dir: PathBuf) -> Self {
        let storage = Arc::new(Storage::new(data_dir));
        
        // Check for uncommitted WAL entries (crash recovery)
        if storage.has_uncommitted_wal() {
            let uncommitted = storage.uncommitted_wal_entries();
            tracing::warn!(
                "⚠️ Found {} uncommitted WAL entries — previous run may have crashed",
                uncommitted.len()
            );
            for entry in &uncommitted {
                tracing::info!(
                    "  WAL seq={}: {:?} @ ts={}",
                    entry.seq, 
                    std::mem::discriminant(&entry.op),
                    entry.timestamp
                );
            }
            tracing::info!("📋 State will be loaded from last checkpoint. Uncommitted entries logged above for audit.");
            // We do NOT replay WAL entries automatically — the state.json
            // represents the last atomically-committed checkpoint. The WAL
            // entries above are logged for operator awareness / forensics.
            // Future enhancement: selective replay for specific operations.
            storage.wal_truncate();
        }
        
        // Try to load existing state
        let persisted = storage.load_state();
        
        // Helper to generate a fresh genesis hash
        fn generate_genesis_hash() -> [u8; 32] {
            use sha2::{Sha256, Digest};
            let now = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default();
            let mut hasher = Sha256::new();
            hasher.update(b"smithnode-genesis-");
            hasher.update(&now.as_nanos().to_le_bytes());
            hasher.update(&std::process::id().to_le_bytes());
            hasher.finalize().into()
        }
        
        let inner = if let Some(state) = persisted {
            tracing::info!("📊 Restored state: {} validators, {} transactions, height {}", 
                state.validators.len(), state.tx_records.len(), state.height);
            // Use persisted genesis_hash, or generate fresh if missing/zeroed
            let genesis_hash = if state.genesis_hash == [0u8; 32] {
                let new_hash = generate_genesis_hash();
                tracing::info!("🔑 Generated new genesis hash: {}", hex::encode(&new_hash[..8]));
                new_hash
            } else {
                tracing::info!("🔑 Loaded genesis hash: {}", hex::encode(&state.genesis_hash[..8]));
                state.genesis_hash
            };
            StateInner {
                validators: state.validators,
                height: state.height,
                state_root: state.state_root,
                genesis_hash,
                current_challenge: None,
                current_committee: None,
                tx_records: state.tx_records,
                pending_txs: Vec::new(),
                total_supply: state.total_supply,
                reward_per_proof: 100,
                committee_size: 5,
                submitted_verdicts: HashMap::new(),
                governance: state.governance, // Load persisted governance
            }
        } else {
            let genesis_hash = generate_genesis_hash();
            tracing::info!("🔑 Fresh chain - generated genesis hash: {}", hex::encode(&genesis_hash[..8]));
            StateInner {
                validators: HashMap::new(),
                height: 0,
                state_root: [0u8; 32],
                genesis_hash,
                current_challenge: None,
                current_committee: None,
                tx_records: Vec::new(),
                pending_txs: Vec::new(),
                total_supply: 0,
                reward_per_proof: 100,
                committee_size: 5,
                submitted_verdicts: HashMap::new(),
                governance: GovernanceState::default(),
            }
        };

        Self {
            inner: Arc::new(RwLock::new(inner)),
            storage,
        }
    }

    /// Persist current state to disk
    pub fn save(&self) -> anyhow::Result<()> {
        let inner = self.inner.read_or_recover();
        let persisted = PersistedState {
            validators: inner.validators.clone(),
            height: inner.height,
            state_root: inner.state_root,
            tx_records: inner.tx_records.clone(),
            total_supply: inner.total_supply,
            governance: inner.governance.clone(),
            genesis_hash: inner.genesis_hash,
        };
        self.storage.save_state(&persisted)
    }
    
    /// Get the genesis hash for this chain instance
    pub fn get_genesis_hash(&self) -> [u8; 32] {
        self.inner.read_or_recover().genesis_hash
    }

    /// Apply state received from a peer (state sync)
    /// Only applies if peer state is ahead of ours AND state root is verified
    /// SECURITY (C1): Verifies the state root matches the claimed validators/supply
    pub fn apply_peer_state(
        &self, 
        height: u64, 
        claimed_state_root: [u8; 32],
        total_supply: u64,
        validators: Vec<ValidatorInfo>,
    ) -> bool {
        let mut inner = self.inner.write_or_recover();
        
        // Only apply if peer is ahead
        if height <= inner.height {
            return false;
        }
        
        // SECURITY: Sanity-check the claimed state
        // The state root is a chained hash (prev_root || height || supply || challenge_hash)
        // so we cannot recompute it from validators alone. Instead, apply practical guards:
        
        // Guard 1: Supply must be reasonable (max 10B SMITH = 10_000_000_000)
        if total_supply > 10_000_000_000 {
            tracing::warn!("⚠️ Rejecting peer state: unreasonable supply {}", total_supply);
            return false;
        }
        
        // Guard 2: Validator balances must sum to <= total_supply
        let balance_sum: u64 = validators.iter().map(|v| v.balance).sum();
        if balance_sum > total_supply {
            tracing::warn!("⚠️ Rejecting peer state: validator balances {} exceed supply {}", balance_sum, total_supply);
            return false;
        }
        
        // Guard 3: State root must not be all zeros (except genesis)
        if claimed_state_root == [0u8; 32] && height > 0 {
            tracing::warn!("⚠️ Rejecting peer state: zero state root at height {}", height);
            return false;
        }
        
        // Guard 4: Must have at least 1 validator
        if validators.is_empty() {
            tracing::warn!("⚠️ Rejecting peer state: no validators");
            return false;
        }
        
        tracing::info!("🔄 Applying VERIFIED peer state: height {} -> {}, {} validators",
            inner.height, height, validators.len());
        
        // Update state
        inner.height = height;
        inner.state_root = claimed_state_root;
        inner.total_supply = total_supply;
        
        // SECURITY: Preserve nonces from existing validators to prevent replay attacks
        let existing_nonces: HashMap<String, u64> = inner.validators.iter()
            .map(|(k, v)| (k.clone(), v.nonce))
            .collect();
        
        // Update validators
        inner.validators.clear();
        for mut v in validators {
            let pubkey_hex = hex::encode(&v.public_key);
            // Preserve existing nonce (higher of local vs peer to prevent replay)
            if let Some(&existing_nonce) = existing_nonces.get(&pubkey_hex) {
                v.nonce = v.nonce.max(existing_nonce);
            }
            inner.validators.insert(pubkey_hex, v);
        }
        
        // Clear current challenge (peer will broadcast new one)
        inner.current_challenge = None;
        inner.current_committee = None;
        
        drop(inner);
        
        // WAL: Log the state sync before checkpointing
        if let Err(e) = self.storage.wal_append(crate::storage::WalOp::StateSynced {
            height,
            state_root_hex: hex::encode(claimed_state_root),
        }) {
            tracing::warn!("⚠️ WAL write for state sync failed: {}", e);
        }
        
        // Persist to disk
        if let Err(e) = self.save() {
            tracing::error!("Failed to save synced state: {}", e);
        }
        
        true
    }

    /// Produce a turbo block — no AI puzzles required.
    /// Blocks are produced every 2 seconds. Pending transactions are included.
    /// Active validators share the block reward proportionally.
    /// Returns (height, prev_state_root, new_state_root, challenge_hash, total_supply) or None.
    pub fn produce_turbo_block(&self) -> Option<(u64, [u8; 32], [u8; 32], [u8; 32], u64)> {
        // Refuse if state is tainted by lock poisoning
        if STATE_TAINTED.load(Ordering::SeqCst) {
            tracing::error!("🚨 Refusing to produce block: state is tainted. Restart the node.");
            return None;
        }
        let mut inner = self.inner.write_or_recover();
        
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        
        // Get ALL active validators (for tracking/display)
        let active_validators: Vec<String> = inner.validators.iter()
            .filter(|(_, v)| {
                let time_since_active = now.saturating_sub(v.last_active_timestamp);
                time_since_active <= ACTIVE_THRESHOLD_SECS
            })
            .map(|(k, _)| k.clone())
            .collect();
        
        if active_validators.is_empty() {
            return None;
        }
        
        // Save previous state root BEFORE any mutations
        let prev_state_root = inner.state_root;
        
        // Use a deterministic seed for committee selection based on state
        let committee_seed: [u8; 32] = {
            let mut hasher = Sha256::new();
            hasher.update(b"committee_seed");
            hasher.update(&prev_state_root);
            hasher.update(&inner.height.to_le_bytes());
            hasher.finalize().into()
        };
        
        // Select committee: reputation-weighted subset of active validators
        // Uses governance param committee_size (default: 5)
        let committee = Self::select_committee_from_inner(&inner, &committee_seed);
        
        // If committee selection returned empty (shouldn't happen since we have active validators),
        // fall back to all active validators
        let rewarded_validators = if committee.is_empty() {
            tracing::warn!("⚠️ Committee selection returned empty, falling back to all active validators");
            active_validators.clone()
        } else {
            tracing::info!(
                "👥 Block {} committee: {}/{} active validators selected (reputation-weighted)",
                inner.height + 1,
                committee.len(),
                active_validators.len()
            );
            committee
        };
        
        // Distribute reward equally among COMMITTEE members only
        let reward_per_proof = inner.governance.params.reward_per_proof;
        let num_committee = rewarded_validators.len() as u64;
        let reward_each = reward_per_proof / num_committee.max(1);
        
        // Give each committee member their share
        let next_height = inner.height + 1;
        for pubkey in rewarded_validators.iter() {
            if let Some(v) = inner.validators.get_mut(pubkey) {
                v.balance += reward_each;
                v.validations_count += 1;
                v.last_validation_height = next_height;
            }
        }
        
        let total_reward = reward_each * num_committee;
        inner.total_supply += total_reward;
        
        // Compute challenge hash (deterministic — NO timestamp, only state data)
        let challenge_hash: [u8; 32] = {
            let mut hasher = Sha256::new();
            hasher.update(&prev_state_root);
            hasher.update(&inner.height.to_le_bytes());
            hasher.update(&inner.total_supply.to_le_bytes());
            hasher.finalize().into()
        };
        
        // Record the block transaction
        let tx_hash = {
            let mut hasher = Sha256::new();
            hasher.update(b"turbo_block");
            hasher.update(&inner.height.to_le_bytes());
            hasher.update(&challenge_hash);
            hex::encode::<[u8; 32]>(hasher.finalize().into())
        };
        
        let current_height = inner.height;
        inner.tx_records.push(TxRecord {
            hash: tx_hash,
            tx_type: "block".to_string(),
            from: rewarded_validators.first().cloned().unwrap_or_default(),
            to: None,
            amount: total_reward,
            status: "confirmed".to_string(),
            timestamp: now,
            height: current_height + 1,
            validators: Some(rewarded_validators),
            challenge_hash: Some(hex::encode(challenge_hash)),
        });
        
        // Drain pending txs (they're included in this block)
        inner.pending_txs.clear();
        
        // Advance height
        inner.height += 1;
        
        // Compute new state root (must match verification in p2p/mod.rs handle_block_message)
        // Formula: hash(prev_state_root || height || total_supply || challenge_hash || validator_commitment)
        let val_commitment = validator_set_hash(&inner.validators);
        let new_state_root = compute_state_root_hash(
            &prev_state_root,
            inner.height,
            inner.total_supply,
            &challenge_hash,
            &val_commitment,
        );
        inner.state_root = new_state_root;
        
        // Clean up old verdict records
        let h = inner.height;
        inner.submitted_verdicts.retain(|&(height, _), _| height + 10 > h);
        
        let height = inner.height;
        let state_root = inner.state_root;
        let total_supply = inner.total_supply;
        
        drop(inner);
        
        // Persist every 10th block (not every 2s to reduce disk I/O)
        if height % 10 == 0 {
            if let Err(e) = self.save() {
                tracing::warn!("⚠️ Failed to save turbo block state: {}", e);
            }
        }
        
        Some((height, prev_state_root, state_root, challenge_hash, total_supply))
    }

    /// Record result of a P2P liveness challenge (async, doesn't block blocks)
    pub fn record_liveness_result(&self, challenger: &str, target: &str, success: bool) {
        let mut inner = self.inner.write_or_recover();
        
        if let Some(v) = inner.validators.get_mut(target) {
            if success {
                v.reputation_score = v.reputation_score.saturating_add(10);
                tracing::info!("✅ Liveness proof: {}... passed (rep +10)", &target[..16.min(target.len())]);
            } else {
                v.reputation_score = v.reputation_score.saturating_sub(25);
                tracing::warn!("❌ Liveness fail: {}... (rep -25, challenged by {}...)", 
                    &target[..16.min(target.len())], &challenger[..16.min(challenger.len())]);
                
                // Slash for failed liveness after multiple failures
                if v.reputation_score < 25 {
                    let slash = 5u64.min(v.balance);
                    v.balance -= slash;
                    inner.total_supply -= slash;
                    tracing::warn!("⚡ SLASHED {}... for {} SMITH: repeated liveness failures", 
                        &target[..16.min(target.len())], slash);
                }
            }
        }
    }

    /// Select committee members based on reputation-weighted random selection (static version)
    /// Doesn't take &self — safe to call while holding a write lock on inner
    fn select_committee_from_inner(inner: &StateInner, seed: &[u8; 32]) -> Vec<String> {
        let current_time = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        
        // Filter to only ACTIVE validators (online in last 5 minutes)
        let mut validators: Vec<_> = inner.validators.iter()
            .filter(|(_, v)| {
                let time_since_active = current_time.saturating_sub(v.last_active_timestamp);
                time_since_active <= ACTIVE_THRESHOLD_SECS
            })
            .collect();
        // CRITICAL: Sort by pubkey for deterministic committee selection across nodes.
        // HashMap iteration order is non-deterministic, so without sorting,
        // different nodes could select different committees from the same seed.
        validators.sort_by_key(|(k, _)| (*k).clone());
        
        if validators.is_empty() {
            return Vec::new();
        }
        
        // Use governance params for committee size
        let governed_committee_size = inner.governance.params.committee_size;
        let committee_size = governed_committee_size.min(validators.len());
        let mut selected: Vec<String> = Vec::with_capacity(committee_size);
        let mut used_indices: std::collections::HashSet<usize> = std::collections::HashSet::new();
        
        // Use seed for deterministic random selection
        let mut rng_state = u64::from_le_bytes(seed[0..8].try_into().unwrap());
        
        for _ in 0..committee_size {
            let available_weight: u64 = validators.iter().enumerate()
                .filter(|(idx, _)| !used_indices.contains(idx))
                .map(|(_, (_, v))| v.reputation_score.max(1))
                .sum();
            
            if available_weight == 0 {
                break;
            }
            
            rng_state = rng_state.wrapping_mul(6364136223846793005).wrapping_add(1);
            let rand_val = rng_state % available_weight;
            
            let mut cumulative: u64 = 0;
            for (idx, (pubkey, validator)) in validators.iter().enumerate() {
                if used_indices.contains(&idx) {
                    continue;
                }
                cumulative += validator.reputation_score.max(1);
                if cumulative > rand_val {
                    selected.push(pubkey.to_string());
                    used_indices.insert(idx);
                    break;
                }
            }
        }
        
        selected
    }

    /// Select committee members based on reputation-weighted random selection
    /// ONLY selects from ACTIVE validators (online in last 5 minutes)
    fn select_committee(&self, inner: &StateInner, seed: &[u8; 32]) -> Vec<String> {
        let current_time = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        
        // Filter to only ACTIVE validators (online in last 5 minutes)
        let mut validators: Vec<_> = inner.validators.iter()
            .filter(|(_, v)| {
                let time_since_active = current_time.saturating_sub(v.last_active_timestamp);
                time_since_active <= ACTIVE_THRESHOLD_SECS
            })
            .collect();
        // CRITICAL: Sort by pubkey for deterministic committee selection across nodes
        validators.sort_by_key(|(k, _)| (*k).clone());
        
        if validators.is_empty() {
            tracing::warn!("⚠️ No active validators available for committee selection!");
            return Vec::new();
        }
        
        tracing::info!("🤖 Selecting committee from {} ACTIVE validators", validators.len());
        
        // Calculate total reputation weight from active validators only
        let total_weight: u64 = validators.iter()
            .map(|(_, v)| v.reputation_score.max(1))
            .sum();
        
        if total_weight == 0 {
            return Vec::new();
        }
        
        // Select committee_size members (or all if fewer validators)
        // M1: Use governance params instead of hardcoded committee_size
        let governed_committee_size = inner.governance.params.committee_size;
        let committee_size = governed_committee_size.min(validators.len());
        let mut selected: Vec<String> = Vec::with_capacity(committee_size);
        let mut used_indices: std::collections::HashSet<usize> = std::collections::HashSet::new();
        
        // Use seed for deterministic random selection
        let mut rng_state = u64::from_le_bytes(seed[0..8].try_into().unwrap());
        
        for _ in 0..committee_size {
            // Recalculate available weight excluding already-selected validators
            let available_weight: u64 = validators.iter().enumerate()
                .filter(|(idx, _)| !used_indices.contains(idx))
                .map(|(_, (_, v))| v.reputation_score.max(1))
                .sum();
            
            if available_weight == 0 {
                break;
            }
            
            // Simple LCG random number generator
            rng_state = rng_state.wrapping_mul(6364136223846793005).wrapping_add(1);
            let rand_val = rng_state % available_weight;
            
            // Find validator based on weighted selection (only from available)
            let mut cumulative: u64 = 0;
            for (idx, (pubkey, validator)) in validators.iter().enumerate() {
                if used_indices.contains(&idx) {
                    continue;
                }
                cumulative += validator.reputation_score.max(1);
                if cumulative > rand_val {
                    selected.push(pubkey.to_string());
                    used_indices.insert(idx);
                    break;
                }
            }
        }
        
        selected
    }

    /// Finalize an expired challenge with partial approvals
    /// This prevents blocks from getting stuck when committee can't reach full threshold
    /// Also slashes committee members who didn't submit proofs
    /// SECURITY (H5): Uses single write lock to prevent TOCTOU race conditions
    fn finalize_expired_challenge(&self) {
        let mut inner = self.inner.write_or_recover();
        
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        
        // Check if we have an expired, non-finalized committee
        let should_process = if let Some(ref committee) = inner.current_committee {
            now > committee.expires_at && !committee.finalized
        } else {
            false
        };
        
        if !should_process {
            return;
        }
        
        // Collect absent members and slash them (all under write lock to prevent TOCTOU)
        let absent_members: Vec<String> = inner.current_committee.as_ref().unwrap()
            .members.iter()
            .filter(|m| !m.submitted_proof)
            .map(|m| m.pubkey.clone())
            .collect();
        
        // Slash absent members (inline to avoid dropping the lock)
        for pubkey in &absent_members {
            let slash_amount = 10u64; // committee absence penalty
            if let Some(validator) = inner.validators.get_mut(pubkey) {
                let actual_slash = slash_amount.min(validator.balance);
                validator.balance -= actual_slash;
                validator.reputation_score = validator.reputation_score.saturating_sub(50);
                inner.total_supply -= actual_slash;
                
                let height = inner.height;
                let tx_hash = {
                    let mut hasher = Sha256::new();
                    hasher.update(b"slash");
                    hasher.update(pubkey.as_bytes());
                    hasher.update(&actual_slash.to_le_bytes());
                    hasher.update(&height.to_le_bytes());
                    hex::encode::<[u8; 32]>(hasher.finalize().into())
                };
                
                inner.tx_records.push(TxRecord {
                    hash: tx_hash,
                    tx_type: "slash".to_string(),
                    from: pubkey.to_string(),
                    to: None,
                    amount: actual_slash,
                    status: "slashed: committee absence".to_string(),
                    timestamp: now,
                    height,
                    validators: None,
                    challenge_hash: None,
                });
                
                tracing::warn!(
                    "⚡ SLASHED validator {}... for {} SMITH: committee absence",
                    &pubkey[..16.min(pubkey.len())],
                    actual_slash
                );
            }
        }
        
        // Check if we have at least 1 approval
        let committee = inner.current_committee.as_ref().unwrap();
        if committee.approvals < 1 {
            // No valid proofs, just clear the challenge
            inner.current_challenge = None;
            inner.current_committee = None;
            tracing::info!("⏰ Challenge expired with no valid proofs, clearing");
            return;
        }
        
        // Get committee info before mutating
        let challenge_hash = committee.challenge_hash;
        let approving_validators: Vec<String> = committee.members.iter()
            .filter(|m| m.proof_valid)
            .map(|m| m.pubkey.clone())
            .collect();
        
        if approving_validators.is_empty() {
            inner.current_challenge = None;
            inner.current_committee = None;
            tracing::info!("⏰ Challenge expired with no valid proofs, clearing");
            return;
        }
        
        let num_approvers = approving_validators.len() as u64;
        let reward_per_validator = inner.governance.params.reward_per_proof / num_approvers.max(1);
        
        tracing::info!(
            "⏰ Challenge expired! Finalizing with {}/{} approvals",
            num_approvers,
            committee.members.len()
        );
        
        // Distribute rewards to all approving committee members
        for approver_pubkey in &approving_validators {
            if let Some(v) = inner.validators.get_mut(approver_pubkey) {
                v.balance += reward_per_validator;
            }
        }
        
        inner.total_supply += reward_per_validator * num_approvers;
        
        // Record the transaction
        let tx_hash = {
            let mut hasher = Sha256::new();
            hasher.update(b"block_finalized_partial");
            hasher.update(&inner.height.to_le_bytes());
            hasher.update(&challenge_hash);
            hex::encode::<[u8; 32]>(hasher.finalize().into())
        };
        
        let current_height = inner.height;
        inner.tx_records.push(TxRecord {
            hash: tx_hash,
            tx_type: "block".to_string(),
            from: approving_validators.first().cloned().unwrap_or_default(),
            to: None,
            amount: reward_per_validator * num_approvers,
            status: "confirmed".to_string(),
            timestamp: now,
            height: current_height,
            validators: Some(approving_validators),
            challenge_hash: Some(hex::encode(challenge_hash)),
        });
        
        // Finalize block
        let prev_root = inner.state_root;
        inner.height += 1;
        
        // Compute new state root (includes validator commitment for balance verification)
        let val_commitment = validator_set_hash(&inner.validators);
        let new_state_root = compute_state_root_hash(
            &prev_root,
            inner.height,
            inner.total_supply,
            &challenge_hash,
            &val_commitment,
        );
        inner.state_root = new_state_root;
        
        // Clear challenge and committee
        inner.current_challenge = None;
        inner.current_committee = None;
        
        // Clean up old verdict records (only keep last 10 blocks to prevent memory growth)
        let current_height = inner.height;
        inner.submitted_verdicts.retain(|&(h, _), _| h + 10 > current_height);
        
        tracing::info!(
            "📦 Block {} FINALIZED (partial)! {} validators approved, {} SMITH distributed",
            inner.height,
            num_approvers,
            reward_per_validator * num_approvers
        );
    }

    /// Generate a new cognitive challenge with committee selection
    pub fn generate_challenge(&self) -> CognitiveChallenge {
        // First, finalize any expired challenge with partial approvals
        self.finalize_expired_challenge();
        
        let mut inner = self.inner.write_or_recover();
        
        // Create challenge hash from current state
        let mut hasher = Sha256::new();
        hasher.update(&inner.state_root);
        hasher.update(&inner.height.to_le_bytes());
        hasher.update(&std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs()
            .to_le_bytes());
        
        let challenge_hash: [u8; 32] = hasher.finalize().into();
        
        // Select committee for this block
        let committee_members = self.select_committee(&inner, &challenge_hash);
        let committee_size = committee_members.len();
        let threshold = if committee_size > 0 { (committee_size * 2 / 3).max(1) } else { 1 };
        
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        
        // Create committee
        let committee = BlockCommittee {
            block_height: inner.height + 1,
            members: committee_members.iter().map(|pk| CommitteeMember {
                pubkey: pk.clone(),
                submitted_proof: false,
                proof_valid: false,
                puzzle_correct: false,
            }).collect(),
            challenge_hash,
            created_at: now,
            expires_at: now + 30, // 30 second window (devnet: fast blocks)
            finalized: false,
            approvals: 0,
            threshold,
        };
        
        if !committee.members.is_empty() {
            tracing::info!(
                "👥 Committee selected for block {}: {} members, threshold: {}/{}",
                committee.block_height,
                committee.members.len(),
                threshold,
                committee.members.len()
            );
            for member in &committee.members {
                tracing::debug!("   - {}...", &member.pubkey[..16]);
            }
        }
        
        inner.current_committee = Some(committee);
        
        // Generate a cognitive puzzle for this challenge
        let puzzle = CognitivePuzzle::generate(&challenge_hash, 1);
        
        tracing::info!(
            "🧠 Cognitive puzzle generated: {:?} - '{}'",
            puzzle.puzzle_type,
            &puzzle.prompt[..50.min(puzzle.prompt.len())]
        );
        
        // Create a transaction verification challenge with cognitive puzzle
        let challenge = CognitiveChallenge {
            challenge_type: ChallengeType::TransactionVerification,
            challenge_hash,
            height: inner.height,
            difficulty: 1, // Base difficulty
            pending_tx_hashes: inner.pending_txs.iter()
                .map(|tx| tx.hash())
                .collect(),
            created_at: now,
            expires_at: now + 30, // 30 second window (devnet: fast blocks)
            cognitive_puzzle: Some(puzzle),
        };
        
        inner.current_challenge = Some(challenge.clone());
        challenge
    }

    /// Get current committee info
    pub fn get_committee(&self) -> Option<BlockCommittee> {
        self.inner.read_or_recover().current_committee.clone()
    }

    /// Get the current active challenge
    pub fn get_current_challenge(&self) -> Option<CognitiveChallenge> {
        self.inner.read_or_recover().current_challenge.clone()
    }

    /// Apply a transaction to the state
    pub fn apply_tx(&self, tx: NodeTx) -> TxResult {
        // Refuse mutations if state was tainted by a lock poisoning event
        if STATE_TAINTED.load(Ordering::SeqCst) {
            tracing::error!("🚨 Refusing transaction: state is tainted (poisoned lock detected). Restart the node.");
            return TxResult::Error("Node state is tainted — restart required".into());
        }
        let result = match tx {
            NodeTx::SubmitProof {
                ref validator_pubkey,
                ref challenge_hash,
                ref signature,
                ref verdict_digest,
                ref puzzle_answer,
            } => {
                self.process_proof_submission(
                    validator_pubkey,
                    challenge_hash,
                    signature,
                    verdict_digest,
                    puzzle_answer.as_deref(),
                )
            }
            NodeTx::Transfer {
                ref from,
                ref to,
                amount,
                nonce,
                ref signature,
            } => {
                // Enforce max pending TXs (transfers are not consensus-critical)
                if self.inner.read_or_recover().pending_txs.len() >= MAX_PENDING_TXS {
                    return TxResult::Error("Block is full (max 1000 transactions). Try next block.".into());
                }
                self.process_transfer(from, to, amount, nonce, signature)
            }
            NodeTx::RegisterValidator { ref public_key } => {
                // Enforce max pending TXs
                if self.inner.read_or_recover().pending_txs.len() >= MAX_PENDING_TXS {
                    return TxResult::Error("Block is full (max 1000 transactions). Try next block.".into());
                }
                self.register_validator(public_key)
            }
            NodeTx::AIMessage { .. } => {
                // AI messages are stored off-chain in the P2P layer
                // On-chain we just record that a message was sent
                TxResult::Success { reward: 0, new_balance: 0 }
            }
            NodeTx::CreateProposal {
                ref proposer,
                proposal_type,
                new_value,
                ref description_hash,
                ref signature,
            } => {
                self.process_create_proposal(proposer, proposal_type, new_value, description_hash, signature)
            }
            NodeTx::VoteProposal {
                ref voter,
                proposal_id,
                vote,
                ref signature,
                ref reason,
            } => {
                self.process_vote_proposal(voter, proposal_id, vote, signature, reason.as_deref())
            }
            NodeTx::ExecuteProposal {
                ref executor,
                proposal_id,
                ref signature,
            } => {
                self.process_execute_proposal(executor, proposal_id, signature)
            }
        };

        // WAL: Log the successful operation before checkpointing
        if result.is_success() {
            let wal_op = match (&tx, &result) {
                (_, TxResult::BlockFinalized { block_height, state_root, .. }) => {
                    let inner = self.inner.read_or_recover();
                    Some(crate::storage::WalOp::BlockFinalized {
                        height: *block_height,
                        state_root_hex: hex::encode(state_root),
                        total_supply: inner.total_supply,
                    })
                }
                (NodeTx::SubmitProof { validator_pubkey, challenge_hash, .. }, TxResult::Success { reward, .. }) if *reward > 0 => {
                    Some(crate::storage::WalOp::ProofAccepted {
                        validator_pubkey_hex: hex::encode(validator_pubkey),
                        challenge_hash_hex: hex::encode(challenge_hash),
                        reward: *reward,
                    })
                }
                (NodeTx::Transfer { from, to, amount, .. }, _) => {
                    Some(crate::storage::WalOp::Transfer {
                        from_hex: hex::encode(from),
                        to_hex: hex::encode(to),
                        amount: *amount,
                    })
                }
                (NodeTx::RegisterValidator { public_key }, _) => {
                    Some(crate::storage::WalOp::ValidatorRegistered {
                        pubkey_hex: hex::encode(public_key),
                    })
                }
                (NodeTx::CreateProposal { .. } | NodeTx::VoteProposal { .. } | NodeTx::ExecuteProposal { .. }, _) => {
                    Some(crate::storage::WalOp::GovernanceAction {
                        action: format!("{:?}", std::mem::discriminant(&tx)),
                        detail: String::new(),
                    })
                }
                _ => None,
            };
            if let Some(op) = wal_op {
                if let Err(e) = self.storage.wal_append(op) {
                    tracing::warn!("⚠️ WAL write failed (state will still be saved): {}", e);
                }
            }
        }

        // NOTE: Per-tx save removed for performance (#14). State is persisted
        // via periodic turbo block checkpoints (every 10th block) and WAL entries.
        // This eliminates ~2-5MB JSON serialization on every single transaction.

        result
    }

    /// Process a proof submission from an AI validator
    fn process_proof_submission(
        &self,
        validator_pubkey: &[u8; 32],
        challenge_hash: &[u8; 32],
        signature: &[u8; 64],
        verdict_digest: &[u8; 32],
        puzzle_answer: Option<&str>,
    ) -> TxResult {
        let pubkey_hex = hex::encode(validator_pubkey);
        
        // First, verify signature (before acquiring write lock so we can slash if invalid)
        let (_challenge_height, is_sig_valid, challenge_exists) = {
            let inner = self.inner.read_or_recover();
            let challenge = inner.current_challenge.as_ref();
            let height = challenge.map(|c| c.height).unwrap_or(0);
            let exists = challenge.is_some();
            
            let verifying_key = match VerifyingKey::from_bytes(validator_pubkey) {
                Ok(k) => k,
                Err(_) => return TxResult::Error("Invalid public key".into()),
            };
            
            // Message is: challenge_hash || verdict_digest || height (8 bytes LE)
            let mut message = Vec::with_capacity(72);
            message.extend_from_slice(challenge_hash);
            message.extend_from_slice(verdict_digest);
            message.extend_from_slice(&height.to_le_bytes());
            
            let sig = Signature::from_bytes(signature);
            (height, verifying_key.verify(&message, &sig).is_ok(), exists)
        };
        
        // If the challenge no longer exists (block already finalized), 
        // the proof is just late — don't slash, just reject gracefully
        if !challenge_exists {
            return TxResult::Error("No active challenge (block already finalized)".into());
        }
        
        // Slash for invalid signature and return error
        if !is_sig_valid {
            if let Err(e) = self.slash_for_invalid_proof(&pubkey_hex) {
                tracing::warn!("Could not slash for invalid proof: {}", e);
            }
            return TxResult::Error("Signature verification failed - validator slashed".into());
        }
        
        let mut inner = self.inner.write_or_recover();
        
        // 1. Verify the challenge exists and matches
        let current_challenge = match &inner.current_challenge {
            Some(c) => c.clone(),
            None => return TxResult::Error("No active challenge".into()),
        };
        
        if &current_challenge.challenge_hash != challenge_hash {
            return TxResult::Error("Challenge hash mismatch".into());
        }
        
        // 1b. Check if challenge has expired
        if current_challenge.is_expired() {
            return TxResult::Error("Challenge has expired".into());
        }
        
        // 1c. Verify cognitive puzzle answer (Proof of Cognition)
        let puzzle_correct = if let Some(ref puzzle) = current_challenge.cognitive_puzzle {
            if let Some(answer) = puzzle_answer {
                let answer_hash = super::challenge::CognitivePuzzle::hash_answer(answer);
                if answer_hash == puzzle.expected_answer_hash {
                    tracing::info!("🧠 Puzzle answer CORRECT from {}...", &pubkey_hex[..16]);
                    true
                } else {
                    tracing::debug!("🧠 Puzzle answer incorrect from {}... (not penalized)", &pubkey_hex[..16]);
                    false
                }
            } else {
                tracing::debug!("🧠 No puzzle answer from {}... (allowed but no bonus)", &pubkey_hex[..16]);
                false
            }
        } else {
            false // No puzzle in this challenge
        };
        
        // 2. Check if validator is in current committee (if committee exists)
        let committee_mode = inner.current_committee.is_some() && 
            inner.current_committee.as_ref().unwrap().members.len() > 1;
        
        if committee_mode {
            let committee = inner.current_committee.as_ref().unwrap();
            let is_member = committee.members.iter().any(|m| m.pubkey == pubkey_hex);
            
            if !is_member {
                return TxResult::Error(format!(
                    "Validator {} not in committee for block {}",
                    &pubkey_hex[..16],
                    committee.block_height
                ));
            }
            
            // Check if already submitted
            let already_submitted = committee.members.iter()
                .find(|m| m.pubkey == pubkey_hex)
                .map(|m| m.submitted_proof)
                .unwrap_or(false);
            
            if already_submitted {
                return TxResult::Error("Validator already submitted proof for this block".into());
            }
        }
        
        // 2b. EQUIVOCATION DETECTION: Check if validator already submitted a DIFFERENT verdict
        // L1 fix: Use challenge height (height+1) since proofs are for the next block
        let challenge_height = inner.height + 1;
        let verdict_key = (challenge_height, pubkey_hex.clone());
        
        if let Some(previous_verdict) = inner.submitted_verdicts.get(&verdict_key) {
            // Validator already submitted for this block - check if same verdict
            if previous_verdict != verdict_digest {
                // EQUIVOCATION DETECTED! Different verdict for same block = double voting
                tracing::error!(
                    "⚠️ EQUIVOCATION DETECTED! Validator {}... submitted conflicting verdicts for block {}",
                    &pubkey_hex[..16],
                    challenge_height
                );
                // Release lock before slashing
                drop(inner);
                if let Err(e) = self.slash_for_equivocation(&pubkey_hex) {
                    tracing::warn!("Could not slash for equivocation: {}", e);
                }
                return TxResult::Error("Equivocation detected - validator slashed for double voting".into());
            }
            // Same verdict, this is a duplicate (already handled by committee check)
        } else {
            // First submission for this block/validator - record the verdict
            inner.submitted_verdicts.insert(verdict_key, *verdict_digest);
        }
        
        // Note: Signature already verified before acquiring write lock (with slashing for invalid)
        
        // 3. Update committee member status
        let mut should_finalize = false;
        let mut committee_approvals = 0;
        let mut committee_threshold = 1;
        let mut _committee_members_count = 1;
        
        if committee_mode {
            let committee = inner.current_committee.as_mut().unwrap();
            
            // Mark this validator as having submitted
            if let Some(member) = committee.members.iter_mut().find(|m| m.pubkey == pubkey_hex) {
                member.submitted_proof = true;
                member.proof_valid = true;
                member.puzzle_correct = puzzle_correct;
            }
            
            committee.approvals += 1;
            committee_approvals = committee.approvals;
            committee_threshold = committee.threshold;
            _committee_members_count = committee.members.len();
            
            tracing::info!(
                "✅ Validator {}... approved block {} ({}/{})",
                &pubkey_hex[..16],
                committee.block_height,
                committee.approvals,
                committee.threshold
            );
            
            // Check if threshold reached
            if committee.approvals >= committee.threshold && !committee.finalized {
                should_finalize = true;
                committee.finalized = true;
            }
        } else {
            // Single validator mode (backwards compatible for < committee_size validators)
            should_finalize = true;
        }
        
        // 5. Update validator stats (always, even if block not finalized yet)
        let height = inner.height;
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        
        let validator = inner.validators
            .entry(pubkey_hex.clone())
            .or_insert_with(|| ValidatorInfo {
                public_key: *validator_pubkey,
                balance: 0,
                validations_count: 0,
                reputation_score: 100,
                last_validation_height: 0,
                last_active_timestamp: now,
                is_online: true,
                nonce: 0,
            });
        
        validator.validations_count += 1;
        validator.last_validation_height = height;
        validator.last_active_timestamp = now;
        validator.is_online = true;
        validator.reputation_score = (validator.reputation_score + 1).min(1000);
        
        // 6. If threshold reached, finalize block and distribute rewards
        if should_finalize {
            // Collect all approving validators for reward distribution
            let approving_validators: Vec<String> = if committee_mode {
                let committee = inner.current_committee.as_ref().unwrap();
                committee.members.iter()
                    .filter(|m| m.proof_valid)
                    .map(|m| m.pubkey.clone())
                    .collect()
            } else {
                vec![pubkey_hex.clone()]
            };
            
            let num_approvers = approving_validators.len() as u64;
            let reward_per_validator = inner.governance.params.reward_per_proof / num_approvers.max(1);
            // Puzzle bonus: 50% extra reward for correct puzzle answers
            
            // Collect all committee members who answered the puzzle correctly
            let puzzle_solvers: Vec<String> = if committee_mode {
                let committee = inner.current_committee.as_ref().unwrap();
                committee.members.iter()
                    .filter(|m| m.proof_valid && m.puzzle_correct)
                    .map(|m| m.pubkey.clone())
                    .collect()
            } else if puzzle_correct {
                vec![pubkey_hex.clone()]
            } else {
                vec![]
            };
            let puzzle_bonus = if !puzzle_solvers.is_empty() { reward_per_validator / 2 } else { 0 };
            
            // Distribute rewards to all approving committee members
            for approver_pubkey in &approving_validators {
                if let Some(v) = inner.validators.get_mut(approver_pubkey) {
                    v.balance += reward_per_validator;
                }
            }
            
            // Give puzzle bonus to ALL validators who solved correctly
            let mut total_puzzle_bonus = 0u64;
            for solver_pubkey in &puzzle_solvers {
                if let Some(v) = inner.validators.get_mut(solver_pubkey) {
                    v.balance += puzzle_bonus;
                    total_puzzle_bonus += puzzle_bonus;
                    tracing::info!("🧠 Puzzle bonus: +{} SMITH to {}...", puzzle_bonus, &solver_pubkey[..16.min(solver_pubkey.len())]);
                }
            }
            
            inner.total_supply += reward_per_validator * num_approvers + total_puzzle_bonus;
            
            // Record the transaction
            let tx_hash = {
                let mut hasher = Sha256::new();
                hasher.update(b"block_finalized");
                hasher.update(&inner.height.to_le_bytes());
                hasher.update(challenge_hash);
                hex::encode::<[u8; 32]>(hasher.finalize().into())
            };
            
            let current_height = inner.height;
            inner.tx_records.push(TxRecord {
                hash: tx_hash.clone(),
                tx_type: "block".to_string(),
                from: pubkey_hex.clone(), // Triggering validator
                to: None,
                amount: reward_per_validator * num_approvers,
                status: "confirmed".to_string(),
                timestamp: std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_secs(),
                height: current_height,
                validators: Some(approving_validators.clone()),
                challenge_hash: Some(hex::encode(challenge_hash)),
            });
            
            // Finalize block
            let prev_root = inner.state_root;
            inner.height += 1;
            
            // Compute new state root (includes validator commitment for balance verification)
            let val_commitment = validator_set_hash(&inner.validators);
            let new_state_root = compute_state_root_hash(
                &prev_root,
                inner.height,
                inner.total_supply,
                challenge_hash,
                &val_commitment,
            );
            inner.state_root = new_state_root;
            
            // Clear challenge and committee
            inner.current_challenge = None;
            inner.current_committee = None;
            
            // Clean up old verdict records (only keep last 10 blocks to prevent memory growth)
            let current_height = inner.height;
            inner.submitted_verdicts.retain(|&(h, _), _| h + 10 > current_height);
            
            // Prune tx_records to prevent unbounded memory growth (keep last 10000)
            const MAX_TX_RECORDS: usize = 10_000;
            if inner.tx_records.len() > MAX_TX_RECORDS {
                let drain_count = inner.tx_records.len() - MAX_TX_RECORDS;
                inner.tx_records.drain(..drain_count);
            }
            
            tracing::info!(
                "📦 Block {} FINALIZED! {} validators approved, {} SMITH distributed",
                inner.height,
                num_approvers,
                reward_per_validator * num_approvers
            );
            tracing::info!(
                "🔗 New state root: {}",
                &hex::encode(&new_state_root)[..32]
            );
            
            // Return BlockFinalized so RPC can broadcast over P2P
            let new_balance = inner.validators.get(&pubkey_hex).map(|v| v.balance).unwrap_or(0);
            let finalized_height = inner.height;
            TxResult::BlockFinalized {
                reward: reward_per_validator,
                new_balance,
                block_height: finalized_height,
                state_root: new_state_root,
            }
        } else {
            // Proof accepted but block not yet finalized (waiting for more committee votes)
            let new_balance = inner.validators.get(&pubkey_hex).map(|v| v.balance).unwrap_or(0);
            
            tracing::info!(
                "⏳ Proof accepted from {}..., waiting for threshold ({}/{})",
                &pubkey_hex[..16],
                committee_approvals,
                committee_threshold
            );
            
            // Return 0 reward for now - reward distributed when block finalizes
            TxResult::Success {
                reward: 0,
                new_balance,
            }
        }
    }

    /// Process a token transfer
    fn process_transfer(
        &self,
        from: &[u8; 32],
        to: &[u8; 32],
        amount: u64,
        nonce: u64,
        signature: &[u8; 64],
    ) -> TxResult {
        let mut inner = self.inner.write_or_recover();
        
        let from_hex = hex::encode(from);
        let to_hex = hex::encode(to);
        
        // Verify sender has enough balance
        let sender = match inner.validators.get(&from_hex) {
            Some(v) => v.clone(),
            None => return TxResult::Error("Sender not found".into()),
        };
        
        if sender.balance < amount {
            return TxResult::Error("Insufficient balance".into());
        }
        
        // Verify nonce to prevent replay attacks
        if nonce != sender.nonce {
            return TxResult::Error(format!(
                "Invalid nonce: expected {}, got {}",
                sender.nonce, nonce
            ));
        }
        
        // Verify signature
        let verifying_key = match VerifyingKey::from_bytes(from) {
            Ok(k) => k,
            Err(_) => return TxResult::Error("Invalid sender public key".into()),
        };
        
        // Message is: to || amount || nonce (prevents replay)
        let mut message = Vec::new();
        message.extend_from_slice(to);
        message.extend_from_slice(&amount.to_le_bytes());
        message.extend_from_slice(&nonce.to_le_bytes());
        
        // Signature::from_bytes doesn't return Result in ed25519-dalek 2.x
        let sig = Signature::from_bytes(signature);
        
        if verifying_key.verify(&message, &sig).is_err() {
            return TxResult::Error("Transfer signature verification failed".into());
        }
        
        // Execute transfer and increment nonce
        let sender_mut = inner.validators.get_mut(&from_hex).unwrap();
        sender_mut.balance -= amount;
        sender_mut.nonce += 1; // Increment nonce to prevent replay
        
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        
        let recipient = inner.validators
            .entry(to_hex.clone())
            .or_insert_with(|| ValidatorInfo {
                public_key: *to,
                balance: 0,
                validations_count: 0,
                reputation_score: 50,
                last_validation_height: 0,
                last_active_timestamp: now,
                is_online: false, // Recipient not necessarily online
                nonce: 0,
            });
        recipient.balance += amount;
        
        let new_balance = recipient.balance;
        let height = inner.height;
        
        // Record the transaction
        let tx_hash = {
            let mut hasher = Sha256::new();
            hasher.update(b"transfer");
            hasher.update(from);
            hasher.update(to);
            hasher.update(&amount.to_le_bytes());
            hasher.update(&nonce.to_le_bytes()); // M3: include nonce for unique hashes
            hex::encode::<[u8; 32]>(hasher.finalize().into())
        };
        
        inner.tx_records.push(TxRecord {
            hash: tx_hash,
            tx_type: "transfer".to_string(),
            from: from_hex,
            to: Some(to_hex),
            amount,
            status: "confirmed".to_string(),
            timestamp: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_secs(),
            height,
            validators: None,
            challenge_hash: None,
        });
        
        TxResult::Success {
            reward: 0,
            new_balance,
        }
    }

    /// Register a new validator
    fn register_validator(&self, public_key: &[u8; 32]) -> TxResult {
        // Rate limiting is enforced per-key in the RPC layer (not here)
        // to avoid a global counter that attackers could exhaust to block legitimate users
        
        // Verify the public key is a valid ed25519 point
        if ed25519_dalek::VerifyingKey::from_bytes(public_key).is_err() {
            return TxResult::Error("Invalid ed25519 public key".into());
        }
        
        let mut inner = self.inner.write_or_recover();
        
        let pubkey_hex = hex::encode(public_key);
        
        if inner.validators.contains_key(&pubkey_hex) {
            return TxResult::Error("Validator already registered".into());
        }
        
        // M3 fix: Enforce max_validators cap to prevent unbounded registration/minting
        let max_validators = inner.governance.params.max_validators as usize;
        if inner.validators.len() >= max_validators {
            return TxResult::Error(format!("Maximum validator count ({}) reached", max_validators));
        }
        
        // Initial funding for new validators
        const INITIAL_VALIDATOR_BALANCE: u64 = 100;
        
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        
        inner.validators.insert(pubkey_hex.clone(), ValidatorInfo {
            public_key: *public_key,
            balance: INITIAL_VALIDATOR_BALANCE,
            validations_count: 0,
            reputation_score: 50, // Start with neutral reputation
            last_validation_height: 0,
            last_active_timestamp: now,
            is_online: true, // New registrations are considered online
            nonce: 0,
        });
        
        // Update total supply
        inner.total_supply += INITIAL_VALIDATOR_BALANCE;
        
        let height = inner.height;
        
        // Record the registration
        let tx_hash = {
            let mut hasher = Sha256::new();
            hasher.update(b"register");
            hasher.update(public_key);
            hex::encode::<[u8; 32]>(hasher.finalize().into())
        };
        
        inner.tx_records.push(TxRecord {
            hash: tx_hash,
            tx_type: "register".to_string(),
            from: pubkey_hex.clone(),
            to: None,
            amount: INITIAL_VALIDATOR_BALANCE,
            status: "confirmed".to_string(),
            timestamp: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_secs(),
            height,
            validators: None,
            challenge_hash: None,
        });
        
        tracing::info!("📝 New validator registered: {}... (funded with {} SMITH)", &pubkey_hex[..16], INITIAL_VALIDATOR_BALANCE);
        
        TxResult::Registered {
            public_key: pubkey_hex,
        }
    }

    /// Get validator info by public key
    pub fn get_validator(&self, pubkey_hex: &str) -> Option<ValidatorInfo> {
        self.inner.read_or_recover().validators.get(pubkey_hex).cloned()
    }

    // ============ SLASHING SYSTEM ============

    /// Slash a validator for malicious behavior
    /// Returns the amount slashed, burns tokens from total supply
    pub fn slash_validator(&self, pubkey_hex: &str, amount: u64, reason: &str) -> Result<u64, String> {
        let mut inner = self.inner.write_or_recover();
        
        let validator = inner.validators.get_mut(pubkey_hex)
            .ok_or_else(|| format!("Validator {} not found", pubkey_hex))?;
        
        // Calculate actual slash amount (can't slash more than balance)
        let slash_amount = amount.min(validator.balance);
        
        // Apply slash
        validator.balance -= slash_amount;
        validator.reputation_score = validator.reputation_score.saturating_sub(50);
        
        // Burn slashed tokens (reduce total supply)
        inner.total_supply -= slash_amount;
        
        let height = inner.height;
        
        // Record the slash transaction
        let tx_hash = {
            let mut hasher = Sha256::new();
            hasher.update(b"slash");
            hasher.update(pubkey_hex.as_bytes());
            hasher.update(&slash_amount.to_le_bytes());
            hasher.update(&height.to_le_bytes());
            hex::encode::<[u8; 32]>(hasher.finalize().into())
        };
        
        inner.tx_records.push(TxRecord {
            hash: tx_hash,
            tx_type: "slash".to_string(),
            from: pubkey_hex.to_string(),
            to: None,
            amount: slash_amount,
            status: format!("slashed: {}", reason),
            timestamp: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_secs(),
            height,
            validators: None,
            challenge_hash: None,
        });
        
        tracing::warn!(
            "⚡ SLASHED validator {}... for {} SMITH: {}",
            &pubkey_hex[..16.min(pubkey_hex.len())],
            slash_amount,
            reason
        );
        
        Ok(slash_amount)
    }

    /// Slash validator for missing committee duty (10 SMITH)
    pub fn slash_for_committee_absence(&self, pubkey_hex: &str) -> Result<u64, String> {
        self.slash_validator(pubkey_hex, 10, "committee absence")
    }

    /// Slash validator for submitting invalid proof (25 SMITH)
    pub fn slash_for_invalid_proof(&self, pubkey_hex: &str) -> Result<u64, String> {
        self.slash_validator(pubkey_hex, 25, "invalid proof")
    }

    /// Slash validator for equivocation/double voting (50 SMITH)
    /// Used when a validator submits conflicting proofs for the same block
    pub fn slash_for_equivocation(&self, pubkey_hex: &str) -> Result<u64, String> {
        self.slash_validator(pubkey_hex, 50, "equivocation")
    }

    // ============ END SLASHING SYSTEM ============

    /// Get tx_records for P2P state sync (limit to last 1000 for bandwidth)
    pub fn get_tx_records_for_sync(&self) -> Vec<TxRecord> {
        let inner = self.inner.read_or_recover();
        // Return last 1000 transactions for sync
        let len = inner.tx_records.len();
        let start = len.saturating_sub(1000);
        inner.tx_records[start..].to_vec()
    }

    /// Merge tx_records from peer (for state sync)
    pub fn merge_tx_records(&self, peer_records: Vec<TxRecord>) {
        let mut inner = self.inner.write_or_recover();
        
        // Build set of existing hashes for dedup
        let existing_hashes: std::collections::HashSet<_> = 
            inner.tx_records.iter().map(|tx| tx.hash.clone()).collect();
        
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        
        // Add new records that we don't have, with basic validation
        let mut new_count = 0;
        for record in peer_records {
            // Skip records with empty hashes (invalid)
            if record.hash.is_empty() {
                continue;
            }
            // Skip records with unreasonable timestamps (> 1 day in future)
            if record.timestamp > now + 86400 {
                continue;
            }
            if !existing_hashes.contains(&record.hash) {
                inner.tx_records.push(record);
                new_count += 1;
            }
        }
        
        if new_count > 0 {
            // Sort by height to maintain order
            inner.tx_records.sort_by_key(|tx| tx.height);
            // Cap total records to prevent unbounded growth from merges
            const MAX_MERGED_TX_RECORDS: usize = 10_000;
            if inner.tx_records.len() > MAX_MERGED_TX_RECORDS {
                let excess = inner.tx_records.len() - MAX_MERGED_TX_RECORDS;
                inner.tx_records.drain(..excess);
            }
            tracing::info!("📥 Merged {} new transactions from peer", new_count);
        }
    }

    /// Get a transaction by its hash
    pub fn get_transaction_by_hash(&self, hash: &str) -> Option<TxRecord> {
        let inner = self.inner.read_or_recover();
        inner.tx_records.iter().find(|tx| tx.hash == hash).cloned()
    }

    /// Get transactions with pagination (page is 1-indexed) and optional type filter
    pub fn get_transactions_paginated(&self, page: usize, per_page: usize, tx_type: Option<String>) -> (Vec<TxRecord>, usize) {
        let inner = self.inner.read_or_recover();
        
        // Filter by type if specified (skip if "all" or empty)
        let filtered: Vec<&TxRecord> = if let Some(ref filter_type) = tx_type {
            if filter_type == "all" || filter_type.is_empty() {
                inner.tx_records.iter().collect()
            } else {
                inner.tx_records
                    .iter()
                    .filter(|tx| &tx.tx_type == filter_type)
                    .collect()
            }
        } else {
            inner.tx_records.iter().collect()
        };
        
        let total = filtered.len();
        let offset = (page - 1) * per_page;
        
        // Get transactions in reverse order (newest first) with pagination
        let transactions: Vec<TxRecord> = filtered
            .into_iter()
            .rev()
            .skip(offset)
            .take(per_page)
            .cloned()
            .collect();
        
        (transactions, total)
    }

    /// Get current block height
    pub fn get_height(&self) -> u64 {
        self.inner.read_or_recover().height
    }

    /// Reset state for chain restart (when sequencer has been reset)
    /// This clears all local state and adopts the new genesis_hash from the sequencer
    pub fn reset_for_chain_restart(&self, new_genesis_hash: [u8; 32]) {
        let mut inner = self.inner.write_or_recover();
        
        // Clear all in-memory state
        inner.height = 0;
        inner.state_root = [0u8; 32];
        inner.total_supply = 0;
        inner.validators.clear();
        inner.current_challenge = None;
        inner.current_committee = None;
        inner.tx_records.clear();
        inner.pending_txs.clear();
        inner.submitted_verdicts.clear();
        inner.governance = GovernanceState::default();
        
        // Adopt the new genesis_hash from the sequencer
        inner.genesis_hash = new_genesis_hash;
        
        // CRITICAL: Also reset the state.json and WAL files so restarts don't reload old state
        drop(inner); // Release the lock before file operations
        
        // Reset state.json to empty genesis (overwrite, not delete - safer for sandboxed envs)
        if let Err(e) = self.storage.reset_state_file() {
            tracing::warn!("⚠️ Failed to reset state file during chain reset: {}", e);
        }
        
        // Truncate WAL
        self.storage.wal_truncate();
        
        // Save immediately to persist the new genesis_hash
        if let Err(e) = self.save() {
            tracing::warn!("⚠️ Failed to save state after chain reset: {}", e);
        }
        
        tracing::info!("🔄 State reset for chain restart - adopted new genesis {}", hex::encode(&new_genesis_hash[..8]));
    }

    /// Get state root
    pub fn get_state_root(&self) -> [u8; 32] {
        self.inner.read_or_recover().state_root
    }

    /// Get total supply
    pub fn get_total_supply(&self) -> u64 {
        self.inner.read_or_recover().total_supply
    }

    /// Get all validators
    pub fn get_all_validators(&self) -> Vec<ValidatorInfo> {
        self.inner.read_or_recover().validators.values().cloned().collect()
    }
    
    /// Get count of active validators (online in last 90 seconds via P2P presence)
    pub fn get_active_validator_count(&self) -> usize {
        let inner = self.inner.read_or_recover();
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        
        inner.validators.values()
            .filter(|v| now - v.last_active_timestamp < ACTIVE_THRESHOLD_SECS)
            .count()
    }
    
    /// Update validator presence from P2P heartbeat
    /// This is called when we receive a presence message over gossipsub
    pub fn update_validator_presence(&self, pubkey_hex: &str, timestamp: u64, _height: u64) {
        let mut inner = self.inner.write_or_recover();
        
        if let Some(validator) = inner.validators.get_mut(pubkey_hex) {
            // Only update if this is a newer timestamp
            if timestamp > validator.last_active_timestamp {
                validator.last_active_timestamp = timestamp;
                validator.is_online = true;
            }
        }
        // Note: We don't create new validators from presence messages
        // They must register first via the RPC
    }

    /// Set the current challenge (used when receiving from P2P)
    pub fn set_current_challenge(&self, challenge: CognitiveChallenge) {
        let mut inner = self.inner.write_or_recover();
        inner.current_challenge = Some(challenge);
    }

    /// Verify and apply a proof from P2P network
    pub fn verify_and_apply_proof(&self, response: &super::challenge::ChallengeResponse) -> Result<TxResult, String> {
        // Parse hex strings to bytes
        let validator_pubkey: [u8; 32] = hex::decode(&response.validator_pubkey)
            .map_err(|e| format!("Invalid validator pubkey hex: {}", e))?
            .try_into()
            .map_err(|_| "Invalid validator pubkey length")?;
        
        let challenge_hash: [u8; 32] = hex::decode(&response.challenge_hash)
            .map_err(|e| format!("Invalid challenge hash hex: {}", e))?
            .try_into()
            .map_err(|_| "Invalid challenge hash length")?;
        
        let signature: [u8; 64] = hex::decode(&response.signature)
            .map_err(|e| format!("Invalid signature hex: {}", e))?
            .try_into()
            .map_err(|_| "Invalid signature length")?;
        
        let verdict_digest: [u8; 32] = hex::decode(&response.verdict_digest)
            .map_err(|e| format!("Invalid verdict digest hex: {}", e))?
            .try_into()
            .map_err(|_| "Invalid verdict digest length")?;
        
        // Apply the proof submission
        let tx = NodeTx::SubmitProof {
            validator_pubkey,
            challenge_hash,
            signature,
            verdict_digest,
            puzzle_answer: response.puzzle_answer.clone(),
        };
        
        match self.apply_tx(tx) {
            TxResult::Error(e) => Err(e),
            result => Ok(result),
        }
    }

    /// Apply a block header received from P2P
    pub fn apply_block(&self, header: &BlockHeader) -> Result<(), String> {
        let mut inner = self.inner.write_or_recover();
        
        // Verify block height is sequential
        if header.height != inner.height + 1 && header.height != inner.height {
            return Err(format!(
                "Block height mismatch: expected {} or {}, got {}",
                inner.height,
                inner.height + 1,
                header.height
            ));
        }
        
        // Apply block
        inner.height = header.height;
        
        // H3: Compute new state root from block data (includes validator commitment)
        let val_commitment = validator_set_hash(&inner.validators);
        let new_state_root = compute_state_root_hash(
            &header.prev_state_root,
            header.height,
            inner.total_supply,
            &header.challenge_hash,
            &val_commitment,
        );
        inner.state_root = new_state_root;
        inner.current_challenge = None;
        
        // Clear pending txs (already recorded in tx_records)
        inner.pending_txs.clear();
        
        Ok(())
    }
    
    /// Apply a block received from a P2P peer, including full state snapshot.
    /// The block producer is authoritative — they ran the actual STF transitions,
    /// so we adopt their state (validators, balances, supply) along with the block.
    pub fn apply_block_with_state(
        &self,
        header: &BlockHeader,
        total_supply: u64,
        validators: &[ValidatorInfo],
    ) -> Result<(), String> {
        let mut inner = self.inner.write_or_recover();
        
        // Accept blocks that advance our chain
        if header.height <= inner.height {
            return Err(format!(
                "Block height {} is not newer than our height {}",
                header.height, inner.height
            ));
        }
        if header.height > inner.height + 1 {
            tracing::info!(
                "🔄 Catching up: jumping from height {} → {} (skipping {} blocks)",
                inner.height, header.height, header.height - inner.height - 1
            );
        }
        
        // Apply block height
        inner.height = header.height;
        
        // Adopt the producer's total supply (reflects rewards distributed)
        inner.total_supply = total_supply;
        
        // Merge validator state from producer (preserving higher nonces for replay protection)
        let existing_nonces: std::collections::HashMap<String, u64> = inner.validators.iter()
            .map(|(k, v)| (k.clone(), v.nonce))
            .collect();
        
        inner.validators.clear();
        for v in validators {
            let pubkey_hex = hex::encode(&v.public_key);
            let mut validator = v.clone();
            // Preserve higher nonce to prevent replay attacks
            if let Some(&existing_nonce) = existing_nonces.get(&pubkey_hex) {
                if existing_nonce > validator.nonce {
                    validator.nonce = existing_nonce;
                }
            }
            inner.validators.insert(pubkey_hex, validator);
        }
        
        // Compute new state root from block data (includes validator commitment for balance verification)
        let val_commitment = validator_set_hash(&inner.validators);
        let new_state_root = compute_state_root_hash(
            &header.prev_state_root,
            header.height,
            inner.total_supply,
            &header.challenge_hash,
            &val_commitment,
        );
        inner.state_root = new_state_root;
        
        // Clear current challenge (it was finalized)
        inner.current_challenge = None;
        inner.current_committee = None;
        
        // Clear pending txs (already recorded in tx_records)
        inner.pending_txs.clear();
        
        tracing::info!("🔄 Block {} applied with full state: {} validators, {} total supply, root: {}...",
            header.height, inner.validators.len(), inner.total_supply, &hex::encode(new_state_root)[..16]);
        
        Ok(())
    }

    /// Get number of pending proofs (for block message)
    pub fn get_pending_proof_count(&self) -> u64 {
        let inner = self.inner.read_or_recover();
        inner.pending_txs.iter()
            .filter(|tx| matches!(tx, NodeTx::SubmitProof { .. }))
            .count() as u64
    }
    
    // ============ GOVERNANCE SYSTEM ============
    
    /// Process create proposal transaction
    fn process_create_proposal(
        &self,
        proposer: &[u8; 32],
        proposal_type: u8,
        new_value: u64,
        description_hash: &[u8; 32],
        signature: &[u8; 64],
    ) -> TxResult {
        let proposer_hex = hex::encode(proposer);
        
        // Verify signature first (before acquiring write lock)
        let verifying_key = match VerifyingKey::from_bytes(proposer) {
            Ok(k) => k,
            Err(_) => return TxResult::Error("Invalid proposer public key".to_string()),
        };
        
        // Message: proposal_type || new_value || description_hash
        let mut message = Vec::with_capacity(41);
        message.push(proposal_type);
        message.extend_from_slice(&new_value.to_le_bytes());
        message.extend_from_slice(description_hash);
        
        let sig = Signature::from_bytes(signature);
        if verifying_key.verify(&message, &sig).is_err() {
            return TxResult::Error("Invalid proposal signature".to_string());
        }
        
        let mut inner = self.inner.write_or_recover();
        
        // Verify proposer is a registered validator with sufficient stake
        let min_stake = inner.governance.params.min_validator_stake;
        match inner.validators.get(&proposer_hex) {
            Some(v) if v.balance >= min_stake => {}, // OK
            Some(v) => return TxResult::Error(format!(
                "Insufficient stake to propose: {} < {} required", 
                v.balance, min_stake
            )),
            None => return TxResult::Error("Proposer is not a registered validator".to_string()),
        }
        
        // Convert proposal type byte to ProposalType
        let prop_type = match proposal_type {
            0 => ProposalType::ChangeReward { new_value },
            1 => ProposalType::ChangeCommitteeSize { new_value: new_value as usize },
            2 => ProposalType::ChangeMinStake { new_value },
            3 => ProposalType::ChangeSlashPenalty { new_value: new_value as u8 },
            4 => ProposalType::ChangeAIRateLimit { new_value },
            5 => ProposalType::ChangeMaxValidators { new_value: new_value as usize },
            _ => return TxResult::Error("Invalid proposal type".to_string()),
        };
        
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        
        let description = prop_type.description();
        let current_height = inner.height;
        
        match inner.governance.create_proposal(
            proposer_hex.clone(),
            prop_type,
            description,
            now,
            current_height,
        ) {
            Ok(id) => {
                // Generate tx hash for proposal creation
                let tx_hash = {
                    let mut hasher = Sha256::new();
                    hasher.update(b"create_proposal");
                    hasher.update(proposer);
                    hasher.update(&id.to_le_bytes());
                    hasher.update(&now.to_le_bytes());
                    hex::encode::<[u8; 32]>(hasher.finalize().into())
                };
                
                // Store tx_hash on the proposal
                if let Some(p) = inner.governance.get_proposal_mut(id) {
                    p.tx_hash = Some(tx_hash.clone());
                }
                
                // Create TxRecord for the proposal
                inner.tx_records.push(TxRecord {
                    hash: tx_hash,
                    tx_type: "governance_propose".to_string(),
                    from: proposer_hex,
                    to: None,
                    amount: 0,
                    status: format!("proposal #{} created", id),
                    timestamp: now,
                    height: current_height,
                    validators: None,
                    challenge_hash: None,
                });
                
                tracing::info!("📋 New governance proposal #{} created", id);
                TxResult::ProposalCreated { proposal_id: id }
            }
            Err(e) => TxResult::Error(e),
        }
    }
    
    /// Process vote on proposal
    fn process_vote_proposal(
        &self,
        voter: &[u8; 32],
        proposal_id: u64,
        vote: bool,
        signature: &[u8; 64],
        reason: Option<&str>,
    ) -> TxResult {
        let voter_hex = hex::encode(voter);
        
        // Verify signature first (before acquiring write lock)
        let verifying_key = match VerifyingKey::from_bytes(voter) {
            Ok(k) => k,
            Err(_) => return TxResult::Error("Invalid voter public key".to_string()),
        };
        
        // Message: proposal_id || vote
        let mut message = Vec::with_capacity(9);
        message.extend_from_slice(&proposal_id.to_le_bytes());
        message.push(if vote { 1 } else { 0 });
        
        let sig = Signature::from_bytes(signature);
        if verifying_key.verify(&message, &sig).is_err() {
            return TxResult::Error("Invalid vote signature".to_string());
        }
        
        let mut inner = self.inner.write_or_recover();
        
        // Get voter's stake weight (must have non-zero balance to vote)
        let stake_weight = match inner.validators.get(&voter_hex) {
            Some(v) if v.balance > 0 => v.balance,
            Some(_) => return TxResult::Error("Voter has no stake".to_string()),
            None => return TxResult::Error("Voter is not a registered validator".to_string()),
        };
        
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        
        // Log AI reasoning if provided
        if let Some(r) = reason {
            let vote_str = if vote { "YES" } else { "NO" };
            tracing::info!("🧠 AI vote reasoning on proposal #{}: {} votes {} — {}", 
                proposal_id, &voter_hex[..16], vote_str, r);
        }
        
        let mut vote_record = Vote {
            voter: voter_hex,
            vote,
            stake_weight,
            timestamp: now,
            signature: hex::encode(signature),
            reason: reason.map(|s| s.to_string()),
            tx_hash: None,
        };
        
        // Calculate total stake before borrowing governance
        let total_stake: u64 = inner.validators.values().map(|v| v.balance).sum();
        
        // Generate tx hash for the vote
        let vote_tx_hash = {
            let mut hasher = Sha256::new();
            hasher.update(b"vote_proposal");
            hasher.update(voter);
            hasher.update(&proposal_id.to_le_bytes());
            hasher.update(&[if vote { 1 } else { 0 }]);
            hasher.update(&now.to_le_bytes());
            hex::encode::<[u8; 32]>(hasher.finalize().into())
        };
        
        // Set tx_hash on the vote record
        vote_record.tx_hash = Some(vote_tx_hash.clone());
        
        let voter_hex_for_record = vote_record.voter.clone();
        
        // Add vote to proposal
        match inner.governance.get_proposal_mut(proposal_id) {
            Some(proposal) => {
                match proposal.add_vote(vote_record) {
                    Ok(_) => {
                        let current_height = inner.height;
                        
                        // Create TxRecord for the vote
                        inner.tx_records.push(TxRecord {
                            hash: vote_tx_hash,
                            tx_type: "governance_vote".to_string(),
                            from: voter_hex_for_record,
                            to: None,
                            amount: 0,
                            status: format!("voted {} on proposal #{}", if vote { "FOR" } else { "AGAINST" }, proposal_id),
                            timestamp: now,
                            height: current_height,
                            validators: None,
                            challenge_hash: None,
                        });
                        
                        tracing::info!("🗳️ Vote recorded on proposal #{} (evaluated at voting period end)", proposal_id);
                        TxResult::VoteRecorded { proposal_id, vote }
                    }
                    Err(e) => TxResult::Error(e),
                }
            }
            None => TxResult::Error("Proposal not found".to_string()),
        }
    }
    
    /// Process execute proposal (after passing + delay)
    fn process_execute_proposal(
        &self,
        executor: &[u8; 32],
        proposal_id: u64,
        signature: &[u8; 64],
    ) -> TxResult {
        let executor_hex = hex::encode(executor);
        
        // Verify signature first (before acquiring write lock)
        let verifying_key = match VerifyingKey::from_bytes(executor) {
            Ok(k) => k,
            Err(_) => return TxResult::Error("Invalid executor public key".to_string()),
        };
        
        // Message: proposal_id
        let message = proposal_id.to_le_bytes();
        
        let sig = Signature::from_bytes(signature);
        if verifying_key.verify(&message, &sig).is_err() {
            return TxResult::Error("Invalid execute signature".to_string());
        }
        
        let mut inner = self.inner.write_or_recover();
        
        // Verify executor is a validator (anyone can execute, but must be validator)
        if !inner.validators.contains_key(&executor_hex) {
            return TxResult::Error("Executor is not a registered validator".to_string());
        }
        
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        
        let current_height = inner.height;
        
        match inner.governance.execute_proposal(proposal_id, now, current_height) {
            Ok(_) => {
                let param_info = inner.governance.param_history.last()
                    .map(|p| (p.param_name.clone(), p.old_value.clone(), p.new_value.clone()))
                    .unwrap_or_default();
                
                // Generate tx hash for execution
                let exec_tx_hash = {
                    let mut hasher = Sha256::new();
                    hasher.update(b"execute_proposal");
                    hasher.update(executor);
                    hasher.update(&proposal_id.to_le_bytes());
                    hasher.update(&now.to_le_bytes());
                    hex::encode::<[u8; 32]>(hasher.finalize().into())
                };
                
                // Store execution tx_hash on the proposal
                if let Some(p) = inner.governance.get_proposal_mut(proposal_id) {
                    p.execution_tx_hash = Some(exec_tx_hash.clone());
                }
                
                // Create TxRecord for the execution
                inner.tx_records.push(TxRecord {
                    hash: exec_tx_hash,
                    tx_type: "governance_execute".to_string(),
                    from: executor_hex,
                    to: None,
                    amount: 0,
                    status: format!("executed proposal #{}: {} → {}", proposal_id, param_info.0, param_info.2),
                    timestamp: now,
                    height: current_height,
                    validators: None,
                    challenge_hash: None,
                });
                
                tracing::info!("✅ Proposal #{} executed: {}", proposal_id, param_info.0);
                TxResult::ProposalExecuted { 
                    proposal_id, 
                    param_changed: param_info.0,
                }
            }
            Err(e) => TxResult::Error(e),
        }
    }
    
    /// Get governance state summary for AI context
    pub fn get_governance_summary(&self) -> String {
        let inner = self.inner.read_or_recover();
        inner.governance.state_summary(
            inner.validators.len(),
            inner.height,
            inner.total_supply,
        )
    }
    
    /// Get all active proposals
    pub fn get_active_proposals(&self) -> Vec<super::governance::Proposal> {
        let inner = self.inner.read_or_recover();
        inner.governance.proposals.iter()
            .filter(|p| p.status == ProposalStatus::Active || p.status == ProposalStatus::Passed)
            .cloned()
            .collect()
    }
    
    /// Get all governance proposals (M2 fix: needed for RPC endpoint)
    pub fn get_governance_proposals(&self) -> Vec<super::governance::Proposal> {
        let inner = self.inner.read_or_recover();
        inner.governance.proposals.clone()
    }
    
    /// Get proposal by ID
    pub fn get_proposal(&self, id: u64) -> Option<super::governance::Proposal> {
        let inner = self.inner.read_or_recover();
        inner.governance.get_proposal(id).cloned()
    }
    
    /// Get current network parameters
    pub fn get_network_params(&self) -> super::governance::NetworkParams {
        let inner = self.inner.read_or_recover();
        inner.governance.params.clone()
    }
    
    /// Tick governance: expire stale proposals + auto-execute passed ones
    /// Also finalizes any expired challenges with partial approvals
    pub fn tick_governance(&self) {
        // Finalize any expired challenge before governance tick
        self.finalize_expired_challenge();
        
        let mut inner = self.inner.write_or_recover();
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        // Use active validator stake for quorum, not total_supply.
        // Using total_supply (which includes offline validators) makes it impossible
        // to reach quorum when most validators are offline.
        let active_stake: u64 = inner.validators.values()
            .filter(|v| now.saturating_sub(v.last_active_timestamp) <= ACTIVE_THRESHOLD_SECS)
            .map(|v| v.balance)
            .sum();
        // Fall back to total supply if no active validators (prevents division by zero in quorum)
        let quorum_stake = if active_stake > 0 { active_stake } else { inner.total_supply };
        let height = inner.height;
        let auto_executed = inner.governance.tick(now, quorum_stake, height);
        
        // Create TxRecords for auto-executed proposals
        for (proposal_id, param_name, old_value, new_value) in auto_executed {
            let exec_tx_hash = inner.governance.get_proposal(proposal_id)
                .and_then(|p| p.execution_tx_hash.clone())
                .unwrap_or_else(|| {
                    let mut hasher = Sha256::new();
                    hasher.update(b"auto_execute_fallback");
                    hasher.update(&proposal_id.to_le_bytes());
                    hasher.update(&now.to_le_bytes());
                    hex::encode::<[u8; 32]>(hasher.finalize().into())
                });
            
            inner.tx_records.push(TxRecord {
                hash: exec_tx_hash,
                tx_type: "governance_execute".to_string(),
                from: "auto".to_string(),
                to: None,
                amount: 0,
                status: format!("auto-executed proposal #{}: {} {} → {}", proposal_id, param_name, old_value, new_value),
                timestamp: now,
                height,
                validators: None,
                challenge_hash: None,
            });
        }
    }
    
    // ============ END GOVERNANCE SYSTEM ============
}

/// Result of proof verification
pub struct ProofResult {
    pub reward: u64,
}

impl Default for SmithNodeState {
    fn default() -> Self {
        Self::new()
    }
}
