---
name: defipoly
description: >
  Play the Defipoly blockchain Monopoly game on Solana — buy properties, earn yield,
  steal, shield, claim rewards. Use when the user wants to play Defipoly, check their
  Defipoly portfolio, buy/sell properties, shield against theft, claim DEFI rewards,
  steal from other players, or check the leaderboard.
version: 3.0.0
metadata:
  openclaw:
    requires:
      env:
        - BACKEND_URL
        - WALLET_FILE
      bins:
        - node
    primaryEnv: BACKEND_URL
---

# Defipoly Game Agent

You are a Defipoly player. Defipoly is a Monopoly-inspired DeFi game on Solana where you buy property slots, earn daily yield in DEFI tokens, shield your properties against theft, steal from other players or the bank, and roll dice for discounts and bonuses.

## Setup

Before running any command, ensure dependencies are installed:

```bash
if [ ! -d "{baseDir}/node_modules" ]; then cd {baseDir} && npm install; fi
```

## How to Play

All game actions use the `agent-play.js` CLI script. It handles authentication, transaction signing, and submission automatically.

```bash
node {baseDir}/scripts/agent-play.js <command> [args]
```

### Environment Variables

- `WALLET_FILE` — path to JSON keypair file (e.g. `wallets/rengonclaw.json`)
- `WALLET_PRIVATE_KEY` — alternative: base58-encoded private key
- `BACKEND_URL` — e.g. `https://api.defipoly.app` or `http://localhost:3101`

### Commands

**Authentication (auto-handled, but can be run manually):**
```bash
node {baseDir}/scripts/agent-play.js auth
```

**Game actions (build -> sign -> submit in one call):**
```bash
node {baseDir}/scripts/agent-play.js init                          # Initialize player account (once)
node {baseDir}/scripts/agent-play.js buy <propertyId> [slots=1]    # Buy property slots
node {baseDir}/scripts/agent-play.js sell <propertyId> <slots>      # Sell property slots
node {baseDir}/scripts/agent-play.js shield <propertyId> [hours=24] # Activate theft protection
node {baseDir}/scripts/agent-play.js claim                          # Claim accumulated DEFI rewards
node {baseDir}/scripts/agent-play.js bank-steal <propertyId>        # Attempt bank steal
node {baseDir}/scripts/agent-play.js steal <targetWallet> <propertyId>  # Attempt player steal
```

**Read-only (no wallet needed):**
```bash
node {baseDir}/scripts/agent-play.js status       # Player profile (properties, income, cooldowns)
node {baseDir}/scripts/agent-play.js properties   # All 22 properties
node {baseDir}/scripts/agent-play.js properties 0 # Specific property
node {baseDir}/scripts/agent-play.js config       # Game config
node {baseDir}/scripts/agent-play.js leaderboard  # Top players
```

### Output Format

- Actions: `OK buy propertyId=0 slots=2 sig=5xK3...` or `FAIL <error message>`
- Read-only: JSON to stdout
- Exit code 0 = success, 1 = failure

### Examples

```bash
# Check what properties are available
node {baseDir}/scripts/agent-play.js properties

# Check your status
node {baseDir}/scripts/agent-play.js status

# Buy 2 slots of property 0 (Brown - Mediterranean Ave)
node {baseDir}/scripts/agent-play.js buy 0 2

# Shield property 0 for 24 hours
node {baseDir}/scripts/agent-play.js shield 0 24

# Claim accumulated rewards
node {baseDir}/scripts/agent-play.js claim

# Attempt bank steal on property 1
node {baseDir}/scripts/agent-play.js bank-steal 1

# Steal from another player
node {baseDir}/scripts/agent-play.js steal <theirWalletAddress> 3
```

## The 22 Properties

There are 22 properties in 8 color sets. Completing a full set gives a yield bonus.

| Set | Color | IDs | Price (DEFI) | Yield | Set Bonus | Buy Cooldown |
|-----|-------|-----|-------------|-------|-----------|--------------|
| 0 | Brown | 0-1 | 1,500 | 1-6% | 30% | 6h |
| 1 | Light Blue | 2-4 | 3,500 | 6.5% | 32.86% | 8h |
| 2 | Pink | 5-7 | 7,500 | 7% | 35.71% | 10h |
| 3 | Orange | 8-10 | 15,000 | 7.5% | 38.57% | 12h |
| 4 | Red | 11-13 | 30,000 | 8% | 41.43% | 16h |
| 5 | Yellow | 14-16 | 60,000 | 8.5% | 44.29% | 20h |
| 6 | Green | 17-19 | 120,000 | 9% | 47.14% | 24h |
| 7 | Dark Blue | 20-21 | 240,000 | 10% | 50% | 28h |

## Bank Steal Cooldowns

| Set | Cooldown |
|-----|----------|
| Brown | 30 min |
| Light Blue | 1h |
| Pink | 1.5h |
| Orange | 2h |
| Red | 3h |
| Yellow | 4h |
| Green | 5h |
| Dark Blue | 6h |

## Dice System

Players can roll dice every 6 hours. Outcomes:

| Roll | Effect |
|------|--------|
| 1+1 (snake eyes) | 5% of property value as token bonus |
| 2+2 | Double Defense: 12h steal protection on all properties |
| 3+3 | Steal Cooldown Reset: all steal cooldowns cleared |
| 4+4 | Buy Cooldown Reset: all buy cooldowns cleared |
| 5+5 | Compound Interest: claim rewards with +10% bonus |
| 6+6 (jackpot) | 50% off any property in owned sets + reset all buy cooldowns |
| Total 11 (mini jackpot) | 20% off any property in owned sets |
| Other totals | 30% off a specific color set |

Dice rolls and claims happen through the frontend — the API does not have a dice endpoint yet.

## Strategy Guidelines

When making decisions, consider:

1. **Set completion** — Owning all properties in a color set gives a large yield bonus (30-50%). Prioritize completing sets you're close to finishing.
2. **ROI** — Cheaper properties (Brown, Light Blue) have faster cooldowns and lower risk. Expensive properties (Green, Dark Blue) have higher yield but longer cooldowns and higher steal cost.
3. **Shield timing** — Shield expensive or unshielded properties before going idle. Shield duration of 24h is the default sweet spot.
4. **Claim regularly** — Unclaimed rewards don't compound. Claim when rewards have accumulated significantly.
5. **Bank steal** — Success rate varies by scarcity tier (30-70%). Cheaper properties have shorter cooldowns so you can attempt more often. Good for building up slot count on Brown/Light Blue.
6. **Diversify** — Don't put all tokens into one property. Spread across sets to reduce theft impact.
7. **Monitor cooldowns** — Check player status before attempting buys or steals to avoid wasting transactions on cooldown-blocked actions.

## Important Notes

- All on-chain transactions cost SOL for fees. Make sure your wallet has enough SOL (0.01+ SOL).
- Property prices are in DEFI tokens (6 decimals on-chain).
- Bank steal success is determined server-side. The build response includes a `success` field in `details` so you know the outcome before submitting.
- Steal attempts against players also have server-determined outcomes (~33% success rate).
- If a request fails with a rate limit or network error, wait 30-60 seconds before retrying.
- JWT tokens are cached and auto-refreshed. If you get auth errors, run `node {baseDir}/scripts/agent-play.js auth` to force re-authenticate.
- Always check game state (`status`, `properties`) before taking actions to avoid wasting SOL on transactions that will fail (e.g., cooldown active, insufficient balance).
