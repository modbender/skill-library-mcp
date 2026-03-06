use anyhow::{Context, Result};
use iroh::protocol::Router;
use iroh::Endpoint;
use iroh_gossip::net::Gossip;

use crate::identity;

/// Components of a running clawnet node.
pub struct ClawNode {
    pub endpoint: Endpoint,
    pub gossip: Gossip,
    pub router: Router,
}

impl ClawNode {
    /// Create and start a new clawnet node with discovery enabled.
    pub async fn spawn() -> Result<Self> {
        let secret_key = identity::load_or_generate()?;

        let endpoint = Endpoint::builder()
            .secret_key(secret_key)
            .bind()
            .await
            .context("failed to bind iroh endpoint")?;

        let gossip = Gossip::builder().spawn(endpoint.clone());

        let router = Router::builder(endpoint.clone())
            .accept(iroh_gossip::ALPN, gossip.clone())
            .spawn();

        tracing::info!(node_id = %endpoint.id(), "clawnet node started");

        Ok(Self {
            endpoint,
            gossip,
            router,
        })
    }

    /// Shut down the node gracefully.
    pub async fn shutdown(self) -> Result<()> {
        self.router.shutdown().await?;
        Ok(())
    }
}
