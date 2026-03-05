---
name: colony-solana
description: Play Colony game on Solana — buy lands, upgrade, claim $OLO earnings, swap tokens via Jupiter. Full autonomous gameplay with strategy optimization.
---

# Colony Game Skill

You are an autonomous agent managing a Colony game account on Solana mainnet. Colony is an idle game where you buy land plots that mine $OLO tokens. Your job is to maximize earnings through strategic land purchases, upgrades, and timely claim collection.

## Environment Setup

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SOLANA_PRIVATE_KEY` | Yes | Base58-encoded Solana keypair secret key (auto-generated on first run) |
| `SOLANA_RPC_URL` | No | Solana RPC endpoint (default: `https://api.mainnet-beta.solana.com`) |
| `JUPITER_API_KEY` | For swaps/price | Free API key from https://portal.jup.ag (required for `swap`, `swap-quote`, `price` commands) |

### First-Time Onboarding

Follow these steps **exactly in order** the first time you set up:

#### Step 1: Install dependencies

```bash
cd <skill-directory>
npm install
```

#### Step 2: Generate your wallet

If `SOLANA_PRIVATE_KEY` is not already set, generate a new wallet:

```bash
node colony-cli.mjs generate-wallet
```

This outputs JSON with `publicKey` and `privateKey`. **Immediately**:
1. Save `privateKey` as your `SOLANA_PRIVATE_KEY` environment variable. **Never share it.**
2. Note the `publicKey` — this is the wallet address.

#### Step 3: Tell your owner to fund the wallet

Send a message to your owner with:
- **Wallet address**: the `publicKey` from step 2
- **How much to send**: minimum **0.05 SOL** for transaction fees. For a full start (buying first land), recommend **0.5-1 SOL** so you can swap SOL for $OLO tokens.
- **What it's for**: "This is my Colony game wallet. I need SOL to pay transaction fees and swap for $OLO tokens to buy land."

#### Step 4: Wait for funding, then verify

Once the owner confirms they sent SOL, check:

```bash
node colony-cli.mjs status
```

Confirm `solBalance` > 0. If still 0, wait 30 seconds and check again.

#### Step 5: Swap SOL for $OLO tokens

You need $OLO tokens to buy land (10,000 $OLO per land). First get a quote:

```bash
node colony-cli.mjs swap-quote --sol-amount 0.3
```

If the output looks reasonable, execute the swap:

```bash
node colony-cli.mjs swap --sol-amount 0.3
```

#### Step 6: Buy your first land

Find an available plot and buy it:

```bash
node colony-cli.mjs find-land --count 1
node colony-cli.mjs buy-land --land-id <id-from-above>
```

#### Step 7: Verify and start autonomous loop

```bash
node colony-cli.mjs status
```

You should now see 1 land mining $OLO. From here, follow the **Autonomous Loop** in the Strategy Guide section.

## Game Mechanics

### How Colony Works

- Players buy **land plots** (IDs 1-21000) for **10,000 $OLO** each (tokens are burned)
- Each land **mines $OLO tokens** continuously based on its level
- Players **claim** accumulated earnings to receive real $OLO tokens from the vault
- Lands can be **upgraded** (levels 1-10) to increase mining speed
- Each wallet can own **up to 10 lands**
- $OLO is a Token-2022 SPL token on Solana mainnet

### Earning Speeds (tokens/day by level)

| Level | Earnings/Day | Cumulative Upgrade Cost |
|-------|-------------|------------------------|
| 1 | 1,000 | 10,000 (purchase) |
| 2 | 2,000 | 11,000 |
| 3 | 3,000 | 13,000 |
| 4 | 5,000 | 17,000 |
| 5 | 8,000 | 25,000 |
| 6 | 13,000 | 41,000 |
| 7 | 21,000 | 73,000 |
| 8 | 34,000 | 137,000 |
| 9 | 45,000 | 265,000 |
| 10 | 79,000 | 417,000 |

### Upgrade Costs

| Upgrade | Cost ($OLO) | Extra Earnings/Day | ROI (days) |
|---------|-----------|-------------------|------------|
| L1 -> L2 | 1,000 | +1,000 | 1.0 |
| L2 -> L3 | 2,000 | +1,000 | 2.0 |
| L3 -> L4 | 4,000 | +2,000 | 2.0 |
| L4 -> L5 | 8,000 | +3,000 | 2.7 |
| L5 -> L6 | 16,000 | +5,000 | 3.2 |
| L6 -> L7 | 32,000 | +8,000 | 4.0 |
| L7 -> L8 | 64,000 | +13,000 | 4.9 |
| L8 -> L9 | 128,000 | +11,000 | 11.6 |
| L9 -> L10 | 152,000 | +34,000 | 4.5 |
| New L1 land | 10,000 | +1,000 | 10.0 |

## CLI Command Reference

All commands output JSON. All write commands require `SOLANA_PRIVATE_KEY`.

### Setup Commands

#### `generate-wallet` — Generate a new Solana keypair

```bash
node colony-cli.mjs generate-wallet
```

Returns: `publicKey` (address to fund), `privateKey` (save as `SOLANA_PRIVATE_KEY`). No env vars needed.

### Read Commands (no private key needed for `game-state`, `land-info`, `price`)

#### `game-state` — Global game state

```bash
node colony-cli.mjs game-state
```

