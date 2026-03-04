use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;

use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};

use crate::config;

/// A local friend record.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FriendInfo {
    pub node_id: String,
    #[serde(default)]
    pub alias: Option<String>,
    pub added_at: u64,
}

/// Get the path to the friends store file.
fn store_path() -> Result<PathBuf> {
    let dir = config::data_dir()?;
    Ok(dir.join("friends.json"))
}

/// Load all friends from disk.
pub fn load() -> Result<HashMap<String, FriendInfo>> {
    let path = store_path()?;
    if !path.exists() {
        return Ok(HashMap::new());
    }
    let contents = fs::read_to_string(&path).context("failed to read friends store")?;
    let friends: HashMap<String, FriendInfo> =
        serde_json::from_str(&contents).context("failed to parse friends store")?;
    Ok(friends)
}

/// Save all friends to disk.
pub fn save(friends: &HashMap<String, FriendInfo>) -> Result<()> {
    let path = store_path()?;
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).context("failed to create data directory")?;
    }
    let contents =
        serde_json::to_string_pretty(friends).context("failed to serialize friends")?;
    fs::write(&path, contents).context("failed to write friends store")?;
    Ok(())
}

/// Add a friend. Overwrites alias if already present.
pub fn add(node_id: &str, alias: Option<&str>) -> Result<FriendInfo> {
    let mut friends = load()?;
    let info = FriendInfo {
        node_id: node_id.to_string(),
        alias: alias.map(|s| s.to_string()),
        added_at: crate::protocol::now_secs(),
    };
    friends.insert(node_id.to_string(), info.clone());
    save(&friends)?;
    Ok(info)
}

/// Remove a friend. Returns true if the friend existed.
pub fn remove(node_id: &str) -> Result<bool> {
    let mut friends = load()?;
    let existed = friends.remove(node_id).is_some();
    if existed {
        save(&friends)?;
    }
    Ok(existed)
}

/// List all friends sorted by added_at (newest first).
pub fn list() -> Result<Vec<FriendInfo>> {
    let friends = load()?;
    let mut result: Vec<FriendInfo> = friends.into_values().collect();
    result.sort_by(|a, b| b.added_at.cmp(&a.added_at));
    Ok(result)
}

/// Check if a node ID is a friend.
pub fn is_friend(node_id: &str) -> Result<bool> {
    let friends = load()?;
    Ok(friends.contains_key(node_id))
}
