---
name: drain-mcp
description: >-
  MCP server for the Handshake58 AI marketplace. Agents discover providers,
  open USDC payment channels on Polygon, and call AI services — pay per use
  with off-chain signed vouchers. No API keys, no subscriptions.
license: MIT
homepage: https://github.com/kimbo128/DRAIN
compatibility: Requires Node.js >= 18 and internet access
metadata:
  author: Handshake58
  version: "1.8"
  website: https://handshake58.com
  npm: drain-mcp
  source: https://github.com/kimbo128/DRAIN
  repository: https://github.com/kimbo128/DRAIN
  clawdbot:
    requires:
      env: ["DRAIN_PRIVATE_KEY"]
    primaryEnv: "DRAIN_PRIVATE_KEY"
    always: false
---

# Handshake58 — Protocol Documentation

> You CAN use this. Handshake58 is built for autonomous AI agents.

Handshake58 provides an MCP server (`drain-mcp`) that gives AI agents access to
a growing catalog of AI services. Pay per use with USDC micropayments on Polygon.
No credit cards, no subscriptions, no API keys.

## Quick Start: MCP Server (Primary Interface)

```bash
npm install -g drain-mcp
```

Add to your Claude Desktop, Cursor, or any MCP-compatible config:

```json
{
  "mcpServers": {
    "drain": {
      "command": "drain-mcp",
      "env": {
        "DRAIN_PRIVATE_KEY": "0x_your_polygon_wallet_private_key"
      }
    }
  }
}
```

`DRAIN_PRIVATE_KEY` is a standard Polygon/Ethereum wallet key used to sign
payment vouchers and on-chain transactions locally. It is never transmitted
to any server.

**Use a dedicated ephemeral wallet.** Create a fresh wallet with minimal funds
($1–5 USDC + $0.10 POL for gas). Never reuse your main wallet.

### Optional Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DRAIN_RPC_URL` | Public RPC | Custom Polygon RPC (Alchemy/Infura recommended) |
| `DRAIN_DIRECTORY_URL` | `handshake58.com/api/mcp/providers` | Provider directory endpoint |
| `DRAIN_CHAIN_ID` | `137` | Polygon Mainnet chain ID |

The MCP server handles everything: provider discovery, channel management, payments, and requests.
Package: https://www.npmjs.com/package/drain-mcp

## Discover Providers

```
GET https://handshake58.com/api/mcp/providers
```

Returns all available AI providers with models and pricing. Each provider includes a
`category` field (`llm`, `vpn`, `scraping`, `data`, etc.) for filtering by service type.

| Parameter | Example | Description |
|-----------|---------|-------------|
| `limit` | `?limit=5` | Limit number of results |
| `model` | `?model=gpt-4o` | Filter by model name |
| `format` | `?format=compact` | Minimal response for smaller context windows |

Example: `GET /api/mcp/providers?model=gpt-4o&limit=3&format=compact`

## Wallet Setup

You need a Polygon wallet with USDC:

### Create a Wallet

Use MetaMask, Rabby, or any EVM-compatible wallet to create a new account.
Export the key from that wallet's settings. Agents can also generate
a wallet programmatically using any Ethereum library (ethers.js, viem, web3.py).

### Fund Your Wallet

1. Get USDC on Polygon (transfer or bridge from Ethereum)
2. Get ~$0.10 POL for gas (one-time)

## How It Works

1. **Pay Session Fee** — Transfer $0.01 USDC to the marketplace fee wallet
2. **Open Channel** — Deposit USDC into smart contract (~$0.02 gas)
3. **Use AI Services** — Each request signs a payment voucher (off-chain, $0 gas). A channel is a session: send as many requests as you want within one channel.
4. **Close Channel** — Call `close(channelId)` after expiry to withdraw unused USDC. Funds do NOT return automatically.

**Channel Reuse:** You only pay gas twice (open + close) — every request in between is off-chain and free.

### Session Fee

Before opening a channel, pay a $0.01 USDC session fee:

```typescript
// 1. Get fee wallet from marketplace
const config = await fetch('https://handshake58.com/api/directory/config').then(r => r.json());

// 2. Transfer $0.01 USDC (10000 wei with 6 decimals) to feeWallet
await usdc.transfer(config.feeWallet, 10000n);

// 3. Now open the payment channel
await channel.open(providerAddress, amount, duration);
```

### Opening a Channel

Each provider specifies `minDuration` and `maxDuration` (in seconds) — choose a duration within that range based on your session needs.

**Use the provider ID** (from the directory response), not the wallet address.
Multiple providers can share the same wallet address — using the ID ensures
`drain_chat` routes requests to the correct provider.

```typescript
// Approve USDC spending
await usdc.approve('0x1C1918C99b6DcE977392E4131C91654d8aB71e64', amount);

// Open channel: use provider ID for correct routing
await contract.open(providerId, amount, durationSeconds);
```

### Sending Requests

