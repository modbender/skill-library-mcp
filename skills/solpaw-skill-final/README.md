# SolPaw Skill for OpenClaw

**Launch tokens on Solana via Pump.fun — directly from your OpenClaw agent.**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/LvcidPsyche/solpaw-skill)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Website](https://img.shields.io/badge/Website-solpaw.fun-orange)](https://solpaw.fun)
[![API Docs](https://img.shields.io/badge/API-Docs-blue)](https://solpaw.fun/docs)

---

## Overview

SolPaw Skill enables OpenClaw agents to autonomously launch memecoins on Solana through Pump.fun. Perfect for:

- AI agents creating community tokens
- Automated trading bot launches
- Agent identity/reputation tokens
- Experimental DeFi projects

**Pricing:**
- **0.1 SOL** one-time launch fee
- **No ongoing fees ever**
- Creator wallet receives 100% of Pump.fun trading fees

---

## Quick Start

### 1. Install the Skill

```bash
openclaw skills install solpaw-launcher
```

Or manually clone to your skills directory:

```bash
cd ~/.openclaw/skills
git clone https://github.com/LvcidPsyche/solpaw-skill.git solpaw-launcher
```

### 2. Configure

Add to your `agent-config.yml`:

```yaml
skills:
  - name: solpaw-launcher
    config:
      api_endpoint: https://api.solpaw.fun/api/v1
      api_key: ${SOLPAW_API_KEY}
      default_creator_wallet: ${CREATOR_WALLET}
```

Set environment variables:

```bash
export SOLPAW_API_KEY="sk-solpaw-your-api-key"
export CREATOR_WALLET="YourSolanaWalletAddress"
```

### 3. Register Your Agent

```bash
curl -X POST https://api.solpaw.fun/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "MyCoolAgent",
    "default_fee_wallet": "'${CREATOR_WALLET}'"
  }'
```

Save the returned `api_key` — it's shown only once.

### 4. Launch a Token

```typescript
import SolPawSkill from './solpaw-skill';

const solpaw = new SolPawSkill({
  apiEndpoint: 'https://api.solpaw.fun/api/v1',
  apiKey: process.env.SOLPAW_API_KEY,
  defaultCreatorWallet: process.env.CREATOR_WALLET,
});

// Launch!
const result = await solpaw.launchToken({
  name: 'AgentCoin',
  symbol: 'AGENT',
  description: 'Launched autonomously by an AI agent on Solana',
  launch_fee_signature: 'your-0.1-sol-payment-signature',
  initial_buy_sol: 0.5,
});

if (result.success) {
  console.log(`🚀 Token launched: ${result.pumpfun_url}`);
  console.log(`💰 Mint: ${result.mint}`);
} else {
  console.error(`❌ Launch failed: ${result.error}`);
}
```

---

## API Reference

### Constructor

```typescript
new SolPawSkill(config: SolPawConfig)
```

**Config:**
- `apiEndpoint` (string, required): SolPaw API URL
- `apiKey` (string, required): Your agent API key
- `defaultCreatorWallet` (string, required): Default Solana wallet for fees

### Methods

#### `getPlatformInfo()`

Get platform configuration — wallet address, launch fee, and daily limits.

```typescript
const info = await solpaw.getPlatformInfo();
// {
//   platform_wallet: "GosroTTvsbgc8FdqSdNtrmWxGbZp2ShH5NP5pK1yAR4K",
//   launch_fee_sol: 0.1,
//   daily_limit: 1
// }
```

#### `launchToken(params)`

Launch a token on Pump.fun.

**Parameters:**
- `name` (string, required): Token name (min 2 chars)
- `symbol` (string, required): Token symbol (min 2 chars)
- `description` (string, required): Token description (min 10 chars)
- `launch_fee_signature` (string, required): Transaction signature of 0.1 SOL payment
- `image_url` (string, optional): Token image URL
- `creator_wallet` (string, optional): Override default creator wallet
- `twitter` (string, optional): Twitter/X URL
- `telegram` (string, optional): Telegram URL
- `website` (string, optional): Website URL
- `initial_buy_sol` (number, optional): Initial SOL to buy (default: 0)
- `slippage` (number, optional): Slippage % (default: 10)
- `priority_fee` (number, optional): Priority fee in SOL (default: 0.0005)

**Returns:**
```typescript
{
  success: boolean;
  mint?: string;              // Token mint address
  signature?: string;         // Transaction signature
  pumpfun_url?: string;       // Pump.fun page URL
  solscan_url?: string;       // Solscan explorer URL
  launch_fee?: {
    amount_sol: number;
    platform_wallet: string;
    payment_signature: string;
  };
  error?: string;             // Error message if failed
}
```

#### `getMyTokens(page?, limit?)`

List tokens launched by this agent.

```typescript
const { tokens, total } = await solpaw.getMyTokens(1, 20);
```

#### `getFeeSummary()`

Get fee earnings summary.

```typescript
const fees = await solpaw.getFeeSummary();
// {
//   total_fees_sol: 1.5,
//   platform_share_sol: 0.15,
//   token_count: 3
// }
```

#### `getPlatformStats()`

Get public platform statistics.

```typescript
const stats = await solpaw.getPlatformStats();
```

---

## Launch Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Agent     │────▶│  SolPaw API  │────▶│  PumpPortal API │
│  (You)      │     │ (This Skill) │     │   (pump.fun)    │
└──────┬──────┘     └──────────────┘     └─────────────────┘
       │                                         │
       │ 1. Send 0.1 SOL to platform wallet      │
       │◄────────────────────────────────────────┘
       │
       │ 2. Call launchToken() with tx signature
       │─────────────────────────────────────────▶
       │
       │ 3. Server verifies payment on-chain
       │    Uploads metadata to IPFS
       │    Calls PumpPortal API
       │
       │◄─────────────────────────────────────────
       │ 4. Return mint, signature, URLs
```

---

## Security

- **Private keys never touch the server** — You sign the 0.1 SOL payment locally
- **CSRF protection** — Single-use tokens for state-changing operations
- **Rate limiting** — 3 launches per minute, 1 per day per agent
- **Payment verification** — Each 0.1 SOL transaction verified on-chain
- **Signature deduplication** — Each payment can only be used once

---

## Self-Hosting (Optional)

Want to run your own SolPaw instance?

```bash
git clone https://github.com/LvcidPsyche/solpaw.git
cd solpaw
cp .env.example .env
# Edit .env with your values
docker compose up -d
```

See the [main repo](https://github.com/LvcidPsyche/solpaw) for full deployment docs.

---

## Requirements

- OpenClaw agent with skills support
- Node.js 20+ (for TypeScript skill)
- Solana wallet with 0.1 SOL + transaction fees
- PumpPortal API key (if self-hosting)

---

## License

MIT © 2026 SolPaw

---

## Links

- **Main Repo:** https://github.com/LvcidPsyche/solpaw
- **API Docs:** https://api.solpaw.fun/api/v1/info
- **Pump.fun:** https://pump.fun
- **OpenClaw:** https://openclaw.ai
