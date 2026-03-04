---
name: venice-admin
description: Venice AI account administration - check balance, view usage history, and manage API keys. Requires an Admin API key.
homepage: https://venice.ai
metadata:
  {
    "openclaw":
      {
        "emoji": "⚙️",
        "requires": { "bins": ["uv"], "env": ["VENICE_API_KEY"] },
        "primaryEnv": "VENICE_API_KEY",
        "install":
          [
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
          ],
      },
  }
---

# Venice Admin

Manage your Venice AI account - check balance, view usage history, and manage API keys.

**⚠️ Important:** These endpoints require an **Admin API key**, not a regular inference key. Create one at [venice.ai](https://venice.ai) → Settings → API Keys → Create Admin Key.

**API Base URL:** `https://api.venice.ai/api/v1`

## Setup

1. Create an **Admin API key** from [venice.ai](https://venice.ai) → Settings → API Keys
2. Set the environment variable:

```bash
export VENICE_API_KEY="your_admin_api_key_here"
```

---

## Check Balance

View your current DIEM and USD balances.

```bash
uv run {baseDir}/scripts/balance.py
```

**Output includes:**
- Whether you can consume (has balance)
- Current consumption currency (DIEM or USD)
- DIEM balance and epoch allocation
- USD balance

---

## View Usage History

View detailed usage history with filtering and pagination.

```bash
uv run {baseDir}/scripts/usage.py
```

**Options:**

- `--currency`: Filter by currency: `DIEM`, `USD`, `VCU` (default: `DIEM`)
- `--start-date`: Start date filter (ISO format: `2024-01-01`)
- `--end-date`: End date filter (ISO format: `2024-12-31`)
- `--limit`: Results per page (default: `50`, max: `200`)
- `--page`: Page number (default: `1`)
- `--sort`: Sort order: `asc` or `desc` (default: `desc`)
- `--format`: Output format: `json` or `csv` (default: `json`)
- `--output`: Save to file instead of stdout

**Examples:**

```bash
# Last 50 DIEM transactions
uv run {baseDir}/scripts/usage.py

# USD usage in January 2024
uv run {baseDir}/scripts/usage.py --currency USD --start-date 2024-01-01 --end-date 2024-01-31

# Export to CSV
uv run {baseDir}/scripts/usage.py --format csv --output usage.csv
```

---

## List API Keys

View all your API keys.

```bash
uv run {baseDir}/scripts/api_keys_list.py
```

**Output includes:**
- Key ID and name
- Key type (Admin, Inference, etc.)
- Creation date
- Last used date
- Rate limits

---

## Runtime Note

This skill uses `uv run` which automatically installs Python dependencies (httpx) via [PEP 723](https://peps.python.org/pep-0723/) inline script metadata. No manual Python package installation required - `uv` handles everything.

---

## Security Notes

- **Admin keys have elevated permissions** - protect them carefully
- Admin keys can view billing info and manage other keys
- Never commit admin keys to version control
- Consider using inference-only keys for production workloads

## API Reference

| Endpoint | Description | Auth Required |
|----------|-------------|---------------|
| `GET /billing/balance` | Check DIEM/USD balance | Admin key |
| `GET /billing/usage` | View usage history | Admin key |
| `GET /api_keys` | List all API keys | Admin key |

Full API docs: [docs.venice.ai](https://docs.venice.ai)

