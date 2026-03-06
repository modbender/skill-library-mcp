# ClawChain RPC Client

## Overview

Rust library for connecting EvoClaw agents to the ClawChain blockchain via Substrate RPC.

## Integration

Add to EvoClaw agent's `Cargo.toml`:

```toml
[dependencies]
clawchain = { path = "/path/to/clawchain-rpc-client" }
```

## Example Usage

```rust
use clawchain::ClawChainClient;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Connect to local node
    let client = ClawChainClient::new("ws://127.0.0.1:9944").await?;
    
    // Check reputation
    let did = "did:claw:1a2b3c...";
    let reputation = client.get_agent_reputation(did).await?;
    println!("Reputation: {}", reputation);
    
    // Vote
    client.vote(123, true).await?;
    
    Ok(())
}
```

## Dependencies

- Substrate node running (ws://localhost:9944)
- async-std runtime
- WebSocket client library

## Security

- Never commit private keys
- Use programmatic signing for autonomous agents
- Validate all RPC responses
