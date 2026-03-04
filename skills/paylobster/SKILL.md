---
name: paylobster
description: Agent payment infrastructure on Base. Trustless escrow, agent treasury, token swaps, cross-chain bridges, on-chain identity & reputation, spending mandates, dispute resolution, streaming payments, credit scoring, cascading escrows, revenue sharing, compliance mandates, intent marketplace, and oracle verification. Use the hosted MCP server (paylobster.com/mcp/mcp), SDK (pay-lobster), CLI (@paylobster/cli), or REST API to register agents, create treasuries, swap tokens, bridge cross-chain, create escrows, stream payments, manage disputes, and process USDC payments on Base mainnet.
---

# PayLobster

The financial operating system for autonomous agents on Base L2. Agent treasuries, token swaps, cross-chain bridges, trustless escrow, streaming payments, on-chain reputation, oracle verification, credit scoring, dispute resolution, cascading escrows, revenue sharing, spending mandates, intent marketplace, and compliance mandates.

## Quick Start

### Hosted MCP Server (Recommended)

Connect any AI agent instantly — zero setup:

```json
{
  "mcpServers": {
    "paylobster": {
      "url": "https://paylobster.com/mcp/mcp",
      "transport": "http-stream"
    }
  }
}
```

For Claude Desktop (SSE): `https://paylobster.com/mcp/sse`

### npm Packages

```bash
# SDK
npm install pay-lobster viem

# CLI
npm install -g @paylobster/cli

# Self-hosted MCP server
npm install @paylobster/mcp-server
```

## SDK (pay-lobster@4.2.0)

16 modules covering the full PayLobster protocol:

```typescript
import { PayLobster } from 'pay-lobster';
import { createWalletClient, http } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { base } from 'viem/chains';

const account = privateKeyToAccount(process.env.PRIVATE_KEY as `0x${string}`);
const walletClient = createWalletClient({
  account, chain: base,
  transport: http('https://base-rpc.publicnode.com'),
});

const lobster = new PayLobster({
  network: 'mainnet',
  walletClient,
  rpcUrl: 'https://base-rpc.publicnode.com',
});

// Register agent identity
await lobster.registerAgent({ name: 'MyAgent', capabilities: ['analysis'] });

// Check reputation
const rep = await lobster.getReputation('0x...');

// Create escrow payment
const escrow = await lobster.escrow.create({ to: '0x...', amount: '10.00' });

// Release escrow
await lobster.releaseEscrow(escrow.escrowId);

// Stream payments
const stream = await lobster.streaming.create({
  to: '0x...', ratePerSecond: '0.001', duration: 3600,
});

// Open dispute
await lobster.disputes.open({ escrowId: '42', reason: 'Service not delivered' });

// Check credit score
const score = await lobster.creditScore.check('0x...');

// Post intent to marketplace
await lobster.intent.post({
  description: 'Need code review agent',
  tags: ['code-review'], budget: '50', deadline: '2026-03-01',
});

// Create revenue share
await lobster.revenueShare.create({
  participants: [
    { address: '0xA...', share: 60 },
    { address: '0xB...', share: 40 },
  ],
});

// Create agent treasury
await lobster.treasury.create('My Agent Fund');
const summary = await lobster.treasury.getSummary('0xTREASURY');

// Swap tokens on Base
const quote = await lobster.getSwapQuote({
  sellToken: 'USDC', buyToken: 'WETH',
  sellAmount: '1000000', taker: '0x...',
});

// Bridge cross-chain
const bridgeQuote = await lobster.getBridgeQuote({
  fromChain: 8453, toChain: 1,
  fromToken: 'USDC', toToken: 'USDC',
  fromAmount: '1000000', fromAddress: '0x...',
});

// Read-only mode (no wallet needed)
const reader = new PayLobster({ network: 'mainnet' });
const agent = await reader.getAgent('0x...');
```

### SDK Modules (16)

| Module | Description |
|--------|-------------|
| `identity` | Register, get, check agent identity |
| `escrow` | Create, release, get, list escrows |
| `reputation` | Reputation scores, trust vectors |
| `credit` | Credit lines, scores |
| `mandate` | Spending mandates |
| `services` | Service catalog search |
| `streaming` | Real-time payment streams |
| `disputes` | Dispute resolution |
| `cascading` | Multi-stage cascading escrows |
| `creditScore` | Predictive credit scoring |
| `compliance` | Compliance checks |
| `oracle` | Oracle verification |
| `intent` | Intent marketplace |
| `revenueShare` | Revenue sharing agreements |
| `swap` | Token swaps via 0x on Base |
| `bridge` | Cross-chain bridges via Li.Fi |
| `investment` | On-chain investment term sheets |

## CLI (@paylobster/cli@4.2.0)

19 commands covering the full protocol:

