# eth-node

Manage Ethereum execution client nodes — start, stop, sync status, peers, logs, config.

## Quick Start

```bash
# Install (macOS)
brew install geth
cargo install reth --git https://github.com/paradigmxyz/reth --locked

# Start node with proper security
reth node --http --http.addr 127.0.0.1 --http.api eth,net,web3 &> reth.log 2>&1 &

# Check sync status
curl -s -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_syncing","id":1}' | jq
```

## Key Features

- **macOS-optimized:** Homebrew and cargo install instructions
- **Security-focused:** Explicit localhost binding, proper log redirection
- **Multi-client:** Support for reth, geth, and other EL clients
- **Admin operations:** Peer management, node diagnostics

## Requirements

- `reth`, `geth`, or other Ethereum execution client
- `curl` for JSON-RPC calls
- `jq` for JSON formatting

See [SKILL.md](./SKILL.md) for complete documentation.