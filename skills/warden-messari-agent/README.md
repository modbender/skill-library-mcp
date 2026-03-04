# Warden Messari Agent

Communicate with the Messari Deep Research agent by Warden Protocol. This skill teaches you (or your agent) how to discover, authenticate, query, and verify the Messari agent using the A2A protocol, x402 payments, and ERC-8004 on-chain identity.

## What It Covers

- **Discovery**: Fetch the agent card to learn capabilities, pricing, and supported protocols
- **A2A Messaging**: Send natural language crypto queries via JSON-RPC 2.0 (`message/send`)
- **x402 Payments**: Handle the HTTP 402 payment flow with USDC on Base or Solana
- **ERC-8004 Verification**: Cross-reference on-chain registry data with the agent's hosted registration

## Quick Start

```bash
# Discover the agent
curl -s https://messari.agents.wardenprotocol.org/.well-known/agent-card.json | jq .

# Send a query (will return 402 if payments are enabled)
curl -s -X POST https://messari.agents.wardenprotocol.org/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "What is Bitcoin's market cap?"}]
      }
    },
    "id": "req-001"
  }'
```

## Installation

```bash
# Via ClawHub
clawd install wardenprotocol/warden-messari-agent
```

## The Agent

The Messari Agent answers questions about crypto assets, protocols, and projects. It draws from Messari's quantitative data (market data, asset metrics, fundraising, token unlocks) and qualitative data (research, news, blogs, feeds, documents).

- **URL**: https://messari.agents.wardenprotocol.org
- **Protocol**: A2A v0.5.0 (JSON-RPC 2.0)
- **Payment**: $0.25 USDC per request via x402 on Base mainnet
- **Provider**: Warden Protocol

## License

CC0-1.0
