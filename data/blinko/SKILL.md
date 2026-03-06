---
name: blinko
version: 1.1.0
description: Play Blinko (on-chain Plinko) headlessly on Abstract chain. Use when an agent wants to play Blinko games, check game stats, view leaderboards, or track honey rewards. Handles the full commit-reveal flow including API auth, on-chain game creation, simulation, and settlement.
author: Bearish (@BearishAF)
metadata: {"clawdbot":{"env":["WALLET_PRIVATE_KEY"]}}
---

# Blinko

Play [Blinko](https://blinko.gg) headlessly on Abstract. Provably fair Plinko with on-chain settlement.

## Important

- **This skill signs on-chain transactions that spend real ETH.** Use a dedicated hot wallet with only the funds you're willing to risk.
- Each game costs gas (Abstract chain) on top of your bet amount.
- Your private key is used locally to sign messages and transactions. It is sent to the Abstract RPC and Blinko API as signed outputs only, never as plaintext.
- Agents can invoke this skill autonomously when installed.

## Quick Start

### Play a Game
```bash
export WALLET_PRIVATE_KEY=0x...
node scripts/play-blinko.js 0.001
```

### Check Stats
```bash
node scripts/stats.js 0xYourAddress profile
```

## Scripts

| Script | Purpose |
|--------|---------|
| `play-blinko.js` | Play a full game (auth → create → commit → play → settle) |
| `stats.js` | View profile, games, leaderboard, honey balance |

## Play

```bash
export WALLET_PRIVATE_KEY=0x...
node scripts/play-blinko.js [betETH] [--hard] [--v2]
```

| Flag | Effect |
|------|--------|
| `--hard` | Hard mode (0% main game RTP, must trigger bonus to win) |
| `--v2` | V2 algorithm and config |

Examples:
```bash
node scripts/play-blinko.js 0.001                # Normal, 0.001 ETH
node scripts/play-blinko.js 0.005 --hard          # Hard mode
node scripts/play-blinko.js 0.002 --v2            # V2 algorithm
node scripts/play-blinko.js 0.003 --hard --v2     # V2 hard mode
```

**Bet limits:** 0.0001 - 0.1 ETH

## Stats

```bash
node scripts/stats.js <address> [command] [limit]
```

| Command | Shows |
|---------|-------|
| `profile` | Name, honey, game stats, streak |
| `games [N]` | Last N games with results |
| `leaderboard` | Top 10 + your rank |
| `honey` | Honey balance breakdown |

## How It Works

```
API → Chain → API → Chain
```

1. **Login** — Sign message with wallet, get JWT
2. **Create** — API generates game seed, returns server signature
3. **Commit** — Call `createGame()` on-chain with ETH bet + random salt
4. **Play** — API combines seeds, simulates physics, returns result
5. **Settle** — Call `cashOut()` (win) or `markGameAsLost()` (loss) on-chain

All games are provably fair via commit-reveal scheme.

## Game Mechanics

- **10 balls** dropped through 8 rows of pins
- **Bin multipliers:** 2x, 1.5x, 0.5x, 0.2x, 0.1x, 0.1x, 0.2x, 0.5x, 1.5x, 2x
- **Bonus:** Collect B-O-N-U-S letters to trigger bonus rounds (up to level 9)
- **Honey:** Earned by hitting special pins (requires a referrer)

## Key Information

| Item | Value |
|------|-------|
| Chain | Abstract (2741) |
| RPC | `https://api.abs.xyz` (hardcoded) |
| Contract | `0x1859072d67fdD26c8782C90A1E4F078901c0d763` |
| API | `https://api.blinko.gg` |
| Game | [blinko.gg](https://blinko.gg) |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `WALLET_PRIVATE_KEY` | Yes (for play) | Private key for signing transactions. Use a hot wallet. |

## Dependencies

```bash
npm install ethers@6
```
