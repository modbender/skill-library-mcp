---
name: ordiscan
description: Inscribe content on Bitcoin via the Ordiscan API. Pays per-request with USDC on Base using the x402 protocol.
homepage: https://ordiscan.com/docs/api
metadata: {"clawdbot":{"emoji":"🟠","requires":{"anyBins":["awal","node"],"env":["X402_PRIVATE_KEY"],"config":["~/.evm-wallet.json"]},"primaryEnv":"X402_PRIVATE_KEY"}}
---

# Ordiscan API

Inscribe content and query Ordinals data via the Ordiscan API. Every request is paid with USDC on Base using the **x402 payment protocol** -- no API key needed.

## What this skill can do

- **Inscribe content on Bitcoin** -- text, images, HTML, SVG, and any other file type. The server builds and broadcasts the Bitcoin transactions for you. You only pay USDC on Base.
- **Query Ordinals data** -- look up inscriptions, addresses, runes, BRC-20 tokens, rare sats, and more.

## Setup

Two payment modes are supported. Use the signing script by default. Only use `awal` if it's already installed and authenticated.

### Default -- Signing script

Requires `node` and the `X402_PRIVATE_KEY` environment variable (an Ethereum private key with USDC on Base).

If `X402_PRIVATE_KEY` is not already set, check if `~/.evm-wallet.json` exists (created by the `evm-wallet` skill). If it does, read the private key from it:

```bash
X402_PRIVATE_KEY=$(node -e "console.log(JSON.parse(require('fs').readFileSync(require('os').homedir()+'/.evm-wallet.json','utf8')).privateKey)")
```

If neither the env var nor the wallet file is available, suggest using the `awal` wallet.

```bash
# Install dependencies (only once)
npm install --prefix <skill-dir>

# Verify connectivity
X402_PRIVATE_KEY=$X402_PRIVATE_KEY node <skill-dir>/scripts/x402-sign.mjs balance
```

### Alternative -- Coinbase Agentic Wallet (`awal`)

If `awal` is already installed and authenticated, it can be used instead. One command handles the full x402 negotiate-sign-pay flow.

```bash
# Check if awal is already available and authenticated
which awal && npx awal status
```

## Making requests with signing script

This is a 3-step flow: request -> sign -> retry. The example below inscribes text, but the same pattern works for any endpoint.

### Step 1: Send the request (get 402 + payment header)

```bash
CONTENT=$(echo -n "Hello from OpenClaw!" | base64)
BODY="{\"contentType\":\"text/plain\",\"base64_content\":\"$CONTENT\",\"recipientAddress\":\"bc1p...\"}"

HEADER=$(curl -s -o /tmp/x402_body.json -w '%header{Payment-Required}' \
  -X POST -H "Content-Type: application/json" \
  -d "$BODY" \
  "https://api.ordiscan.com/v1/inscribe")
```

Check the price before paying:
```bash
cat /tmp/x402_body.json
```

For GET requests (e.g. querying data), omit `-X POST` and `-d`.

### Step 2: Sign the payment

```bash
PAYMENT=$(X402_PRIVATE_KEY=$X402_PRIVATE_KEY node <skill-dir>/scripts/x402-sign.mjs sign "$HEADER")
```

The script reads the base64-encoded `Payment-Required` header, signs an ERC-3009 `TransferWithAuthorization`, and outputs the base64-encoded `Payment-Signature` header to stdout. Diagnostics go to stderr.

### Step 3: Retry with payment

```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Payment-Signature: $PAYMENT" \
  -d "$BODY" \
  "https://api.ordiscan.com/v1/inscribe"
```

## Making requests with awal

If `awal` is already available, it handles the full x402 flow in one command:

### Querying data

```bash
npx awal x402 pay "https://api.ordiscan.com/v1/inscription/0"
```

### Inscribing content

```bash
npx awal x402 pay "https://api.ordiscan.com/v1/inscribe" \
  --method POST \
  --data '{"contentType":"text/plain","base64_content":"SGVsbG8gd29ybGQ=","recipientAddress":"bc1p..."}' \
  --max-amount 5000000
```

The `--max-amount` flag caps the payment in USDC base units (6 decimals). `5000000` = $5.00 USDC.

## Preparing content for inscription

When the user asks to inscribe something, follow these steps:

### 1. Determine the content and MIME type

- **User provides text** (e.g. "inscribe 'Hello world'"): use `text/plain`
- **User provides a file path**: detect the MIME type from the extension:
  | Extension | Content type |
  |---|---|
  | `.txt` | `text/plain` |
  | `.html`, `.htm` | `text/html` |
  | `.svg` | `image/svg+xml` |
  | `.json` | `application/json` |
  | `.png` | `image/png` |
  | `.jpg`, `.jpeg` | `image/jpeg` |
  | `.gif` | `image/gif` |
  | `.webp` | `image/webp` |
  | `.mp3` | `audio/mpeg` |
  | `.mp4` | `video/mp4` |
  | `.pdf` | `application/pdf` |

### 2. Base64-encode the content

For text:
```bash
CONTENT=$(echo -n 'Hello world' | base64)
```

For a file:
```bash
CONTENT=$(base64 -w0 path/to/file)
```

`-w0` disables line wrapping (important -- the API expects a single unbroken base64 string). On macOS, `base64` doesn't wrap by default, so `-w0` can be omitted.

### 3. Get the recipient Bitcoin address

Ask the user for their Bitcoin address if not already provided. This is the address that will own the inscription.

### 4. Call the inscribe endpoint

See the worked examples below.

## Inscribe endpoint (deep dive)

`POST /v1/inscribe` creates a Bitcoin inscription. The server builds and broadcasts the commit + reveal transactions.

