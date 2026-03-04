use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::Arc;
use std::time::Duration;

use anyhow::Result;
use futures_lite::StreamExt;
use iroh_gossip::api::Event;

use crate::config;
use crate::discovery::DiscoveryListener;
use crate::gossip;
use crate::node::ClawNode;
use crate::protocol::{self, BotAnnouncement, GossipMessage, PeerInfo, WireMessage, MSG_ALPN};
use crate::store;

/// Shared daemon state for status queries.
pub struct DaemonState {
    pub running: AtomicBool,
    pub announcements_sent: AtomicU64,
    pub peers_discovered: AtomicU64,
    pub start_time: u64,
}

impl DaemonState {
    pub fn new() -> Self {
        Self {
            running: AtomicBool::new(true),
            announcements_sent: AtomicU64::new(0),
            peers_discovered: AtomicU64::new(0),
            start_time: protocol::now_secs(),
        }
    }
}

/// Run the continuous discovery daemon.
pub async fn run(interval_secs: u64) -> Result<()> {
    let cfg = config::load()?;
    let node = ClawNode::spawn().await?;
    let state = Arc::new(DaemonState::new());

    let node_id = node.endpoint.id().to_string();
    tracing::info!(node_id = %node_id, "daemon started");
    eprintln!("Daemon started. Node ID: {node_id}");
    eprintln!("Press Ctrl+C to stop.");

    // Get QUIC port from iroh endpoint
    let quic_port = node
        .endpoint
        .bound_sockets()
        .first()
        .map(|a| a.port())
        .unwrap_or(0);

    // Spawn discovery listener on well-known UDP port
    let discovery_shutdown = Arc::new(AtomicBool::new(false));
    let discovery_port = cfg.discovery_port;
    match DiscoveryListener::bind(
        discovery_port,
        node_id.clone(),
        cfg.name.clone(),
        cfg.capabilities.clone(),
        quic_port,
        discovery_shutdown.clone(),
    )
    .await
    {
        Ok(listener) => {
            eprintln!("Discovery listener on UDP port {discovery_port}");
            tokio::spawn(async move {
                listener.listen().await;
            });
        }
        Err(e) => {
            tracing::warn!("failed to start discovery listener: {e}");
            eprintln!("Warning: could not bind discovery port {discovery_port}: {e}");
        }
    }

    let topic = gossip::subscribe(&node.gossip, vec![]).await?;
    let (sender, mut receiver) = topic.split();

    // Spawn message acceptor for direct connections
    let endpoint = node.endpoint.clone();
    let accept_state = state.clone();
    tokio::spawn(async move {
        accept_loop(endpoint, accept_state).await;
    });

    // Periodic announcement task
    let announce_sender = sender.clone();
    let announce_cfg = cfg.clone();
    let announce_node_id = node_id.clone();
    let announce_state = state.clone();
    tokio::spawn(async move {
        let mut interval = tokio::time::interval(Duration::from_secs(interval_secs));
        loop {
            interval.tick().await;
            let ann = GossipMessage::Announce(BotAnnouncement {
                node_id: announce_node_id.clone(),
                name: announce_cfg.name.clone(),
                version: env!("CARGO_PKG_VERSION").to_string(),
                capabilities: announce_cfg.capabilities.clone(),
                openclaw_version: announce_cfg.openclaw_version.clone(),
                mode: announce_cfg.mode.clone(),
                timestamp: protocol::now_secs(),
                ttl: announce_cfg.peer_ttl,
                metadata: announce_cfg.metadata.clone(),
            });
            if let Err(e) = announce_sender.broadcast(ann.to_bytes().into()).await {
                tracing::warn!("failed to broadcast announcement: {e}");
            } else {
                announce_state
                    .announcements_sent
                    .fetch_add(1, Ordering::Relaxed);
            }
        }
    });

    // Listen for incoming gossip messages
    let listen_state = state.clone();
    let listen_node_id = node_id.clone();
    loop {
        tokio::select! {
            _ = tokio::signal::ctrl_c() => {
                eprintln!("\nShutting down...");
                discovery_shutdown.store(true, Ordering::Relaxed);
                // Send leave message
                let leave = GossipMessage::Leave {
                    node_id: listen_node_id.clone(),
                    timestamp: protocol::now_secs(),
                };
                let _ = sender.broadcast(leave.to_bytes().into()).await;
                break;
            }
            event = receiver.try_next() => {
                match event {
                    Ok(Some(Event::Received(msg))) => {
                        match GossipMessage::from_bytes(&msg.content) {
                            Ok(GossipMessage::Announce(ann)) => {
                                if ann.node_id == listen_node_id {
                                    continue;
                                }
                                tracing::info!(peer = %ann.node_id, name = %ann.name, "discovered peer");
                                eprintln!("Discovered: {} ({})", ann.name, &ann.node_id[..16.min(ann.node_id.len())]);
                                let peer = PeerInfo {
                                    node_id: ann.node_id.clone(),
                                    name: ann.name,
                                    capabilities: ann.capabilities,
                                    last_seen: protocol::now_secs(),
                                    ttl: ann.ttl,
                                    addresses: vec![],
                                    metadata: ann.metadata,
                                };
                                let _ = store::upsert(peer);
                                listen_state.peers_discovered.fetch_add(1, Ordering::Relaxed);
                            }
                            Ok(GossipMessage::Leave { node_id, .. }) => {
                                tracing::info!(peer = %node_id, "peer left");
                                eprintln!("Peer left: {}", &node_id[..16.min(node_id.len())]);
                            }
                            Err(e) => {
                                tracing::debug!("failed to parse gossip message: {e}");
                            }
                        }
                    }
                    Ok(Some(_)) => {}
                    Ok(None) => break,
                    Err(e) => {
                        tracing::warn!("gossip receive error: {e}");
                        break;
                    }
                }
            }
        }
    }

    listen_state.running.store(false, Ordering::Relaxed);
    node.shutdown().await?;
    Ok(())
}