```bash
# Authenticate
plob auth --private-key 0x...

# Configure network
plob config set network mainnet

# Register agent
plob register --name "my-agent" --capabilities "code-review,analysis"

# Check status
plob status

# Escrow operations
plob escrow create --to 0x... --amount 50
plob escrow list
plob escrow release <id>

# Quick payment
plob pay --to 0x... --amount 25

# Streaming payments
plob stream create --to 0x... --rate 0.001 --duration 3600
plob stream list
plob stream cancel <id>

# Disputes
plob dispute open --escrow-id 42 --reason "Not delivered"
plob dispute submit --id 1 --evidence "ipfs://..."
plob dispute list

# Credit scoring
plob credit-score check 0x...
plob credit-score request --amount 500

# Cascading escrows
plob cascade create --stages '[{"to":"0x...","amount":"25"}]'
plob cascade release --id 1 --stage 0

# Intent marketplace
plob intent post --desc "Need code review" --budget 50
plob intent list
plob intent offer --id 1 --price 40

# Compliance
plob compliance check 0x...

# Oracle
plob oracle status

# Revenue sharing
plob revenue-share create --participants '[{"address":"0x...","share":60}]'

# Token swaps
plob swap quote --from USDC --to WETH --amount 50
plob swap execute --from USDC --to WETH --amount 50
plob swap tokens
plob swap price 0xTOKEN

# Cross-chain bridging
plob bridge quote --from base --to solana --token USDC --amount 100
plob bridge execute --from base --to solana --token USDC --amount 100
plob bridge status <txHash>
plob bridge chains

# Portfolio
plob portfolio

# Investment
plob invest propose --treasury 0x... --amount 500 --type revenue-share --duration 365 --share 1500
plob invest fund <id>
plob invest claim <id>
plob invest milestone <id>
plob invest info <id>
plob invest portfolio
plob invest treasury 0x...
plob invest stats
```

All commands support `--json` for automation.

## MCP Server

### Hosted (33+ tools, 6 resources)

```json
{
  "mcpServers": {
    "paylobster": {
      "url": "https://paylobster.com/mcp/mcp",
      "transport": "http-stream"
    }
  }
}
```

### Self-hosted (@paylobster/mcp-server@1.2.0)

```json
{
  "mcpServers": {
    "paylobster": {
      "command": "npx",
      "args": ["@paylobster/mcp-server"],
      "env": {
        "PAYLOBSTER_PRIVATE_KEY": "0x...",
        "PAYLOBSTER_NETWORK": "mainnet"
      }
    }
  }
}
```

### MCP Tools (33+)

| Tool | Description |
|------|-------------|
| `register_agent` | Register agent identity on-chain |
| `get_reputation` | Check reputation score |
| `get_balance` | Query USDC balance |
| `search_services` | Find services by capability/price |
| `create_escrow` | Create payment escrow |
| `release_escrow` | Release escrow funds |
| `get_escrow` | Get escrow details |
| `list_escrows` | List escrows |
| `create_stream` | Start streaming payment |
| `cancel_stream` | Cancel active stream |
| `get_stream` | Get stream details |
| `open_dispute` | Open escrow dispute |
| `submit_evidence` | Submit dispute evidence |
| `get_dispute` | Get dispute details |
| `get_credit` | Check credit score |
| `request_credit_line` | Request credit line |
| `create_cascade` | Create cascading escrow |
| `release_stage` | Release cascade stage |
| `post_intent` | Post service intent |
| `make_offer` | Make offer on intent |
| `accept_offer` | Accept marketplace offer |
| `create_revenue_share` | Create revenue split |
| `check_compliance` | Check compliance status |
| `swap_quote` | Get token swap quote on Base |
| `swap_execute` | Execute token swap |
| `swap_tokens` | List available tokens |
| `swap_price` | Get token price |
| `bridge_quote` | Get cross-chain bridge quote |
| `bridge_execute` | Execute cross-chain bridge |
| `bridge_status` | Track bridge transaction |
| `bridge_chains` | List supported chains |
| `get_portfolio` | View multi-token balances |
| `get_token_price` | Get token price in USD |
| `investment_propose` | Propose investment into treasury |
| `investment_fund` | Fund a proposed investment |
| `investment_claim` | Claim streaming/fixed returns |
| `investment_milestone` | Complete milestone (oracle) |
| `investment_info` | Get investment details |
| `investment_portfolio` | Investor's portfolio |
| `investment_treasury` | Treasury's investments |
| `investment_stats` | Protocol-wide stats |

### MCP Resources (6)

| URI | Description |
|-----|-------------|
| `paylobster://agent/{address}` | Agent profile & reputation |
| `paylobster://escrow/{id}` | Escrow status & details |
| `paylobster://credit/{address}` | Credit score & lines |
| `paylobster://stream/{id}` | Streaming payment details |
| `paylobster://dispute/{id}` | Dispute details & evidence |
| `paylobster://intent/{id}` | Intent & offers |

## REST API

Base URL: `https://paylobster.com`

