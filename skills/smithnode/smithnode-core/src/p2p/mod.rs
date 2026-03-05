//! P2P Network Layer for SmithNode
//!
//! Uses libp2p for decentralized gossipsub-based networking.
//! Validators gossip challenges and proofs across the network.

use libp2p::{
    futures::StreamExt,
    gossipsub::{self, IdentTopic, MessageAuthenticity},
    mdns,
    noise,
    swarm::{NetworkBehaviour, SwarmEvent},
    tcp, yamux, Multiaddr, PeerId, Swarm,
};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use sha2::{Sha256, Digest};
use std::sync::{Arc, RwLock, RwLockReadGuard, RwLockWriteGuard};
use std::time::Duration;
use tokio::sync::mpsc;

use crate::stf::{SmithNodeState, CognitiveChallenge, ChallengeResponse, BlockHeader};

/// Current node version - used for P2P compatibility checks
pub const SMITH_VERSION: &str = env!("CARGO_PKG_VERSION");

/// Extension trait that recovers from poisoned RwLocks gracefully.
trait PoisonRecover<T> {
    fn read_or_recover(&self) -> RwLockReadGuard<'_, T>;
    fn write_or_recover(&self) -> RwLockWriteGuard<'_, T>;
}

impl<T> PoisonRecover<T> for RwLock<T> {
    fn read_or_recover(&self) -> RwLockReadGuard<'_, T> {
        self.read().unwrap_or_else(|poisoned| {
            tracing::error!("🚨 P2P RwLock was poisoned (read) — recovering but data may be inconsistent");
            poisoned.into_inner()
        })
    }
    fn write_or_recover(&self) -> RwLockWriteGuard<'_, T> {
        self.write().unwrap_or_else(|poisoned| {
            tracing::error!("🚨 P2P RwLock was poisoned (write) — recovering but data may be inconsistent");
            poisoned.into_inner()
        })
    }
}

/// Topics for gossipsub
const TOPIC_CHALLENGES: &str = "smithnode/challenges/1.0.0";
const TOPIC_PROOFS: &str = "smithnode/proofs/1.0.0";
const TOPIC_BLOCKS: &str = "smithnode/blocks/1.0.0";
const TOPIC_STATE_SYNC: &str = "smithnode/state-sync/1.0.0";
const TOPIC_PRESENCE: &str = "smithnode/presence/1.0.0";
pub const TOPIC_UPGRADES: &str = "smithnode/upgrades/1.0.0";
const TOPIC_AI_MESSAGES: &str = "smithnode/ai-messages/1.0.0";
const TOPIC_TRANSACTIONS: &str = "smithnode/transactions/1.0.0";
const TOPIC_GOVERNANCE: &str = "smithnode/governance/1.0.0";
const TOPIC_PEER_RELAY: &str = "smithnode/peer-relay/1.0.0";

/// Trusted operator public keys for upgrade announcements
/// These are the ONLY keys that can announce valid upgrades
/// Format: hex-encoded Ed25519 public keys (32 bytes = 64 hex chars)
/// 
/// Loaded from Cargo.toml [package.metadata.smithnode] at compile time,
/// plus runtime sources:
///   1. SMITHNODE_OPERATOR_KEYS env var (comma-separated hex pubkeys)
///   2. Falls back to the node operator's own key (from node_key.json)

/// Get the list of trusted operator keys at runtime
fn get_trusted_operator_keys() -> Vec<String> {
    // Start with keys from Cargo.toml (baked in at compile time)
    let builtin_keys = env!("SMITHNODE_OPERATOR_KEYS_BUILTIN");
    let mut keys: Vec<String> = builtin_keys
        .split(',')
        .filter(|k| !k.is_empty())
        .map(|k| k.to_string())
        .collect();
    
    // Load from environment variable
    if let Ok(env_keys) = std::env::var("SMITHNODE_OPERATOR_KEYS") {
        for key in env_keys.split(',') {
            let key = key.trim().to_string();
            if key.len() == 64 && hex::decode(&key).is_ok() {
                if !keys.contains(&key) {
                    keys.push(key);
                }
            }
        }
    }
    
    // Load from node_key.json in data dir (the node operator trusts themselves)
    let data_dir = std::env::var("SMITHNODE_DATA_DIR")
        .unwrap_or_else(|_| ".smithnode-data".to_string());
    let node_key_path = std::path::Path::new(&data_dir).join("node_key.json");
    if let Ok(data) = std::fs::read_to_string(&node_key_path) {
        if let Ok(parsed) = serde_json::from_str::<serde_json::Value>(&data) {
            if let Some(pubkey) = parsed["public_key"].as_str() {
                let pubkey = pubkey.to_string();
                if pubkey.len() == 64 && !keys.contains(&pubkey) {
                    keys.push(pubkey);
                }
            }
        }
    }
    
    keys
}

/// Tracks validators that have been VERIFIED via P2P gossipsub
/// These are TRUE P2P validators, not just RPC agents
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct P2PValidatorInfo {
    pub public_key: String,
    pub peer_id: Option<String>,  // libp2p peer ID if known
    pub last_seen_timestamp: u64,
    pub last_height: u64,
    pub version: String,
    pub presence_count: u64,      // Number of valid presence messages received
    pub first_seen: u64,
}

/// Global tracker for P2P-verified validators
#[derive(Clone, Default)]
pub struct P2PValidatorTracker {
    /// Map of validator pubkey -> P2P info
    validators: Arc<RwLock<HashMap<String, P2PValidatorInfo>>>,
}

impl P2PValidatorTracker {
    pub fn new() -> Self {
        Self::default()
    }
    
    /// Record a validated presence message from P2P network
    pub fn record_presence(&self, presence: &PresenceMessage) {
        let mut validators = self.validators.write_or_recover();
        
        let entry = validators.entry(presence.validator_pubkey.clone()).or_insert_with(|| {
            P2PValidatorInfo {
                public_key: presence.validator_pubkey.clone(),
                peer_id: None,
                last_seen_timestamp: presence.timestamp,
                last_height: presence.height,
                version: presence.version.clone(),
                presence_count: 0,
                first_seen: presence.timestamp,
            }
        });
        
        entry.last_seen_timestamp = presence.timestamp;
        entry.last_height = presence.height;
        entry.version = presence.version.clone();
        entry.presence_count += 1;
    }
    
    /// Get all P2P-verified validators
    pub fn get_verified_validators(&self) -> Vec<P2PValidatorInfo> {
        let validators = self.validators.read_or_recover();
        validators.values().cloned().collect()
    }
    
    /// Check if a validator is P2P-verified (seen via gossipsub)
    pub fn is_p2p_verified(&self, pubkey: &str) -> bool {
        let validators = self.validators.read_or_recover();
        validators.contains_key(pubkey)
    }
    
    /// Get P2P-verified validators that are still online (seen in last 2 minutes)
    pub fn get_online_p2p_validators(&self) -> Vec<P2PValidatorInfo> {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        
        let validators = self.validators.read_or_recover();
        validators.values()
            .filter(|v| v.last_seen_timestamp > now.saturating_sub(120))
            .cloned()
            .collect()
    }
    
    /// Get count of P2P-verified validators
    pub fn count(&self) -> usize {
        self.validators.read_or_recover().len()
    }
}

/// Global P2P validator tracker instance
static P2P_VALIDATOR_TRACKER: std::sync::OnceLock<P2PValidatorTracker> = std::sync::OnceLock::new();

pub fn get_p2p_validator_tracker() -> &'static P2PValidatorTracker {
    P2P_VALIDATOR_TRACKER.get_or_init(P2PValidatorTracker::new)
}

/// AI Message storage
use crate::rpc::AIMessageRecord;
use std::collections::VecDeque;

struct AIMessageStore {
    /// Messages indexed by validator pubkey (both from and to)
    messages: RwLock<std::collections::HashMap<String, VecDeque<AIMessageRecord>>>,
    /// All messages in order
    all_messages: RwLock<VecDeque<AIMessageRecord>>,
}

impl AIMessageStore {
    fn new() -> Self {
        Self {
            messages: RwLock::new(std::collections::HashMap::new()),
            all_messages: RwLock::new(VecDeque::new()),
        }
    }
    
    fn store(&self, msg: AIMessageRecord) {
        // Store in all messages
        {
            let mut all = self.all_messages.write_or_recover();
            all.push_back(msg.clone());
            // Keep last 10000 messages
            while all.len() > 10000 {
                all.pop_front();
            }
        }
        
        // Index by sender
        {
            let mut by_validator = self.messages.write_or_recover();
            let from_msgs = by_validator.entry(msg.from.clone()).or_insert_with(VecDeque::new);
            from_msgs.push_back(msg.clone());
            while from_msgs.len() > 1000 {
                from_msgs.pop_front();
            }
        }
        
        // Index by recipient if not broadcast
        if msg.to != "broadcast" {
            let mut by_validator = self.messages.write_or_recover();
            let to_msgs = by_validator.entry(msg.to.clone()).or_insert_with(VecDeque::new);
            to_msgs.push_back(msg);
            while to_msgs.len() > 1000 {
                to_msgs.pop_front();
            }
        }
    }
    
    fn get_for_validator(&self, pubkey: &str, limit: usize) -> Vec<AIMessageRecord> {
        let by_validator = self.messages.read_or_recover();
        if let Some(msgs) = by_validator.get(pubkey) {
            msgs.iter().rev().take(limit).cloned().collect()
        } else {
            Vec::new()
        }
    }
    
    fn get_all(&self, limit: usize) -> Vec<AIMessageRecord> {
        let all = self.all_messages.read_or_recover();
        all.iter().rev().take(limit).cloned().collect()
    }
}

static AI_MESSAGE_STORE: std::sync::OnceLock<AIMessageStore> = std::sync::OnceLock::new();

fn get_ai_message_store() -> &'static AIMessageStore {
    AI_MESSAGE_STORE.get_or_init(AIMessageStore::new)
}

/// Store an AI message
pub fn store_ai_message(msg: AIMessageRecord) {
    get_ai_message_store().store(msg);
}

/// Get AI messages for a validator
pub fn get_ai_messages(pubkey: &str, limit: usize) -> Vec<AIMessageRecord> {
    if pubkey.is_empty() || pubkey == "all" {
        get_ai_message_store().get_all(limit)
    } else {
        get_ai_message_store().get_for_validator(pubkey, limit)
    }
}

/// Global peer info (set on network init)
static LOCAL_PEER_INFO: std::sync::OnceLock<PeerInfo> = std::sync::OnceLock::new();

#[derive(Clone, Debug)]
pub struct PeerInfo {
    pub peer_id: String,
    pub p2p_port: u16,
    /// Dynamically discovered external addresses
    pub external_addrs: Arc<RwLock<Vec<String>>>,
}

impl PeerInfo {
    /// Add an external address (called when swarm discovers it)
    pub fn add_external_addr(&self, addr: &str) {
        let mut addrs = self.external_addrs.write_or_recover();
        let full_addr = format!("{}/p2p/{}", addr, self.peer_id);
        if !addrs.contains(&full_addr) {
            addrs.push(full_addr);
        }
    }
    
    /// Get all known external addresses for this node
    pub fn get_multiaddrs(&self) -> Vec<String> {
        self.external_addrs.read_or_recover().clone()
    }
}

/// Get this node's peer info (peer ID and port)
pub fn get_local_peer_info() -> Option<&'static PeerInfo> {
    LOCAL_PEER_INFO.get()
}

/// Bootstrap peers - known peers that new nodes can connect to
/// These are set from TRUSTED_OPERATOR_KEYS peer IDs or discovered dynamically
static BOOTSTRAP_PEERS: std::sync::OnceLock<Arc<RwLock<Vec<String>>>> = std::sync::OnceLock::new();

pub fn get_bootstrap_peers() -> Vec<String> {
    BOOTSTRAP_PEERS.get()
        .map(|p| p.read_or_recover().clone())
        .unwrap_or_default()
}

pub fn add_bootstrap_peer(multiaddr: String) {
    let peers = BOOTSTRAP_PEERS.get_or_init(|| Arc::new(RwLock::new(Vec::new())));
    let mut list = peers.write_or_recover();
    if !list.contains(&multiaddr) {
        list.push(multiaddr);
    }
}

/// Release management: Tracks versions seen on the network AND verified upgrade announcements
#[derive(Clone, Default)]
pub struct VersionTracker {
    /// Map of version -> (count of peers, first seen timestamp)
    versions: Arc<RwLock<HashMap<String, (usize, u64)>>>,
    /// Newest version detected on the network
    newest_version: Arc<RwLock<Option<String>>>,
    /// Latest verified upgrade announcement from trusted operator
    latest_upgrade: Arc<RwLock<Option<UpgradeAnnouncement>>>,
}

impl VersionTracker {
    pub fn new() -> Self {
        Self::default()
    }
    
