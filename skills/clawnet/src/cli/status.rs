use anyhow::Result;

use crate::output::{self, DaemonStatusOutput};
use crate::store;

pub fn run(json: bool) -> Result<()> {
    // Check peer store for recent activity
    let peers = store::list(false)?;

    output::print(
        &DaemonStatusOutput {
            running: false,
            node_id: None,
            uptime_secs: None,
            peers_discovered: peers.len(),
            announcements_sent: 0,
        },
        json,
    );
    Ok(())
}
