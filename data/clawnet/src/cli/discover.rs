use std::time::Duration;

use anyhow::Result;
use futures_lite::StreamExt;
use iroh_gossip::api::Event;

use crate::gossip;
use crate::node::ClawNode;
use crate::output::{self, DiscoverOutput, PeerEntry};
use crate::protocol::{self, GossipMessage, PeerInfo};
use crate::store;

pub async fn run(timeout_secs: u64, max_peers: Option<usize>, json: bool) -> Result<()> {
    let node = ClawNode::spawn().await?;

    let topic = gossip::subscribe(&node.gossip, vec![]).await?;
    let (_sender, mut receiver) = topic.split();

    let mut discovered: Vec<PeerInfo> = Vec::new();
    let deadline = tokio::time::Instant::now() + Duration::from_secs(timeout_secs);

    if !json {
        eprintln!("Discovering peers (timeout: {timeout_secs}s)...");
    }

    loop {
        tokio::select! {
            _ = tokio::time::sleep_until(deadline) => break,
            event = receiver.try_next() => {
                match event {
                    Ok(Some(Event::Received(msg))) => {
                        if let Ok(GossipMessage::Announce(ann)) = GossipMessage::from_bytes(&msg.content) {
                            // Skip self
                            if ann.node_id == node.endpoint.id().to_string() {
                                continue;
                            }
                            let peer = PeerInfo {
                                node_id: ann.node_id.clone(),
                                name: ann.name.clone(),
                                capabilities: ann.capabilities.clone(),
                                last_seen: protocol::now_secs(),
                                ttl: ann.ttl,
                                addresses: vec![],
                                metadata: ann.metadata.clone(),
                            };
                            // Deduplicate
                            if !discovered.iter().any(|p| p.node_id == peer.node_id) {
                                store::upsert(peer.clone())?;
                                discovered.push(peer);
                            }
                            if let Some(max) = max_peers {
                                if discovered.len() >= max {
                                    break;
                                }
                            }
                        }
                    }
                    Ok(Some(_)) => {}
                    Ok(None) => break,
                    Err(_) => break,
                }
            }
        }
    }

    let entries: Vec<PeerEntry> = discovered
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
    output::print(
        &DiscoverOutput {
            discovered: entries,
            count,
            timeout_secs,
        },
        json,
    );

    node.shutdown().await?;
    Ok(())
}
