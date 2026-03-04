# Epstein Emails API

Query 383,000+ court-released Epstein emails via a pay-per-request API. Structured JSON. USDC on Base via the x402 protocol.

## Required Credentials

This skill requires a funded EVM wallet to make payments. You **must** have:

| Variable | Format | Required | Description |
|---|---|---|---|
| `XCLAW02_PRIVATE_KEY` | `0x` + 64 hex chars | Yes | EVM wallet private key for signing payments |

Your wallet must hold USDC on Base (eip155:8453). Each API request costs **$0.001 USDC**.

**Security:** Never log, display, or echo your private key. Use environment variables only. Use a dedicated hot wallet funded with only what you need — do not use a wallet holding significant funds.

## When to Use This Skill

Use this skill when:

- The user asks about Epstein, Jeffrey Epstein, or Ghislaine Maxwell emails
- The user wants to search court-released documents or public records from the Epstein case
- The user needs structured email data (sender, recipient, date, subject, body) from the Epstein archive
- The user wants to cross-reference names, dates, or connections in the Epstein files

## How to Respond

| User Says/Asks | What to Do |
|---|---|
| "Search Epstein emails for X" | Use `/api/search` — costs 1 request ($0.001). Confirm with user before calling. |
| "Who emailed whom?" | Use `/api/emails` with `from`/`to` filters — costs 1 request ($0.001). Confirm first. |
| "Show emails from a date" | Use `/api/emails` with `date` filter — costs 1 request ($0.001). Confirm first. |
| "How many emails mention X?" | Use free `/api/preview` first (no cost). Report count. Only use paid search if user wants full results. |
| "Get all emails" | **Warn the user about cost first.** Full pagination could cost ~$0.384 (384 requests at 1000/page). Get explicit approval before starting. |
| "What's in the Epstein files?" | Explain the dataset — no API call needed. |

**Important:** Always confirm with the user before making paid requests. Never paginate through the full dataset without explicit user approval and a cost estimate.

## Spending Safeguards

- **Always estimate cost before multi-request operations.** Formula: `ceil(total_results / 1000) * $0.001`
- **Use the free `/api/preview` endpoint first** to check result counts before committing to paid requests.
- **Never auto-paginate** through all results without explicit user approval.
- **Single requests are fine** — one search or one filtered query costs $0.001. Just confirm with the user.
- **Set a spending limit** in your x402 client if supported (e.g., `max_amount` parameter).

## API Base URL

```
https://epsteinemails.xyz
```

## Endpoints

### GET /api/preview (FREE)

Free preview search. Use this first to check result counts before making paid requests. Rate limited (10 req/min), truncated bodies, max 10 results. **No payment required.**

**Query Parameters:**

| Param | Type | Description |
|---|---|---|
| `q` | string | Search query (min 2 characters) |

**Response:**

```json
{
  "query": "american",
  "total_matches": 15,
  "returned": 10,
  "preview": true,
  "results": [
    {
      "from": "Natalia Molotkova",
      "to": "",
      "date": "Wed 2/1/2017 8:06:26 PM",
      "subject": "Round Trip ticket Barcelona/Miami",
      "body": "Title: American Express Middle seats OK? Regards, Natal...",
      "source_file": "EFTA02205655.pdf"
    }
  ]
}
```

### GET /api/emails (PAID — $0.001)

List and filter emails with pagination. Requires x402 payment.

**Query Parameters:**

| Param | Type | Description |
|---|---|---|
| `from` | string | Filter by sender (case-insensitive substring) |
| `to` | string | Filter by recipient |
| `subject` | string | Filter by subject line |
| `date` | string | Filter by date (e.g. "2017", "Wed") |
| `source_file` | string | Filter by source PDF filename |
| `limit` | int | Max results per page (default/max: 1000) |
| `offset` | int | Pagination offset (default: 0) |

**Response:**

```json
{
  "total": 383579,
  "returned": 2,
  "offset": 0,
  "limit": 2,
  "has_more": true,
  "next_offset": 2,
  "emails": [
    {
      "from": "Natalia Molotkova",
      "to": "",
      "date": "Wed 2/1/2017 8:06:26 PM",
      "subject": "Round Trip ticket Barcelona/Miami",
      "body": "Title: American Express...",
      "cc": "",
      "bcc": "",
      "source_file": "EFTA02205655.pdf",
      "source_url": "https://www.justice.gov/epstein/files/DataSet%2011/EFTA02205655.pdf"
    }
  ]
}
```

