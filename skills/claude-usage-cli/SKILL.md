---
name: claude-usage-cli
description: Query Claude API usage and cost reports from the command line. Secure macOS Keychain storage for Admin API key. Table/JSON output.
metadata: {"clawdbot":{"emoji":"📊","os":["macos"],"requires":{"bins":["claude-usage","node"]},"install":[{"id":"npm","kind":"shell","command":"npm install -g claude-usage-cli","bins":["claude-usage"],"label":"Install claude-usage-cli via npm"}],"source":"https://github.com/cyberash-dev/claude-usage-cli"}}
---

# claude-usage-cli

⚠️ **DEPRECATED** — This skill is no longer maintained. Please use [`claude-cost-cli`](https://clawhub.com/skills/claude-cost-cli) instead, which provides the same functionality with active support.

---

A CLI for querying Anthropic Admin API usage and cost data. Requires an Admin API key (`sk-ant-admin...`) from Claude Console → Settings → Admin Keys. Credentials are stored in macOS Keychain.

## Installation

Requires Node.js >= 18 and macOS. The package is open source: https://github.com/cyberash-dev/claude-usage-cli

```bash
npm install -g claude-usage-cli
```

Install from source (if you prefer to audit the code before running):
```bash
git clone https://github.com/cyberash-dev/claude-usage-cli.git
cd claude-usage-cli
npm install && npm run build && npm link
```

After installation the `claude-usage` command is available globally.

## Quick Start

```bash
claude-usage config set-key     # Interactive prompt: enter Admin API key (masked)
claude-usage usage              # Token usage for the last 7 days
claude-usage cost               # Cost breakdown for the last 7 days
claude-usage cost --sum         # Total spend for the last 7 days
```

## API Key Management

Store API key (interactive masked prompt, validates `sk-ant-admin` prefix):
```bash
claude-usage config set-key
```

Show stored key (masked):
```bash
claude-usage config show
```

Remove key from Keychain:
```bash
claude-usage config remove-key
```

## Usage Reports

```bash
claude-usage usage                                    # Last 7 days, daily, grouped by model
claude-usage usage --period 30d                       # Last 30 days
claude-usage usage --from 2026-01-01 --to 2026-01-31 # Custom date range
claude-usage usage --model claude-sonnet-4            # Filter by model
claude-usage usage --api-keys apikey_01Rj,apikey_02Xz # Filter by API key IDs
claude-usage usage --group-by model,api_key_id        # Group by multiple dimensions
claude-usage usage --bucket 1h                        # Hourly granularity (1d, 1h, 1m)
```

JSON output (for scripting):
```bash
claude-usage usage --json
claude-usage usage --period 30d --json
```

Output columns: Date, Model, Input Tokens, Cached Tokens, Output Tokens, Web Searches.

## Cost Reports

```bash
claude-usage cost                                           # Last 7 days, grouped by description
claude-usage cost --period 30d                              # Last 30 days
claude-usage cost --from 2026-01-01 --to 2026-01-31        # Custom date range
claude-usage cost --group-by workspace_id,description       # Group by workspace and description
claude-usage cost --sum                                     # Total cost only
```

JSON output (for scripting):
```bash
claude-usage cost --json
claude-usage cost --sum --json
```

Output columns: Date, Description, Model, Amount (USD), Token Type, Tier.

## Flag Reference

### `usage`
| Flag | Description | Default |
|------|-------------|---------|
| `--from <date>` | Start date (YYYY-MM-DD or ISO) | 7 days ago |
| `--to <date>` | End date (YYYY-MM-DD or ISO) | now |
| `--period <days>` | Shorthand period (7d, 30d, 90d) | 7d |
| `--model <models>` | Filter by model(s), comma-separated | all |
| `--api-keys <ids>` | Filter by API key ID(s), comma-separated | all |
| `--group-by <fields>` | Group by model, api_key_id, workspace_id, service_tier | model |
| `--bucket <width>` | Bucket width: 1d, 1h, 1m | 1d |
| `--json` | Output as JSON | false |

### `cost`
| Flag | Description | Default |
|------|-------------|---------|
| `--from <date>` | Start date (YYYY-MM-DD or ISO) | 7 days ago |
| `--to <date>` | End date (YYYY-MM-DD or ISO) | now |
| `--period <days>` | Shorthand period (7d, 30d, 90d) | 7d |
| `--group-by <fields>` | Group by workspace_id, description | description |
| `--sum` | Output total cost only | false |
| `--json` | Output as JSON | false |

## Security and Data Storage

- **Admin API key**: stored exclusively in macOS Keychain (service: `claude-usage-cli`). Never written to disk in plaintext.
- **No config files**: all settings are passed via CLI flags. Nothing is stored on disk besides the Keychain entry.
- **Network**: the API key is only sent to `api.anthropic.com` over HTTPS. No other outbound connections are made.
- **Scope**: the Admin API key grants read-only access to organization usage and cost data. It cannot modify billing, create API keys, or access conversation content.
- **No caching**: query results are not cached or persisted to disk.

## API Reference

This CLI wraps the Anthropic Admin API:
- Usage: `GET /v1/organizations/usage_report/messages`
- Cost: `GET /v1/organizations/cost_report`

Documentation: https://platform.claude.com/docs/en/build-with-claude/usage-cost-api
