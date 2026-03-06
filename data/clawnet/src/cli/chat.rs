use anyhow::{Context, Result};
use iroh::EndpointId;
use tokio::io::AsyncBufReadExt;

use crate::node::ClawNode;
use crate::protocol::{self, WireMessage};

pub async fn run(node_id_str: &str) -> Result<()> {
    let node = ClawNode::spawn().await?;
    let my_id = node.endpoint.id().to_string();

    let target: EndpointId = node_id_str.parse().context("invalid node ID")?;

    eprintln!(
        "Connecting to {}...",
        &node_id_str[..16.min(node_id_str.len())]
    );

    let connection = node
        .endpoint
        .connect(target, protocol::MSG_ALPN)
        .await
        .context("failed to connect to peer")?;

    let (mut send, mut recv) = connection
        .open_bi()
        .await
        .context("failed to open stream")?;

    eprintln!("Connected. Type messages and press Enter. Ctrl+C to quit.\n");

    // Spawn a task to read incoming messages from the peer
    let recv_handle = tokio::spawn(async move {
        loop {
            match protocol::read_length_prefixed(&mut recv).await {
                Ok(buf) => match WireMessage::from_bytes(&buf) {
                    Ok(WireMessage::Chat { from, content, .. }) => {
                        println!(
                            "{}: {}",
                            &from[..16.min(from.len())],
                            content
                        );
                    }
                    Ok(WireMessage::ChatEnd { .. }) => {
                        eprintln!("Peer ended chat session.");
                        break;
                    }
                    _ => {}
                },
                Err(_) => break,
            }
        }
    });

    // Read stdin lines and send as Chat messages
    let stdin = tokio::io::BufReader::new(tokio::io::stdin());
    let mut lines = stdin.lines();

    loop {
        tokio::select! {
            line = lines.next_line() => {
                match line {
                    Ok(Some(text)) => {
                        if text.is_empty() {
                            continue;
                        }
                        let msg = WireMessage::Chat {
                            from: my_id.clone(),
                            content: text,
                            timestamp: protocol::now_secs(),
                        };
                        if protocol::write_length_prefixed(&mut send, &msg.to_bytes()).await.is_err() {
                            eprintln!("Connection lost.");
                            break;
                        }
                    }
                    Ok(None) => break, // EOF
                    Err(_) => break,
                }
            }
            _ = tokio::signal::ctrl_c() => {
                break;
            }
        }
    }

    // Send ChatEnd
    let end = WireMessage::ChatEnd {
        from: my_id,
        timestamp: protocol::now_secs(),
    };
    let _ = protocol::write_length_prefixed(&mut send, &end.to_bytes()).await;
    let _ = send.finish();

    recv_handle.abort();
    connection.close(0u32.into(), b"chat-end");
    node.shutdown().await?;
    Ok(())
}