    /// Record a version seen from a peer
    pub fn record_version(&self, version: &str) {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        
        let mut versions = self.versions.write_or_recover();
        let entry = versions.entry(version.to_string()).or_insert((0, now));
        entry.0 += 1;
        
        // Update newest version if this one is newer
        let mut newest = self.newest_version.write_or_recover();
        let should_update = match newest.as_ref() {
            None => true,
            Some(current) => Self::compare_versions(version, current) == std::cmp::Ordering::Greater,
        };
        
        if should_update {
            *newest = Some(version.to_string());
            // Only warn if peer version is actually NEWER than our version
            if Self::compare_versions(version, SMITH_VERSION) == std::cmp::Ordering::Greater {
                tracing::warn!(
                    "🚀 Newer version {} detected on network! Current: {}",
                    version, SMITH_VERSION
                );
            }
        }
    }
    
    /// Record a verified upgrade announcement from trusted operator
    pub fn record_upgrade(&self, upgrade: UpgradeAnnouncement) {
        // Only accept if signature verifies AND from trusted operator
        if !upgrade.verify() {
            tracing::warn!("Rejecting invalid/untrusted upgrade announcement");
            return;
        }
        
        let mut latest = self.latest_upgrade.write_or_recover();
        let should_update = match latest.as_ref() {
            None => true,
            Some(current) => Self::compare_versions(&upgrade.version, &current.version) == std::cmp::Ordering::Greater,
        };
        
        if should_update {
            tracing::info!(
                "📦 VERIFIED upgrade announcement: v{} from operator {}...",
                upgrade.version,
                &upgrade.operator_pubkey[..16]
            );
            if upgrade.mandatory {
                tracing::warn!("⚠️ This is a MANDATORY upgrade!");
            }
            *latest = Some(upgrade);
        }
    }
    
    /// Compare semver versions (returns Ordering)
    fn compare_versions(a: &str, b: &str) -> std::cmp::Ordering {
        let parse = |s: &str| -> (u32, u32, u32) {
            let parts: Vec<&str> = s.split('.').collect();
            (
                parts.first().and_then(|p| p.parse().ok()).unwrap_or(0),
                parts.get(1).and_then(|p| p.parse().ok()).unwrap_or(0),
                parts.get(2).and_then(|p| p.parse().ok()).unwrap_or(0),
            )
        };
        parse(a).cmp(&parse(b))
    }
    
    /// Check if we need to update
    pub fn needs_update(&self) -> Option<String> {
        let newest = self.newest_version.read_or_recover();
        if let Some(ref newest_ver) = *newest {
            if Self::compare_versions(newest_ver, SMITH_VERSION) == std::cmp::Ordering::Greater {
                return Some(newest_ver.clone());
            }
        }
        None
    }
    
    /// Get latest verified upgrade announcement
    pub fn get_latest_upgrade(&self) -> Option<UpgradeAnnouncement> {
        self.latest_upgrade.read_or_recover().clone()
    }
    
    /// Get version stats for debugging
    pub fn get_version_stats(&self) -> HashMap<String, (usize, u64)> {
        self.versions.read_or_recover().clone()
    }
}

/// Global version tracker (shared between P2P and RPC)
static VERSION_TRACKER: std::sync::OnceLock<VersionTracker> = std::sync::OnceLock::new();

pub fn get_version_tracker() -> &'static VersionTracker {
    VERSION_TRACKER.get_or_init(VersionTracker::new)
}

/// Network behaviour combining gossipsub and mDNS
#[derive(NetworkBehaviour)]
#[behaviour(to_swarm = "SmithNodeBehaviourEvent")]
pub struct SmithNodeBehaviour {
    gossipsub: gossipsub::Behaviour,
    mdns: mdns::tokio::Behaviour,
}

/// Events produced by the network behaviour
#[derive(Debug)]
pub enum SmithNodeBehaviourEvent {
    Gossipsub(gossipsub::Event),
    Mdns(mdns::Event),
}

impl From<gossipsub::Event> for SmithNodeBehaviourEvent {
    fn from(event: gossipsub::Event) -> Self {
        SmithNodeBehaviourEvent::Gossipsub(event)
    }
}

impl From<mdns::Event> for SmithNodeBehaviourEvent {
    fn from(event: mdns::Event) -> Self {
        SmithNodeBehaviourEvent::Mdns(event)
    }
}

/// Challenge broadcast message
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ChallengeMessage {
    pub challenge: CognitiveChallenge,
    pub broadcast_height: u64,
    pub broadcaster_peer_id: String,
}

/// Proof submission message  
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ProofMessage {
    pub response: ChallengeResponse,
    pub submitted_at: u64,
}

/// Block broadcast message
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BlockMessage {
    pub header: BlockHeader,
    pub proof_count: u64,
    pub state_root_hex: String,
    /// The new state root AFTER block finalization (authoritative from block producer)
    #[serde(default)]
    pub new_state_root_hex: String,
    /// Total supply after block (needed so receivers can update their state)
    #[serde(default)]
    pub total_supply: u64,
    /// Validator snapshots after block (balances updated with rewards)
    #[serde(default)]
    pub validators: Vec<ValidatorSnapshot>,
    /// Producer's public key (hex) — must be a registered validator
    #[serde(default)]
    pub producer_pubkey: String,
    /// Ed25519 signature over SHA256(height || prev_state_root || challenge_hash || new_state_root || total_supply || genesis_hash)
    #[serde(default)]
    pub producer_signature: String,
    /// Genesis hash - unique per chain instance, enables reset detection
    #[serde(default)]
    pub genesis_hash: String,
}

impl BlockMessage {
    /// Compute the message bytes that the producer signs
    fn signing_payload(&self) -> Vec<u8> {
        let mut payload = Vec::with_capacity(144); // 112 + 32 for genesis_hash
        payload.extend_from_slice(&self.header.height.to_le_bytes());
        payload.extend_from_slice(&self.header.prev_state_root);
        payload.extend_from_slice(&self.header.challenge_hash);
        // Include new state root + total_supply so they can't be tampered
        if let Ok(root_bytes) = hex::decode(&self.new_state_root_hex) {
            payload.extend_from_slice(&root_bytes);
        }
        payload.extend_from_slice(&self.total_supply.to_le_bytes());
        // Include genesis_hash so blocks from different chains are rejected
        if let Ok(genesis_bytes) = hex::decode(&self.genesis_hash) {
            payload.extend_from_slice(&genesis_bytes);
        }
        payload
    }

    /// Verify the producer's signature on this block message.
    /// Returns true if signature is valid AND producer is in the validator set.
    pub fn verify_producer_signature(&self) -> bool {
        use ed25519_dalek::{Signature, Verifier, VerifyingKey};

        if self.producer_pubkey.is_empty() || self.producer_signature.is_empty() {
            return false; // Unsigned blocks are rejected
        }

        let pubkey_bytes: [u8; 32] = match hex::decode(&self.producer_pubkey) {
            Ok(b) if b.len() == 32 => b.try_into().unwrap(),
            _ => return false,
        };
        let verifying_key = match VerifyingKey::from_bytes(&pubkey_bytes) {
            Ok(k) => k,
            Err(_) => return false,
        };
        let sig_bytes: [u8; 64] = match hex::decode(&self.producer_signature) {
            Ok(b) if b.len() == 64 => b.try_into().unwrap(),
            _ => return false,
        };
        let signature = Signature::from_bytes(&sig_bytes);
        let payload = self.signing_payload();
        verifying_key.verify(&payload, &signature).is_ok()
    }
}

/// State sync request - sent by new nodes joining the network
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct StateRequestMessage {
    pub requester_peer_id: String,
    pub current_height: u64,  // 0 if starting fresh
    /// Unique nonce so gossipsub doesn't de-duplicate repeated requests
    #[serde(default)]
    pub nonce: u64,
}

/// State sync response - full state snapshot from a peer
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct StateResponseMessage {
    pub responder_peer_id: String,
    pub height: u64,
    pub state_root: String,
    pub total_supply: u64,
    pub validators: Vec<ValidatorSnapshot>,
    /// Transaction history for full state replication
    #[serde(default)]
    pub tx_records: Vec<TxRecordSnapshot>,
}

/// Transaction record for state sync
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TxRecordSnapshot {
    pub hash: String,
    pub tx_type: String,
    pub from: String,
    pub to: Option<String>,
    pub amount: u64,
    pub status: String,
    pub timestamp: u64,
    pub height: u64,
    pub validators: Option<Vec<String>>,
    pub challenge_hash: Option<String>,
}

/// Validator info for state sync
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ValidatorSnapshot {
    pub public_key: String,
    pub balance: u64,
    pub validations_count: u64,
    pub reputation_score: u64,
    pub last_active_timestamp: u64,
    /// Transaction nonce — prevents replay attacks after state sync
    #[serde(default)]
    pub nonce: u64,
}

/// Presence/Heartbeat message - validators broadcast their presence regularly
/// SIGNED to prevent impersonation attacks
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct PresenceMessage {
    /// Validator's public key (hex)
    pub validator_pubkey: String,
    /// Current block height the validator is at
    pub height: u64,
    /// Timestamp of this heartbeat
    pub timestamp: u64,
    /// Node version
    pub version: String,
    /// Signature over (pubkey || height || timestamp) - prevents impersonation
    /// Format: ed25519 signature (64 bytes hex)
    pub signature: String,
}

impl PresenceMessage {
    /// Verify the signature on this presence message
    pub fn verify_signature(&self) -> bool {
        use ed25519_dalek::{Signature, Verifier, VerifyingKey};
        
        // Parse public key
        let pubkey_bytes: [u8; 32] = match hex::decode(&self.validator_pubkey) {
            Ok(bytes) if bytes.len() == 32 => bytes.try_into().unwrap(),
            _ => return false,
        };
        
        let verifying_key = match VerifyingKey::from_bytes(&pubkey_bytes) {
            Ok(k) => k,
            Err(_) => return false,
        };
        
        // Parse signature
        let sig_bytes: [u8; 64] = match hex::decode(&self.signature) {
            Ok(bytes) if bytes.len() == 64 => bytes.try_into().unwrap(),
            _ => return false,
        };
        let signature = Signature::from_bytes(&sig_bytes);
        
        // Build message: pubkey || height || timestamp
        let mut message = Vec::with_capacity(48);
        message.extend_from_slice(&pubkey_bytes);
        message.extend_from_slice(&self.height.to_le_bytes());
        message.extend_from_slice(&self.timestamp.to_le_bytes());
        
        verifying_key.verify(&message, &signature).is_ok()
    }
}

/// Signed upgrade announcement - broadcast by trusted operators
/// Only messages signed by keys in TRUSTED_OPERATOR_KEYS are accepted
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct UpgradeAnnouncement {
    /// New version (semver)
    pub version: String,
    /// Download URLs for different platforms
    pub download_urls: UpgradeUrls,
    /// SHA256 checksums for verification
    pub checksums: UpgradeChecksums,
    /// Timestamp of announcement
    pub timestamp: u64,
    /// Is this a mandatory upgrade? (if true, old versions may be rejected)
    pub mandatory: bool,
    /// Release notes / changelog
    pub release_notes: Option<String>,
    /// Operator public key (hex)
    pub operator_pubkey: String,
    /// Signature over the announcement
    pub signature: String,
}

#[derive(Clone, Debug, Serialize, Deserialize, Default)]
pub struct UpgradeUrls {
    pub darwin_arm64: Option<String>,
    pub darwin_x64: Option<String>,
    pub linux_x64: Option<String>,
    pub linux_arm64: Option<String>,
    pub windows_x64: Option<String>,
}

#[derive(Clone, Debug, Serialize, Deserialize, Default)]
pub struct UpgradeChecksums {
    pub darwin_arm64: Option<String>,
    pub darwin_x64: Option<String>,
    pub linux_x64: Option<String>,
    pub linux_arm64: Option<String>,
    pub windows_x64: Option<String>,
}

/// P2P Peer Relay Announcement — after a peer downloads the upgrade binary,
/// it announces itself as a relay so other peers can download from it via P2P
/// instead of requiring external HTTP access.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct PeerRelayAnnouncement {
    /// Version being relayed
    pub version: String,
    /// Platform this relay has (e.g. "darwin_arm64", "linux_x64")
    pub platform: String,
    /// URL where the binary can be downloaded from this peer (e.g. http://peer-ip:port/binary)
    pub relay_url: String,
    /// SHA256 checksum of the binary
    pub checksum: String,
    /// Peer ID of the relayer
    pub peer_id: String,
    /// Timestamp
    pub timestamp: u64,
}

/// Global peer relay tracker — collects relay announcements from peers
static PEER_RELAYS: std::sync::OnceLock<Arc<RwLock<Vec<PeerRelayAnnouncement>>>> = std::sync::OnceLock::new();

