use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;

use anyhow::{Context, Result};

use crate::config;
use crate::protocol::PeerInfo;

/// Get the path to the peer cache file.
fn store_path() -> Result<PathBuf> {
    let dir = config::data_dir()?;
    Ok(dir.join("peers.json"))
}

/// Load cached peers from disk.
pub fn load() -> Result<HashMap<String, PeerInfo>> {
    let path = store_path()?;
    if !path.exists() {
        return Ok(HashMap::new());
    }
    let contents = fs::read_to_string(&path).context("failed to read peer cache")?;
    let peers: HashMap<String, PeerInfo> =
        serde_json::from_str(&contents).context("failed to parse peer cache")?;
    Ok(peers)
}

/// Save peers to disk.
pub fn save(peers: &HashMap<String, PeerInfo>) -> Result<()> {
    let path = store_path()?;
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).context("failed to create data directory")?;
    }
    let contents = serde_json::to_string_pretty(peers).context("failed to serialize peers")?;
    fs::write(&path, contents).context("failed to write peer cache")?;
    Ok(())
}

/// Add or update a peer in the cache.
pub fn upsert(peer: PeerInfo) -> Result<()> {
    let mut peers = load()?;
    peers.insert(peer.node_id.clone(), peer);
    save(&peers)
}

/// Remove expired peers from the cache.
pub fn prune_expired() -> Result<usize> {
    let mut peers = load()?;
    let before = peers.len();
    peers.retain(|_, p| !p.is_expired());
    let removed = before - peers.len();
    if removed > 0 {
        save(&peers)?;
    }
    Ok(removed)
}

/// Get all peers, optionally filtering expired ones.
pub fn list(include_expired: bool) -> Result<Vec<PeerInfo>> {
    let peers = load()?;
    let mut result: Vec<PeerInfo> = if include_expired {
        peers.into_values().collect()
    } else {
        peers.into_values().filter(|p| !p.is_expired()).collect()
    };
    result.sort_by(|a, b| b.last_seen.cmp(&a.last_seen));
    Ok(result)
}
