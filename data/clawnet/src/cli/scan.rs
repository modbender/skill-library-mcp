use anyhow::Result;

use crate::output;
use crate::scanner::{self, ScanConfig};

/// Estimate host count from CIDR prefix length without iterating.
fn estimate_hosts(range: &str) -> Result<u64> {
    let net: ipnet::IpNet = range.parse()?;
    let host_bits = match net {
        ipnet::IpNet::V4(n) => 32 - n.prefix_len() as u64,
        ipnet::IpNet::V6(n) => 128 - n.prefix_len() as u64,
    };
    if host_bits == 0 {
        Ok(1)
    } else if host_bits >= 64 {
        Ok(u64::MAX)
    } else {
        // Subtract 2 for network + broadcast on IPv4, but for /31 and /32 it's special
        let total = 1u64 << host_bits;
        if host_bits <= 1 {
            Ok(total)
        } else {
            Ok(total.saturating_sub(2))
        }
    }
}

pub async fn run(range: &str, timeout: u64, concurrency: usize, port: u16, json: bool) -> Result<()> {
    if !json {
        let host_count = estimate_hosts(range)?;
        eprintln!("Scanning {} ({} hosts)...", range, host_count);
    }

    let config = ScanConfig {
        timeout_ms: timeout,
        concurrency,
        port,
    };

    let (results, stats) = scanner::scan(range, config).await?;

    let entries: Vec<output::ScanResultEntry> = results
        .into_iter()
        .map(|r| output::ScanResultEntry {
            ip: r.ip.to_string(),
            node_id: r.node_id,
            name: r.name,
            version: r.version,
            capabilities: r.capabilities,
            quic_port: r.quic_port,
            rtt_ms: r.rtt_ms,
        })
        .collect();

    let out = output::ScanOutput {
        range: range.to_string(),
        results: entries,
        stats: output::ScanStatsOutput {
            total_ips: stats.total_ips,
            responses: stats.responses,
            duration_ms: stats.duration_ms,
        },
    };

    output::print(&out, json);
    Ok(())
}