pub fn get_peer_relays() -> &'static Arc<RwLock<Vec<PeerRelayAnnouncement>>> {
    PEER_RELAYS.get_or_init(|| Arc::new(RwLock::new(Vec::new())))
}

/// Record a peer relay
/// Maximum number of peer relay entries to prevent unbounded memory growth
const MAX_PEER_RELAYS: usize = 500;

pub fn record_peer_relay(relay: PeerRelayAnnouncement) {
    let relays = get_peer_relays();
    let mut list = relays.write_or_recover();
    // Don't duplicate
    if !list.iter().any(|r| r.peer_id == relay.peer_id && r.version == relay.version && r.platform == relay.platform) {
        tracing::info!("🌱 New peer relay: peer {} has v{} for {}", &relay.peer_id[..12.min(relay.peer_id.len())], relay.version, relay.platform);
        // Cap to prevent unbounded memory growth from spam
        if list.len() >= MAX_PEER_RELAYS {
            // Remove oldest quarter of entries
            let drain_count = list.len() / 4;
            list.drain(0..drain_count);
            tracing::debug!("🧹 Pruned {} old peer relay entries", drain_count);
        }
        list.push(relay);
    }
}

/// Get relay URLs for a specific version and platform
pub fn get_relay_urls(version: &str, platform: &str) -> Vec<String> {
    let relays = get_peer_relays();
    let list = relays.read_or_recover();
    list.iter()
        .filter(|r| r.version == version && r.platform == platform)
        .map(|r| r.relay_url.clone())
        .collect()
}

impl UpgradeAnnouncement {
    /// Verify the signature AND check it's from a trusted operator
    pub fn verify(&self) -> bool {
        use ed25519_dalek::{Signature, Verifier, VerifyingKey};
        
        // Check if operator is in trusted list (dynamic lookup)
        let trusted_keys = get_trusted_operator_keys();
        if !trusted_keys.iter().any(|k| k == &self.operator_pubkey) {
            tracing::warn!("Upgrade from untrusted operator: {}...", &self.operator_pubkey[..16.min(self.operator_pubkey.len())]);
            return false;
        }
        
        // Parse public key
        let pubkey_bytes: [u8; 32] = match hex::decode(&self.operator_pubkey) {
            Ok(bytes) if bytes.len() == 32 => bytes.try_into().unwrap(),
            _ => return false,
        };
        
        let verifying_key = match VerifyingKey::from_bytes(&pubkey_bytes) {
            Ok(k) => k,
            Err(_) => return false,
        };
        
        // Parse signature
        let sig_bytes: [u8; 64] = match hex::decode(&self.signature) {
            Ok(bytes) if bytes.len() == 64 => bytes.try_into().unwrap(),
            _ => return false,
        };
        let signature = Signature::from_bytes(&sig_bytes);
        
        // Build message: version || timestamp || mandatory || download_urls || checksums
        // SECURITY: Include download URLs in signed payload to prevent URL-swap supply-chain attacks
        let mut message = Vec::new();
        message.extend_from_slice(self.version.as_bytes());
        message.extend_from_slice(&self.timestamp.to_le_bytes());
        message.push(if self.mandatory { 1 } else { 0 });
        // Include download URLs in signature to prevent URL-swap attacks
        if let Some(ref u) = self.download_urls.darwin_arm64 { message.extend_from_slice(u.as_bytes()); }
        if let Some(ref u) = self.download_urls.darwin_x64 { message.extend_from_slice(u.as_bytes()); }
        if let Some(ref u) = self.download_urls.linux_x64 { message.extend_from_slice(u.as_bytes()); }
        if let Some(ref u) = self.download_urls.linux_arm64 { message.extend_from_slice(u.as_bytes()); }
        if let Some(ref u) = self.download_urls.windows_x64 { message.extend_from_slice(u.as_bytes()); }
        // Include checksums in signature to prevent tampering
        if let Some(ref c) = self.checksums.darwin_arm64 { message.extend_from_slice(c.as_bytes()); }
        if let Some(ref c) = self.checksums.darwin_x64 { message.extend_from_slice(c.as_bytes()); }
        if let Some(ref c) = self.checksums.linux_x64 { message.extend_from_slice(c.as_bytes()); }
        if let Some(ref c) = self.checksums.linux_arm64 { message.extend_from_slice(c.as_bytes()); }
        if let Some(ref c) = self.checksums.windows_x64 { message.extend_from_slice(c.as_bytes()); }
        
        verifying_key.verify(&message, &signature).is_ok()
    }
}

/// Registration broadcast message — validators announce themselves via P2P gossip
/// All nodes that receive this apply the registration, keeping state in sync
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RegisterValidatorMessage {
    /// Validator's public key (hex)
    pub public_key: String,
    /// Timestamp of registration request
    pub timestamp: u64,
    /// Signature over (public_key_bytes || timestamp) to prove key ownership
    pub signature: String,
}

impl RegisterValidatorMessage {
    /// Verify the signature proves ownership of the public key
    pub fn verify_signature(&self) -> bool {
        use ed25519_dalek::{Signature, Verifier, VerifyingKey};
        
        let pubkey_bytes: [u8; 32] = match hex::decode(&self.public_key) {
            Ok(bytes) if bytes.len() == 32 => bytes.try_into().unwrap(),
            _ => return false,
        };
        
        let verifying_key = match VerifyingKey::from_bytes(&pubkey_bytes) {
            Ok(k) => k,
            Err(_) => return false,
        };
        
        let sig_bytes: [u8; 64] = match hex::decode(&self.signature) {
            Ok(bytes) if bytes.len() == 64 => bytes.try_into().unwrap(),
            _ => return false,
        };
        let signature = Signature::from_bytes(&sig_bytes);
        
        // Message: pubkey_bytes || timestamp
        let mut message = Vec::with_capacity(40);
        message.extend_from_slice(&pubkey_bytes);
        message.extend_from_slice(&self.timestamp.to_le_bytes());
        
        verifying_key.verify(&message, &signature).is_ok()
    }
}

/// Commands that can be sent to the P2P network from other parts of the system
#[derive(Clone, Debug)]
pub enum NetworkCommand {
    BroadcastChallenge(CognitiveChallenge),
    BroadcastProof(ChallengeResponse),
    /// Block header + optional signing key for producer signature
    BroadcastBlock(BlockHeader, Option<(String, ed25519_dalek::SigningKey)>), // (pubkey_hex, signing_key)
    /// Turbo block: height, prev_state_root, new_state_root, challenge_hash, total_supply
    BroadcastTurboBlock(u64, [u8; 32], [u8; 32], [u8; 32], u64),
    /// P2P liveness challenge between validators
    BroadcastLivenessChallenge(LivenessChallenge),
    /// Response to a liveness challenge
    BroadcastLivenessResponse(LivenessResponse),
    DialPeer(String),  // Multiaddr as string
    RequestStateSync,  // Request state from peers
    BroadcastPresence(PresenceMessage),  // Heartbeat presence announcement
    BroadcastAIMessage(AINetworkMessage),  // AI-to-AI message
    BroadcastRegistration(RegisterValidatorMessage),  // Validator registration via P2P
    BroadcastGovernance(GovernanceGossipMessage),  // Governance proposals/votes via P2P
    BroadcastTransfer(TransferGossipMessage),  // Transfer broadcast via P2P
    BroadcastUpgrade(UpgradeAnnouncement),  // Upgrade announcement via P2P
    BroadcastPeerRelay(PeerRelayAnnouncement),  // "I have the binary, download from me"
}

/// P2P liveness challenge — validators quiz each other asynchronously
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct LivenessChallenge {
    /// Who is challenging
    pub challenger: String,
    /// Who is being challenged
    pub target: String,
    /// The puzzle prompt
    pub puzzle_prompt: String,
    /// Expected answer (hashed, so target can't cheat)
    pub answer_hash: String,
    /// Challenge ID
    pub challenge_id: String,
    /// When this challenge expires
    pub expires_at: u64,
    /// Challenger's signature
    pub signature: String,
}

/// Response to a P2P liveness challenge
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct LivenessResponse {
    /// Challenge ID being responded to
    pub challenge_id: String,
    /// Responder pubkey
    pub responder: String,
    /// The AI's answer to the puzzle
    pub answer: String,
    /// Responder's signature
    pub signature: String,
}

/// Governance gossip message for P2P propagation
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct GovernanceGossipMessage {
    pub action: GovernanceAction,
    pub timestamp: u64,
}

/// Governance action types
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum GovernanceAction {
    CreateProposal {
        proposer: String,
        proposal_type: u8,
        new_value: u64,
        description_hash: String,
        signature: String,
    },
    CastVote {
        voter: String,
        proposal_id: u64,
        vote: bool,
        signature: String,
        #[serde(default)]
        reason: Option<String>,
    },
    ExecuteProposal {
        executor: String,
        proposal_id: u64,
        signature: String,
    },
}

/// Transfer gossip message for P2P propagation
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TransferGossipMessage {
    pub from: String,
    pub to: String,
    pub amount: u64,
    pub nonce: u64,
    pub signature: String,
}

/// Tagged wrapper for messages sharing the transactions topic
/// Prevents serde ambiguity between Registration and Transfer
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(tag = "msg_type")]
pub enum TransactionTopicMessage {
    Registration(RegisterValidatorMessage),
    Transfer(TransferGossipMessage),
}

/// AI message for P2P network communication between validators
/// Topics allowed: upgrade, marketing, dev, code, governance, security, performance, consensus
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AINetworkMessage {
    /// Sender validator public key (hex)
    pub from_validator: String,
    /// Target validator (hex) or "broadcast" for all
    pub to_validator: String,
    /// Topic of discussion (upgrade, marketing, dev, code, governance, security, performance, consensus)
    pub topic: Option<String>,
    /// The actual message/query content (prefixed with [topic])
    pub content: String,
    /// AI-generated response (if this is a response)
    pub response: Option<String>,
    /// AI provider used (groq, together - both FREE)
    pub ai_provider: Option<String>,
    /// Model used (default: llama-3.1-70b)
    pub model: Option<String>,
    /// Timestamp
    pub timestamp: u64,
    /// Signature over (from || to || content_hash || timestamp)
    pub signature: String,
    /// Message hash for deduplication
    pub message_hash: String,
    /// Is this a response to another message?
    pub in_reply_to: Option<String>,
    /// Message type: "query", "response", "broadcast"
    pub message_type: String,
    /// On-chain transaction hash
    pub tx_hash: Option<String>,
}

/// Events emitted by the P2P network to be handled by state
#[derive(Clone, Debug)]
pub enum NetworkEvent {
    ChallengeReceived(ChallengeMessage),
    ProofReceived(ProofMessage),
    BlockReceived(BlockMessage),
    PeerConnected(String),
    PeerDisconnected(String),
    StateReceived(StateResponseMessage),  // Received state from peer
    StateRequested(String),  // Peer requested our state
    PresenceReceived(PresenceMessage),  // Validator heartbeat received
    AIMessageReceived(AINetworkMessage),  // AI-to-AI message received
    RegistrationReceived(RegisterValidatorMessage),  // Validator registered via P2P
    GovernanceReceived(GovernanceGossipMessage),  // Governance action via P2P
    TransferReceived(TransferGossipMessage),  // Transfer via P2P
    LivenessChallengeReceived(LivenessChallenge),  // P2P liveness challenge targeting us
    LivenessResponseReceived(LivenessResponse),  // Response to our liveness challenge
}

/// The P2P network handler
pub struct SmithNodeNetwork {
    swarm: Swarm<SmithNodeBehaviour>,
    challenge_topic: IdentTopic,
    proof_topic: IdentTopic,
    block_topic: IdentTopic,
    state_sync_topic: IdentTopic,
    presence_topic: IdentTopic,
    _upgrade_topic: IdentTopic,  // Used for receiving only (operators broadcast from external tool)
    ai_message_topic: IdentTopic,  // AI-to-AI communication
    transaction_topic: IdentTopic,  // Transaction/registration broadcast
    governance_topic: IdentTopic,  // Governance proposals/votes broadcast
    peer_relay_topic: IdentTopic,  // P2P binary distribution relay announcements
    local_peer_id: String,
    state: SmithNodeState,
    command_rx: mpsc::Receiver<NetworkCommand>,
    event_tx: mpsc::Sender<NetworkEvent>,
    /// Registrations that failed gossip publish (InsufficientPeers) — retried when mesh forms
    pending_registrations: Vec<RegisterValidatorMessage>,
    /// Optional validator signing key for signing block broadcasts
    validator_signer: Option<(String, ed25519_dalek::SigningKey)>,
}

/// Handle to send commands to the network
#[derive(Clone)]
pub struct NetworkHandle {
    command_tx: mpsc::Sender<NetworkCommand>,
}