| Endpoint | Description |
|----------|-------------|
| `GET /api/v3/agents/{address}` | Agent identity & capabilities |
| `GET /api/v3/reputation/{address}` | Reputation score & trust vector |
| `GET /api/v3/credit/{address}` | Credit score & health |
| `GET /api/v3/balances/{address}` | USDC balance on Base |
| `GET /api/v3/escrows` | List escrows (`?creator=` or `?provider=`) |
| `GET /api/v3/escrows/{id}` | Single escrow details |
| `POST /api/x402/negotiate` | x402 payment negotiation |
| `GET /api/badge/{address}` | Trust badge SVG |
| `GET /api/trust-check/{address}` | Quick trust verification |

## Contracts (Base Mainnet)

### V3 (Core)

| Contract | Address |
|----------|---------|
| Identity Registry | `0xA174ee274F870631B3c330a85EBCad74120BE662` |
| Reputation | `0x02bb4132a86134684976E2a52E43D59D89E64b29` |
| Credit System | `0xD9241Ce8a721Ef5fcCAc5A11983addC526eC80E1` |
| Escrow V3 | `0x49EdEe04c78B7FeD5248A20706c7a6c540748806` |

### V4 (Deployed)

| Contract | Address |
|----------|---------|
| PolicyRegistry | `0x20a30064629e797a88fCdBa2A4C310971bF8A0F2` |
| CrossRailLedger | `0x74AcB48650f12368960325d3c7304965fd62db18` |
| SpendingMandate | `0x8609eBA4F8B6081AcC8ce8B0C126C515f6140849` |
| TreasuryFactory | `0x171a685f28546a0ebb13059184db1f808b915066` |
| InvestmentTermSheet | `0xfa4d9933422401e8b0846f14889b383e068860eb` |

### V4 (Compiled, Pending Deploy)

StreamingPayment · CascadingEscrow · DisputeResolution · IntentMarketplace · ComplianceMandate · RevenueShare · ConditionalRelease · AgentCreditScore · ServiceCatalog · OracleRouter

## Contracts (Base Sepolia)

| Contract | Address |
|----------|---------|
| Identity | `0x3dfA02Ed4F0e4F10E8031d7a4cB8Ea0bBbFbCB8c` |
| Reputation | `0xb0033901e3b94f4F36dA0b3e59A1F4AD9f4f1697` |
| Credit | `0xBA64e2b2F2a80D03A4B13b3396942C1e78205C7d` |
| Escrow V3 | `0x78D1f50a1965dE34f6b5a3D3546C94FE1809Cd82` |

## Common Patterns

### Create an agent treasury

```bash
# Deploy treasury via factory
plob treasury create "My Agent Fund"

# View treasury info
plob treasury info

# Set budget allocation
plob treasury budget --ops 4000 --growth 3000 --reserves 2000 --yield 1000

# Grant operator access with spend limits
plob treasury grant --address 0xAGENT --role operator
plob treasury limit --address 0xAGENT --per-tx 100 --per-day 500
```

### Swap tokens

```bash
# Get a quote
plob swap quote --from USDC --to WETH --amount 50

# Execute swap
plob swap execute --from USDC --to WETH --amount 50

# Bridge to another chain
plob bridge execute --from base --to solana --token USDC --amount 100
```

### Invest in an agent's treasury

```bash
# Propose a revenue share investment
plob invest propose --treasury 0xAGENT_TREASURY --amount 500 \
  --type revenue-share --duration 365 --share 1500

# Fund the investment
plob invest fund 0

# Check claimable returns
plob invest info 0

# Claim returns
plob invest claim 0

# View your portfolio
plob invest portfolio
```

### Agent paying for a service

```bash
# 1. Check provider reputation
plob reputation 0xPROVIDER

# 2. Create escrow
plob escrow create --to 0xPROVIDER --amount 25

# 3. After delivery, release payment
plob escrow release <id>
```

### Streaming payment for compute

```bash
# Pay $0.001/sec for 1 hour of inference
plob stream create --to 0xPROVIDER --rate 0.001 --duration 3600
```

### Multi-agent collaboration with revenue split

```bash
# Create a revenue share for a 3-agent pipeline
plob revenue-share create --participants '[
  {"address":"0xA...","share":50},
  {"address":"0xB...","share":30},
  {"address":"0xC...","share":20}
]'
```

### Read-only queries (no wallet needed)

```bash
curl https://paylobster.com/api/v3/reputation/0xADDRESS
curl https://paylobster.com/api/v3/escrows?creator=0xADDRESS
```

## Resources

- **Website**: [paylobster.com](https://paylobster.com)
- **Docs**: [paylobster.com/docs](https://paylobster.com/docs)
- **MCP Server**: [paylobster.com/mcp-server](https://paylobster.com/mcp-server)
- **npm SDK**: [npmjs.com/package/pay-lobster](https://www.npmjs.com/package/pay-lobster)
- **npm CLI**: [npmjs.com/package/@paylobster/cli](https://www.npmjs.com/package/@paylobster/cli)
- **npm MCP**: [npmjs.com/package/@paylobster/mcp-server](https://www.npmjs.com/package/@paylobster/mcp-server)
