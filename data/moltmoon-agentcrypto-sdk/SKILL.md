---
name: moltmoon-sdk
description: Complete OpenClaw-ready operating skill for @moltmoon/sdk V2. Use when an agent needs to install, configure, and operate the MoltMoon SDK or CLI end-to-end on Base mainnet, including launch dry-runs, metadata/image validation, live token launches, quote checks, buys, sells, rewards claiming, migration, troubleshooting, and safe production runbooks.
---

# MoltMoon SDK Skill (OpenClaw) - V2

Use this skill to operate the MoltMoon SDK/CLI as a complete agent workflow on Base mainnet.

## V2 Economics Overview

MoltMoon V2 uses **MoltTokenV2** (SafeMoon-style reflection tokens) with **BondingCurveMarketV2** bonding curves:

| Parameter | Value |
|-----------|-------|
| Total supply | 1B tokens per launch |
| Buy fee | 0% |
| Sell fee | 5% (1% holder reflections + 2% creator + 2% treasury) |
| Curve allocation | 80% on bonding curve, 20% reserved for LP |
| Virtual base | $3,000 USDC |
| Min seed (normal) | $20 USDC |
| Platform cut | 10% of seed to treasury |
| Graduation | At 95% of curve tokens sold (avoids asymptotic pricing) |
| LP lock | 180 days on Aerodrome after graduation |
| Creator upfront | Seed-scaled share from curve bucket (capped 20%) |

**Reflection mechanics**: Every sell triggers 1% redistribution to all token holders (SafeMoon rOwned/tOwned). 4% is auto-swapped to USDC and split 50/50 between creator and treasury. Buys and wallet-to-wallet transfers are tax-free.

**Post-graduation**: After graduating to Aerodrome DEX, the sell tax continues via multi-DEX pair detection. LP is time-locked for 180 days.

## Install

Use one of these paths:

```bash
npm install @moltmoon/sdk
```

or run without install:

```bash
npx -y @moltmoon/sdk moltlaunch --help
```

## Runtime Configuration

Set environment variables before any write action:

```env
MOLTMOON_API_URL=https://api.moltmoon.ai
MOLTMOON_NETWORK=base
MOLTMOON_PRIVATE_KEY=0x...   # 32-byte hex key with 0x prefix
```

Notes:
- `MOLTMOON_NETWORK` supports `base` only.
- `MOLTMOON_PRIVATE_KEY` (or `PRIVATE_KEY`) is required for launch/buy/sell/claim.

## Supported CLI Commands

Global options:
- `--api-url <url>`
- `--network base`
- `--private-key <0x...>`

Commands:
- `launch` Launch token (with metadata/image/socials, includes approval + create flow)
- `tokens` List tokens
- `buy` Approve USDC + buy in one flow
- `sell` Approve token + sell in one flow
- `quote-buy` Fetch buy quote only (0% fee)
- `quote-sell` Fetch sell quote only (shows 5% fee deducted)
- `rewards-earned` Check unclaimed USDC rewards for a wallet
- `rewards-claim` Claim unclaimed USDC rewards (requires signer)
- `migration-status` Check V1 to V2 migration status
- `migrate` Migrate V1 tokens to V2 (approve + migrate flow)

## Canonical CLI Runbooks

### 1) Dry-run launch first (no chain tx)

```bash
npx -y @moltmoon/sdk mltl launch \
  --name "Agent Token" \
  --symbol "AGT" \
  --description "Agent launch token on MoltMoon" \
  --website "https://example.com" \
  --twitter "https://x.com/example" \
  --discord "https://discord.gg/example" \
  --image "./logo.png" \
  --seed 20 \
  --dry-run \
  --json
```

### 2) Live launch

```bash
npx -y @moltmoon/sdk mltl launch \
  --name "Agent Token" \
  --symbol "AGT" \
  --description "Agent launch token on MoltMoon" \
  --seed 20 \
  --json
```

### 3) Trade flow

```bash
# Buy (0% fee)
npx -y @moltmoon/sdk mltl quote-buy --market 0xMARKET --usdc 1 --json
npx -y @moltmoon/sdk mltl buy --market 0xMARKET --usdc 1 --slippage 500 --json

# Sell (5% fee: 1% reflection + 2% creator + 2% treasury)
npx -y @moltmoon/sdk mltl quote-sell --market 0xMARKET --tokens 100 --json
npx -y @moltmoon/sdk mltl sell --market 0xMARKET --token 0xTOKEN --amount 100 --slippage 500 --json
```

### 4) Rewards flow ($MOLTM holders)

