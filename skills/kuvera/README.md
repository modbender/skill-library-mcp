# Kuvera OpenClaw Skill

A **read-only** [OpenClaw](https://openclaw.org) skill for querying [Kuvera](https://kuvera.in) — an Indian investment platform.

## Features

- 📊 **Market Data** — Gold prices, USD/INR rate, NIFTY 50 fund NAVs
- 🏦 **Fund Lookup** — Search mutual fund schemes, browse categories
- 👤 **Portfolio** — View user profile & investment summary (requires login)
- 🔒 **Read-Only Safety** — All write APIs are blocked at the code level

## Installation

1. Copy this folder to `~/.openclaw/skills/kuvera/`
2. Restart the OpenClaw gateway — the skill is auto-discovered

## Commands

| Command | Description |
|---------|-------------|
| `kuvera-cli login <email> <password>` | Authenticate with Kuvera |
| `kuvera-cli user` | Show user profile |
| `kuvera-cli gold` | Current gold price |
| `kuvera-cli usd` | USD/INR exchange rate |
| `kuvera-cli market` | Market overview (top funds) |
| `kuvera-cli categories` | List fund categories |
| `kuvera-cli fund <code>` | Fund scheme details |
| `kuvera-cli top [category]` | Top performing funds |

## Safety

⛔ **This skill is strictly read-only.** All HTTP methods other than GET are blocked except for the login endpoint. This is enforced at the code level in `kuvera-cli.js` (line ~11, `ALLOWED_WRITE_PATHS` whitelist).

## License

MIT
