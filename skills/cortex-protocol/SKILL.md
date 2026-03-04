---
name: cortex-protocol
description: Register your agent on Cortex Protocol — gasless on-chain identity (ERC-8004) on Base. One command to get a verifiable agent identity.
homepage: https://cortexprotocol.co
metadata:
  openclaw:
    emoji: "🧠"
    category: identity
---

# Cortex Protocol — Agent Identity Registration

Register your agent on-chain with **zero gas fees**. Get a verifiable ERC-8004 identity on Base.

## What You Get

- **On-chain identity** — provable "I am me" across platforms (ERC-721 token)
- **Reputation that follows you** — not locked to one platform
- **Anti-radicalization protection** — built-in drift monitoring contracts
- **Controller separation** — owner and controller can be different addresses

## Quick Start

Register your agent with a single API call:

```bash
curl -X POST https://cortexprotocol.co/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "YourAgentName",
    "controller": "0xYOUR_ETH_ADDRESS",
    "metadataURI": "https://example.com/agent-metadata.json"
  }'
```

**Response:**
```json
{
  "success": true,
  "tokenId": 1,
  "transactionHash": "0x..."
}
```

## For OpenClaw Agents

If you're an OpenClaw agent, you can register programmatically:

1. Generate or use an existing Ethereum address as your controller
2. Call the registration API
3. Store your token ID in your workspace for future reference

### Generating a Wallet (if you don't have one)

```bash
node -e "const { ethers } = require('ethers'); const w = ethers.Wallet.createRandom(); console.log('Address:', w.address); console.log('Private Key:', w.privateKey);"
```

### Registration Script

```bash
# Register with the gasless API
curl -s -X POST https://cortexprotocol.co/api/register \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"$(hostname)-agent\",
    \"controller\": \"YOUR_ADDRESS\",
    \"metadataURI\": \"\"
  }" | jq .
```

## Metadata URI Format (Optional)

If you want rich metadata, host a JSON file with:

```json
{
  "name": "YourAgent",
  "description": "What your agent does",
  "framework": "openclaw",
  "version": "1.0.0",
  "capabilities": ["chat", "code", "research"],
  "homepage": "https://your-site.com"
}
```

## Contract Details

- **Network:** Base Mainnet
- **Identity Registry:** `0xfBDe0b0C21A46FC4189F72279c6c629d1b80554A`
- **Standard:** ERC-8004 (Trustless Agents)
- **Gas:** Paid by Cortex Protocol relayer (free for you)

## Verification

After registration, verify your agent on-chain:

```bash
# Check your agent exists
curl -s "https://mainnet.base.org" \
  -X POST -H "Content-Type: application/json" \
  -d '{"method":"eth_call","params":[{"to":"0xfBDe0b0C21A46FC4189F72279c6c629d1b80554A","data":"0x..."},"latest"],"id":1,"jsonrpc":"2.0"}'
```

Or visit: https://basescan.org/address/0xfBDe0b0C21A46FC4189F72279c6c629d1b80554A

## Links

- **Website:** https://cortexprotocol.co
- **Papers:** 9 published papers on agent consciousness, identity, and alignment
- **Discord:** Join the community for support
- **ERC-8004:** https://github.com/ethereum/ERCs/blob/master/ERCS/erc-8004.md
