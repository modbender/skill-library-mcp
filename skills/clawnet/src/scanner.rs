use std::collections::HashMap;
use std::net::{IpAddr, SocketAddr};
use std::sync::Arc;
use std::time::Instant;

use anyhow::{Context, Result};
use ipnet::IpNet;
use serde::{Deserialize, Serialize};
use tokio::net::UdpSocket;
use tokio::sync::Mutex;

use crate::discovery;
use crate::protocol::PeerInfo;
use crate::store;

/// Configuration for a scan operation.
#[derive(Debug, Clone)]
pub struct ScanConfig {
    pub timeout_ms: u64,
    pub concurrency: usize,
    pub port: u16,
}

/// A single discovered bot from scanning.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScanResult {
    pub ip: IpAddr,
    pub node_id: String,
    pub name: String,
    pub version: String,
    pub capabilities: Vec<String>,
    pub quic_port: u16,
    pub rtt_ms: f64,
}

/// Aggregate statistics for a scan run.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScanStats {
    pub total_ips: usize,
    pub responses: usize,
    pub duration_ms: u64,
}

/// Maximum IPs allowed in a single scan (prevent accidental DoS).
const MAX_SCAN_IPS: usize = 1_048_576; // /12 for IPv4

/// Estimate host count from prefix length without iterating.
fn estimate_host_count(net: &IpNet) -> u64 {
    let host_bits = match net {
        IpNet::V4(n) => 32 - n.prefix_len() as u64,
        IpNet::V6(n) => 128 - n.prefix_len() as u64,
    };
    if host_bits == 0 {
        1
    } else if host_bits >= 64 {
        u64::MAX
    } else {
        let total = 1u64 << host_bits;
        if host_bits <= 1 { total } else { total.saturating_sub(2) }
    }
}

/// Scan a CIDR range for ClawNet bots.
pub async fn scan(range: &str, config: ScanConfig) -> Result<(Vec<ScanResult>, ScanStats)> {
    let net: IpNet = range.parse().context("invalid CIDR range")?;

    // Check size before iterating to avoid OOM on huge ranges
    let estimated = estimate_host_count(&net);
    if estimated == 0 {
        anyhow::bail!("CIDR range contains no host addresses");
    }
    if estimated > MAX_SCAN_IPS as u64 {
        anyhow::bail!(
            "range too large: ~{estimated} IPs (max {MAX_SCAN_IPS}). \
             Use a smaller CIDR prefix (e.g. /16 or smaller)"
        );
    }

    let ips: Vec<IpAddr> = net.hosts().collect();
    let total_ips = ips.len();

    let socket = Arc::new(
        UdpSocket::bind("0.0.0.0:0")
            .await
            .context("failed to bind scanner socket")?,
    );

    let probe = discovery::build_probe();
    let send_times: Arc<Mutex<HashMap<IpAddr, Instant>>> =
        Arc::new(Mutex::new(HashMap::with_capacity(total_ips)));
    let results: Arc<Mutex<Vec<ScanResult>>> = Arc::new(Mutex::new(Vec::new()));

    let scan_start = Instant::now();
    let semaphore = Arc::new(tokio::sync::Semaphore::new(config.concurrency));

    // Sender task: send probes to all IPs
    let sender_socket = socket.clone();
    let sender_times = send_times.clone();
    let port = config.port;
    let sender = tokio::spawn(async move {
        for ip in ips {
            let permit = semaphore.clone().acquire_owned().await;
            let sock = sender_socket.clone();
            let times = sender_times.clone();
            tokio::spawn(async move {
                let dest = SocketAddr::new(ip, port);
                {
                    let mut map = times.lock().await;
                    map.insert(ip, Instant::now());
                }
                let _ = sock.send_to(&probe, dest).await;
                drop(permit);
            });
        }
    });

    // Receiver task: collect responses until timeout
    let recv_socket = socket.clone();
    let recv_times = send_times.clone();
    let recv_results = results.clone();
    let timeout = std::time::Duration::from_millis(config.timeout_ms);
    let receiver = tokio::spawn(async move {
        let mut buf = [0u8; 512];
        let deadline = Instant::now() + timeout;

        loop {
            let remaining = deadline.saturating_duration_since(Instant::now());
            if remaining.is_zero() {
                break;
            }

            let recv_result = tokio::time::timeout(
                remaining,
                recv_socket.recv_from(&mut buf),
            )
            .await;

            match recv_result {
                Ok(Ok((len, src))) => {
                    if let Ok(response) = discovery::parse_response(&buf[..len]) {
                        let rtt_ms = {
                            let map = recv_times.lock().await;
                            map.get(&src.ip())
                                .map(|t| t.elapsed().as_secs_f64() * 1000.0)
                                .unwrap_or(0.0)
                        };
                        let result = ScanResult {
                            ip: src.ip(),
                            node_id: response.node_id,
                            name: response.name,
                            version: response.version,
                            capabilities: response.capabilities,
                            quic_port: response.quic_port,
                            rtt_ms,
                        };
                        recv_results.lock().await.push(result);
                    }
                }
                Ok(Err(e)) => {
                    tracing::debug!("recv error: {e}");
                }
                Err(_) => break, // overall timeout
            }
        }
    });

    // Wait for sender to finish, then wait for receiver (bounded by timeout)
    let _ = sender.await;
    let _ = receiver.await;

    let duration_ms = scan_start.elapsed().as_millis() as u64;
    let mut final_results = results.lock().await.clone();

    // Sort by IP for consistent output
    final_results.sort_by(|a, b| a.ip.cmp(&b.ip));

    // Auto-add discovered bots to peer store
    for r in &final_results {
        let peer = PeerInfo {
            node_id: r.node_id.clone(),
            name: r.name.clone(),
            capabilities: r.capabilities.clone(),
            last_seen: crate::protocol::now_secs(),
            ttl: 300,
            addresses: vec![r.ip.to_string()],
            metadata: std::collections::HashMap::new(),
        };
        let _ = store::upsert(peer);
    }

    let stats = ScanStats {
        total_ips,
        responses: final_results.len(),
        duration_ms,
    };

    Ok((final_results, stats))
}