impl NetworkHandle {
    pub async fn broadcast_challenge(&self, challenge: CognitiveChallenge) -> anyhow::Result<()> {
        self.command_tx.send(NetworkCommand::BroadcastChallenge(challenge)).await?;
        Ok(())
    }

    pub async fn broadcast_proof(&self, response: ChallengeResponse) -> anyhow::Result<()> {
        self.command_tx.send(NetworkCommand::BroadcastProof(response)).await?;
        Ok(())
    }

    pub async fn broadcast_block(&self, header: BlockHeader, signer: Option<(String, ed25519_dalek::SigningKey)>) -> anyhow::Result<()> {
        self.command_tx.send(NetworkCommand::BroadcastBlock(header, signer)).await?;
        Ok(())
    }
    
    /// Dial a peer by multiaddr
    pub async fn dial_peer(&self, addr: &str) -> anyhow::Result<()> {
        self.command_tx.send(NetworkCommand::DialPeer(addr.to_string())).await?;
        Ok(())
    }
    
    /// Request state sync from peers (for new nodes joining)
    pub async fn request_state_sync(&self) -> anyhow::Result<()> {
        self.command_tx.send(NetworkCommand::RequestStateSync).await?;
        Ok(())
    }
    
    /// Broadcast presence/heartbeat
    pub async fn broadcast_presence(&self, presence: PresenceMessage) -> anyhow::Result<()> {
        self.command_tx.send(NetworkCommand::BroadcastPresence(presence)).await?;
        Ok(())
    }
    
    /// Broadcast AI message to the network
    pub async fn broadcast_ai_message(&self, message: AINetworkMessage) -> anyhow::Result<()> {
        self.command_tx.send(NetworkCommand::BroadcastAIMessage(message)).await?;
        Ok(())
    }
    
    /// Broadcast validator registration via P2P gossip
    /// All nodes that receive this will apply the registration, keeping state in sync
    pub async fn broadcast_registration(&self, msg: RegisterValidatorMessage) -> anyhow::Result<()> {
        self.command_tx.send(NetworkCommand::BroadcastRegistration(msg)).await?;
        Ok(())
    }
    
    /// Broadcast governance action (proposal/vote/execute) via P2P gossip
    pub async fn broadcast_governance(&self, msg: GovernanceGossipMessage) -> anyhow::Result<()> {
        self.command_tx.send(NetworkCommand::BroadcastGovernance(msg)).await?;
        Ok(())
    }
    
    /// Broadcast transfer via P2P gossip
    pub async fn broadcast_transfer(&self, msg: TransferGossipMessage) -> anyhow::Result<()> {
        self.command_tx.send(NetworkCommand::BroadcastTransfer(msg)).await?;
        Ok(())
    }
    
    /// Broadcast a turbo block with full verification data
    pub async fn broadcast_turbo_block(&self, height: u64, prev_state_root: [u8; 32], state_root: [u8; 32], challenge_hash: [u8; 32], total_supply: u64) -> anyhow::Result<()> {
        self.command_tx.send(NetworkCommand::BroadcastTurboBlock(height, prev_state_root, state_root, challenge_hash, total_supply)).await?;
        Ok(())
    }
    
    /// Broadcast a P2P liveness challenge to another validator
    pub async fn broadcast_liveness_challenge(&self, challenge: LivenessChallenge) -> anyhow::Result<()> {
        self.command_tx.send(NetworkCommand::BroadcastLivenessChallenge(challenge)).await?;
        Ok(())
    }
    
    /// Broadcast a liveness challenge response
    pub async fn broadcast_liveness_response(&self, response: LivenessResponse) -> anyhow::Result<()> {
        self.command_tx.send(NetworkCommand::BroadcastLivenessResponse(response)).await?;
        Ok(())
    }
    
    /// Broadcast an upgrade announcement to the network
    pub async fn broadcast_upgrade(&self, announcement: UpgradeAnnouncement) -> anyhow::Result<()> {
        self.command_tx.send(NetworkCommand::BroadcastUpgrade(announcement)).await?;
        Ok(())
    }
    
    /// Broadcast that we have the binary and can relay it to peers
    pub async fn broadcast_peer_relay(&self, relay: PeerRelayAnnouncement) -> anyhow::Result<()> {
        self.command_tx.send(NetworkCommand::BroadcastPeerRelay(relay)).await?;
        Ok(())
    }
}

impl SmithNodeNetwork {
    pub async fn new(
        port: u16, 
        state: SmithNodeState,
    ) -> anyhow::Result<(Self, NetworkHandle, mpsc::Receiver<NetworkEvent>)> {
        Self::new_with_data_dir(port, state, None).await
    }
    
    /// Try to derive P2P identity from operator key (for deterministic sequencer peer ID)
    /// Returns None if operator key not available or derivation fails
    fn try_derive_from_operator_key() -> Option<libp2p::identity::Keypair> {
        // Try SMITHNODE_OPERATOR_SECRET env var first (hex-encoded 32-byte secret key)
        if let Ok(secret_hex) = std::env::var("SMITHNODE_OPERATOR_SECRET") {
            if let Ok(secret_bytes) = hex::decode(secret_hex.trim()) {
                if secret_bytes.len() == 32 {
                    if let Ok(keypair) = libp2p::identity::Keypair::ed25519_from_bytes(secret_bytes.clone()) {
                        return Some(keypair);
                    }
                }
            }
        }
        
        // Try loading from node_key.json
        let data_dir = std::env::var("SMITHNODE_DATA_DIR")
            .unwrap_or_else(|_| ".smithnode-data".to_string());
        let node_key_path = std::path::Path::new(&data_dir).join("node_key.json");
        
        if let Ok(data) = std::fs::read_to_string(&node_key_path) {
            if let Ok(parsed) = serde_json::from_str::<serde_json::Value>(&data) {
                if let Some(secret_hex) = parsed["secret_key"].as_str() {
                    if let Ok(secret_bytes) = hex::decode(secret_hex) {
                        if secret_bytes.len() == 32 {
                            if let Ok(keypair) = libp2p::identity::Keypair::ed25519_from_bytes(secret_bytes.clone()) {
                                return Some(keypair);
                            }
                        }
                    }
                }
            }
        }
        
        None
    }

    /// Create a new P2P network with optional data directory for persistent identity
    pub async fn new_with_data_dir(
        port: u16, 
        state: SmithNodeState,
        data_dir: Option<&std::path::Path>,
    ) -> anyhow::Result<(Self, NetworkHandle, mpsc::Receiver<NetworkEvent>)> {
        Self::new_with_identity(port, state, data_dir, None).await
    }
    
    /// Create a new P2P network with explicit identity secret
    /// If identity_secret is provided, P2P peer ID is derived from it (deterministic)
    pub async fn new_with_identity(
        port: u16, 
        state: SmithNodeState,
        data_dir: Option<&std::path::Path>,
        identity_secret: Option<&[u8]>,
    ) -> anyhow::Result<(Self, NetworkHandle, mpsc::Receiver<NetworkEvent>)> {
        // Derive P2P identity
        // Priority: 1) Explicit secret, 2) Operator key (env/file), 3) Generate ephemeral
        
        let local_key = if let Some(secret) = identity_secret {
            // Derive from provided secret (validator keypair)
            if secret.len() == 32 {
                libp2p::identity::Keypair::ed25519_from_bytes(secret.to_vec())
                    .map_err(|e| anyhow::anyhow!("Failed to derive P2P identity from secret: {}", e))?
            } else {
                return Err(anyhow::anyhow!("Identity secret must be 32 bytes"));
            }
        } else if let Some(keypair) = Self::try_derive_from_operator_key() {
            tracing::info!("🔐 P2P identity derived from operator key (sequencer)");
            keypair
        } else {
            // Generate ephemeral keypair (shouldn't happen in production)
            tracing::warn!("⚠️  No identity secret provided, generating ephemeral P2P identity");
            libp2p::identity::Keypair::generate_ed25519()
        };
        
        let local_peer_id = PeerId::from(local_key.public());
        
        // Store peer info globally for RPC access (external addrs added dynamically)
        let _ = LOCAL_PEER_INFO.set(PeerInfo {
            peer_id: local_peer_id.to_string(),
            p2p_port: port,
            external_addrs: Arc::new(RwLock::new(Vec::new())),
        });
        
        tracing::info!("══════════════════════════════════════════════════════════════════");
        tracing::info!("🔑 P2P PEER ID: {}", local_peer_id);
        tracing::info!("══════════════════════════════════════════════════════════════════");
        tracing::info!("📡 Other peers can connect using this peer ID");
        tracing::info!("   Example: /ip4/<IP>/tcp/{}/p2p/{}", port, local_peer_id);
        tracing::info!("   Actual addresses will be logged when discovered");
        tracing::info!("══════════════════════════════════════════════════════════════════");
        
        // Configure gossipsub
        // SECURITY (L3): Use SHA256 instead of DefaultHasher for collision resistance
        let message_id_fn = |message: &gossipsub::Message| {
            let mut hasher = Sha256::new();
            hasher.update(&message.data);
            gossipsub::MessageId::from(hex::encode(hasher.finalize()))
        };
        
        // Configure gossipsub for small networks (1-3 nodes)
        // Lower mesh requirements so publishing works with fewer peers
        let gossipsub_config = gossipsub::ConfigBuilder::default()
            .heartbeat_interval(Duration::from_secs(10))
            .validation_mode(gossipsub::ValidationMode::Strict)
            .message_id_fn(message_id_fn)
            // Small network settings - allow publishing with 0 peers
            .mesh_n(2)           // Target 2 peers in mesh (default: 6)
            .mesh_n_low(1)       // Minimum 1 peer before grafting (default: 4)
            .mesh_n_high(4)      // Max 4 peers before pruning (default: 12)
            .mesh_outbound_min(0) // Don't require outbound peers (default: 2)
            .gossip_lazy(2)      // Gossip to 2 peers (default: 6)
            .build()
            .map_err(|e| anyhow::anyhow!("Gossipsub config error: {}", e))?;
        
        let gossipsub = gossipsub::Behaviour::new(
            MessageAuthenticity::Signed(local_key.clone()),
            gossipsub_config,
        )
        .map_err(|e| anyhow::anyhow!("Gossipsub error: {}", e))?;
        
        // Configure mDNS for local peer discovery
        let mdns = mdns::tokio::Behaviour::new(
            mdns::Config::default(),
            local_peer_id,
        )?;
        
        let behaviour = SmithNodeBehaviour { gossipsub, mdns };
        
        // Build the swarm with DNS support for resolving hostnames
        let mut swarm = libp2p::SwarmBuilder::with_existing_identity(local_key)
            .with_tokio()
            .with_tcp(
                tcp::Config::default(),
                noise::Config::new,
                yamux::Config::default,
            )?
            .with_dns()?  // Enable DNS resolution for multiaddrs like /dns4/hostname/tcp/port
            .with_behaviour(|_| behaviour)?
            .with_swarm_config(|c| c.with_idle_connection_timeout(Duration::from_secs(60)))
            .build();
        
        // Create topics
        let challenge_topic = IdentTopic::new(TOPIC_CHALLENGES);
        let proof_topic = IdentTopic::new(TOPIC_PROOFS);
        let block_topic = IdentTopic::new(TOPIC_BLOCKS);
        let state_sync_topic = IdentTopic::new(TOPIC_STATE_SYNC);
        let presence_topic = IdentTopic::new(TOPIC_PRESENCE);
        let upgrade_topic = IdentTopic::new(TOPIC_UPGRADES);
        let ai_message_topic = IdentTopic::new(TOPIC_AI_MESSAGES);
        let transaction_topic = IdentTopic::new(TOPIC_TRANSACTIONS);
        let governance_topic = IdentTopic::new(TOPIC_GOVERNANCE);
        let peer_relay_topic = IdentTopic::new(TOPIC_PEER_RELAY);
        
        // Subscribe to topics
        swarm.behaviour_mut().gossipsub.subscribe(&challenge_topic)?;
        swarm.behaviour_mut().gossipsub.subscribe(&proof_topic)?;
        swarm.behaviour_mut().gossipsub.subscribe(&block_topic)?;
        swarm.behaviour_mut().gossipsub.subscribe(&state_sync_topic)?;
        swarm.behaviour_mut().gossipsub.subscribe(&presence_topic)?;
        swarm.behaviour_mut().gossipsub.subscribe(&upgrade_topic)?;
        swarm.behaviour_mut().gossipsub.subscribe(&ai_message_topic)?;
        swarm.behaviour_mut().gossipsub.subscribe(&transaction_topic)?;
        swarm.behaviour_mut().gossipsub.subscribe(&governance_topic)?;
        swarm.behaviour_mut().gossipsub.subscribe(&peer_relay_topic)?;
        
        // Listen on all interfaces
        let listen_addr: Multiaddr = format!("/ip4/0.0.0.0/tcp/{}", port).parse()?;
        swarm.listen_on(listen_addr)?;

        // Create channels for communication
        let (command_tx, command_rx) = mpsc::channel(100);
        let (event_tx, event_rx) = mpsc::channel(100);
        
        let network = Self {
            swarm,
            challenge_topic,
            proof_topic,
            block_topic,
            state_sync_topic,
            presence_topic,
            _upgrade_topic: upgrade_topic,
            ai_message_topic,
            transaction_topic,
            governance_topic,
            peer_relay_topic,
            local_peer_id: local_peer_id.to_string(),
            state,
            command_rx,
            event_tx,
            pending_registrations: Vec::new(),
            validator_signer: None,
        };

        let handle = NetworkHandle { command_tx };
        
        Ok((network, handle, event_rx))
    }
    
