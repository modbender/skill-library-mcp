use anyhow::{Context, Result};
use iroh::EndpointId;

use crate::node::ClawNode;
use crate::output::{self, SendOutput};
use crate::protocol::{self, DirectMessage, WireMessage};

pub async fn run(node_id_str: &str, message: &str, json: bool) -> Result<()> {
    let node = ClawNode::spawn().await?;

    let target: EndpointId = node_id_str
        .parse()
        .context("invalid node ID")?;

    if !json {
        eprintln!("Sending message to {node_id_str}...");
    }

    let connection = node
        .endpoint
        .connect(target, protocol::MSG_ALPN)
        .await
        .context("failed to connect to peer")?;

    let (mut send_stream, mut recv_stream) = connection
        .open_bi()
        .await
        .context("failed to open bidirectional stream")?;

    let msg = WireMessage::Text(DirectMessage {
        from: node.endpoint.id().to_string(),
        content: message.to_string(),
        timestamp: protocol::now_secs(),
    });

    let bytes = msg.to_bytes();
    let bytes_len = bytes.len();

    protocol::write_length_prefixed(&mut send_stream, &bytes).await?;
    send_stream.finish().context("failed to finish stream")?;

    // Try to read response
    let response = match tokio::time::timeout(
        std::time::Duration::from_secs(5),
        read_response(&mut recv_stream),
    )
    .await
    {
        Ok(Ok(resp)) => Some(resp),
        _ => None,
    };

    output::print(
        &SendOutput {
            status: "sent".to_string(),
            node_id: node_id_str.to_string(),
            bytes_sent: bytes_len,
            response,
        },
        json,
    );

    connection.close(0u32.into(), b"done");
    node.shutdown().await?;
    Ok(())
}

async fn read_response(recv: &mut iroh::endpoint::RecvStream) -> Result<String> {
    let buf = protocol::read_length_prefixed(recv).await?;
    let msg = WireMessage::from_bytes(&buf)?;
    match msg {
        WireMessage::Text(dm) => Ok(dm.content),
        _ => anyhow::bail!("unexpected response type"),
    }
}
