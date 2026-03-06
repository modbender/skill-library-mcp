use anyhow::Result;

use crate::friends;
use crate::output::{self, FriendAddOutput, FriendEntry, FriendListOutput};

pub fn add(node_id: &str, alias: Option<&str>, json: bool) -> Result<()> {
    let info = friends::add(node_id, alias)?;
    output::print(
        &FriendAddOutput {
            status: "added".to_string(),
            node_id: info.node_id,
            alias: info.alias,
        },
        json,
    );
    Ok(())
}

pub fn remove(node_id: &str, json: bool) -> Result<()> {
    let existed = friends::remove(node_id)?;
    let status = if existed { "removed" } else { "not found" };
    output::print(
        &FriendAddOutput {
            status: status.to_string(),
            node_id: node_id.to_string(),
            alias: None,
        },
        json,
    );
    Ok(())
}

pub fn list(json: bool) -> Result<()> {
    let all = friends::list()?;
    let count = all.len();
    let entries: Vec<FriendEntry> = all
        .into_iter()
        .map(|f| FriendEntry {
            node_id: f.node_id,
            alias: f.alias,
            added_at: f.added_at,
        })
        .collect();
    output::print(&FriendListOutput { friends: entries, count }, json);
    Ok(())
}