    /// Set the validator signing key for block authentication
    pub fn set_validator_signer(&mut self, pubkey_hex: String, signing_key: ed25519_dalek::SigningKey) {
        self.validator_signer = Some((pubkey_hex, signing_key));
    }
    
    /// Run the network event loop
    pub async fn run(mut self) -> anyhow::Result<()> {
        tracing::info!("🌐 P2P network starting...");
        
        // Timer to retry pending registrations every 3 seconds
        let mut reg_retry_interval = tokio::time::interval(tokio::time::Duration::from_secs(3));
        reg_retry_interval.set_missed_tick_behavior(tokio::time::MissedTickBehavior::Skip);
        
        loop {
            tokio::select! {
                // Handle incoming swarm events
                event = self.swarm.select_next_some() => {
                    self.handle_swarm_event(event).await;
                }
                // Handle outgoing commands
                Some(cmd) = self.command_rx.recv() => {
                    self.handle_command(cmd).await;
                }
                // Retry pending registrations periodically
                _ = reg_retry_interval.tick() => {
                    if !self.pending_registrations.is_empty() {
                        let pending = std::mem::take(&mut self.pending_registrations);
                        let mut still_pending = Vec::new();
                        for reg_msg in pending {
                            if let Ok(data) = serde_json::to_vec(&TransactionTopicMessage::Registration(reg_msg.clone())) {
                                match self.swarm
                                    .behaviour_mut()
                                    .gossipsub
                                    .publish(self.transaction_topic.clone(), data)
                                {
                                    Ok(_) => {
                                        tracing::info!("📢 Registration retry succeeded for {}...",
                                            &reg_msg.public_key[..16.min(reg_msg.public_key.len())]);
                                    }
                                    Err(_) => {
                                        still_pending.push(reg_msg);
                                    }
                                }
                            }
                        }
                        self.pending_registrations = still_pending;
                    }
                }
            }
        }
    }

    async fn handle_swarm_event<E>(&mut self, event: SwarmEvent<SmithNodeBehaviourEvent, E>)
    where E: std::fmt::Debug
    {
        match event {
            SwarmEvent::Behaviour(SmithNodeBehaviourEvent::Mdns(mdns::Event::Discovered(peers))) => {
                for (peer_id, addr) in peers {
                    tracing::info!("🔍 Discovered peer: {} at {}", peer_id, addr);
                    self.swarm.behaviour_mut().gossipsub.add_explicit_peer(&peer_id);
                    let _ = self.event_tx.send(NetworkEvent::PeerConnected(peer_id.to_string())).await;
                }
            }
            SwarmEvent::Behaviour(SmithNodeBehaviourEvent::Mdns(mdns::Event::Expired(peers))) => {
                for (peer_id, _) in peers {
                    tracing::info!("👋 Peer expired: {}", peer_id);
                    self.swarm.behaviour_mut().gossipsub.remove_explicit_peer(&peer_id);
                    let _ = self.event_tx.send(NetworkEvent::PeerDisconnected(peer_id.to_string())).await;
                }
            }
            SwarmEvent::Behaviour(SmithNodeBehaviourEvent::Gossipsub(gossipsub::Event::Message {
                propagation_source,
                message_id,
                message,
            })) => {
                let topic = message.topic.as_str();
                tracing::info!(
                    "📨 Received message on {}: {:?} from {}",
                    topic,
                    message_id,
                    propagation_source
                );
                
                // Handle different message types based on topic
                match topic {
                    TOPIC_CHALLENGES => {
                        self.handle_challenge_message(&message.data).await;
                    }
                    TOPIC_PROOFS => {
                        self.handle_proof_message(&message.data).await;
                    }
                    TOPIC_BLOCKS => {
                        self.handle_block_message(&message.data).await;
                    }
                    TOPIC_STATE_SYNC => {
                        self.handle_state_sync_message(&message.data).await;
                    }
                    TOPIC_PRESENCE => {
                        self.handle_presence_message(&message.data).await;
                    }
                    TOPIC_UPGRADES => {
                        self.handle_upgrade_message(&message.data).await;
                    }
                    TOPIC_AI_MESSAGES => {
                        self.handle_ai_message(&message.data).await;
                    }
                    TOPIC_TRANSACTIONS => {
                        self.handle_transaction_message(&message.data).await;
                    }
                    TOPIC_GOVERNANCE => {
                        self.handle_governance_message(&message.data).await;
                    }
                    TOPIC_PEER_RELAY => {
                        self.handle_peer_relay_message(&message.data).await;
                    }
                    _ => {}
                }
            }
            SwarmEvent::NewListenAddr { address, .. } => {
                tracing::info!("📡 Listening on {}/p2p/{}", address, self.local_peer_id);
                // Record this as an external address
                if let Some(peer_info) = get_local_peer_info() {
                    peer_info.add_external_addr(&address.to_string());
                }
            }
            SwarmEvent::ConnectionEstablished { peer_id, endpoint, .. } => {
                tracing::info!("🤝 Connected to peer: {} via {:?}", peer_id, endpoint);
                // Record connected peers as potential bootstrap peers
                let addr = endpoint.get_remote_address();
                let multiaddr = format!("{}/p2p/{}", addr, peer_id);
                add_bootstrap_peer(multiaddr);
            }
            SwarmEvent::ConnectionClosed { peer_id, .. } => {
                tracing::info!("👋 Disconnected from peer: {}", peer_id);
            }
            _ => {}
        }
    }

    async fn handle_challenge_message(&mut self, data: &[u8]) {
        match serde_json::from_slice::<ChallengeMessage>(data) {
            Ok(msg) => {
                tracing::info!(
                    "🎯 New challenge received: height={}, type={:?}, expires_at={}",
                    msg.challenge.height,
                    msg.challenge.challenge_type,
                    msg.challenge.expires_at
                );
                
                // Check if challenge is still valid
                if msg.challenge.is_expired() {
                    tracing::warn!("⚠️ Received expired challenge, ignoring");
                    return;
                }
                
                // Update local state with the new challenge if it's newer
                let current = self.state.get_current_challenge();
                let should_update = match &current {
                    None => true,
                    Some(existing) => msg.challenge.height > existing.height,
                };
                
                if should_update {
                    self.state.set_current_challenge(msg.challenge.clone());
                    tracing::info!(
                        "✅ Challenge accepted: {} pending txs to validate",
                        msg.challenge.pending_tx_hashes.len()
                    );
                }
                
                // Emit event for external handlers
                let _ = self.event_tx.send(NetworkEvent::ChallengeReceived(msg)).await;
            }
            Err(_) => {
                // Try parsing as a P2P liveness challenge (different struct, same topic)
                match serde_json::from_slice::<LivenessChallenge>(data) {
                    Ok(liveness) => {
                        let now = std::time::SystemTime::now()
                            .duration_since(std::time::UNIX_EPOCH)
                            .unwrap_or_default()
                            .as_secs();
                        if liveness.expires_at < now {
                            tracing::debug!("⏰ Expired liveness challenge from {}...", &liveness.challenger[..16.min(liveness.challenger.len())]);
                            return;
                        }
                        tracing::info!("🧪 Liveness challenge received from {}... target={}...",
                            &liveness.challenger[..16.min(liveness.challenger.len())],
                            &liveness.target[..16.min(liveness.target.len())]);
                        let _ = self.event_tx.send(NetworkEvent::LivenessChallengeReceived(liveness)).await;
                    }
                    Err(e2) => {
                        tracing::error!("❌ Failed to parse challenge message: {}", e2);
                    }
                }
            }
        }
    }

    async fn handle_proof_message(&mut self, data: &[u8]) {
        match serde_json::from_slice::<ProofMessage>(data) {
            Ok(msg) => {
                tracing::info!(
                    "✅ Proof submission received from validator: {}",
                    &msg.response.validator_pubkey[..16.min(msg.response.validator_pubkey.len())]
                );
                
                // Capture state root BEFORE applying proof (needed for block broadcast)
                let pre_block_state_root = self.state.get_state_root();
                let challenge_hash_hex = msg.response.challenge_hash.clone();
                
                // Verify the proof signature and apply to state
                match self.state.verify_and_apply_proof(&msg.response) {
                    Ok(crate::stf::TxResult::Success { reward, .. }) => {
                        tracing::info!(
                            "🏆 Proof verified! Validator {} earned {} SMITH (waiting for threshold)",
                            &msg.response.validator_pubkey[..16.min(msg.response.validator_pubkey.len())],
                            reward
                        );
                    }
                    Ok(crate::stf::TxResult::BlockFinalized { reward, block_height, state_root, .. }) => {
                        tracing::info!(
                            "📦 Block {} FINALIZED via P2P proof! {} SMITH distributed",
                            block_height, reward
                        );
                        tracing::info!("🔗 New state root: {}...", &hex::encode(state_root)[..16]);
                        
                        // Auto-broadcast the finalized block to the network
                        let challenge_hash: [u8; 32] = match hex::decode(&challenge_hash_hex)
                            .ok()
                            .and_then(|b| <[u8; 32]>::try_from(b).ok()) {
                            Some(h) => h,
                            None => {
                                tracing::error!("❌ Invalid challenge hash hex, cannot broadcast block");
                                return;
                            }
                        };
                        // Compute tx_root as SHA256(challenge_hash) — the challenge_hash
                        // already commits to all pending_tx_hashes
                        let tx_root = {
                            use sha2::{Sha256, Digest};
                            let mut hasher = Sha256::new();
                            hasher.update(&challenge_hash);
                            let result: [u8; 32] = hasher.finalize().into();
                            result
                        };
                        let block = crate::stf::BlockHeader {
                            height: block_height,
                            prev_state_root: pre_block_state_root,
                            tx_root,
                            timestamp: std::time::SystemTime::now()
                                .duration_since(std::time::UNIX_EPOCH)
                                .unwrap_or_default()
                                .as_secs(),
                            challenge_hash,
                        };
                        
                        // Collect state snapshot for broadcast
                        let validators: Vec<ValidatorSnapshot> = self.state.get_all_validators()
                            .into_iter()
                            .map(|v| ValidatorSnapshot {
                                public_key: hex::encode(v.public_key),
                                balance: v.balance,
                                validations_count: v.validations_count,
                                reputation_score: v.reputation_score,
                                last_active_timestamp: v.last_active_timestamp,
                                nonce: v.nonce,
                            })
                            .collect();
                        let mut block_msg = BlockMessage {
                            header: block.clone(),
                            proof_count: 0,
                            state_root_hex: hex::encode(pre_block_state_root),
                            new_state_root_hex: hex::encode(self.state.get_state_root()),
                            total_supply: self.state.get_total_supply(),
                            validators,
                            producer_pubkey: String::new(),
                            producer_signature: String::new(),
                            genesis_hash: hex::encode(self.state.get_genesis_hash()),
                        };
                        
                        // Sign the block if we have a validator signer
                        if let Some((ref pubkey, ref signer)) = self.validator_signer {
                            block_msg.producer_pubkey = pubkey.clone();
                            let payload = block_msg.signing_payload();
                            let sig: ed25519_dalek::Signature = ed25519_dalek::Signer::sign(signer, &payload);
                            block_msg.producer_signature = hex::encode(sig.to_bytes());
                        }
                        
                        if let Ok(block_data) = serde_json::to_vec(&block_msg) {
                            if let Err(e) = self.swarm
                                .behaviour_mut()
                                .gossipsub
                                .publish(self.block_topic.clone(), block_data)
                            {
                                tracing::debug!("Block broadcast skipped (no peers): {}", e);
                            } else {
                                tracing::info!("📢 Broadcasted finalized block {}", block_height);
                            }
                        }
                    }
                    Ok(_) => {
                        // Other TxResult variants — shouldn't happen for proof submission
                    }
                    Err(e) => {
                        tracing::warn!("⚠️ Proof verification failed: {}", e);
                    }
                }
                
                // Emit event
                let _ = self.event_tx.send(NetworkEvent::ProofReceived(msg)).await;
            }
            Err(_) => {
                // Try parsing as a liveness response (different struct, same topic)
                match serde_json::from_slice::<LivenessResponse>(data) {
                    Ok(response) => {
                        tracing::info!("✅ Liveness response from {}... for challenge {}...",
                            &response.responder[..16.min(response.responder.len())],
                            &response.challenge_id[..16.min(response.challenge_id.len())]);
                        let _ = self.event_tx.send(NetworkEvent::LivenessResponseReceived(response)).await;
                    }
                    Err(e2) => {
                        tracing::error!("❌ Failed to parse proof message: {}", e2);
                    }
                }
            }
        }
    }