### GET /api/search (PAID — $0.001)

Full-text search across all email fields. Requires x402 payment.

**Query Parameters:**

| Param | Type | Description |
|---|---|---|
| `q` | string | Search query (required, searches from/to/subject/body/date/cc/bcc) |
| `limit` | int | Max results per page (default/max: 1000) |
| `offset` | int | Pagination offset (default: 0) |

**Response:**

```json
{
  "query": "schedule",
  "total_matches": 42,
  "returned": 2,
  "offset": 0,
  "limit": 2,
  "has_more": true,
  "next_offset": 2,
  "results": [
    {
      "index": 5,
      "email": {
        "from": "Jeffrey Epstein",
        "to": "Ghislaine Maxwell",
        "date": "Thu 3/15/2017 10:30:00 AM",
        "subject": "Schedule",
        "body": "...",
        "cc": "",
        "bcc": "",
        "source_file": "EFTA02205700.pdf",
        "source_url": "https://www.justice.gov/epstein/files/DataSet%2011/EFTA02205700.pdf"
      }
    }
  ]
}
```

## Quick Start (Python)

```python
# pip install "x402[httpx,evm]" eth_account

import asyncio
import os
from eth_account import Account
from x402 import x402Client
from x402.http.clients import x402HttpxClient
from x402.mechanisms.evm import EthAccountSigner
from x402.mechanisms.evm.exact.register import register_exact_evm_client

# Load private key from environment variable — never hardcode
account = Account.from_key(os.environ["XCLAW02_PRIVATE_KEY"])
client = x402Client()
register_exact_evm_client(client, EthAccountSigner(account))

async def main():
    async with x402HttpxClient(client) as http:
        resp = await http.get(
            "https://epsteinemails.xyz/api/search?q=schedule&limit=10"
        )
        data = resp.json()
        print(f"Found {data['total_matches']} matches")
        for r in data["results"]:
            e = r["email"]
            print(f"  {e['from']} -> {e['to']}: {e['subject']}")

asyncio.run(main())
```

## Pagination

All paid endpoints support pagination. Max 1000 results per request.

**Before paginating, estimate cost and get user approval:**

```python
# Step 1: Use free preview to check total matches
preview = await http.get(
    "https://epsteinemails.xyz/api/preview?q=travel"
)
total = preview.json()["total_matches"]
est_cost = ((total + 999) // 1000) * 0.001
print(f"{total} matches — full retrieval will cost ~${est_cost:.3f} ({(total + 999) // 1000} requests)")
# Step 2: Only proceed with user approval

# Step 3: Paginate
all_results = []
offset = 0
while True:
    resp = await http.get(
        f"https://epsteinemails.xyz/api/search?q=travel&limit=1000&offset={offset}"
    )
    data = resp.json()
    all_results.extend(data["results"])
    if not data["has_more"]:
        break
    offset = data["next_offset"]
```

## Payment Details

| Field | Value |
|---|---|
| Protocol | x402 (HTTP 402 Payment Required) |
| Price | $0.001 USDC per request |
| Network | Base (eip155:8453) |
| Token | USDC (0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913) |
| Gas | None (facilitator-sponsored) |
| Facilitator | Coinbase CDP (https://api.cdp.coinbase.com/platform/v2/x402) |
| Recipient | 0xF9702D558eAEC22a655df33b1E3Ac996fAC2f1Ea |

The payment flow is automatic when using an x402-compatible client:

1. Client sends GET request
2. Server returns 402 with payment requirements in headers
3. Client signs a USDC payment and retries with payment header
4. Server verifies via Coinbase CDP facilitator, settles onchain, returns data

## Data Provenance

All emails are OCR'd from court-released PDF documents published by the U.S. Department of Justice at https://www.justice.gov/epstein. Each email record includes a `source_file` field and a `source_url` field linking directly to the original DOJ-hosted PDF.

## Error Handling

| Status | Meaning |
|---|---|
| 200 | Success |
| 400 | Bad request (missing `q` param on search) |
| 402 | Payment required (x402 client handles this automatically) |
| 429 | Rate limited (preview endpoint only, wait 60s) |

## Links

- API: https://epsteinemails.xyz
- x402 Protocol: https://x402.org
- x402 Python SDK: `pip install "x402[httpx,evm]"`
- Source documents: https://www.justice.gov/epstein