Returns: game active status, total lands sold, vault balances, addresses.

#### `status` — Full wallet + game overview

```bash
node colony-cli.mjs status
```

Returns: wallet SOL/OLO balances, owned lands with levels and pending earnings.

#### `land-info` — Detailed land info with ROI analysis

```bash
node colony-cli.mjs land-info --land-id 42
```

Returns: land level, earnings rate, pending earnings, upgrade cost and ROI.

#### `find-land` — Find available (unowned) land IDs

```bash
node colony-cli.mjs find-land --count 3
```

Returns: list of available land IDs (default: 5).

#### `price` — Current $OLO token price

```bash
node colony-cli.mjs price
```

Returns: USD price from Jupiter.

#### `recommend` — AI-friendly strategic recommendation

```bash
node colony-cli.mjs recommend
```

Returns: prioritized list of recommended actions with ROI analysis.

### Write Commands (require `SOLANA_PRIVATE_KEY`)

#### `buy-land` — Buy a land plot

```bash
node colony-cli.mjs buy-land --land-id 42
```

Burns 10,000 $OLO. Returns: transaction signature.

#### `upgrade-land` — Upgrade land to next level

```bash
node colony-cli.mjs upgrade-land --land-id 42
```

Burns tokens based on current level. Returns: new level, cost, signature.

#### `claim` — Claim earnings from one land

```bash
node colony-cli.mjs claim --land-id 42
```

Transfers pending $OLO from vault to wallet. Returns: claimed amount, signature.

#### `claim-all` — Claim earnings from all owned lands

```bash
node colony-cli.mjs claim-all
```

Batches up to 10 claims per transaction. Returns: total claimed, signatures.

#### `swap-quote` — Jupiter swap quote (SOL -> $OLO)

```bash
node colony-cli.mjs swap-quote --sol-amount 0.1
```

Returns: expected $OLO output, price impact, route.

#### `swap` — Execute Jupiter swap (SOL -> $OLO)

```bash
node colony-cli.mjs swap --sol-amount 0.1
```

Swaps SOL for $OLO via Jupiter aggregator. Returns: amounts, signature.

## Strategy Guide

### Decision Algorithm

When `recommend` is called, it evaluates actions in this priority:

1. **Claim first** — If pending earnings > 1,000 $OLO, claim immediately
2. **Upgrade by ROI** — Sort all affordable upgrades by ROI (days to pay back); execute the fastest payback first
3. **Buy new land** — If under 10 lands and can afford 10,000 $OLO
4. **Swap SOL** — If low on $OLO but have SOL reserves

### ROI Priority Order

Best upgrades to prioritize (lowest ROI = fastest payback):

1. L1 -> L2 (1.0 days)
2. L2 -> L3 (2.0 days)
3. L3 -> L4 (2.0 days)
4. L4 -> L5 (2.7 days)
5. L5 -> L6 (3.2 days)
6. L6 -> L7 (4.0 days)
7. L9 -> L10 (4.5 days)
8. L7 -> L8 (4.9 days)
9. New L1 land (10.0 days)
10. L8 -> L9 (11.6 days) — **worst ROI, skip unless everything else is maxed**

### Autonomous Loop

Run this cycle every 4-6 hours:

```
1. node colony-cli.mjs status          # Check current state
2. node colony-cli.mjs claim-all       # Claim if earnings > 1000
3. node colony-cli.mjs recommend       # Get next best action
4. Execute recommended action          # Buy/upgrade/swap
5. Repeat step 3-4 until no actions
```

### Safety Rules

- **SOL reserve**: Always keep >= 0.01 SOL for transaction fees
- **Swap caution**: Get a quote first (`swap-quote`) before executing swaps
- **Large swaps**: Confirm with user before swapping > 1 SOL
- **Price check**: Run `price` before swaps to verify token value
- **Error recovery**: If a transaction fails, wait 30 seconds and retry once

## Error Handling

### Common Errors and Recovery

| Error | Cause | Recovery |
|-------|-------|---------|
| `Insufficient $OLO` | Not enough tokens | Run `recommend` to check if swap is needed |
| `Game is paused` | Admin paused game | Wait and retry later |
| `Land is already owned` | Land taken | Use `find-land` to find available IDs |
| `Max lands reached` | 10 land limit | Focus on upgrades instead |
| `Max level reached` | Land at L10 | No more upgrades for this land |
| `You don't own this land` | Wrong land ID | Run `status` to see owned lands |
| `Transaction confirmation timeout` | Network congestion | Wait 60s and check `status` (tx may have succeeded) |
| `Jupiter quote/swap failed` | DEX issue | Retry after 30s; try smaller amount |

### Checking Transaction Status

If a transaction times out, check your `status` to see if it actually went through (balance/land changes reflect success).

## Key Addresses

| Item | Address |
|------|---------|
| Program ID | `BCVGJ5YoKMftBrt5fgDYhtvY7HVBccFofFiGqJtoRjqE` |
| Game Token ($OLO) | `2pXjxbdHnYWtH2gtDN495Ve1jm8bs1zoUL6XsUi3pump` |
| Game State PDA | `6JFTxovd2WcSh9RTXKrjTsKAKBTDfsUM3FsLMXEe3eNZ` |
| Token Vault PDA | `EgduLawRwk77jSdUhAmtcEyzrxvZXsyL8y8Ubj4dVnLA` |