    async fn handle_block_message(&mut self, data: &[u8]) {
        match serde_json::from_slice::<BlockMessage>(data) {
            Ok(msg) => {
                tracing::info!(
                    "📦 New block received: height={}, proofs={}, state_root={}",
                    msg.header.height,
                    msg.proof_count,
                    &msg.state_root_hex[..16.min(msg.state_root_hex.len())]
                );
                
                // SECURITY: Verify producer signature — reject unsigned/forged blocks
                if !msg.producer_signature.is_empty() {
                    if !msg.verify_producer_signature() {
                        tracing::warn!(
                            "⚠️ REJECTING block {}: invalid producer signature from {}...",
                            msg.header.height,
                            &msg.producer_pubkey[..16.min(msg.producer_pubkey.len())]
                        );
                        return;
                    }
                    // Log if producer is a known validator or the block authority node
                    if self.state.get_validator(&msg.producer_pubkey).is_some() {
                        tracing::info!("✅ Block {} producer signature VERIFIED (validator {}...)", msg.header.height,
                            &msg.producer_pubkey[..16.min(msg.producer_pubkey.len())]);
                    } else {
                        tracing::info!("✅ Block {} producer signature VERIFIED (authority node {}...)", msg.header.height,
                            &msg.producer_pubkey[..16.min(msg.producer_pubkey.len())]);
                    }
                } else {
                    tracing::warn!(
                        "⚠️ REJECTING block {}: no producer signature (unsigned blocks are no longer accepted)",
                        msg.header.height
                    );
                    return;
                }
                
                // Verify block header and update state
                let current_height = self.state.get_height();
                
                // CHAIN RESET DETECTION via genesis_hash comparison
                // If the block's genesis_hash differs from ours, the sequencer was reset
                let local_genesis = hex::encode(self.state.get_genesis_hash());
                let block_genesis = &msg.genesis_hash;
                
                if !block_genesis.is_empty() && !local_genesis.is_empty() && block_genesis != &local_genesis {
                    // Different genesis_hash = new chain instance, we must reset
                    tracing::warn!(
                        "🔄 CHAIN RESET DETECTED! Genesis hash mismatch. Block: {}..., Local: {}...",
                        &block_genesis[..16.min(block_genesis.len())],
                        &local_genesis[..16.min(local_genesis.len())]
                    );
                    tracing::info!("Sequencer at height {}, we're at {}. Resetting local state...", 
                        msg.header.height, current_height);
                    // Adopt the new genesis_hash from the sequencer
                    let new_genesis: [u8; 32] = match hex::decode(block_genesis) {
                        Ok(bytes) if bytes.len() == 32 => bytes.try_into().unwrap(),
                        _ => {
                            tracing::error!("Invalid genesis_hash format in block, cannot reset");
                            return;
                        }
                    };
                    self.state.reset_for_chain_restart(new_genesis);
                    tracing::info!("✅ Local state reset. Adopted new genesis from sequencer.");
                    // Continue processing this block as the first block of the new chain
                } else if msg.header.height <= current_height {
                    // Same chain, but old block - just skip it
                    tracing::debug!(
                        "⚠️ Received old block (height {}), current height is {}",
                        msg.header.height,
                        current_height
                    );
                    return;
                }
                
                // SECURITY: Verify the claimed new_state_root matches recomputation from header
                if !msg.new_state_root_hex.is_empty() {
                    // Compute validator commitment from the received validator snapshots
                    // Must match the formula in stf/state.rs compute_state_root_hash()
                    let val_commitment: [u8; 32] = {
                        let mut sorted_vals: Vec<_> = msg.validators.iter().collect();
                        sorted_vals.sort_by_key(|v| v.public_key.as_str());
                        let mut hasher = Sha256::new();
                        for v in &sorted_vals {
                            hasher.update(v.public_key.as_bytes());
                            hasher.update(&v.balance.to_le_bytes());
                            hasher.update(&v.nonce.to_le_bytes());
                        }
                        hasher.finalize().into()
                    };
                    let recomputed = {
                        let mut hasher = Sha256::new();
                        hasher.update(&msg.header.prev_state_root);
                        hasher.update(&msg.header.height.to_le_bytes());
                        hasher.update(&msg.total_supply.to_le_bytes());
                        hasher.update(&msg.header.challenge_hash);
                        hasher.update(&val_commitment);
                        let result: [u8; 32] = hasher.finalize().into();
                        hex::encode(result)
                    };
                    if recomputed != msg.new_state_root_hex {
                        tracing::warn!(
                            "⚠️ REJECTING block {}: state root mismatch! Claimed: {}... Recomputed: {}...",
                            msg.header.height,
                            &msg.new_state_root_hex[..16.min(msg.new_state_root_hex.len())],
                            &recomputed[..16]
                        );
                        return;
                    }
                }
                
                // SECURITY: Verify validator balance sum doesn't exceed total_supply
                let balance_sum: u64 = msg.validators.iter().map(|v| v.balance).sum();
                if balance_sum > msg.total_supply {
                    tracing::warn!(
                        "⚠️ REJECTING block {}: validator balances {} exceed total_supply {}",
                        msg.header.height, balance_sum, msg.total_supply
                    );
                    return;
                }
                
                // Convert validator snapshots to ValidatorInfo for state sync
                let validator_infos: Vec<crate::stf::ValidatorInfo> = msg.validators.iter()
                    .filter_map(|v| {
                        let pubkey_bytes = hex::decode(&v.public_key).ok()?;
                        if pubkey_bytes.len() != 32 { return None; }
                        let mut pubkey = [0u8; 32];
                        pubkey.copy_from_slice(&pubkey_bytes);
                        Some(crate::stf::ValidatorInfo {
                            public_key: pubkey,
                            balance: v.balance,
                            validations_count: v.validations_count,
                            reputation_score: v.reputation_score,
                            last_active_timestamp: v.last_active_timestamp,
                            last_validation_height: 0,
                            is_online: true,
                            nonce: v.nonce,
                        })
                    })
                    .collect();
                
                // Apply block with full state from the producer
                if let Err(e) = self.state.apply_block_with_state(
                    &msg.header,
                    msg.total_supply,
                    &validator_infos,
                ) {
                    tracing::error!("❌ Failed to apply block: {}", e);
                } else {
                    tracing::info!("✅ Block {} applied successfully (state synced)", msg.header.height);
                }
                
                // Emit event
                let _ = self.event_tx.send(NetworkEvent::BlockReceived(msg)).await;
            }
            Err(e) => {
                tracing::error!("❌ Failed to parse block message: {}", e);
            }
        }
    }

