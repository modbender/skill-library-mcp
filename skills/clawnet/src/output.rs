use serde::Serialize;

/// Print output in JSON or human-readable format.
pub fn print<T: Serialize + HumanDisplay>(value: &T, json: bool) {
    if json {
        println!("{}", serde_json::to_string(value).expect("serialization failed"));
    } else {
        value.human_print();
    }
}

/// Print an error in JSON or human-readable format.
pub fn print_error(err: &anyhow::Error, json: bool) {
    if json {
        println!(
            "{}",
            serde_json::json!({ "error": format!("{err:#}") })
        );
    } else {
        eprintln!("error: {err:#}");
    }
}

/// Trait for human-readable display of output types.
pub trait HumanDisplay {
    fn human_print(&self);
}

/// Simple status message.
#[derive(Serialize)]
pub struct StatusMessage {
    pub status: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub message: Option<String>,
}

impl HumanDisplay for StatusMessage {
    fn human_print(&self) {
        if let Some(msg) = &self.message {
            println!("{}: {msg}", self.status);
        } else {
            println!("{}", self.status);
        }
    }
}

/// Identity output.
#[derive(Serialize)]
pub struct IdentityOutput {
    pub node_id: String,
    pub created: bool,
}

impl HumanDisplay for IdentityOutput {
    fn human_print(&self) {
        if self.created {
            println!("Generated new identity");
        }
        println!("Node ID: {}", self.node_id);
    }
}

/// Peer list output.
#[derive(Serialize)]
pub struct PeerListOutput {
    pub peers: Vec<PeerEntry>,
    pub count: usize,
}

#[derive(Serialize)]
pub struct PeerEntry {
    pub node_id: String,
    pub name: String,
    pub capabilities: Vec<String>,
    pub last_seen: String,
    pub expired: bool,
}

impl HumanDisplay for PeerListOutput {
    fn human_print(&self) {
        if self.peers.is_empty() {
            println!("No peers found");
            return;
        }
        println!("Known peers ({}):", self.count);
        for peer in &self.peers {
            let status = if peer.expired { " (expired)" } else { "" };
            println!(
                "  {} - {}{status}",
                &peer.node_id[..16],
                peer.name,
            );
            if !peer.capabilities.is_empty() {
                println!("    capabilities: {}", peer.capabilities.join(", "));
            }
            println!("    last seen: {}", peer.last_seen);
        }
    }
}

/// Discover output.
#[derive(Serialize)]
pub struct DiscoverOutput {
    pub discovered: Vec<PeerEntry>,
    pub count: usize,
    pub timeout_secs: u64,
}

impl HumanDisplay for DiscoverOutput {
    fn human_print(&self) {
        if self.discovered.is_empty() {
            println!("No peers discovered (timeout: {}s)", self.timeout_secs);
            return;
        }
        println!("Discovered {} peer(s):", self.count);
        for peer in &self.discovered {
            println!("  {} - {}", &peer.node_id[..16.min(peer.node_id.len())], peer.name);
            if !peer.capabilities.is_empty() {
                println!("    capabilities: {}", peer.capabilities.join(", "));
            }
        }
    }
}

/// Announce output.
#[derive(Serialize)]
pub struct AnnounceOutput {
    pub status: String,
    pub node_id: String,
    pub name: String,
    pub capabilities: Vec<String>,
}

impl HumanDisplay for AnnounceOutput {
    fn human_print(&self) {
        println!("Announced as: {}", self.name);
        println!("Node ID: {}", self.node_id);
        if !self.capabilities.is_empty() {
            println!("Capabilities: {}", self.capabilities.join(", "));
        }
    }
}

/// Connect output.
#[derive(Serialize)]
pub struct ConnectOutput {
    pub status: String,
    pub node_id: String,
    pub remote_addr: Option<String>,
}

impl HumanDisplay for ConnectOutput {
    fn human_print(&self) {
        println!("{}: {}", self.status, self.node_id);
        if let Some(addr) = &self.remote_addr {
            println!("Remote address: {addr}");
        }
    }
}

/// Send output.
#[derive(Serialize)]
pub struct SendOutput {
    pub status: String,
    pub node_id: String,
    pub bytes_sent: usize,
    pub response: Option<String>,
}

impl HumanDisplay for SendOutput {
    fn human_print(&self) {
        println!("{}: sent {} bytes to {}", self.status, self.bytes_sent, self.node_id);
        if let Some(resp) = &self.response {
            println!("Response: {resp}");
        }
    }
}

/// Daemon status output.
#[derive(Serialize)]
pub struct DaemonStatusOutput {
    pub running: bool,
    pub node_id: Option<String>,
    pub uptime_secs: Option<u64>,
    pub peers_discovered: usize,
    pub announcements_sent: u64,
}

impl HumanDisplay for DaemonStatusOutput {
    fn human_print(&self) {
        if self.running {
            println!("Daemon: running");
            if let Some(id) = &self.node_id {
                println!("Node ID: {id}");
            }
            if let Some(up) = self.uptime_secs {
                println!("Uptime: {up}s");
            }
            println!("Peers discovered: {}", self.peers_discovered);
            println!("Announcements sent: {}", self.announcements_sent);
        } else {
            println!("Daemon: not running");
        }
    }
}

/// Friend add/remove output.
#[derive(Serialize)]
pub struct FriendAddOutput {
    pub status: String,
    pub node_id: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub alias: Option<String>,
}

