use anyhow::{Context, Result};
use iroh::EndpointId;
use iroh_gossip::net::Gossip;
use iroh_gossip::proto::TopicId;
use sha2::{Digest, Sha256};

/// The topic string used for OpenClaw bot discovery.
const DISCOVERY_TOPIC: &str = "openclaw-bot-discovery-v1";

/// Derive the TopicId from the discovery topic string.
pub fn discovery_topic() -> TopicId {
    let hash = Sha256::digest(DISCOVERY_TOPIC.as_bytes());
    TopicId::from_bytes(hash.into())
}

/// Subscribe to the discovery topic and return sender/receiver handles.
pub async fn subscribe(
    gossip: &Gossip,
    bootstrap_peers: Vec<EndpointId>,
) -> Result<iroh_gossip::api::GossipTopic> {
    let topic = discovery_topic();
    let sub = gossip
        .subscribe_and_join(topic, bootstrap_peers)
        .await
        .context("failed to subscribe to discovery topic")?;
    Ok(sub)
}
