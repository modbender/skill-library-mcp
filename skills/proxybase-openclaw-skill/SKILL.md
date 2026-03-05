---
name: proxybase
description: Purchase and manage SOCKS5 residential proxies via ProxyBase API with cryptocurrency payments. Supports order creation, payment polling, proxy delivery, bandwidth monitoring, IP rotation, and top-ups.
user-invocable: true
metadata:
  {"openclaw": {"emoji": "🌐", "homepage": "https://proxybase.xyz", "requires": {"bins": ["curl", "jq"], "env": ["PROXYBASE_API_URL"]}, "primaryEnv": "PROXYBASE_API_KEY", "install": [{"id": "jq-brew", "kind": "brew", "formula": "jq", "bins": ["jq"], "label": "Install jq (brew)", "os": ["darwin", "linux"]}]}}
---

# ProxyBase — SOCKS5 Proxy Purchasing & Management

ProxyBase provides **US residential SOCKS5 proxies** for AI agents via a REST API
with cryptocurrency payments. Proxies never expire by time — only by bandwidth.

## Quick Reference

| Item | Value |
|---|---|
| API Base | `$PROXYBASE_API_URL` (default: `https://api.proxybase.xyz/v1`) |
| SOCKS5 Host | `api.proxybase.xyz:1080` |
| Auth Header | `X-API-Key: <key>` (key starts with `pk_`) |
| Payments | Crypto (USDT, USDCSOL, BTC, ETH, SOL, etc.) |
| Pricing | ~$10/GB US residential |

## Setup

This skill uses **zero-configuration** registration. The first time any
ProxyBase command is run, the agent automatically registers and stores
credentials in `{baseDir}/state/credentials.env`. No manual API key setup
or `openclaw.json` edits are required.

For manual or debugging use, you can also register explicitly:

```bash
bash {baseDir}/proxybase.sh register
```

## State Files

All persistent state lives in `{baseDir}/state/`:
- `credentials.env` — API key (`PROXYBASE_API_KEY=pk_...`)
- `orders.json` — Tracked orders with status and proxy info
- `.proxy-env` — Sourceable SOCKS5 proxy environment variables

## API Reference

### Register Agent (one-time)

```bash
curl -s -X POST "$PROXYBASE_API_URL/agents" | jq .
```

Returns `{ "agent_id": "...", "api_key": "pk_..." }`.
**Save the api_key** — it is required for every subsequent call.

### List Packages

```bash
curl -s "$PROXYBASE_API_URL/packages" -H "X-API-Key: $PROXYBASE_API_KEY" | jq .
```

Returns array of packages:
- `us_residential_1gb` — 1 GB, $10
- `us_residential_5gb` — 5 GB, $50
- `us_residential_10gb` — 10 GB, $100

Each has: `id`, `name`, `bandwidth_bytes`, `price_usd`, `proxy_type`, `country`.

### List Payment Currencies

```bash
curl -s "$PROXYBASE_API_URL/currencies" -H "X-API-Key: $PROXYBASE_API_KEY" | jq .
```

Returns `{ "currencies": ["usdcsol", "btc", "eth", "sol", ...] }`.
Default: `usdcsol`.

### Create Order

```bash
curl -s -X POST "$PROXYBASE_API_URL/orders" \
  -H "X-API-Key: $PROXYBASE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"package_id":"PACKAGE_ID","pay_currency":"usdcsol"}' | jq .
```

Parameters:
- `package_id` (required) — from list packages
- `pay_currency` (optional) — default `usdcsol`
- `callback_url` (optional) — webhook URL for status notifications

Returns: `order_id`, `payment_id`, `pay_address`, `pay_amount`, `pay_currency`,
`price_usd`, `status`, `expiration_estimate_date`.

### Check Order Status

```bash
curl -s "$PROXYBASE_API_URL/orders/ORDER_ID/status" \
  -H "X-API-Key: $PROXYBASE_API_KEY" | jq .
```

Status progression:
`payment_pending` → `confirming` → `paid` → `proxy_active` → `bandwidth_exhausted`

When `proxy_active`, the response includes:
```json
{
  "status": "proxy_active",
  "proxy": {
    "host": "api.proxybase.xyz",
    "port": 1080,
    "username": "pb_xxxx",
    "password": "xxxx"
  },
  "bandwidth_used": 52428800,
  "bandwidth_total": 1073741824
}
```

