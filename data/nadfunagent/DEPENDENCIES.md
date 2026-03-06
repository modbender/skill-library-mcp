# Repository Dependencies (Clean Install)

## OpenClaw skills

This repo is designed to work with the following OpenClaw skills. Install them separately for a clean setup.

| Skill | Purpose | How to install |
|-------|---------|-----------------|
| **monad-development** | RPC, wallet, chain id | `clawhub install monad-development` |
| **nadfun-trading** | Buy/sell scripts (or copy this repo's `trading/` folder) | `clawhub install nadfun-trading` **or** `cp -r trading ~/.openclaw/workspace/skills/nadfun-trading/` and `npm install` there |
| **nadfun-indexer** | CurveCreate, CurveBuy events | `clawhub install nadfun-indexer` |
| **nadfun-agent-api** | Markets, holdings, market data | `clawhub install nadfun-agent-api` |

## What this repo contains

- **SKILL.md** — Agent instructions (nadfunagent). Copied to `~/.openclaw/workspace/skills/nadfunagent/`.
- **trading/** — Scripts (buy-token.js, sell-token.js, check-pnl.js, execute-bonding-v2.js, etc.). Use as the nadfun-trading skill (copy `trading/` to skills and run `npm install`) or run from any directory with `NADFUN_ENV_PATH` and `POSITIONS_REPORT_PATH` set.
- **scripts/** — Node.js helpers (check_positions.js, save_tokens.js, write_positions_report.js). Data path: `NADFUNAGENT_DATA_DIR`.

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `NADFUN_ENV_PATH` | `$HOME/nadfunagent/.env` | Path to `.env` (MONAD_PRIVATE_KEY, MONAD_RPC_URL, etc.) |
| `POSITIONS_REPORT_PATH` | `$HOME/nadfunagent/positions_report.json` | Positions report file (entry, P&L). |
| `NADFUNAGENT_DATA_DIR` | `$HOME/nadfunagent` | Data directory for `scripts/` (`.env`, `found_tokens.json`, `positions_report.json`). |

Scripts use `__dirname` or these env vars (no hardcoded skill paths). Run from repo: `cd trading && node execute-bonding-v2.js`.

## Post-install check

1. `cd trading && npm install`
2. Create `.env` (or set `NADFUN_ENV_PATH`)
3. Install skills: `clawhub install monad-development nadfun-trading nadfun-indexer nadfun-agent-api`
4. Install agent: copy SKILL.md to `~/.openclaw/workspace/skills/nadfunagent/` or `clawhub install nadfunagent`
5. Run cycle: `cd trading && node execute-bonding-v2.js`

No private keys or API keys are stored in the repo; all examples use placeholders. Contract addresses (LENS, routers, MMIND) are public on Monad.
