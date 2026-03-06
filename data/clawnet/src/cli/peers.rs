use anyhow::Result;

use crate::output::{self, PeerEntry, PeerListOutput};
use crate::store;

pub fn run(online_only: bool, json: bool) -> Result<()> {
    let include_expired = !online_only;
    let peers = store::list(include_expired)?;

    let entries: Vec<PeerEntry> = peers
        .iter()
        .map(|p| PeerEntry {
            node_id: p.node_id.clone(),
            name: p.name.clone(),
            capabilities: p.capabilities.clone(),
            last_seen: chrono::DateTime::from_timestamp(p.last_seen as i64, 0)
                .map(|dt| dt.to_rfc3339())
                .unwrap_or_else(|| p.last_seen.to_string()),
            expired: p.is_expired(),
        })
        .collect();

    let count = entries.len();
    output::print(&PeerListOutput { peers: entries, count }, json);
    Ok(())
}