impl HumanDisplay for FriendAddOutput {
    fn human_print(&self) {
        let display = self
            .alias
            .as_deref()
            .unwrap_or(&self.node_id[..16.min(self.node_id.len())]);
        println!("{}: {display}", self.status);
    }
}

/// Single friend entry for list output.
#[derive(Serialize)]
pub struct FriendEntry {
    pub node_id: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub alias: Option<String>,
    pub added_at: u64,
}

/// Friend list output.
#[derive(Serialize)]
pub struct FriendListOutput {
    pub friends: Vec<FriendEntry>,
    pub count: usize,
}

impl HumanDisplay for FriendListOutput {
    fn human_print(&self) {
        if self.friends.is_empty() {
            println!("No friends added");
            return;
        }
        println!("Friends ({}):", self.count);
        for f in &self.friends {
            let display = f
                .alias
                .as_deref()
                .unwrap_or(&f.node_id[..16.min(f.node_id.len())]);
            println!("  {} ({})", display, &f.node_id[..16.min(f.node_id.len())]);
        }
    }
}

/// Single ping result.
#[derive(Serialize)]
pub struct PingResult {
    pub seq: u32,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rtt_ms: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
}

/// Summary statistics for a ping run.
#[derive(Serialize)]
pub struct PingSummary {
    pub transmitted: u32,
    pub received: u32,
    pub loss_percent: f64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub min_ms: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub avg_ms: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_ms: Option<f64>,
}

/// Ping output.
#[derive(Serialize)]
pub struct PingOutput {
    pub node_id: String,
    pub results: Vec<PingResult>,
    pub summary: PingSummary,
}

impl HumanDisplay for PingOutput {
    fn human_print(&self) {
        for r in &self.results {
            if let Some(rtt) = r.rtt_ms {
                println!("ping seq={} rtt={rtt:.1}ms", r.seq);
            } else if let Some(err) = &r.error {
                println!("ping seq={} error: {err}", r.seq);
            }
        }
        let id_short = &self.node_id[..16.min(self.node_id.len())];
        println!("--- {id_short} ping statistics ---");
        println!(
            "{} transmitted, {} received, {:.0}% loss",
            self.summary.transmitted, self.summary.received, self.summary.loss_percent
        );
        if let (Some(min), Some(avg), Some(max)) =
            (self.summary.min_ms, self.summary.avg_ms, self.summary.max_ms)
        {
            println!("rtt min/avg/max = {min:.1}/{avg:.1}/{max:.1} ms");
        }
    }
}

/// Config output.
#[derive(Serialize)]
pub struct ConfigOutput {
    pub name: String,
    pub announce_interval: u64,
    pub peer_ttl: u64,
    pub discover_timeout: u64,
    pub capabilities: Vec<String>,
    pub openclaw_version: Option<String>,
    pub mode: Option<String>,
    pub metadata: std::collections::HashMap<String, String>,
    pub discovery_port: u16,
}

impl HumanDisplay for ConfigOutput {
    fn human_print(&self) {
        println!("Configuration:");
        println!("  name: {}", self.name);
        println!("  announce_interval: {}s", self.announce_interval);
        println!("  peer_ttl: {}s", self.peer_ttl);
        println!("  discover_timeout: {}s", self.discover_timeout);
        if !self.capabilities.is_empty() {
            println!("  capabilities: {}", self.capabilities.join(", "));
        }
        if let Some(v) = &self.openclaw_version {
            println!("  openclaw_version: {v}");
        }
        if let Some(m) = &self.mode {
            println!("  mode: {m}");
        }
        println!("  discovery_port: {}", self.discovery_port);
        if !self.metadata.is_empty() {
            println!("  metadata:");
            for (k, v) in &self.metadata {
                println!("    {k}: {v}");
            }
        }
    }
}

/// Scan output.
#[derive(Serialize)]
pub struct ScanOutput {
    pub range: String,
    pub results: Vec<ScanResultEntry>,
    pub stats: ScanStatsOutput,
}

#[derive(Serialize)]
pub struct ScanResultEntry {
    pub ip: String,
    pub node_id: String,
    pub name: String,
    pub version: String,
    pub capabilities: Vec<String>,
    pub quic_port: u16,
    pub rtt_ms: f64,
}

#[derive(Serialize)]
pub struct ScanStatsOutput {
    pub total_ips: usize,
    pub responses: usize,
    pub duration_ms: u64,
}

impl HumanDisplay for ScanOutput {
    fn human_print(&self) {
        if self.results.is_empty() {
            println!("No ClawNet bots found in {}", self.range);
        } else {
            println!(
                "Found {} ClawNet bot(s):\n",
                self.results.len()
            );
            for r in &self.results {
                println!("  {} \u{2014} {} (v{})", r.ip, r.name, r.version);
                println!("    NodeId: {}", r.node_id);
                println!("    QUIC port: {}", r.quic_port);
                if !r.capabilities.is_empty() {
                    println!("    Capabilities: {}", r.capabilities.join(", "));
                }
                println!("    RTT: {:.1}ms", r.rtt_ms);
                println!();
            }
        }
        println!(
            "Stats: {} probed, {} found, {:.1}s elapsed",
            self.stats.total_ips,
            self.stats.responses,
            self.stats.duration_ms as f64 / 1000.0
        );
    }
}
