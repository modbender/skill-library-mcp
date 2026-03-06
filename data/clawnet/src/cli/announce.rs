use std::time::Duration;

use anyhow::Result;

use crate::config;
use crate::gossip;
use crate::node::ClawNode;
use crate::output::{self, AnnounceOutput};
use crate::protocol::{self, BotAnnouncement, GossipMessage};

pub async fn run(
    name: Option<String>,
    capabilities: Vec<String>,
    duration_secs: u64,
    json: bool,
) -> Result<()> {
    let cfg = config::load()?;
    let node = ClawNode::spawn().await?;

    let node_id = node.endpoint.id().to_string();
    let bot_name = name.unwrap_or(cfg.name.clone());
    let caps = if capabilities.is_empty() {
        cfg.capabilities.clone()
    } else {
        capabilities
    };

    let announcement = GossipMessage::Announce(BotAnnouncement {
        node_id: node_id.clone(),
        name: bot_name.clone(),
        version: env!("CARGO_PKG_VERSION").to_string(),
        capabilities: caps.clone(),
        openclaw_version: cfg.openclaw_version.clone(),
        mode: cfg.mode.clone(),
        timestamp: protocol::now_secs(),
        ttl: cfg.peer_ttl,
        metadata: cfg.metadata.clone(),
    });

    let topic = gossip::subscribe(&node.gossip, vec![]).await?;
    let (sender, _receiver) = topic.split();

    if !json {
        eprintln!("Announcing presence for {duration_secs}s...");
    }

    sender
        .broadcast(announcement.to_bytes().into())
        .await?;

    // Keep node alive for the specified duration so peers can discover us
    tokio::time::sleep(Duration::from_secs(duration_secs)).await;

    output::print(
        &AnnounceOutput {
            status: "announced".to_string(),
            node_id,
            name: bot_name,
            capabilities: caps,
        },
        json,
    );

    node.shutdown().await?;
    Ok(())
}
