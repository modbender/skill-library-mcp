use std::time::Duration;

use anyhow::{Context, Result};
use iroh::EndpointId;
use tokio::time::Instant;

use crate::node::ClawNode;
use crate::output::{self, PingOutput, PingResult, PingSummary};
use crate::protocol::{self, WireMessage};

pub async fn run(node_id_str: &str, count: u32, json: bool) -> Result<()> {
    let node = ClawNode::spawn().await?;
    let my_id = node.endpoint.id().to_string();

    let target: EndpointId = node_id_str.parse().context("invalid node ID")?;

    if !json {
        eprintln!("PING {} ({} pings)", &node_id_str[..16.min(node_id_str.len())], count);
    }

    let connection = node
        .endpoint
        .connect(target, protocol::MSG_ALPN)
        .await
        .context("failed to connect to peer")?;

    let mut results = Vec::with_capacity(count as usize);

    for seq in 0..count {
        let start = Instant::now();

        let result = match ping_once(&connection, &my_id, seq).await {
            Ok(()) => {
                let rtt = start.elapsed();
                let rtt_ms = rtt.as_secs_f64() * 1000.0;
                if !json {
                    eprintln!("ping seq={seq} rtt={rtt_ms:.1}ms");
                }
                PingResult {
                    seq,
                    rtt_ms: Some(rtt_ms),
                    error: None,
                }
            }
            Err(e) => {
                if !json {
                    eprintln!("ping seq={seq} error: {e:#}");
                }
                PingResult {
                    seq,
                    rtt_ms: None,
                    error: Some(format!("{e:#}")),
                }
            }
        };
        results.push(result);

        // Wait 1s between pings (except after the last one)
        if seq + 1 < count {
            tokio::time::sleep(Duration::from_secs(1)).await;
        }
    }

    let summary = compute_summary(&results, count);

    output::print(
        &PingOutput {
            node_id: node_id_str.to_string(),
            results,
            summary,
        },
        json,
    );

    connection.close(0u32.into(), b"done");
    node.shutdown().await?;
    Ok(())
}

async fn ping_once(
    connection: &iroh::endpoint::Connection,
    my_id: &str,
    seq: u32,
) -> Result<()> {
    let (mut send, mut recv) = connection
        .open_bi()
        .await
        .context("failed to open stream")?;

    let ping = WireMessage::Ping {
        from: my_id.to_string(),
        seq,
        timestamp: protocol::now_secs(),
    };

    let bytes = ping.to_bytes();
    protocol::write_length_prefixed(&mut send, &bytes).await?;
    send.finish().context("failed to finish send stream")?;

    // Wait for pong with timeout
    let resp_bytes = tokio::time::timeout(
        Duration::from_secs(5),
        protocol::read_length_prefixed(&mut recv),
    )
    .await
    .context("ping timeout")?
    .context("failed to read pong")?;

    let msg = WireMessage::from_bytes(&resp_bytes)?;
    match msg {
        WireMessage::Pong { seq: pong_seq, .. } if pong_seq == seq => Ok(()),
        _ => anyhow::bail!("unexpected response"),
    }
}

fn compute_summary(results: &[PingResult], count: u32) -> PingSummary {
    let rtts: Vec<f64> = results.iter().filter_map(|r| r.rtt_ms).collect();
    let received = rtts.len() as u32;
    let loss_percent = if count > 0 {
        ((count - received) as f64 / count as f64) * 100.0
    } else {
        0.0
    };

    let (min_ms, avg_ms, max_ms) = if rtts.is_empty() {
        (None, None, None)
    } else {
        let min = rtts.iter().cloned().fold(f64::INFINITY, f64::min);
        let max = rtts.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
        let avg = rtts.iter().sum::<f64>() / rtts.len() as f64;
        (Some(min), Some(avg), Some(max))
    };

    PingSummary {
        transmitted: count,
        received,
        loss_percent,
        min_ms,
        avg_ms,
        max_ms,
    }
}