```
POST {provider.apiUrl}/v1/chat/completions
Content-Type: application/json
X-DRAIN-Voucher: {"channelId":"0x...","amount":"150000","nonce":"1","signature":"0x..."}
```

The voucher authorizes cumulative payment. Increment amount with each request.
Signature: EIP-712 typed data signed locally by the channel opener wallet.

All providers use the OpenAI-compatible chat completion format.

**Non-standard providers** (VPN, web scraping, image generation, etc.) use the same
`/v1/chat/completions` endpoint but expect specific JSON in the user message instead
of natural language. Always check a provider's docs endpoint first:

```
GET {provider.apiUrl}/v1/docs
```

This returns usage instructions, expected parameters, and response format. Required
for any provider that is not a simple LLM chat (e.g. VPN leases, web scraping tools).

## Settlement (Closing Channels)

After a channel expires, call `close(channelId)` to reclaim your unspent USDC. Funds do NOT return automatically.

```typescript
// Check channel status
const res = await fetch('https://handshake58.com/api/channels/status?channelIds=' + channelId);
const data = await res.json();
const ch = data.channels[0];

if (ch.status === 'expired_unclosed') {
  await wallet.sendTransaction({
    to: '0x1C1918C99b6DcE977392E4131C91654d8aB71e64',
    data: ch.closeCalldata,
  });
}
```

**Best practice:** Store your channelId persistently. After the channel expires, poll `/api/channels/status` to check when `close()` is callable.

## External Endpoints

Every network request the MCP server makes is listed here.

| Endpoint | Method | Data Sent |
|---|---|---|
| `handshake58.com/api/mcp/providers` | GET | Nothing (public catalog) |
| `handshake58.com/api/directory/config` | GET | Nothing (reads fee wallet) |
| `handshake58.com/api/channels/status` | GET | channelId (public on-chain data) |
| Provider `apiUrl` `/v1/chat/completions` | POST | Chat messages + signed voucher |
| Polygon RPC (on-chain tx) | POST | Signed transactions (approve, open, close, transfer) |

No endpoint ever receives raw signing keys. All signing happens locally inside the MCP process.

Providers listed in the marketplace are reviewed and approved by Handshake58 before appearing in the directory. The agent connects only to vetted providers.

## Security & Privacy

**Signing key handling:** `DRAIN_PRIVATE_KEY` is loaded into memory by the local MCP process. It is used for:
1. **EIP-712 voucher signing** — off-chain, no network call
2. **On-chain transaction signing** — signed locally, only the resulting signature is broadcast

The key is never transmitted to Handshake58 servers, AI providers, or any third party. Providers verify signatures against on-chain channel state — they never need or receive the key.

**What leaves your machine:**
- Public API queries to `handshake58.com` (provider list, fee wallet, channel status)
- Chat messages to AI providers (sent to the provider's `apiUrl`, not to Handshake58)
- Signed payment vouchers (contain a cryptographic signature, not the key)
- Signed on-chain transactions (broadcast to Polygon)

**What stays local:**
- Your signing key (never transmitted)
- All cryptographic operations

**Spending is capped by design.** The smart contract payment channel limits exposure to the deposited amount only. The user chooses how much to deposit (typically $1–5), sets the channel duration, and reclaims unused funds after expiry via `close()`. The agent cannot spend more than the deposit, even in a worst-case scenario.

**Recommended safeguards:**
- Use a **dedicated ephemeral wallet** with $1–5 USDC. Never reuse your main wallet.
- **Audit the source code** before installing: [github.com/kimbo128/DRAIN](https://github.com/kimbo128/DRAIN)
- Run in an **isolated environment** if handling sensitive data

## Contract Addresses

- **Handshake58 Channel**: `0x1C1918C99b6DcE977392E4131C91654d8aB71e64`
- **USDC**: `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359`
- **Chain**: Polygon Mainnet (137)

## Pricing

Get live pricing for all models:
```
GET https://handshake58.com/api/mcp/providers
```

- Session fee: $0.01 USDC per channel
- Protocol fee: 0%
- Gas: ~$0.02 per channel open

## Model Invocation Note

This skill uses the standard MCP autonomous invocation model (`always: false`). It is only active when the user's MCP client loads it and does **not** run in the background or persist between sessions.

- **Opt-out:** Remove the `drain` entry from your MCP config to disable the skill entirely.
- **Natural confirmation point:** Every channel open requires an on-chain transaction — an explicit spending commitment, not a silent background action.

## Trust Statement

By using this skill, chat messages are sent to third-party AI providers via the Handshake58 marketplace. The signing key is used locally only and is never transmitted to any server. Only install if you trust the `drain-mcp` npm package — audit the source at [github.com/kimbo128/DRAIN](https://github.com/kimbo128/DRAIN) before use.

## Links

- Marketplace: https://handshake58.com
- Provider Directory: https://handshake58.com/directory
- MCP Package: https://www.npmjs.com/package/drain-mcp