```bash
# Check earned USDC rewards
npx -y @moltmoon/sdk mltl rewards-earned --pool 0xPOOL --account 0xWALLET --json

# Claim rewards
npx -y @moltmoon/sdk mltl rewards-claim --pool 0xPOOL --json
```

### 5) V1 to V2 migration

```bash
# Check migration status
npx -y @moltmoon/sdk mltl migration-status --json

# Migrate tokens (approve + swap)
npx -y @moltmoon/sdk mltl migrate --amount 1000 --json
```

## SDK API Surface

Initialize:

```ts
import { MoltmoonSDK } from '@moltmoon/sdk';

const sdk = new MoltmoonSDK({
  baseUrl: process.env.MOLTMOON_API_URL || 'https://api.moltmoon.ai',
  network: 'base',
  privateKey: process.env.MOLTMOON_PRIVATE_KEY as `0x${string}`,
});
```

Read methods:
- `getTokens()` - List all launched tokens
- `getMarket(marketAddress)` - Full market details (V2: includes `holderRewardsPool`, `aerodromePool`, `virtualBase`, `liquidityTokens`, `creator`, `usdc`)
- `getQuoteBuy(marketAddress, usdcIn)` - Buy quote (0% fee)
- `getQuoteSell(marketAddress, tokensIn)` - Sell quote (5% fee deducted)

Launch methods:
- `prepareLaunchToken(params)` -> metadata URI + intents only (dry-run)
- `launchToken(params)` -> executes approve + create

Trade methods:
- `buy(marketAddress, usdcIn, slippageBps?)` - Approve USDC + buy
- `sell(marketAddress, tokensIn, tokenAddress, slippageBps?)` - Approve token + sell

Rewards methods:
- `getRewardsEarned(poolAddress, account)` - Check unclaimed USDC
- `claimRewards(poolAddress)` - Claim USDC rewards

Migration methods:
- `getMigrationStatus()` - V1/V2 migration state
- `migrate(v1Amount)` - Approve V1 + migrate to V2

Utility methods:
- `calculateProgress(marketDetails)` - Graduation progress %
- `calculateMarketCap(marketDetails)` - Market cap in USDC

## MarketDetails V2 Fields

The `getMarket()` response now includes:

```ts
interface MarketDetails {
  market: string;
  token: string;
  usdc: string;                  // USDC contract address
  graduated: boolean;            // true after 95% sold
  curveTokensRemaining: string;
  baseReserveReal: string;       // real USDC in curve
  totalBaseReserve: string;      // virtual + real
  virtualBase: string;           // $3,000 USDC virtual
  liquidityTokens: string;       // reserved for Aerodrome LP
  sellFeeBps: number;            // 500 (5%)
  creator: string;               // token creator address
  holderRewardsPool: string;     // $MOLTM rewards pool
  aerodromePool: string | null;  // DEX pool after graduation
  progressPercent: number;       // 0-95 (graduates at 95)
}
```

## Launch Metadata + Image Rules

Enforce these before launch:
- Image must be PNG or JPEG
- Max size 500KB (`<=100KB` recommended)
- Dimensions must be square, min `512x512`, max `2048x2048`
- Social links must be valid URLs
- Seed for normal launch must be at least `20` USDC

## Failure Diagnosis

- `Missing private key`
  - Set `MOLTMOON_PRIVATE_KEY` or pass `--private-key`.
- `Unsupported network`
  - Use `base` only.
- `transfer amount exceeds allowance`
  - Re-run buy/sell/launch flow so approvals execute.
- `transfer amount exceeds balance`
  - Fund signer with Base ETH (gas) and USDC/token balance.
- `graduated`
  - Market has graduated to Aerodrome. Trade on DEX directly.
- `slippage`
  - Increase `--slippage` bps or reduce trade size.
- `curve`
  - Not enough tokens remaining on curve for requested buy.
- `threshold`
  - Graduation threshold not yet met (need 95% sold).
- `ERR_NAME_NOT_RESOLVED` or fetch errors
  - Check `MOLTMOON_API_URL` DNS and API uptime.
- image validation errors
  - Fix file type/size/dimensions to rules above.

## Operator Policy

- Run dry-run before every first live launch for a new token payload.
- Confirm signer address and chain before write calls.
- Keep secrets in `.env`; never commit keys.
- Record tx hashes after launch/buy/sell/claim for audit trail.
- Graduation is automatic at 95% curve sold - no manual trigger needed.
- After graduation, tokens trade on Aerodrome with continued 5% sell tax.
- $MOLTM holders earn passive USDC from ALL platform sell activity via HolderRewardsPool.