### Top Up Bandwidth

```bash
curl -s -X POST "$PROXYBASE_API_URL/orders/ORDER_ID/topup" \
  -H "X-API-Key: $PROXYBASE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"package_id":"PACKAGE_ID","pay_currency":"usdcsol"}' | jq .
```

Returns same shape as create order. Bandwidth is additive — same credentials,
same proxy, more bandwidth.

### Rotate Proxy IP

```bash
curl -s -X POST "$PROXYBASE_API_URL/orders/ORDER_ID/rotate" \
  -H "X-API-Key: $PROXYBASE_API_KEY" | jq .
```

Returns `{ "order_id": "...", "message": "...", "rotated": true }`.
The next connection gets a fresh IP. Existing connections are unaffected.

## Complete Purchase Flow

### Interactive (Chat with Human)

1. **Load credentials**: `source {baseDir}/state/credentials.env 2>/dev/null`
2. **Register if needed**: Run `bash {baseDir}/proxybase.sh register` if no key
3. **List packages**: Show user available packages with prices
4. **List currencies**: Show user payment options (default: usdcsol)
5. **Create order**: `POST /orders` with chosen package + currency
6. **Present payment**: Show user the `pay_address`, `pay_amount`, `pay_currency`, and `expiration_estimate_date`
7. **PAUSE — human sends crypto payment**
8. **Poll status**: Check every 30s until `proxy_active`, `expired`, or `failed`
9. **Deliver proxy**: Present SOCKS5 credentials to user

### Using the Helper Scripts

For a streamlined flow, use the provided scripts:

**Create order and track it:**
```bash
bash {baseDir}/proxybase.sh order us_residential_1gb usdcsol
```

**Poll an order until terminal state:**
```bash
bash {baseDir}/proxybase.sh poll ORDER_ID
```

**Check all tracked orders:**
```bash
bash {baseDir}/proxybase.sh status
```

**Clean up expired/failed orders:**
```bash
bash {baseDir}/proxybase.sh status --cleanup
```

**Top up bandwidth on an active order:**
```bash
bash {baseDir}/proxybase.sh topup ORDER_ID us_residential_1gb
```

**Rotate proxy credentials (new IP):**
```bash
bash {baseDir}/proxybase.sh rotate ORDER_ID
```

**Poll with extended timeout (for slow BTC confirmations):**
```bash
bash {baseDir}/proxybase.sh poll ORDER_ID --max-attempts 200
```

## Payment Pause — Polling Strategies

After order creation, the flow **must pause** for crypto payment.

### Strategy A: Cron Polling (Recommended for Unattended)

Set up a cron job to poll every 30 seconds:

```json
{
  "name": "proxybase-poll-ORDER_ID",
  "schedule": { "kind": "every", "everyMs": 30000 },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Check the status of ProxyBase order ORDER_ID by running: bash {baseDir}/proxybase.sh poll ORDER_ID --once --quiet\nThe script validates the ORDER_ID internally. If the output shows proxy_active, announce the SOCKS5 credentials to the user and delete this cron job. If expired or failed, announce the failure and delete this cron job. If still pending or confirming, reply with NO_REPLY."
  },
  "delivery": { "mode": "announce", "channel": "last" },
  "deleteAfterRun": false
}
```

### Strategy B: Manual Polling

Tell the user: "Let me know when you've sent the payment and I'll check the status."
When they say they paid:
```bash
bash {baseDir}/proxybase.sh poll ORDER_ID
```

### Strategy C: Webhook (If Gateway is Internet-Reachable)

Pass `callback_url` when creating the order:
```bash
curl -s -X POST "$PROXYBASE_API_URL/orders" \
  -H "X-API-Key: $PROXYBASE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"package_id":"PACKAGE_ID","pay_currency":"usdcsol","callback_url":"https://your-gateway/hooks/proxybase"}'
```

ProxyBase sends status updates to the webhook. Always combine with cron polling as backup.

## Using Your Proxy

### Option 1: Set ENV Variables (Auto-Routes All curl/wget/python)

