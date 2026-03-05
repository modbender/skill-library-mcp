//! Persistent storage for SmithNode state
//!
//! Stores blockchain state to disk so it survives restarts.
//! Includes a Write-Ahead Log (WAL) for crash-safe state transitions.

use std::path::PathBuf;
use std::fs;
use std::io::{BufRead, Write};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

use crate::stf::{ValidatorInfo, TxRecord, GovernanceState};

/// A single WAL entry representing a state transition
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct WalEntry {
    /// Monotonically increasing sequence number
    pub seq: u64,
    /// The type of operation being performed
    pub op: WalOp,
    /// Unix timestamp (seconds) when the entry was written
    pub timestamp: u64,
}

/// The operation types recorded in the WAL
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum WalOp {
    /// A block was finalized
    BlockFinalized {
        height: u64,
        state_root_hex: String,
        total_supply: u64,
    },
    /// A validator was registered
    ValidatorRegistered {
        pubkey_hex: String,
    },
    /// A proof was accepted (reward distributed)
    ProofAccepted {
        validator_pubkey_hex: String,
        challenge_hash_hex: String,
        reward: u64,
    },
    /// A transfer was processed
    Transfer {
        from_hex: String,
        to_hex: String,
        amount: u64,
    },
    /// A validator was slashed
    ValidatorSlashed {
        pubkey_hex: String,
        penalty: u64,
    },
    /// State sync applied from a peer
    StateSynced {
        height: u64,
        state_root_hex: String,
    },
    /// Governance action (proposal/vote/execute)
    GovernanceAction {
        action: String,
        detail: String,
    },
    /// Full state checkpoint committed — all prior entries are superseded
    Checkpoint {
        height: u64,
    },
}

/// Persistent state that gets saved to disk
#[derive(Clone, Debug, Serialize, Deserialize, Default)]
pub struct PersistedState {
    pub validators: HashMap<String, ValidatorInfo>,
    pub height: u64,
    pub state_root: [u8; 32],
    pub tx_records: Vec<TxRecord>,
    pub total_supply: u64,
    /// Governance state (proposals, params, history)
    #[serde(default)]
    pub governance: GovernanceState,
    /// Genesis hash - unique per chain instance, changes on reset
    #[serde(default)]
    pub genesis_hash: [u8; 32],
}

/// Storage manager for blockchain data
pub struct Storage {
    data_dir: PathBuf,
    wal_seq: std::sync::atomic::AtomicU64,
}

impl Storage {
    /// Create a new storage manager
    pub fn new(data_dir: PathBuf) -> Self {
        // Create data directory if it doesn't exist
        if !data_dir.exists() {
            fs::create_dir_all(&data_dir).expect("Failed to create data directory");
        }
        Self {
            data_dir,
            wal_seq: std::sync::atomic::AtomicU64::new(0),
        }
    }

    /// Get the default data directory
    pub fn default_data_dir() -> PathBuf {
        dirs::home_dir()
            .unwrap_or_else(|| PathBuf::from("."))
            .join(".smithnode")
    }

    /// Get the state file path
    fn state_path(&self) -> PathBuf {
        self.data_dir.join("state.json")
    }

    /// Reset state file to fresh genesis (safer than delete))
    pub fn reset_state_file(&self) -> anyhow::Result<()> {
        let path = self.state_path();
        // Write an empty genesis state instead of deleting (safer for sandboxed environments)
        let empty_state = PersistedState::default();
        let json = serde_json::to_string_pretty(&empty_state)?;
        fs::write(&path, json)?;
        tracing::info!("🔄 Reset state file to genesis: {:?}", path);
        Ok(())
    }

    /// Load state from disk
    pub fn load_state(&self) -> Option<PersistedState> {
        let path = self.state_path();
        if path.exists() {
            match fs::read_to_string(&path) {
                Ok(contents) => {
                    match serde_json::from_str(&contents) {
                        Ok(state) => {
                            tracing::info!("📂 Loaded state from {:?}", path);
                            Some(state)
                        }
                        Err(e) => {
                            tracing::warn!("Failed to parse state file: {}", e);
                            None
                        }
                    }
                }
                Err(e) => {
                    tracing::warn!("Failed to read state file: {}", e);
                    None
                }
            }
        } else {
            tracing::info!("📂 No existing state found, starting fresh");
            None
        }
    }

