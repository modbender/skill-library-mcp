use std::collections::HashMap;

use serde::{Deserialize, Serialize};

/// Wire format for gossip bot announcements.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BotAnnouncement {
    pub node_id: String,
    pub name: String,
    pub version: String,
    pub capabilities: Vec<String>,
    #[serde(default)]
    pub openclaw_version: Option<String>,
    #[serde(default)]
    pub mode: Option<String>,
    pub timestamp: u64,
    pub ttl: u64,
    #[serde(default)]
    pub metadata: HashMap<String, String>,
}

/// Gossip message envelope.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum GossipMessage {
    Announce(BotAnnouncement),
    Leave {
        node_id: String,
        timestamp: u64,
    },
}

impl GossipMessage {
    /// Serialize to bytes for gossip wire format.
    pub fn to_bytes(&self) -> Vec<u8> {
        postcard::to_allocvec(self).expect("serialization failed")
    }

    /// Deserialize from gossip wire bytes.
    pub fn from_bytes(bytes: &[u8]) -> anyhow::Result<Self> {
        postcard::from_bytes(bytes).map_err(Into::into)
    }
}

/// Cached peer record for the local peer store.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PeerInfo {
    pub node_id: String,
    pub name: String,
    pub capabilities: Vec<String>,
    pub last_seen: u64,
    pub ttl: u64,
    #[serde(default)]
    pub addresses: Vec<String>,
    #[serde(default)]
    pub metadata: HashMap<String, String>,
}

impl PeerInfo {
    /// Check if this peer record has expired.
    pub fn is_expired(&self) -> bool {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        now > self.last_seen + self.ttl
    }
}

/// Message sent over direct QUIC connections.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DirectMessage {
    pub from: String,
    pub content: String,
    pub timestamp: u64,
}

impl DirectMessage {
    pub fn to_bytes(&self) -> Vec<u8> {
        postcard::to_allocvec(self).expect("serialization failed")
    }

    pub fn from_bytes(bytes: &[u8]) -> anyhow::Result<Self> {
        postcard::from_bytes(bytes).map_err(Into::into)
    }
}

/// ALPN protocol identifier for direct messaging.
pub const MSG_ALPN: &[u8] = b"clawnet/msg/1";

/// Wire protocol version byte for `WireMessage` framing.
const WIRE_VERSION: u8 = 0x01;

/// Extended wire message types for social features.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum WireMessage {
    /// Legacy text message (wraps DirectMessage).
    Text(DirectMessage),
    /// Ping request for latency measurement.
    Ping {
        from: String,
        seq: u32,
        timestamp: u64,
    },
    /// Pong response to a ping.
    Pong {
        from: String,
        seq: u32,
        echo_timestamp: u64,
        timestamp: u64,
    },
    /// Interactive chat message.
    Chat {
        from: String,
        content: String,
        timestamp: u64,
    },
    /// Signal end of chat session.
    ChatEnd {
        from: String,
        timestamp: u64,
    },
}

impl WireMessage {
    /// Serialize with version-byte prefix.
    pub fn to_bytes(&self) -> Vec<u8> {
        let payload = postcard::to_allocvec(self).expect("serialization failed");
        let mut buf = Vec::with_capacity(1 + payload.len());
        buf.push(WIRE_VERSION);
        buf.extend_from_slice(&payload);
        buf
    }

    /// Deserialize: checks for version prefix, falls back to legacy DirectMessage.
    pub fn from_bytes(bytes: &[u8]) -> anyhow::Result<Self> {
        if bytes.first() == Some(&WIRE_VERSION) {
            postcard::from_bytes(&bytes[1..]).map_err(Into::into)
        } else {
            // Legacy: bare DirectMessage without version prefix
            let dm: DirectMessage = postcard::from_bytes(bytes)?;
            Ok(WireMessage::Text(dm))
        }
    }
}

/// Write a length-prefixed message to a QUIC send stream.
pub async fn write_length_prefixed(
    send: &mut iroh::endpoint::SendStream,
    data: &[u8],
) -> anyhow::Result<()> {
    use anyhow::Context;
    let len = data.len() as u32;
    send.write_all(&len.to_be_bytes())
        .await
        .context("failed to write message length")?;
    send.write_all(data)
        .await
        .context("failed to write message body")?;
    Ok(())
}

/// Read a length-prefixed message from a QUIC recv stream.
pub async fn read_length_prefixed(
    recv: &mut iroh::endpoint::RecvStream,
) -> anyhow::Result<Vec<u8>> {
    let mut len_buf = [0u8; 4];
    recv.read_exact(&mut len_buf).await?;
    let len = u32::from_be_bytes(len_buf) as usize;
    if len > 1024 * 1024 {
        anyhow::bail!("message too large: {len} bytes");
    }
    let mut buf = vec![0u8; len];
    recv.read_exact(&mut buf).await?;
    Ok(buf)
}

/// Get the current unix timestamp.
pub fn now_secs() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs()
}
