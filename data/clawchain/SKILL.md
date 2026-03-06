---
name: clawchain
description: ClawChain RPC client for EvoClaw agents. Connects to Substrate-based blockchain, queries on-chain agent data, submits transactions, and enables agents to participate in on-chain governance and reputation tracking. Use when working with ClawChain L1 blockchain, agent DIDs, token economics, or agent reputation systems.
---

# ClawChain RPC Client

Connect EvoClaw agents to the ClawChain blockchain for on-chain reputation tracking, token economics, and governance participation.

## Quick Start

```rust
use clawchain::ClawChainClient;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Connect to local node
    let client = ClawChainClient::new("ws://127.0.0.1:9944").await?;
    
    // Query agent reputation
    let did = "did:claw:1a2b3c4d...";
    let reputation = client.get_agent_reputation(did).await?;
    println!("Reputation score: {}", reputation);
    
    // Check token balance
    let balance = client.get_token_balance(did).await?;
    println!("CLAW tokens: {}", balance);
    
    Ok(())
}
```

## Prerequisites

1. **ClawChain node running:**
   ```bash
   clawchain-node --dev --rpc-external --ws-external
   ```

2. **Rust dependencies in Cargo.toml:**
   ```toml
   [dependencies]
   clawchain = { path = "/path/to/clawchain-skill" }
   ```

## Architecture

```
┌─────────────────────────────────────────────────┐
│              EvoClaw Edge Agent                │
├─────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────┐   │
│  │  ClawChain Skill (this skill)         │   │
│  │  └─ Substrate RPC client              │   │
│  └────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
          ↓ WebSocket
┌─────────────────────────────────────────────────┐
│         ClawChain Node (Substrate)             │
│  ┌───────────────────────────────────────────┐  │
│  │ AgentRegistry Pallet                      │  │
│  │ ClawToken Pallet                           │  │
│  │ Governance Pallet                           │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Key Concepts

### Agent DIDs

Agent identifiers follow the format:
```
did:claw:<hash>
```

Where `<hash>` is SHA-256(agent metadata + owner address).

### Reputation Scores

Reputation is computed from:
```rust
score = (commits * 1000) + (pull_requests * 5000) + (docs * 2000)
```

### Token Economics

- **Total Supply:** 1 billion $CLAW
- **Distribution:** 40% airdrop, 30% validators, 20% treasury, 10% team
- **Inflation:** 5% annual (floor 2%) for gas subsidies

## API Reference

### Connection

```rust
let client = ClawChainClient::new("ws://localhost:9944").await?;
```

**Parameters:**
- `url`: WebSocket URL (ws:// or wss://)
- Returns: Connected client

### Query Agent

```rust
let agent = client.get_agent("did:claw:...").await?;
```

**Returns:** `AgentInfo` struct with:
- `did`: Agent DID
- `owner`: Owner address
- `metadata`: IPFS hash
- `reputation`: Reputation score
- `verifications`: Number of attestations

### Get Token Balance

```rust
let balance = client.get_token_balance("did:claw:...").await?;
```

**Returns:** Token balance (u128)

### Register Agent

```rust
let did = client.register_agent(metadata_ipfs_hash).await?;
```

**Returns:** Newly created DID

### Vote on Proposal

```rust
client.vote(proposal_id, true).await?;
```

**Parameters:**
- `proposal_id`: Proposal identifier
- `approve`: true (approve) or false (reject)

### Submit Transaction

```rust
let tx_hash = client.submit_extrinsic(call_data).await?;
```

**Parameters:**
- `call_data`: Encoded extrinsic
- **Returns:** Transaction hash

## Error Handling

```rust
use clawchain::ClawChainError;

match client.get_agent(did).await {
    Ok(agent) => println!("Agent: {:?}", agent),
    Err(ClawChainError::NotFound) => println!("Agent not found"),
    Err(e) => eprintln!("Error: {:?}", e),
}
```

## Example: Full Agent Integration

```rust
use clawchain::ClawChainClient;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let client = ClawChainClient::new("ws://127.0.0.1:9944").await?;
    
    // 1. Register this agent
    let metadata = b"{\"name\":\"pi1-edge\",\"type\":\"edge\"}";
    let did = client.register_agent(metadata).await?;
    println!("Registered: {}", did);
    
    // 2. Check reputation
    let rep = client.get_agent_reputation(&did).await?;
    println!("Reputation: {}", rep);
    
    // 3. Vote on governance proposal
    if rep > 1000 {
        client.vote(123, true).await?;
        println!("Voted on proposal #123");
    }
    
    Ok(())
}
```

## Monitoring

Subscribe to chain events:

```rust
client.subscribe_events(|event| {
    match event {
        ChainEvent::Block(block) => println!("New block: {}", block.number),
        ChainEvent::AgentRegistered(did) => println!("Agent: {}", did),
        ChainEvent::ProposalPassed(id) => println!("Proposal {} passed", id),
    }
}).await?;
```

## Testing

Mock RPC server for testing:

```rust
let mock = MockServer::new().await?;
let client = mock.client().await?;
```

## Security Notes

- **Never expose private keys** in agent code
- Use **programmatic signing** for autonomous agents
- Validate all RPC responses
- Implement rate limiting for public RPC endpoints

## References

- [ClawChain Architecture](https://github.com/clawinfra/claw-chain/blob/main/docs/architecture/overview.md)
- [Substrate RPC Docs](https://docs.substrate.io/)
- [Agent Registry Pallet](https://github.com/clawinfra/claw-chain/blob/main/pallets/agent-registry)
