# Caravo Agent Skills

Agent Skills for [Caravo](https://caravo.ai) — non-MCP agent integration for OpenClaw, Claude Code, Cursor, Codex, and 40+ other agents.

## Install

### ClawHub (OpenClaw)

```bash
npx clawhub@latest install caravo
```

Or send a message to OpenClaw:

```
Read and install https://caravo.ai/skill.md
```

### Vercel Skills CLI

```bash
npx skills add Caravo-AI/Agent-Skills
```

### Manual (curl)

Download the skill file directly. The content at `caravo.ai/skill.md` is identical to this repo's `SKILL.md` — it's a proxy that always serves the latest version from GitHub.

```bash
curl -fsSL https://caravo.ai/skill.md \
  --create-dirs -o ~/.openclaw/skills/caravo/SKILL.md
```

## What's Inside

`SKILL.md` — A comprehensive agent skill that teaches AI agents how to use Caravo's marketplace via the `caravo` CLI. Supports both API key authentication and x402 USDC payments.

The skill covers:
- Tool search and discovery
- Tool execution with automatic payment
- Review and upvote system
- Tool request submission

## Requirements

- Node.js (for `npx` to auto-install the CLI)
- Either `CARAVO_API_KEY` env var or USDC on Base for x402 payments

## Security & Architecture

**All external service calls are proxied through the Caravo API.** The agent never contacts third-party providers (email gateways, SMS services, scraping engines, AI models, etc.) directly. `CARAVO_API_KEY` is the only credential needed — no provider-specific API keys, tokens, or secrets are required or accessed.

**Wallet & payments:** The CLI auto-generates a fresh, dedicated wallet at `~/.caravo/wallet.json` on first use (x402 mode only). It does **not** import, read, or access any existing crypto wallets, seed phrases, or private keys on your system. Users are never prompted for wallet secrets. The private key stays local and is used solely to sign USDC micropayments on Base.

**Local filesystem access:** The CLI only reads/writes files within `~/.caravo/` (specifically `wallet.json` and `config.json`). It does not access, scan, or modify any other files or directories.

**Open-source & auditable:**

| Component | Source | Package |
|-----------|--------|---------|
| CLI | [Caravo-CLI](https://github.com/Caravo-AI/Caravo-CLI) | [@caravo/cli](https://www.npmjs.com/package/@caravo/cli) |
| MCP Server | [Caravo-MCP](https://github.com/Caravo-AI/Caravo-MCP) | [@caravo/mcp](https://www.npmjs.com/package/@caravo/mcp) |
| Agent Skill | [Agent-Skills](https://github.com/Caravo-AI/Agent-Skills) | — |

## Ecosystem

- [caravo.ai](https://caravo.ai) — Official website and marketplace
- [Caravo-MCP](https://github.com/Caravo-AI/Caravo-MCP) — Official MCP server (`@caravo/mcp`)
- [Caravo-CLI](https://github.com/Caravo-AI/Caravo-CLI) — Command-line interface (`@caravo/cli`)

## License

MIT
