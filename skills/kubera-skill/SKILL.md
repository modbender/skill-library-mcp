---
name: kubera
description: Read and manage Kubera.com portfolio data (net worth, assets, debts, allocation, holdings). Use when a user asks about their finances, net worth, portfolio, investments, holdings, asset allocation, or wants to update asset values in Kubera. Works with any AI agent or CLI that can run Python scripts.
---

# Kubera

Query and update portfolio data via the [Kubera API](https://www.kubera.com).

## Setup

Set environment variables:
```bash
export KUBERA_API_KEY="your-api-key"
export KUBERA_SECRET="your-api-secret"
```

Generate keys at **Kubera Settings > API**. Read-only is recommended unless updates are needed.

## Usage

Run `scripts/kubera.py` with a subcommand:

```bash
# List portfolios
python3 scripts/kubera.py portfolios

# Net worth summary with allocation + top holdings
python3 scripts/kubera.py summary

# Full portfolio JSON (for detailed analysis)
python3 scripts/kubera.py json

# List assets, optionally filter by sheet or sort
python3 scripts/kubera.py assets --sheet Crypto --sort value

# Search assets by name/ticker/account
python3 scripts/kubera.py search "shopify"

# Update an asset (requires write permission + --confirm flag)
python3 scripts/kubera.py update <ITEM_ID> --value 5000 --confirm
```

Use `--json` on `summary`, `assets`, `search`, or `portfolios` for machine-readable output. Use `json` subcommand for the complete raw API response.

For multi-portfolio accounts, pass `--portfolio <ID>`. Single-portfolio accounts auto-select.

## Rate Limits

- 30 req/min, 100/day (Essentials) or 1,000/day (Black)
- Cache `json` output when running multiple queries in a session

## API Details

See [references/api.md](references/api.md) for authentication, endpoints, and object schemas.
