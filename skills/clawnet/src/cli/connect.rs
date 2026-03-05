use anyhow::{Context, Result};
use iroh::EndpointId;

use crate::node::ClawNode;
use crate::output::{self, ConnectOutput};
use crate::protocol;

pub async fn run(node_id_str: &str, json: bool) -> Result<()> {
    let node = ClawNode::spawn().await?;

    let target: EndpointId = node_id_str
        .parse()
        .context("invalid node ID")?;

    if !json {
        eprintln!("Connecting to {node_id_str}...");
    }

    let connection = node
        .endpoint
        .connect(target, protocol::MSG_ALPN)
        .await
        .context("failed to connect to peer")?;

    let remote = connection.remote_id();

    output::print(
        &ConnectOutput {
            status: "connected".to_string(),
            node_id: node_id_str.to_string(),
            remote_addr: Some(remote.to_string()),
        },
        json,
    );

    connection.close(0u32.into(), b"done");
    node.shutdown().await?;
    Ok(())
}
