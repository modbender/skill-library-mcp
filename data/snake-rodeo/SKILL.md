---
name: snake-rodeo
description: >
  Autoplay daemon for the Trifle Snake Rodeo game. Connects to a live game server,
  authenticates via wallet, and votes on snake directions using pluggable AI strategies.
  Use when the user wants to play snake rodeo, run game simulations, or build custom strategies.
license: MIT
compatibility: Requires Node.js 18+. Depends on trifle-auth skill for initial authentication.
metadata:
  author: trifle-labs
  version: "3.2.0"
  homepage: https://snake.rodeo
---

# Snake Rodeo Skill

Play the [Trifle Snake Rodeo](https://trifle.life) automatically with a persistent daemon and modular strategy system. Built on the [snake-rodeo-agents](https://github.com/trifle-labs/snake-rodeo-agents) library.

## How It Works

The game is a multiplayer snake on a grid (hex or cartesian). Teams bid on directions each round — the highest bidder's direction wins. All bids go into a prize pool that the winning team splits. The daemon watches the game via SSE, picks optimal directions using a strategy, and submits votes automatically.

## Prerequisites

- Authenticated via `trifle-auth` skill
- Node.js 18+
- Ball balance (earned from games, auth bonuses, etc.)

## Daemon Commands

```bash
# Start/stop
node snake.mjs start [--detach] [--strategy NAME]
node snake.mjs stop
node snake.mjs status
node snake.mjs attach [-f]

# Pause/resume voting (daemon keeps running)
node snake.mjs pause
node snake.mjs resume

# Configuration
node snake.mjs config [key] [value]
node snake.mjs strategies
node snake.mjs server [live|staging]
node snake.mjs telegram [chat_id|off]

# Manual play
node snake.mjs state
node snake.mjs vote <direction> <team> [amount]
node snake.mjs strategy    # Analyze current game
node snake.mjs balance
```

## Strategies

Five built-in strategies are available. Each extends `BaseStrategy` from `snake-rodeo-agents`.

| Strategy | Alias | Description |
|----------|-------|-------------|
| `expected-value` | `ev`, `default` | BFS pathfinding, dead-end avoidance, game-theoretic team selection, probabilistic defection in multi-agent scenarios. Balanced. |
| `aggressive` | `agg` | Backs leading teams, counter-bids aggressively. |
| `underdog` | `und` | Backs small pools for bigger payouts. |
| `conservative` | `con` | Minimum bids, prioritizes safety. |
| `random` | `rand` | Random valid moves. |

Switch strategy:

```bash
node snake.mjs config strategy aggressive
# or
node snake.mjs start --strategy aggressive
```

### Creating Custom Strategies

Extend `BaseStrategy` from `snake-rodeo-agents`:

```javascript
import { BaseStrategy } from 'snake-rodeo-agents';

export class MyStrategy extends BaseStrategy {
  constructor(options = {}) {
    super('my-strategy', 'My custom strategy', options);
  }

  computeVote(parsed, balance, state) {
    // parsed: ParsedGameState — hex grid, teams, scores, valid directions
    // balance: number — current ball balance
    // state: AgentState — round tracking, team assignment, vote history

    // Return a vote:
    return { direction: 'ne', team: 'A', amount: 1, reason: 'chasing fruit' };

    // Or skip:
    return { skip: true, reason: 'too risky' };
  }

  // Optional: counter-bid when outbid
  shouldCounterBid(parsed, balance, state, ourVote) {
    return null; // or return a new VoteAction
  }
}
```

Key types for strategy development:

- **`ParsedGameState`** — Parsed game with `head`, `teams[]`, `validDirections[]`, `gridRadius`, `prizePool`, `minBid`, `fruitsToWin`
- **`AgentState`** — `{ currentTeam, roundSpend, roundVoteCount, lastRound, gamesPlayed, votesPlaced, wins }`
- **`VoteAction`** — `{ direction, team, amount, reason }`

## snake-rodeo-agents Library

The core logic lives in [snake-rodeo-agents](https://github.com/trifle-labs/snake-rodeo-agents), a standalone TypeScript library. This skill wraps it with daemon management, config persistence, and OpenClaw integration.

### API Client

```javascript
import { SnakeClient, createAndAuthenticate, parseGameState, getStrategy } from 'snake-rodeo-agents';

// Auth (creates a throwaway wallet, no real ETH needed)
const { token, privateKey, address } = await createAndAuthenticate('https://bot.trifle.life');

// Create client
const client = new SnakeClient('https://bot.trifle.life', token);

// Play
const rawState = await client.getGameState();
const parsed = parseGameState(rawState);
const strategy = getStrategy('expected-value');
const vote = strategy.computeVote(parsed, balance, agentState);

if (vote && !vote.skip) {
  await client.submitVote(vote.direction, vote.team, vote.amount);
}
```

**SnakeClient methods:**

| Method | Description |
|--------|-------------|
| `getGameState()` | Current game state (snake, fruits, scores, votes) |
| `getBalance()` | Current ball balance |
| `submitVote(dir, team, amount)` | Submit a direction vote |
| `getRodeos()` | List active rodeo games |
| `getUserStatus()` | User profile and stats |

### Wallet Authentication

SIWE (Sign In With Ethereum) auth with throwaway wallets:

```javascript
import { createAndAuthenticate, reauthenticate, checkToken } from 'snake-rodeo-agents';

// New wallet
const { token, privateKey, address } = await createAndAuthenticate(serverUrl);

// Reuse saved wallet
const { token } = await reauthenticate(serverUrl, savedPrivateKey);

// Check token validity
const user = await checkToken(serverUrl, token);
```

### Game State Utilities

The library provides hex grid utilities for strategy development:

```javascript
import { parseGameState, hexDistance, bfsDistance, floodFillSize, getValidDirections } from 'snake-rodeo-agents';

const parsed = parseGameState(rawState);

// BFS shortest path to a target (respects snake body, grid bounds)
const { distance, firstDir } = bfsDistance(head, target, rawState);

// Flood-fill reachable area (dead-end detection)
const reachable = floodFillSize(head, rawState);

// Hex distance between two positions
const dist = hexDistance(posA, posB);
```

### Tournament Simulator

Run offline tournaments to compare strategies at high speed:

```bash
# CLI
npm run simulate -- ev,aggressive --games 100 --seed 42
npm run simulate -- ev,aggressive,conservative --config small --verbose
npm run simulate -- ev,aggressive --json   # machine-readable output
```

```javascript
// Library
import { SimAgent, runTournament, RODEO_CYCLES, getStrategy } from 'snake-rodeo-agents';

const agents = [
  new SimAgent('a', 'ev-agent', getStrategy('ev')),
  new SimAgent('b', 'agg-agent', getStrategy('aggressive')),
];

const results = runTournament(agents, RODEO_CYCLES, 100, { seed: 42 });
console.log(results.agentStats);
// Same seed = identical results for reproducibility
```

**Simulator options:**

| Flag | Description |
|------|-------------|
| `-g, --games N` | Games per config (default: 100) |
| `-c, --config NAME` | `small\|medium\|large\|all` (default: all) |
| `-s, --seed N` | RNG seed for reproducibility |
| `-v, --verbose` | Print per-round details |
| `--json` | Machine-readable JSON output |

### Telegram Logging

Send game events to a Telegram group:

```javascript
import { TelegramLogger } from 'snake-rodeo-agents';

const tg = new TelegramLogger({
  botToken: process.env.TELEGRAM_BOT_TOKEN,
  chatId: process.env.TELEGRAM_CHAT_ID,
});

await tg.send('<b>Hello</b> from the snake agent!');
```

Configure in the daemon:

```bash
node snake.mjs telegram <chat_id>   # enable
node snake.mjs telegram off          # disable
```

## Configuration

Settings are stored in `~/.config/snake-rodeo/settings.json` (XDG-compliant, isolated from any host agent).

| Key | Default | Description |
|-----|---------|-------------|
| `strategy` | `expected-value` | Active strategy name |
| `server` | `live` | `live` or `staging` |
| `minBalance` | `5` | Minimum balance to place votes |
| `telegramChatId` | `null` | Telegram chat ID for logging |
| `telegramBotToken` | `null` | Telegram bot token (or set `TELEGRAM_BOT_TOKEN` env var) |

### File Locations

| Purpose | Path |
|---------|------|
| Settings | `~/.config/snake-rodeo/settings.json` |
| Auth token | `~/.config/snake-rodeo/auth.json` or `TRIFLE_AUTH_TOKEN` env var |
| Daemon state | `~/.local/state/snake-rodeo/daemon.state` |
| Daemon PID | `~/.local/state/snake-rodeo/daemon.pid` |
| Daemon log | `~/.local/share/snake-rodeo/daemon.log` |

### Authentication

The skill resolves your Trifle auth token in this order:

1. `TRIFLE_AUTH_TOKEN` environment variable (recommended for automation)
2. `~/.config/snake-rodeo/auth.json` — `{ "token": "your-jwt-here" }`

To set up auth, run `snake auth login` (uses `trifle-auth` skill) or set the env var directly.

## Architecture

```
snake-game/                             # OpenClaw skill wrapper
├── SKILL.md                            # This file
├── snake.mjs                           # CLI entry point
├── clawdhub.json                       # ClawHub registry metadata
├── package.json                        # Dependencies (snake-rodeo-agents)
├── lib/
│   ├── config.mjs                      # Settings/paths
│   ├── api.mjs                         # Token-based API (uses OpenClaw auth)
│   ├── process.mjs                     # Daemon PID management
│   └── telegram.mjs                    # Telegram bridge
├── daemon/
│   └── autoplay.mjs                    # Game loop: SSE → strategy → vote
└── node_modules/
    └── snake-rodeo-agents/             # Core library (TypeScript)
        └── dist/
            ├── lib/game-state.js       # Hex grid, BFS, flood-fill
            ├── lib/strategies/         # Strategy implementations
            ├── lib/client.js           # Standalone API client
            ├── lib/auth.js             # Wallet SIWE auth
            ├── lib/simulator.js        # Offline game simulator
            ├── lib/telegram.js         # Telegram logger
            └── bin/play.js             # Standalone CLI runner
```

## Upgrading

```bash
node snake.mjs stop
cd ~/.openclaw/workspace/skills/snake-rodeo
npm install github:trifle-labs/snake-rodeo-agents
node snake.mjs start --detach
```