    async fn handle_command(&mut self, cmd: NetworkCommand) {
        match cmd {
            NetworkCommand::BroadcastChallenge(challenge) => {
                let msg = ChallengeMessage {
                    challenge,
                    broadcast_height: self.state.get_height(),
                    broadcaster_peer_id: self.local_peer_id.clone(),
                };
                
                if let Ok(data) = serde_json::to_vec(&msg) {
                    if let Err(e) = self.swarm
                        .behaviour_mut()
                        .gossipsub
                        .publish(self.challenge_topic.clone(), data) 
                    {
                        tracing::debug!("P2P broadcast skipped (no peers): {}", e);
                    } else {
                        tracing::info!("📢 Broadcasted challenge for height {}", msg.broadcast_height);
                    }
                }
            }
            NetworkCommand::BroadcastProof(response) => {
                let msg = ProofMessage {
                    response,
                    submitted_at: std::time::SystemTime::now()
                        .duration_since(std::time::UNIX_EPOCH)
                        .unwrap_or_default()
                        .as_secs(),
                };
                
                if let Ok(data) = serde_json::to_vec(&msg) {
                    if let Err(e) = self.swarm
                        .behaviour_mut()
                        .gossipsub
                        .publish(self.proof_topic.clone(), data)
                    {
                        tracing::debug!("P2P broadcast skipped (no peers): {}", e);
                    } else {
                        tracing::info!("📢 Broadcasted proof submission");
                    }
                }
            }
            NetworkCommand::BroadcastBlock(header, signer) => {
                // Collect current state snapshot to send with block
                let validators: Vec<ValidatorSnapshot> = self.state.get_all_validators()
                    .into_iter()
                    .map(|v| ValidatorSnapshot {
                        public_key: hex::encode(v.public_key),
                        balance: v.balance,
                        validations_count: v.validations_count,
                        reputation_score: v.reputation_score,
                        last_active_timestamp: v.last_active_timestamp,
                        nonce: v.nonce,
                    })
                    .collect();
                let mut msg = BlockMessage {
                    header: header.clone(),
                    proof_count: self.state.get_pending_proof_count(),
                    state_root_hex: hex::encode(header.prev_state_root),
                    new_state_root_hex: hex::encode(self.state.get_state_root()),
                    total_supply: self.state.get_total_supply(),
                    validators,
                    producer_pubkey: String::new(),
                    producer_signature: String::new(),
                    genesis_hash: hex::encode(self.state.get_genesis_hash()),
                };
                
                // Sign the block if we have a signing key
                if let Some((pubkey_hex, signing_key)) = signer {
                    use ed25519_dalek::Signer;
                    msg.producer_pubkey = pubkey_hex;
                    let payload = msg.signing_payload();
                    let sig = signing_key.sign(&payload);
                    msg.producer_signature = hex::encode(sig.to_bytes());
                }
                
                if let Ok(data) = serde_json::to_vec(&msg) {
                    if let Err(e) = self.swarm
                        .behaviour_mut()
                        .gossipsub
                        .publish(self.block_topic.clone(), data)
                    {
                        tracing::debug!("P2P broadcast skipped (no peers): {}", e);
                    } else {
                        tracing::info!("📢 Broadcasted new block {} (signed by {}...)", header.height,
                            &msg.producer_pubkey[..16.min(msg.producer_pubkey.len())]);
                    }
                }
            }
            NetworkCommand::DialPeer(addr_str) => {
                match addr_str.parse::<Multiaddr>() {
                    Ok(addr) => {
                        tracing::info!("🔗 Dialing peer: {}", addr);
                        match self.swarm.dial(addr.clone()) {
                            Ok(_) => {
                                tracing::info!("📞 Dial initiated to {}", addr);
                            }
                            Err(e) => {
                                tracing::error!("❌ Failed to dial {}: {}", addr, e);
                            }
                        }
                    }
                    Err(e) => {
                        tracing::error!("❌ Invalid multiaddr '{}': {}", addr_str, e);
                    }
                }
            }
            NetworkCommand::RequestStateSync => {
                // Request state from peers
                // Include a nonce so gossipsub doesn't reject repeated requests
                // as duplicates (message_id = SHA256(data), same data = same id)
                let nonce = std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_millis() as u64;
                let msg = StateRequestMessage {
                    requester_peer_id: self.local_peer_id.clone(),
                    current_height: self.state.get_height(),
                    nonce,
                };
                
                if let Ok(data) = serde_json::to_vec(&msg) {
                    if let Err(e) = self.swarm
                        .behaviour_mut()
                        .gossipsub
                        .publish(self.state_sync_topic.clone(), data)
                    {
                        tracing::debug!("P2P state sync request skipped (no peers): {}", e);
                    } else {
                        tracing::info!("📥 Requested state sync from peers (our height: {})", msg.current_height);
                    }
                }
            }
            NetworkCommand::BroadcastPresence(presence) => {
                // Broadcast our presence/heartbeat
                if let Ok(data) = serde_json::to_vec(&presence) {
                    if let Err(e) = self.swarm
                        .behaviour_mut()
                        .gossipsub
                        .publish(self.presence_topic.clone(), data)
                    {
                        tracing::debug!("Failed to broadcast presence: {}", e);
                    }
                }
            }
            NetworkCommand::BroadcastAIMessage(message) => {
                // Broadcast AI message to the network
                tracing::info!("🤖 Broadcasting AI message from {} to {}", 
                    &message.from_validator[..16.min(message.from_validator.len())],
                    if message.to_validator == "broadcast" { "all" } else { &message.to_validator[..16.min(message.to_validator.len())] }
                );
                if let Ok(data) = serde_json::to_vec(&message) {
                    if let Err(e) = self.swarm
                        .behaviour_mut()
                        .gossipsub
                        .publish(self.ai_message_topic.clone(), data)
                    {
                        tracing::warn!("Failed to broadcast AI message: {}", e);
                    }
                }
            }
            NetworkCommand::BroadcastRegistration(reg_msg) => {
                tracing::info!("📝 Broadcasting validator registration: {}...",
                    &reg_msg.public_key[..16.min(reg_msg.public_key.len())]);
                
                // Clone for potential retry
                let reg_msg_clone = reg_msg.clone();
                
                // Also apply locally so the broadcasting node registers itself
                let pubkey_bytes: [u8; 32] = match hex::decode(&reg_msg.public_key) {
                    Ok(bytes) if bytes.len() == 32 => bytes.try_into().unwrap(),
                    _ => {
                        tracing::error!("Invalid public key in registration broadcast");
                        return;
                    }
                };
                match self.state.apply_tx(crate::stf::NodeTx::RegisterValidator { public_key: pubkey_bytes }) {
                    crate::stf::TxResult::Registered { .. } => {
                        tracing::info!("✅ Self-registered via P2P broadcast");
                    }
                    crate::stf::TxResult::Error(e) if e.contains("already registered") => {
                        tracing::debug!("Already registered locally");
                    }
                    crate::stf::TxResult::Error(e) => {
                        tracing::warn!("⚠️ Local registration failed: {}", e);
                    }
                    _ => {}
                }
                
                if let Ok(data) = serde_json::to_vec(&TransactionTopicMessage::Registration(reg_msg)) {
                    if let Err(e) = self.swarm
                        .behaviour_mut()
                        .gossipsub
                        .publish(self.transaction_topic.clone(), data)
                    {
                        tracing::warn!("Failed to broadcast registration: {} — will retry when mesh forms", e);
                        self.pending_registrations.push(reg_msg_clone);
                    } else {
                        tracing::info!("📢 Registration broadcasted to P2P network");
                    }
                }
            }
            NetworkCommand::BroadcastGovernance(gov_msg) => {
                tracing::info!("📋 Broadcasting governance action via P2P");
                if let Ok(data) = serde_json::to_vec(&gov_msg) {
                    if let Err(e) = self.swarm
                        .behaviour_mut()
                        .gossipsub
                        .publish(self.governance_topic.clone(), data)
                    {
                        tracing::warn!("Failed to broadcast governance: {}", e);
                    } else {
                        tracing::info!("📢 Governance action broadcasted to P2P network");
                    }
                }
            }
            NetworkCommand::BroadcastTransfer(transfer_msg) => {
                tracing::info!("💸 Broadcasting transfer via P2P: {} SMITH from {}... to {}...",
                    transfer_msg.amount,
                    &transfer_msg.from[..16.min(transfer_msg.from.len())],
                    &transfer_msg.to[..16.min(transfer_msg.to.len())]);
                if let Ok(data) = serde_json::to_vec(&TransactionTopicMessage::Transfer(transfer_msg)) {
                    if let Err(e) = self.swarm
                        .behaviour_mut()
                        .gossipsub
                        .publish(self.transaction_topic.clone(), data)
                    {
                        tracing::warn!("Failed to broadcast transfer: {}", e);
                    } else {
                        tracing::info!("📢 Transfer broadcasted to P2P network");
                    }
                }
            }
            NetworkCommand::BroadcastUpgrade(announcement) => {
                tracing::info!("📦 Broadcasting upgrade v{} via P2P", announcement.version);
                if let Ok(data) = serde_json::to_vec(&announcement) {
                    let upgrade_topic = libp2p::gossipsub::IdentTopic::new(TOPIC_UPGRADES);
                    if let Err(e) = self.swarm
                        .behaviour_mut()
                        .gossipsub
                        .publish(upgrade_topic, data)
                    {
                        tracing::warn!("Failed to broadcast upgrade: {}", e);
                    } else {
                        tracing::info!("📢 Upgrade v{} broadcasted to P2P network", announcement.version);
                    }
                }
            }
            NetworkCommand::BroadcastPeerRelay(relay) => {
                tracing::info!("🌱 Broadcasting peer relay: v{} for {} at {}", relay.version, relay.platform, relay.relay_url);
                if let Ok(data) = serde_json::to_vec(&relay) {
                    if let Err(e) = self.swarm
                        .behaviour_mut()
                        .gossipsub
                        .publish(self.peer_relay_topic.clone(), data)
                    {
                        tracing::warn!("Failed to broadcast peer relay: {}", e);
                    } else {
                        tracing::info!("📢 Peer relay broadcasted to P2P network");
                    }
                }
            }
            NetworkCommand::BroadcastTurboBlock(height, prev_state_root, state_root, challenge_hash, total_supply) => {
                // Build block message for turbo mode with proper verification data
                let block = BlockHeader {
                    height,
                    prev_state_root,
                    tx_root: challenge_hash,
                    timestamp: std::time::SystemTime::now()
                        .duration_since(std::time::UNIX_EPOCH)
                        .unwrap_or_default()
                        .as_secs(),
                    challenge_hash,
                };
                let validators: Vec<ValidatorSnapshot> = self.state.get_all_validators()
                    .into_iter()
                    .map(|v| ValidatorSnapshot {
                        public_key: hex::encode(v.public_key),
                        balance: v.balance,
                        validations_count: v.validations_count,
                        reputation_score: v.reputation_score,
                        last_active_timestamp: v.last_active_timestamp,
                        nonce: v.nonce,
                    })
                    .collect();
                let mut block_msg = BlockMessage {
                    header: block,
                    proof_count: 0,
                    state_root_hex: hex::encode(prev_state_root),
                    new_state_root_hex: hex::encode(state_root),
                    total_supply,
                    validators,
                    producer_pubkey: String::new(),
                    producer_signature: String::new(),
                    genesis_hash: hex::encode(self.state.get_genesis_hash()),
                };
                // Sign if we have a validator signer
                if let Some((ref pubkey, ref signer)) = self.validator_signer {
                    block_msg.producer_pubkey = pubkey.clone();
                    let payload = block_msg.signing_payload();
                    let sig: ed25519_dalek::Signature = ed25519_dalek::Signer::sign(signer, &payload);
                    block_msg.producer_signature = hex::encode(sig.to_bytes());
                }
                if let Ok(block_data) = serde_json::to_vec(&block_msg) {
                    if let Err(e) = self.swarm
                        .behaviour_mut()
                        .gossipsub
                        .publish(self.block_topic.clone(), block_data)
                    {
                        tracing::debug!("Turbo block broadcast skipped (no peers): {}", e);
                    } else {
                        tracing::debug!("⚡ Turbo block {} broadcasted", height);
                    }
                }
            }
            NetworkCommand::BroadcastLivenessChallenge(challenge) => {
                if let Ok(data) = serde_json::to_vec(&challenge) {
                    if let Err(e) = self.swarm
                        .behaviour_mut()
                        .gossipsub
                        .publish(self.challenge_topic.clone(), data)
                    {
                        tracing::debug!("Liveness challenge broadcast skipped: {}", e);
                    } else {
                        tracing::info!("🧪 Liveness challenge sent to {}...", 
                            &challenge.target[..16.min(challenge.target.len())]);
                    }
                }
            }
            NetworkCommand::BroadcastLivenessResponse(response) => {
                if let Ok(data) = serde_json::to_vec(&response) {
                    if let Err(e) = self.swarm
                        .behaviour_mut()
                        .gossipsub
                        .publish(self.proof_topic.clone(), data)
                    {
                        tracing::debug!("Liveness response broadcast skipped: {}", e);
                    } else {
                        tracing::info!("✅ Liveness response sent for challenge {}", 
                            &response.challenge_id[..16.min(response.challenge_id.len())]);
                    }
                }
            }
        }
    }
    
    /// Handle state sync messages (requests and responses)
    async fn handle_state_sync_message(&mut self, data: &[u8]) {
        // Try to parse as a request first
        if let Ok(request) = serde_json::from_slice::<StateRequestMessage>(data) {
            // Someone is asking for state - respond if we have higher state
            let our_height = self.state.get_height();
            if our_height > request.current_height {
                tracing::info!("📤 Peer {} requested state (their height: {}, ours: {})",
                    &request.requester_peer_id[..16.min(request.requester_peer_id.len())],
                    request.current_height,
                    our_height
                );
                
                // Build and send state snapshot
                let validators: Vec<ValidatorSnapshot> = self.state.get_all_validators()
                    .into_iter()
                    .map(|v| ValidatorSnapshot {
                        public_key: hex::encode(v.public_key),
                        balance: v.balance,
                        validations_count: v.validations_count,
                        reputation_score: v.reputation_score,
                        last_active_timestamp: v.last_active_timestamp,
                        nonce: v.nonce,
                    })
                    .collect();
                
                // Get transaction records (limit to last 1000 for bandwidth)
                let tx_records: Vec<TxRecordSnapshot> = self.state.get_tx_records_for_sync()
                    .into_iter()
                    .map(|tx| TxRecordSnapshot {
                        hash: tx.hash,
                        tx_type: tx.tx_type,
                        from: tx.from,
                        to: tx.to,
                        amount: tx.amount,
                        status: tx.status,
                        timestamp: tx.timestamp,
                        height: tx.height,
                        validators: tx.validators,
                        challenge_hash: tx.challenge_hash,
                    })
                    .collect();
                
                let response = StateResponseMessage {
                    responder_peer_id: self.local_peer_id.clone(),
                    height: our_height,
                    state_root: hex::encode(self.state.get_state_root()),
                    total_supply: self.state.get_total_supply(),
                    validators,
                    tx_records,
                };
                
                if let Ok(response_data) = serde_json::to_vec(&response) {
                    let _ = self.swarm
                        .behaviour_mut()
                        .gossipsub
                        .publish(self.state_sync_topic.clone(), response_data);
                }
            }
            
            // Emit event
            let _ = self.event_tx.send(NetworkEvent::StateRequested(request.requester_peer_id)).await;
            return;
        }
        
        // Try to parse as a response
        if let Ok(response) = serde_json::from_slice::<StateResponseMessage>(data) {
            let our_height = self.state.get_height();
            
            // Only accept state that's newer than ours
            if response.height > our_height {
                tracing::info!("📥 Received state from peer {} (height: {}, {} validators)",
                    &response.responder_peer_id[..16.min(response.responder_peer_id.len())],
                    response.height,
                    response.validators.len()
                );
                
                // CRITICAL: Apply state directly here so it works during startup
                // before any event handler is spawned. Previously, state was only
                // applied by the event handler (spawned later), so state sync
                // responses received during the startup wait were never applied.
                let validators: Vec<crate::stf::ValidatorInfo> = response.validators.iter()
                    .filter_map(|v| {
                        let pubkey_bytes = hex::decode(&v.public_key).ok()?;
                        if pubkey_bytes.len() != 32 { return None; }
                        let mut pubkey = [0u8; 32];
                        pubkey.copy_from_slice(&pubkey_bytes);
                        Some(crate::stf::ValidatorInfo {
                            public_key: pubkey,
                            balance: v.balance,
                            validations_count: v.validations_count,
                            reputation_score: v.reputation_score,
                            last_active_timestamp: v.last_active_timestamp,
                            last_validation_height: 0,
                            is_online: true,
                            nonce: v.nonce,
                        })
                    })
                    .collect();
                
                let state_root_bytes = hex::decode(&response.state_root).unwrap_or_default();
                let mut state_root = [0u8; 32];
                if state_root_bytes.len() == 32 {
                    state_root.copy_from_slice(&state_root_bytes);
                }
                
                if self.state.apply_peer_state(
                    response.height,
                    state_root,
                    response.total_supply,
                    validators,
                ) {
                    tracing::info!("✅ P2P layer applied state sync: now at height {}", response.height);
                }
                
                // Also emit event so the event handler can merge tx_records etc.
                let _ = self.event_tx.send(NetworkEvent::StateReceived(response)).await;
            } else {
                tracing::debug!("Ignoring older state from peer (their height: {}, ours: {})",
                    response.height, our_height);
            }
        }
    }
    
