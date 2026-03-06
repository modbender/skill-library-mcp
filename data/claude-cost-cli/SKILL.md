---
name: claude-cost-cli
description: Query Claude API usage and cost reports from the command line. Secure macOS Keychain storage for Admin API key. Table/JSON output.
metadata: {"clawdbot":{"emoji":"📊","os":["macos"],"requires":{"bins":["claude-cost","node"]},"install":[{"id":"npm","kind":"shell","command":"npm install -g claude-cost-cli","bins":["claude-cost"],"label":"Install claude-cost-cli via npm"}],"source":"https://github.com/cyberash-dev/claude-cost-cli"}}
---

# claude-cost-cli

A CLI for querying Anthropic Admin API usage and cost data. Requires an Admin API key (`sk-ant-admin...`) from Claude Console → Settings → Admin Keys. Credentials are stored in macOS Keychain.

## Installation

Requires Node.js >= 18 and macOS. The package is fully open source under the MIT license: https://github.com/cyberash-dev/claude-cost-cli

```bash
npm install -g claude-cost-cli
```

The npm package is published with provenance attestation, linking each release to its source commit via GitHub Actions. You can verify the published contents before installing:
```bash
npm pack claude-cost-cli --dry-run
```

Install from source (if you prefer to audit the code before running):
```bash
git clone https://github.com/cyberash-dev/claude-cost-cli.git
cd claude-cost-cli
npm install && npm run build && npm link
```

After installation the `claude-cost` command is available globally.

## Quick Start

```bash
claude-cost config set-key     # Interactive prompt: enter Admin API key (masked)
claude-cost usage              # Token usage for the last 7 days
claude-cost cost               # Cost breakdown for the last 7 days
claude-cost cost --sum         # Total spend for the last 7 days
```

## API Key Management

Store API key (interactive masked prompt, validates `sk-ant-admin` prefix):
```bash
claude-cost config set-key
```

Show stored key (masked):
```bash
claude-cost config show
```

Remove key from Keychain:
```bash
claude-cost config remove-key
```

## Usage Reports

```bash
claude-cost usage                                    # Last 7 days, daily, grouped by model
claude-cost usage --period 30d                       # Last 30 days
claude-cost usage --from 2026-01-01 --to 2026-01-31 # Custom date range
claude-cost usage --model claude-sonnet-4            # Filter by model
claude-cost usage --api-keys apikey_01Rj,apikey_02Xz # Filter by API key IDs
claude-cost usage --group-by model,api_key_id        # Group by multiple dimensions
claude-cost usage --bucket 1h                        # Hourly granularity (1d, 1h, 1m)
```

JSON output (for scripting):
```bash
claude-cost usage --json
claude-cost usage --period 30d --json
```

Output columns: Date, Model, Input Tokens, Cached Tokens, Output Tokens, Web Searches.

## Cost Reports

```bash
claude-cost cost                                           # Last 7 days, grouped by description
claude-cost cost --period 30d                              # Last 30 days
claude-cost cost --from 2026-01-01 --to 2026-01-31        # Custom date range
claude-cost cost --group-by workspace_id,description       # Group by workspace and description
claude-cost cost --sum                                     # Total cost only
```

JSON output (for scripting):
```bash
claude-cost cost --json
claude-cost cost --sum --json
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

The following properties are by design and can be verified in the source code:

- **Admin API key**: stored exclusively in macOS Keychain (service: `claude-cost-cli`). By design, never written to disk in plaintext. See [`src/infrastructure/keychain-credential-store.ts`](https://github.com/cyberash-dev/claude-cost-cli/blob/main/src/infrastructure/keychain-credential-store.ts) for the implementation.
- **No config files**: all settings are passed via CLI flags. Nothing is stored on disk besides the Keychain entry.
- **Network**: by design, the API key is only sent to `api.anthropic.com` over HTTPS. No other outbound connections are made. See [`src/infrastructure/anthropic-usage-repository.ts`](https://github.com/cyberash-dev/claude-cost-cli/blob/main/src/infrastructure/anthropic-usage-repository.ts) and [`src/infrastructure/anthropic-cost-repository.ts`](https://github.com/cyberash-dev/claude-cost-cli/blob/main/src/infrastructure/anthropic-cost-repository.ts).
- **Scope**: the Admin API key grants read-only access to organization usage and cost data. It cannot modify billing, create API keys, or access conversation content. This is a property of the [Anthropic Admin API](https://platform.claude.com/docs/en/build-with-claude/usage-cost-api), not just this CLI.
- **No caching**: query results are not cached or persisted to disk. The CLI writes output to stdout only.

## API Reference

This CLI wraps the Anthropic Admin API:
- Usage: `GET /v1/organizations/usage_report/messages`
- Cost: `GET /v1/organizations/cost_report`

Documentation: https://platform.claude.com/docs/en/build-with-claude/usage-cost-api
