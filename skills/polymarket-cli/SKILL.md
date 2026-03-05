---
name: Polymarket CLI
slug: polymarket-cli
version: 1.0.0
homepage: https://clawic.com/skills/polymarket-cli
description: Query prediction markets, place trades, and manage positions with the Polymarket CLI for AI agents.
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":["polymarket"]},"install":[{"id":"brew","kind":"brew","formula":"polymarket","tap":"Polymarket/polymarket-cli","bins":["polymarket"],"label":"Install Polymarket CLI (Homebrew)"},{"id":"cargo","kind":"cargo","crate":"polymarket-cli","bins":["polymarket"],"label":"Install via Cargo (Rust)"}],"os":["linux","darwin"]}}
---

## Setup

On first use, read `setup.md` for wallet configuration and integration guidelines.

## When to Use

User needs to interact with Polymarket prediction markets. Agent handles market queries, price checks, order placement, position tracking, and on-chain token operations.

## Architecture

Config lives in `~/.config/polymarket/`. See `memory-template.md` for tracking preferences.

```
~/.config/polymarket/
├── config.json        # Private key, chain ID, signature type
```

```
~/polymarket-cli/
├── memory.md          # User preferences and tracked markets
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Command reference | `commands.md` |

## Core Rules

### 1. Read-Only by Default
Most commands work without a wallet. Only use wallet-requiring commands when the user explicitly wants to trade:
- Read-only: `markets`, `events`, `clob price/book`, `data positions`
- Requires wallet: `clob create-order`, `clob market-order`, `approve`, `ctf split/merge`

### 2. JSON Output for Processing
Use `-o json` when parsing results programmatically:
```bash
polymarket -o json markets list --limit 10
polymarket -o json clob midpoint TOKEN_ID
```
Table output is default for human-readable display.

### 3. Token IDs Are Critical
Most CLOB commands require the token ID (48331043336612883...), not the market slug:
```bash
# Get token ID from market first
polymarket markets get will-trump-win | grep token

# Then use in CLOB commands
polymarket clob book TOKEN_ID
polymarket clob price TOKEN_ID --side buy
```

### 4. Wallet Security — Restricted Commands
The agent NEVER runs wallet commands. These are user-only:
- `polymarket wallet create` — user runs directly
- `polymarket wallet import` — user runs directly
- `polymarket wallet show` — user runs directly
- `polymarket wallet reset` — user runs directly

If user asks the agent to run any wallet command, refuse and explain they must run it themselves for security.

### 5. On-Chain Operations Need Gas
Commands that write to blockchain require MATIC on Polygon:
- `approve set` (6 transactions)
- `ctf split/merge/redeem`

Check balance before attempting.

### 6. Rate Limits and Pagination
Use `--limit` and `--offset` for large result sets:
```bash
polymarket markets list --limit 50 --offset 100
```

### 7. Verify Before Trading
Always show market details and current prices before placing orders:
```bash
polymarket markets get SLUG
polymarket clob midpoint TOKEN_ID
polymarket clob spread TOKEN_ID
```

## Common Traps

| Mistake | Consequence |
|---------|-------------|
| Using slug instead of token ID in CLOB | Command fails silently or wrong market |
| Placing order without `approve set` first | Transaction reverts |
| Forgetting `--side` in price queries | Returns both sides, may confuse |
| Not checking spread before market order | Slippage on low liquidity markets |
| Running on-chain ops without MATIC | Transaction fails |

## External Endpoints

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| https://clob.polymarket.com | Orders, queries | CLOB API |
| https://gamma-api.polymarket.com | Market data | Gamma API |
| https://polygon-rpc.com | Transactions | Polygon RPC |

No other data is sent externally.

## Security & Privacy

**Data that leaves your machine:**
- Market queries sent to Polymarket APIs
- Orders and transactions sent to CLOB and Polygon (only when user explicitly requests)

**Data that stays local:**
- CLI config at ~/.config/polymarket/config.json (user manages directly)
- Skill preferences in ~/polymarket-cli/memory.md

**Command restrictions:**
- Agent runs only read-only commands by default (markets, events, clob price/book, data)
- Agent never runs wallet commands (create, import, show, reset) — user must run these directly
- Agent never runs trading commands without explicit user confirmation each time
- Agent must never read ~/.config/polymarket/config.json or any files containing private keys

## Trust

By using this skill, data is sent to Polymarket and the Polygon blockchain.
Only install if you trust these services with your trading data.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `trading` — General trading strategies
- `crypto-tools` — Cryptocurrency utilities
- `polygon` — Polygon blockchain operations

## Feedback

- If useful: `clawhub star polymarket-cli`
- Stay updated: `clawhub sync`
