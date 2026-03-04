# Colony OpenClaw Skill

OpenClaw skill for autonomously playing [Colony](https://colony.game) — a Solana idle game where you buy land plots that mine $OLO tokens.

## What This Does

An OpenClaw agent with this skill can:
- Generate its own Solana wallet and ask the owner to fund it
- Buy land plots, upgrade them, and claim $OLO earnings
- Swap SOL for $OLO via Jupiter
- Make strategic decisions (best ROI upgrades, when to claim, when to buy)
- Run autonomously on a 4-6 hour loop

## Quick Start

```bash
git clone https://github.com/manylov/colony-openclaw-skill.git
cd colony-openclaw-skill
npm install
```

### Generate a wallet

```bash
node colony-cli.mjs generate-wallet
```

Save the `privateKey` as `SOLANA_PRIVATE_KEY` env var. Fund the `publicKey` address with SOL.

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SOLANA_PRIVATE_KEY` | Yes | Base58 secret key (use `generate-wallet` to create) |
| `SOLANA_RPC_URL` | No | Solana RPC (default: mainnet public) |
| `JUPITER_API_KEY` | For swaps | Free key from https://portal.jup.ag |

### Commands

| Command | Description |
|---------|-------------|
| `generate-wallet` | Create a new Solana keypair |
| `status` | Wallet balances + owned lands + pending earnings |
| `game-state` | Global game state |
| `buy-land --land-id <id>` | Buy a land (burns 10k $OLO) |
| `find-land [--count N]` | Find available land IDs |
| `upgrade-land --land-id <id>` | Upgrade land to next level |
| `claim --land-id <id>` | Claim earnings from one land |
| `claim-all` | Claim all earnings (batched) |
| `land-info --land-id <id>` | Land details + ROI analysis |
| `swap-quote --sol-amount <amt>` | Jupiter quote (SOL -> $OLO) |
| `swap --sol-amount <amt>` | Execute swap |
| `recommend` | AI-friendly next best action |
| `price` | $OLO token price |

All commands output JSON.

## For OpenClaw Agents

The full agent instructions are in [SKILL.md](./SKILL.md) — game mechanics, strategy guide, onboarding flow, error handling.

## Key Info

- **Network**: Solana Mainnet
- **Game Token**: $OLO (`2pXjxbdHnYWtH2gtDN495Ve1jm8bs1zoUL6XsUi3pump`)
- **Program**: `BCVGJ5YoKMftBrt5fgDYhtvY7HVBccFofFiGqJtoRjqE`
- **Max lands per wallet**: 10
- **Land price**: 10,000 $OLO (burned)
- **Levels**: 1-10, earning 1k-79k $OLO/day
