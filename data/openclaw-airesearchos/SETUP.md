# AIresearchOS Setup Guide

## Option 1: API Key (Recommended for Regular Use)

### 1. Create an Account

Sign up at [https://airesearchos.com](https://airesearchos.com)

### 2. Subscribe to Pro

API access requires Pro plan ($30/month). Includes 150 credits/day.

| Mode | Credits | Sources |
|------|---------|---------|
| Scan | 10 | 10-20 |
| Due Diligence | 25 | 50-100 |
| Mission Critical | 100 | 150-300+ |

### 3. Generate API Key

Go to **Dashboard > Settings > API Keys** and generate a key (starts with `aro_sk_`).

### 4. Configure OpenClaw

Add to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "airesearchos": {
        "apiKey": "aro_sk_your_key_here"
      }
    }
  }
}
```

OpenClaw maps `apiKey` to the `AIRESEARCHOS_API_KEY` environment variable at runtime via `primaryEnv`.

### 5. Start a New Session

Start a new OpenClaw session. The skill will detect your API key automatically.

---

## Option 2: x402 Pay-Per-Request (No Account Needed)

Pay with USDC stablecoins on Base network. No signup, no subscription.

### Pricing

| Mode | Cost | Sources |
|------|------|---------|
| Scan | $0.50 USDC | 10-20 |
| Due Diligence | $1.50 USDC | 50-100 |
| Mission Critical | $5.00 USDC | 150-300+ |

### 1. Prerequisites

- **Node.js 18+** installed
- A crypto wallet with **USDC on Base network** (Base mainnet, chain ID 8453)

### 2. Configure Your Wallet Key

Add to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "airesearchos": {
        "env": {
          "AIRESEARCHOS_WALLET_KEY": "0xYOUR_PRIVATE_KEY_HERE"
        }
      }
    }
  }
}
```

OpenClaw injects this into the agent's environment at runtime. It is NOT added to your global shell environment.

**IMPORTANT:** Never share your private key. Never paste it into chat.

### 3. Install x402 Dependencies

The skill bundles a `scripts/package.json` with the required x402 packages. On first use, the agent will run:

```bash
cd {baseDir}/scripts && npm install
```

This installs `@x402/core`, `@x402/evm`, and `viem` locally in the skill's scripts directory. No global packages.

### 4. Getting USDC on Base

**Option A: Coinbase**
1. Buy USDC on Coinbase
2. Withdraw to your wallet address on **Base network**

**Option B: Bridge from Ethereum**
1. Go to [bridge.base.org](https://bridge.base.org)
2. Bridge USDC from Ethereum mainnet to Base

**Option C: Swap on Base**
1. Use a DEX on Base (Uniswap, Aerodrome)
2. Swap ETH → USDC

### 5. Start a New Session

Start a new OpenClaw session. The skill will detect your wallet key and offer x402 payments.

---

## Optional: Custom Base URL

If you're running a self-hosted AIresearchOS instance, set:

```json
{
  "skills": {
    "entries": {
      "airesearchos": {
        "env": {
          "AIRESEARCHOS_BASE_URL": "https://your-instance.example.com"
        }
      }
    }
  }
}
```

Default: `https://airesearchos.com`

---

## Advanced: Coinbase AgentKit

If you need broader blockchain capabilities beyond x402 payments (e.g., programmatic wallet management, multi-chain operations), see Coinbase's AgentKit: https://docs.cdp.coinbase.com/agent-kit/welcome

For this skill, the x402 packages above are all you need.
