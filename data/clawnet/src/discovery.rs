use std::net::SocketAddr;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;

use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use tokio::net::UdpSocket;

/// Well-known UDP port for ClawNet discovery probes.
pub const CLAWNET_DISCOVERY_PORT: u16 = 19851;

/// Magic bytes identifying a ClawNet discovery probe.
pub const PROBE_MAGIC: [u8; 4] = [0x43, 0x4C, 0x41, 0x57]; // "CLAW"

/// Protocol version for discovery probes.
pub const PROBE_VERSION: u8 = 0x01;

/// Minimum probe size (4 magic + 1 version).
const PROBE_SIZE: usize = 5;

/// Maximum UDP response payload (safe without fragmentation).
const MAX_RESPONSE_SIZE: usize = 508;

/// Response payload sent back to scanners.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScanResponse {
    pub node_id: String,
    pub name: String,
    pub version: String,
    pub capabilities: Vec<String>,
    pub quic_port: u16,
}

/// Listens for UDP discovery probes and responds with bot information.
pub struct DiscoveryListener {
    socket: UdpSocket,
    node_id: String,
    name: String,
    version: String,
    capabilities: Vec<String>,
    quic_port: u16,
    shutdown: Arc<AtomicBool>,
}

impl DiscoveryListener {
    /// Bind to the discovery port and create a new listener.
    pub async fn bind(
        port: u16,
        node_id: String,
        name: String,
        capabilities: Vec<String>,
        quic_port: u16,
        shutdown: Arc<AtomicBool>,
    ) -> Result<Self> {
        let addr: SocketAddr = ([0, 0, 0, 0], port).into();
        let socket = UdpSocket::bind(addr)
            .await
            .with_context(|| format!("failed to bind discovery listener on port {port}"))?;
        tracing::info!(port, "discovery listener bound");
        Ok(Self {
            socket,
            node_id,
            name,
            version: env!("CARGO_PKG_VERSION").to_string(),
            capabilities,
            quic_port,
            shutdown,
        })
    }

    /// Run the listener loop, responding to valid probes.
    pub async fn listen(&self) {
        let mut buf = [0u8; 16];
        loop {
            if self.shutdown.load(Ordering::Relaxed) {
                break;
            }

            let (len, src) = match tokio::time::timeout(
                std::time::Duration::from_secs(1),
                self.socket.recv_from(&mut buf),
            )
            .await
            {
                Ok(Ok(result)) => result,
                Ok(Err(e)) => {
                    tracing::debug!("discovery recv error: {e}");
                    continue;
                }
                Err(_) => continue, // timeout, check shutdown flag
            };

            if len < PROBE_SIZE {
                continue;
            }
            if buf[..4] != PROBE_MAGIC {
                continue;
            }
            if buf[4] != PROBE_VERSION {
                continue;
            }

            if let Err(e) = self.send_response(src).await {
                tracing::debug!("failed to send discovery response to {src}: {e}");
            }
        }
        tracing::info!("discovery listener stopped");
    }

    async fn send_response(&self, dest: SocketAddr) -> Result<()> {
        let mut response = ScanResponse {
            node_id: self.node_id.clone(),
            name: self.name.clone(),
            version: self.version.clone(),
            capabilities: self.capabilities.clone(),
            quic_port: self.quic_port,
        };

        // Header: 4 magic + 1 version = 5 bytes
        let header_size = PROBE_SIZE;
        let max_payload = MAX_RESPONSE_SIZE - header_size;

        let mut payload = postcard::to_allocvec(&response)
            .context("failed to serialize scan response")?;

        // Truncate capabilities if payload too large
        while payload.len() > max_payload && !response.capabilities.is_empty() {
            response.capabilities.pop();
            payload = postcard::to_allocvec(&response)
                .context("failed to serialize scan response")?;
        }

        // Truncate name as last resort
        if payload.len() > max_payload {
            response.name = response.name.chars().take(16).collect::<String>() + "...";
            payload = postcard::to_allocvec(&response)
                .context("failed to serialize scan response")?;
        }

        let mut packet = Vec::with_capacity(header_size + payload.len());
        packet.extend_from_slice(&PROBE_MAGIC);
        packet.push(PROBE_VERSION);
        packet.extend_from_slice(&payload);

        self.socket.send_to(&packet, dest).await?;
        tracing::debug!(dest = %dest, "sent discovery response");
        Ok(())
    }
}

/// Build a probe packet (5 bytes).
pub fn build_probe() -> [u8; PROBE_SIZE] {
    let mut probe = [0u8; PROBE_SIZE];
    probe[..4].copy_from_slice(&PROBE_MAGIC);
    probe[4] = PROBE_VERSION;
    probe
}

/// Parse a discovery response packet into a ScanResponse.
pub fn parse_response(data: &[u8]) -> Result<ScanResponse> {
    if data.len() < PROBE_SIZE {
        anyhow::bail!("response too short: {} bytes", data.len());
    }
    if data[..4] != PROBE_MAGIC {
        anyhow::bail!("invalid magic bytes");
    }
    if data[4] != PROBE_VERSION {
        anyhow::bail!("unsupported protocol version: {}", data[4]);
    }
    postcard::from_bytes(&data[PROBE_SIZE..])
        .context("failed to deserialize scan response")
}