```bash
source {baseDir}/state/.proxy-env
# Now all curl/wget commands go through the proxy automatically
curl https://lemontv.xyz/api/ip
```

Or manually:
```bash
export ALL_PROXY="socks5://USERNAME:PASSWORD@api.proxybase.xyz:1080"
export HTTPS_PROXY="socks5://USERNAME:PASSWORD@api.proxybase.xyz:1080"
export NO_PROXY="localhost,127.0.0.1,api.proxybase.xyz"
```

### Option 2: Per-Command Proxy

```bash
curl --proxy socks5://USERNAME:PASSWORD@api.proxybase.xyz:1080 https://lemontv.xyz/api/ip
```

### Option 3: Python with Proxy

```python
import requests
proxies = {"https": "socks5://USERNAME:PASSWORD@api.proxybase.xyz:1080"}
r = requests.get("https://lemontv.xyz/api/ip", proxies=proxies)
print(r.text)
```

### Verify Proxy is Working

```bash
# Direct IP
curl -s https://lemontv.xyz/api/ip | jq .ip

# Proxied IP (should be different)
curl -s --proxy socks5://USERNAME:PASSWORD@api.proxybase.xyz:1080 https://lemontv.xyz/api/ip | jq .ip
```

## Error Handling

| Error | Meaning | Action |
|---|---|---|
| `401 Unauthorized` | API key invalid or missing | Re-register: `bash {baseDir}/proxybase.sh register` |
| `404 Not Found` | Order ID invalid | Check order ID, remove from tracking |
| `429 Too Many Requests` | Rate limited | Wait 5-10s and retry, max 3 attempts |
| `500/502/503` | Server error | Retry up to 3 times with 5s delay |
| `partially_paid` | Underpayment | Tell user the remaining amount; keep polling |
| `expired` | Payment window closed (~24h) | Create new order |
| `failed` | Payment error | Create new order, log for support |
| `bandwidth_exhausted` | All bandwidth used | Top up: `POST /orders/{id}/topup` |

## Important Notes

- Proxies never expire by time — only by bandwidth consumption
- Multiple active proxies per agent are supported
- Bandwidth is tracked in real-time at byte level
- Top-ups are additive (extend existing bandwidth, same credentials)
- Webhook notifications at 80% and 95% bandwidth usage if `callback_url` provided
- Payment expires after ~24h (NOWPayments window)
- USDC on SOL is recommended: fast confirmations, low fees
- **Never expose `api_key` or proxy passwords in chat messages** — use env vars

## Security

### Input Validation

All inputs from API responses and command arguments are validated against strict
character allowlists before use:

- **Proxy credentials** (username, password, host, port): Only alphanumeric
  characters and a limited set of URL-safe symbols are allowed. Shell
  metacharacters (`$`, `` ` ``, `"`, `'`, `;`, `&`, `|`, `>`, `<`, `()`, `{}`,
  `\`) are **rejected**, preventing command injection if the API is compromised.
- **Order IDs, API keys, package IDs**: Only alphanumeric, hyphens, and
  underscores.
- **Proxy env files** (`.proxy-env`): Written with single-quoted values to
  prevent shell expansion when sourced.

### Argument Safety for AI Agent Execution

When the AI agent executes ProxyBase commands, all arguments (order IDs,
package IDs) **must** come from previously validated ProxyBase API responses
or the local `orders.json` state file — never from raw user chat input without
validation. The scripts enforce this by validating all arguments against strict
patterns (e.g., `[a-zA-Z0-9_-]+` for order IDs).

### inject-gateway Safety

The `inject-gateway` command modifies the OpenClaw gateway's systemd service
file. It includes multiple safety guards:

1. **Proxy URL validation**: The URL must match `socks5://user:pass@host:port`
   with only safe characters
2. **Service file verification**: The file must contain `[Service]` and
   reference `openclaw`/`OpenClaw` — arbitrary service files are rejected
3. **Automatic backup**: Creates a `.bak` copy before any modification
4. **Dry-run mode**: Use `--dry-run` to preview changes without applying them:
   ```bash
   bash {baseDir}/proxybase.sh inject-gateway ORDER_ID --dry-run
   ```
5. **Post-write validation**: Verifies the rewritten file contains the
   expected environment lines; restores from backup on failure