/// Accept incoming direct QUIC connections and handle messages.
async fn accept_loop(endpoint: iroh::Endpoint, _state: Arc<DaemonState>) {
    let node_id_str = endpoint.id().to_string();
    loop {
        let incoming = match endpoint.accept().await {
            Some(incoming) => incoming,
            None => break,
        };

        let my_id = node_id_str.clone();
        tokio::spawn(async move {
            let connection = match incoming.await {
                Ok(conn) => conn,
                Err(e) => {
                    tracing::debug!("failed to accept connection: {e}");
                    return;
                }
            };

            let alpn = connection.alpn();
            if &*alpn != MSG_ALPN {
                tracing::debug!(alpn = ?alpn, "unknown ALPN, ignoring");
                return;
            }

            // Accept multiple streams per connection
            loop {
                let (mut send, mut recv) = match connection.accept_bi().await {
                    Ok(streams) => streams,
                    Err(_) => break, // connection closed
                };

                let my_id = my_id.clone();
                tokio::spawn(async move {
                    let buf = match protocol::read_length_prefixed(&mut recv).await {
                        Ok(b) => b,
                        Err(_) => return,
                    };

                    let msg = match WireMessage::from_bytes(&buf) {
                        Ok(m) => m,
                        Err(e) => {
                            tracing::debug!("failed to parse wire message: {e}");
                            return;
                        }
                    };

                    match msg {
                        WireMessage::Text(dm) => {
                            tracing::info!(from = %dm.from, "received direct message");
                            eprintln!(
                                "Message from {}: {}",
                                &dm.from[..16.min(dm.from.len())],
                                dm.content
                            );
                            // Send ack using WireMessage::Text
                            let ack = WireMessage::Text(protocol::DirectMessage {
                                from: my_id,
                                content: "received".to_string(),
                                timestamp: protocol::now_secs(),
                            });
                            let _ = protocol::write_length_prefixed(&mut send, &ack.to_bytes()).await;
                            let _ = send.finish();
                        }
                        WireMessage::Ping { from, seq, timestamp } => {
                            tracing::info!(from = %from, seq, "received ping");
                            let pong = WireMessage::Pong {
                                from: my_id,
                                seq,
                                echo_timestamp: timestamp,
                                timestamp: protocol::now_secs(),
                            };
                            let _ = protocol::write_length_prefixed(&mut send, &pong.to_bytes()).await;
                            let _ = send.finish();
                        }
                        WireMessage::Chat { from, content, .. } => {
                            eprintln!(
                                "[chat] {}: {}",
                                &from[..16.min(from.len())],
                                content
                            );
                            // Continue reading chat messages on this stream
                            loop {
                                match protocol::read_length_prefixed(&mut recv).await {
                                    Ok(buf) => match WireMessage::from_bytes(&buf) {
                                        Ok(WireMessage::Chat { from, content, .. }) => {
                                            eprintln!(
                                                "[chat] {}: {}",
                                                &from[..16.min(from.len())],
                                                content
                                            );
                                        }
                                        Ok(WireMessage::ChatEnd { .. }) => break,
                                        _ => break,
                                    },
                                    Err(_) => break,
                                }
                            }
                        }
                        WireMessage::ChatEnd { .. } => {
                            // Stray ChatEnd, ignore
                        }
                        WireMessage::Pong { .. } => {
                            // Only expected by ping initiator, ignore
                        }
                    }
                });
            }
        });
    }
}