    /// Handle incoming presence/heartbeat message
    /// SECURITY: Verifies signature to prevent impersonation
    async fn handle_presence_message(&mut self, data: &[u8]) {
        match serde_json::from_slice::<PresenceMessage>(data) {
            Ok(presence) => {
                // CRITICAL: Verify signature to prevent impersonation
                if !presence.verify_signature() {
                    tracing::warn!(
                        "⚠️ Rejecting unsigned/invalid presence from {}...",
                        &presence.validator_pubkey[..16.min(presence.validator_pubkey.len())]
                    );
                    return;
                }
                
                // Verify timestamp is recent (within 30 seconds) to prevent replay attacks.
                // Tighter window than before (was 2 minutes) to reduce replay attack surface.
                let now = std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_secs();
                
                if presence.timestamp > now + 10 || presence.timestamp < now.saturating_sub(30) {
                    tracing::debug!("Rejecting stale/future presence message (timestamp: {}, now: {})", presence.timestamp, now);
                    return;
                }
                
                // Track peer versions for release management
                get_version_tracker().record_version(&presence.version);
                
                // *** CRITICAL: Record this as a P2P-VERIFIED validator ***
                // Only validators sending signed presence via gossipsub are true P2P peers
                get_p2p_validator_tracker().record_presence(&presence);
                
                tracing::debug!(
                    "✅ P2P-verified validator: {}... (height={}, presences={})",
                    &presence.validator_pubkey[..16.min(presence.validator_pubkey.len())],
                    presence.height,
                    get_p2p_validator_tracker().validators.read_or_recover()
                        .get(&presence.validator_pubkey)
                        .map(|v| v.presence_count)
                        .unwrap_or(0)
                );
                
                // Update validator's online status in state
                self.state.update_validator_presence(
                    &presence.validator_pubkey,
                    presence.timestamp,
                    presence.height,
                );
                
                // Emit event for external handlers
                let _ = self.event_tx.send(NetworkEvent::PresenceReceived(presence)).await;
            }
            Err(e) => {
                tracing::debug!("Failed to parse presence message: {}", e);
            }
        }
    }

    /// Handle incoming upgrade announcement from trusted operator
    async fn handle_upgrade_message(&mut self, data: &[u8]) {
        match serde_json::from_slice::<UpgradeAnnouncement>(data) {
            Ok(upgrade) => {
                // Verify signature AND trusted operator status
                if !upgrade.verify() {
                    tracing::warn!(
                        "⚠️ Rejecting invalid/untrusted upgrade announcement v{}",
                        upgrade.version
                    );
                    return;
                }
                
                tracing::info!(
                    "📦 Received VERIFIED upgrade announcement: v{} from operator {}...",
                    upgrade.version,
                    &upgrade.operator_pubkey[..16]
                );
                
                // Store in version tracker
                get_version_tracker().record_upgrade(upgrade);
            }
            Err(e) => {
                tracing::debug!("Failed to parse upgrade message: {}", e);
            }
        }
    }
    
    /// Handle incoming peer relay announcement — a peer has the upgrade binary
    async fn handle_peer_relay_message(&mut self, data: &[u8]) {
        match serde_json::from_slice::<PeerRelayAnnouncement>(data) {
            Ok(relay) => {
                tracing::info!(
                    "🌱 Peer {} is relaying v{} for {} at {}",
                    &relay.peer_id[..12.min(relay.peer_id.len())],
                    relay.version,
                    relay.platform,
                    relay.relay_url
                );
                record_peer_relay(relay);
            }
            Err(e) => {
                tracing::debug!("Failed to parse peer relay message: {}", e);
            }
        }
    }
    
    /// Handle incoming transaction/registration message from P2P gossip
    /// Uses tagged enum TransactionTopicMessage to cleanly distinguish message types
    async fn handle_transaction_message(&mut self, data: &[u8]) {
        // First try the new tagged format
        let parsed = match serde_json::from_slice::<TransactionTopicMessage>(data) {
            Ok(msg) => msg,
            Err(_) => {
                // Backwards compatibility: try legacy untagged formats
                if let Ok(reg_msg) = serde_json::from_slice::<RegisterValidatorMessage>(data) {
                    TransactionTopicMessage::Registration(reg_msg)
                } else if let Ok(transfer_msg) = serde_json::from_slice::<TransferGossipMessage>(data) {
                    TransactionTopicMessage::Transfer(transfer_msg)
                } else {
                    tracing::debug!("Failed to parse transaction message");
                    return;
                }
            }
        };
        
        match parsed {
            TransactionTopicMessage::Registration(reg_msg) => {
                // Verify signature to prevent spoofed registrations
                if !reg_msg.verify_signature() {
                    tracing::warn!("⚠️ Rejecting registration with invalid signature from {}...",
                        &reg_msg.public_key[..16.min(reg_msg.public_key.len())]);
                    return;
                }
                
                // Verify timestamp is recent (within 5 minutes)
                let now = std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_secs();
                if reg_msg.timestamp > now + 60 || reg_msg.timestamp < now.saturating_sub(300) {
                    tracing::warn!("⚠️ Rejecting stale registration (timestamp: {})", reg_msg.timestamp);
                    return;
                }
                
                // Apply registration to local state
                let pubkey_bytes: [u8; 32] = match hex::decode(&reg_msg.public_key) {
                    Ok(bytes) if bytes.len() == 32 => bytes.try_into().unwrap(),
                    _ => {
                        tracing::warn!("⚠️ Invalid public key in registration");
                        return;
                    }
                };
                
                match self.state.apply_tx(crate::stf::NodeTx::RegisterValidator { public_key: pubkey_bytes }) {
                    crate::stf::TxResult::Registered { ref public_key } => {
                        tracing::info!("📝 P2P registration applied: {}... (via gossip)", &public_key[..16]);
                    }
                    crate::stf::TxResult::Error(e) if e.contains("already registered") => {
                        tracing::debug!("Validator {}... already registered (P2P duplicate)", &reg_msg.public_key[..16]);
                    }
                    crate::stf::TxResult::Error(e) => {
                        tracing::warn!("⚠️ P2P registration failed for {}...: {}", &reg_msg.public_key[..16], e);
                    }
                    _ => {}
                }
                
                // Emit event
                let _ = self.event_tx.send(NetworkEvent::RegistrationReceived(reg_msg)).await;
            }
            TransactionTopicMessage::Transfer(transfer_msg) => {
                let from: [u8; 32] = match hex::decode(&transfer_msg.from) {
                    Ok(b) if b.len() == 32 => b.try_into().unwrap(),
                    _ => { tracing::warn!("Invalid from key in transfer gossip"); return; }
                };
                let to: [u8; 32] = match hex::decode(&transfer_msg.to) {
                    Ok(b) if b.len() == 32 => b.try_into().unwrap(),
                    _ => { tracing::warn!("Invalid to key in transfer gossip"); return; }
                };
                let sig: [u8; 64] = match hex::decode(&transfer_msg.signature) {
                    Ok(b) if b.len() == 64 => b.try_into().unwrap(),
                    _ => { tracing::warn!("Invalid signature in transfer gossip"); return; }
                };
                
                let tx = crate::stf::NodeTx::Transfer {
                    from,
                    to,
                    amount: transfer_msg.amount,
                    nonce: transfer_msg.nonce,
                    signature: sig,
                };
                match self.state.apply_tx(tx) {
                    crate::stf::TxResult::Success { .. } => {
                        tracing::info!("💸 P2P transfer applied: {} SMITH from {}... to {}...",
                            transfer_msg.amount,
                            &transfer_msg.from[..16],
                            &transfer_msg.to[..16]);
                    }
                    crate::stf::TxResult::Error(e) => {
                        tracing::debug!("P2P transfer rejected: {}", e);
                    }
                    _ => {}
                }
                let _ = self.event_tx.send(NetworkEvent::TransferReceived(transfer_msg)).await;
            }
        }
    }
    
    /// Handle incoming AI-to-AI message
    async fn handle_ai_message(&mut self, data: &[u8]) {
        match serde_json::from_slice::<AINetworkMessage>(data) {
            Ok(msg) => {
                tracing::info!(
                    "🤖 AI Message received: {} → {} (type: {})",
                    &msg.from_validator[..16.min(msg.from_validator.len())],
                    if msg.to_validator == "broadcast" { "all".to_string() } else { msg.to_validator[..16.min(msg.to_validator.len())].to_string() },
                    msg.message_type
                );
                
                // SECURITY (M4): Always forward AI messages to the event handler.
                // Gossip networks relay all messages; the validator agent decides relevance.
                // Previously we filtered on get_validator() which dropped messages for
                // validators not yet synced to local state.
                let _ = self.event_tx.send(NetworkEvent::AIMessageReceived(msg)).await;
            }
            Err(e) => {
                tracing::debug!("Failed to parse AI message: {}", e);
            }
        }
    }

    /// Handle incoming governance message from P2P gossip
    async fn handle_governance_message(&mut self, data: &[u8]) {
        match serde_json::from_slice::<GovernanceGossipMessage>(data) {
            Ok(gov_msg) => {
                // Verify timestamp is recent (within 5 minutes)
                let now = std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_secs();
                if gov_msg.timestamp > now + 60 || gov_msg.timestamp < now.saturating_sub(300) {
                    tracing::warn!("⚠️ Rejecting stale governance message");
                    return;
                }
                
                // Apply governance action to local state
                match &gov_msg.action {
                    GovernanceAction::CreateProposal { proposer, proposal_type, new_value, description_hash, signature } => {
                        let proposer_bytes: [u8; 32] = match hex::decode(proposer) {
                            Ok(b) if b.len() == 32 => b.try_into().unwrap(),
                            _ => { tracing::warn!("Invalid proposer key in governance gossip"); return; }
                        };
                        let desc_bytes: [u8; 32] = match hex::decode(description_hash) {
                            Ok(b) if b.len() == 32 => b.try_into().unwrap(),
                            _ => { tracing::warn!("Invalid description hash in governance gossip"); return; }
                        };
                        let sig_bytes: [u8; 64] = match hex::decode(signature) {
                            Ok(b) if b.len() == 64 => b.try_into().unwrap(),
                            _ => { tracing::warn!("Invalid signature in governance gossip"); return; }
                        };
                        
                        let tx = crate::stf::NodeTx::CreateProposal {
                            proposer: proposer_bytes,
                            proposal_type: *proposal_type,
                            new_value: *new_value,
                            description_hash: desc_bytes,
                            signature: sig_bytes,
                        };
                        match self.state.apply_tx(tx) {
                            crate::stf::TxResult::ProposalCreated { proposal_id } => {
                                tracing::info!("📋 P2P governance: Proposal #{} applied from gossip", proposal_id);
                            }
                            crate::stf::TxResult::Error(e) => {
                                tracing::debug!("P2P governance proposal rejected: {}", e);
                            }
                            _ => {}
                        }
                    }
                    GovernanceAction::CastVote { voter, proposal_id, vote, signature, reason } => {
                        let voter_bytes: [u8; 32] = match hex::decode(voter) {
                            Ok(b) if b.len() == 32 => b.try_into().unwrap(),
                            _ => { tracing::warn!("Invalid voter key in governance gossip"); return; }
                        };
                        let sig_bytes: [u8; 64] = match hex::decode(signature) {
                            Ok(b) if b.len() == 64 => b.try_into().unwrap(),
                            _ => { tracing::warn!("Invalid signature in governance gossip"); return; }
                        };
                        
                        let tx = crate::stf::NodeTx::VoteProposal {
                            voter: voter_bytes,
                            proposal_id: *proposal_id,
                            vote: *vote,
                            signature: sig_bytes,
                            reason: reason.clone(),
                        };
                        match self.state.apply_tx(tx) {
                            crate::stf::TxResult::VoteRecorded { proposal_id, vote } => {
                                tracing::info!("🗳️ P2P governance: Vote on #{} ({}) applied from gossip", 
                                    proposal_id, if vote { "yes" } else { "no" });
                            }
                            crate::stf::TxResult::Error(e) => {
                                tracing::debug!("P2P governance vote rejected: {}", e);
                            }
                            _ => {}
                        }
                    }
                    GovernanceAction::ExecuteProposal { executor, proposal_id, signature } => {
                        let executor_bytes: [u8; 32] = match hex::decode(executor) {
                            Ok(b) if b.len() == 32 => b.try_into().unwrap(),
                            _ => { tracing::warn!("Invalid executor key in governance gossip"); return; }
                        };
                        let sig_bytes: [u8; 64] = match hex::decode(signature) {
                            Ok(b) if b.len() == 64 => b.try_into().unwrap(),
                            _ => { tracing::warn!("Invalid signature in governance gossip"); return; }
                        };
                        
                        let tx = crate::stf::NodeTx::ExecuteProposal {
                            executor: executor_bytes,
                            proposal_id: *proposal_id,
                            signature: sig_bytes,
                        };
                        match self.state.apply_tx(tx) {
                            crate::stf::TxResult::ProposalExecuted { proposal_id, .. } => {
                                tracing::info!("✅ P2P governance: Proposal #{} executed from gossip", proposal_id);
                            }
                            crate::stf::TxResult::Error(e) => {
                                tracing::debug!("P2P governance execute rejected: {}", e);
                            }
                            _ => {}
                        }
                    }
                }
                
                // Emit event
                let _ = self.event_tx.send(NetworkEvent::GovernanceReceived(gov_msg)).await;
            }
            Err(e) => {
                tracing::debug!("Failed to parse governance message: {}", e);
            }
        }
    }
}