### Request body

| Field | Type | Required | Description |
|---|---|---|---|
| `contentType` | string | yes | MIME type (e.g. `text/plain`, `image/png`, `text/html`) |
| `base64_content` | string | yes | Base64-encoded content (max 400KB decoded) |
| `recipientAddress` | string | yes | Bitcoin address to receive the inscription |
| `feeRate` | number | no | Custom fee rate in sat/vB (defaults to medium) |

### 402 response (no payment)

When called without payment, the server returns 402 with dynamic pricing:

```json
{
  "error": { "message": "Payment required..." },
  "priceUsdc": 1.23,
  "totalSats": 4567,
  "feeRate": 12,
  "btcPriceUsd": 100000
}
```

The `Payment-Required` header contains the base64-encoded x402 v2 payment details.

Use the 3-step signing script flow above to handle this. If using `awal`, it handles the 402 flow automatically.

### Success response (200)

```json
{
  "data": {
    "commitTxid": "abc123...",
    "revealTxid": "def456...",
    "inscriptionId": "def456...i0"
  }
}
```

After a successful inscription, always show the user a link to their inscription: `https://ordiscan.com/inscription/{inscriptionId}`

### Worked example with signing script

```bash
CONTENT=$(echo -n "Hello Bitcoin!" | base64)
BODY="{\"contentType\":\"text/plain\",\"base64_content\":\"$CONTENT\",\"recipientAddress\":\"bc1p...\"}"

# Step 1: Get price and payment header
HEADER=$(curl -s -o /tmp/x402_body.json -w '%header{Payment-Required}' \
  -X POST -H "Content-Type: application/json" \
  -d "$BODY" \
  "https://api.ordiscan.com/v1/inscribe")

# Check the price
cat /tmp/x402_body.json

# Step 2: Sign
PAYMENT=$(X402_PRIVATE_KEY=$X402_PRIVATE_KEY node <skill-dir>/scripts/x402-sign.mjs sign "$HEADER")

# Step 3: Send with payment
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Payment-Signature: $PAYMENT" \
  -d "$BODY" \
  "https://api.ordiscan.com/v1/inscribe"
```

### Worked example with awal

```bash
CONTENT=$(echo -n "Hello Bitcoin!" | base64)

npx awal x402 pay "https://api.ordiscan.com/v1/inscribe" \
  --method POST \
  --data "{\"contentType\":\"text/plain\",\"base64_content\":\"$CONTENT\",\"recipientAddress\":\"bc1p...\"}" \
  --max-amount 5000000
```

### Inscribing images

```bash
CONTENT=$(base64 -w0 image.png)

npx awal x402 pay "https://api.ordiscan.com/v1/inscribe" \
  --method POST \
  --data "{\"contentType\":\"image/png\",\"base64_content\":\"$CONTENT\",\"recipientAddress\":\"bc1p...\"}" \
  --max-amount 10000000
```

### Inscribing HTML

```bash
CONTENT=$(echo -n '<html><body><h1>On-chain page</h1></body></html>' | base64)

npx awal x402 pay "https://api.ordiscan.com/v1/inscribe" \
  --method POST \
  --data "{\"contentType\":\"text/html\",\"base64_content\":\"$CONTENT\",\"recipientAddress\":\"bc1p...\"}" \
  --max-amount 5000000
```

## API endpoint reference

See the [Ordiscan API documentation](https://ordiscan.com/docs/api.md)

## Response format

**Success:**
```json
{ "data": { ... } }
```

**Error:**
```json
{ "error": { "message": "..." } }
```

## Error handling

| Status | Meaning | Action |
|---|---|---|
| 400 | Bad request (invalid params) | Fix the request body or parameters |
| 402 | Payment required | Sign and send payment via x402 |
| 429 | Rate limited | Wait and retry (max 10 requests/min for inscribe) |
| 503 | Service unavailable | Server issue, retry later |

## Tips

- **Payment mode**: Use the signing script with `X402_PRIVATE_KEY` by default. Only use `awal` if it's already installed and authenticated (`which awal` succeeds).
- **GET requests cost ~$0.01 USDC each.** Inscription requests vary based on content size and Bitcoin fee rates.
- **For inscriptions, always check the 402 response** to see the price before paying. The `priceUsdc` field tells you the exact cost.
- **Content limit is 400KB** (decoded). For images, keep them reasonable in size.
- **The inscribe endpoint returns `commitTxid` and `revealTxid`**. Track them on `https://mempool.space/tx/{txid}` or `https://ordiscan.com/inscription/{inscriptionId}`.

## External endpoints

| Endpoint | Method | Data sent |
|---|---|---|
| `https://api.ordiscan.com/v1/*` | GET | Query parameters only |
| `https://api.ordiscan.com/v1/inscribe` | POST | Content type, base64-encoded content, recipient Bitcoin address |

All requests are paid via x402 (USDC on Base). Payment is handled by `awal` or the signing script.

## Security & Privacy

- All data is sent to `api.ordiscan.com` over HTTPS.
- **GET requests** send only query parameters (inscription IDs, addresses, etc.).
- **Inscription requests** send the content you want to inscribe (base64-encoded) and a recipient Bitcoin address. This content is published on the Bitcoin blockchain and is permanently public.
- **Mode A (awal)**: No credentials are read beyond what `awal` manages for x402 payments. No data is stored locally.
- **Mode B (signing script)**: Reads `X402_PRIVATE_KEY` from the environment to sign USDC payments on Base. The private key is never sent over the network -- only the resulting EIP-3009 signature is transmitted. No data is stored locally.

By using this skill, your requests and inscription content are sent to Ordiscan. Only install if you trust [Ordiscan](https://ordiscan.com).