    /// Save state to disk
    /// SECURITY (M6): Uses write-to-temp-then-rename for atomic writes.
    /// Prevents corruption if the process crashes mid-write.
    pub fn save_state(&self, state: &PersistedState) -> anyhow::Result<()> {
        let path = self.state_path();
        let contents = serde_json::to_string_pretty(state)?;
        
        // Write to a temporary file first, then atomically rename
        let tmp_path = path.with_extension("json.tmp");
        fs::write(&tmp_path, contents)?;
        fs::rename(&tmp_path, &path)?;
        
        // After successful checkpoint, write a Checkpoint WAL entry and truncate
        let _ = self.wal_append(WalOp::Checkpoint { height: state.height });
        self.wal_truncate();
        
        tracing::debug!("💾 State saved atomically to {:?} (WAL truncated)", path);
        Ok(())
    }

    // ─── Write-Ahead Log (WAL) ─────────────────────────────────────────

    /// Get the WAL file path
    fn wal_path(&self) -> PathBuf {
        self.data_dir.join("wal.jsonl")
    }

    /// Append a WAL entry to the log file.
    /// The entry is fsync'd to ensure it's on disk before returning.
    pub fn wal_append(&self, op: WalOp) -> anyhow::Result<()> {
        let seq = self.wal_seq.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
        let entry = WalEntry {
            seq,
            op,
            timestamp: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_secs(),
        };
        let mut line = serde_json::to_string(&entry)?;
        line.push('\n');

        let wal_path = self.wal_path();
        let file = fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(&wal_path)?;
        let mut writer = std::io::BufWriter::new(&file);
        writer.write_all(line.as_bytes())?;
        writer.flush()?;
        file.sync_all()?;

        Ok(())
    }

    /// Read all WAL entries from disk (used for recovery on startup).
    /// Silently skips malformed lines.
    pub fn wal_read(&self) -> Vec<WalEntry> {
        let wal_path = self.wal_path();
        if !wal_path.exists() {
            return Vec::new();
        }
        let file = match fs::File::open(&wal_path) {
            Ok(f) => f,
            Err(e) => {
                tracing::warn!("⚠️ Failed to open WAL for recovery: {}", e);
                return Vec::new();
            }
        };
        let reader = std::io::BufReader::new(file);
        let mut entries = Vec::new();
        for (line_num, line) in reader.lines().enumerate() {
            match line {
                Ok(text) => {
                    if text.trim().is_empty() {
                        continue;
                    }
                    match serde_json::from_str::<WalEntry>(&text) {
                        Ok(entry) => entries.push(entry),
                        Err(e) => {
                            tracing::warn!("⚠️ WAL line {} malformed, skipping: {}", line_num + 1, e);
                        }
                    }
                }
                Err(e) => {
                    tracing::warn!("⚠️ WAL read error at line {}: {}", line_num + 1, e);
                    break; // Truncated file — stop here
                }
            }
        }
        // Update sequence counter to continue from highest seen
        if let Some(max_seq) = entries.iter().map(|e| e.seq).max() {
            self.wal_seq.store(max_seq + 1, std::sync::atomic::Ordering::SeqCst);
        }
        entries
    }

    /// Truncate (clear) the WAL file after a successful state checkpoint.
    /// This is safe because the full state has been atomically saved.
    pub fn wal_truncate(&self) {
        let wal_path = self.wal_path();
        if wal_path.exists() {
            if let Err(e) = fs::write(&wal_path, b"") {
                tracing::warn!("⚠️ Failed to truncate WAL: {}", e);
            }
        }
    }

    /// Check if there are uncommitted WAL entries (i.e. the WAL is non-empty).
    /// Called on startup to detect a crash that happened between WAL writes
    /// and the state checkpoint.
    pub fn has_uncommitted_wal(&self) -> bool {
        let entries = self.wal_read();
        // If the only entry is a Checkpoint, there's nothing to recover
        if entries.len() == 1 {
            if let WalOp::Checkpoint { .. } = entries[0].op {
                return false;
            }
        }
        // Find entries after the last checkpoint
        let last_checkpoint_idx = entries.iter().rposition(|e| matches!(e.op, WalOp::Checkpoint { .. }));
        match last_checkpoint_idx {
            Some(idx) => idx + 1 < entries.len(), // entries after the checkpoint
            None => !entries.is_empty(),           // no checkpoint at all
        }
    }

    /// Get WAL entries that occurred after the last checkpoint (uncommitted work).
    pub fn uncommitted_wal_entries(&self) -> Vec<WalEntry> {
        let entries = self.wal_read();
        let last_checkpoint_idx = entries.iter().rposition(|e| matches!(e.op, WalOp::Checkpoint { .. }));
        match last_checkpoint_idx {
            Some(idx) => entries[idx + 1..].to_vec(),
            None => entries,
        }
    }
}
