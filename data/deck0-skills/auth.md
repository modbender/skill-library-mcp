# Authentication

All DECK-0 Agent API endpoints (except `GET /api/agents/v1/openapi`) require wallet-based signature authentication using EIP-191 signed messages.

## Required Headers

| Header | Type | Description |
|--------|------|-------------|
| `X-Agent-Wallet-Address` | string | Your Ethereum wallet address (lowercased) |
| `X-Agent-Chain-Id` | string | EVM chain ID used for authentication |
| `X-Agent-Timestamp` | string | Current Unix timestamp in **milliseconds** |
| `X-Agent-Nonce` | string | Unique string, 8-128 characters, single-use |
| `X-Agent-Signature` | string | EIP-191 signature of the canonical payload |

## Canonical Payload

The message to sign is constructed by joining the following lines with `\n`:

```
deck0-agent-auth-v1
method:{METHOD}
path:{PATH}
query:{SORTED_QUERY}
body_sha256:{SHA256_HEX}
timestamp:{TIMESTAMP}
nonce:{NONCE}
chain_id:{CHAIN_ID}
wallet:{WALLET}
```

### Field Details

| Field | Description |
|-------|-------------|
| `{METHOD}` | HTTP method in uppercase (`GET`, `POST`) |
| `{PATH}` | Full request path (e.g., `/api/agents/v1/shop/albums`) |
| `{SORTED_QUERY}` | Query parameters sorted alphabetically by key, then by value. Each key-value pair is URL-encoded and joined with `&`. Empty string if no query params. |
| `{SHA256_HEX}` | Hex-encoded SHA-256 hash of the request body. For `GET`/`HEAD` requests, this is the SHA-256 of an empty string: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `{TIMESTAMP}` | Same value as the `X-Agent-Timestamp` header |
| `{NONCE}` | Same value as the `X-Agent-Nonce` header |
| `{CHAIN_ID}` | Same value as the `X-Agent-Chain-Id` header |
| `{WALLET}` | Wallet address in lowercase |

### Query String Canonicalization

Query parameters are sorted lexicographically by key first, then by value if keys are equal. Each key and value is URL-encoded separately.

**Example**: `?pageSize=20&page=1&inStock=true` becomes `inStock=true&page=1&pageSize=20`

## Signer Selection

Use this signer priority:

1. Existing agent wallet signer provided by the runtime
2. Existing Base wallet signer provided by the runtime
3. Local `DECK0_PRIVATE_KEY` signer fallback

The canonical payload format and `X-Agent-*` headers stay exactly the same regardless of signer source.

When using fallback mode, optional env vars are:

- `DECK0_PRIVATE_KEY` (required for fallback signing)
- `DECK0_CHAIN_ID` (optional, defaults to `8453`) — used for API auth signature verification only; the chain for contract calls (buy/open) comes from the collection or price response and your RPC URL

## Signing Flow (Step by Step)

1. **Generate a timestamp** — current time in Unix milliseconds
2. **Generate a nonce** — random unique string (8-128 chars). Use a UUID or random hex string.
3. **Select `chainId`** — choose the exact chain for auth and set `X-Agent-Chain-Id`
4. **Canonicalize the query string** — sort params alphabetically
5. **Hash the request body** — SHA-256 hex of body bytes (or empty string for GET)
6. **Build the canonical payload** — join all fields with newlines (including `chain_id`)
7. **Sign the payload** — use EIP-191 `personal_sign` with the selected signer (runtime wallet first, `DECK0_PRIVATE_KEY` fallback)
8. **Attach headers** — set all required `X-Agent-*` headers

## Code Example (Fallback mode: local private key with curl and Foundry)

Use this shell script only when no runtime agent wallet signer or Base wallet signer is available.

```bash
#!/usr/bin/env bash
set -euo pipefail

BASE_URL="https://app.deck-0.com"
DECK0_CHAIN_ID="${DECK0_CHAIN_ID:-8453}"
WALLET=$(cast wallet address --private-key "$DECK0_PRIVATE_KEY" | tr '[:upper:]' '[:lower:]')

# --- Helper: canonicalize query string ---
# Sorts query params alphabetically by key, then by value.
canonicalize_query_string() {
  local raw="$1"
  raw="${raw#\?}"  # strip leading "?"
  if [ -z "$raw" ]; then echo ""; return; fi
  echo "$raw" | tr '&' '\n' | sort -t'=' -k1,1 -k2,2 | paste -sd '&' -
}

# --- Helper: sign a request ---
# Usage: sign_request METHOD PATH [QUERY] [BODY]
sign_request() {
  local method="${1^^}"   # uppercase
  local path="$2"
  local query="${3:-}"
  local body="${4:-}"

  local timestamp
  timestamp="$(date +%s)000"
  local nonce
  nonce="$(openssl rand -hex 16)"

  # SHA-256 of body (empty string for GET/HEAD)
  local body_sha256
  body_sha256="$(printf "%s" "$body" | shasum -a 256 | cut -d' ' -f1)"

  # Build canonical payload
  local payload
  payload="deck0-agent-auth-v1
method:${method}
path:${path}
query:${query}
body_sha256:${body_sha256}
timestamp:${timestamp}
nonce:${nonce}
chain_id:${DECK0_CHAIN_ID}
wallet:${WALLET}"

  # Sign with EIP-191 (cast wallet sign uses personal_sign)
  local signature
  signature="$(cast wallet sign --private-key "$DECK0_PRIVATE_KEY" "$payload")"

  # Export for use in curl
  HEADER_WALLET="$WALLET"
  HEADER_CHAIN_ID="$DECK0_CHAIN_ID"
  HEADER_TIMESTAMP="$timestamp"
  HEADER_NONCE="$nonce"
  HEADER_SIGNATURE="$signature"
}

# --- Helper: authenticated GET request ---
make_authenticated_request() {
  local path="$1"
  local query="${2:-}"

  local canonical_query
  canonical_query="$(canonicalize_query_string "$query")"

  sign_request "GET" "$path" "$canonical_query"

  local url="${BASE_URL}${path}"
  if [ -n "$query" ]; then url="${url}?${query}"; fi

  curl -s "$url" \
    -H "X-Agent-Wallet-Address: $HEADER_WALLET" \
    -H "X-Agent-Chain-Id: $HEADER_CHAIN_ID" \
    -H "X-Agent-Timestamp: $HEADER_TIMESTAMP" \
    -H "X-Agent-Nonce: $HEADER_NONCE" \
    -H "X-Agent-Signature: $HEADER_SIGNATURE"
}

# --- Helper: authenticated GET with status code and body file ---
# Usage: HTTP_CODE=$(make_authenticated_request_capture PATH QUERY OUTFILE)
# Prints HTTP status code to stdout; response body is written to OUTFILE.
make_authenticated_request_capture() {
  local path="$1"
  local query="${2:-}"
  local outfile="$3"

  local canonical_query
  canonical_query="$(canonicalize_query_string "$query")"

  sign_request "GET" "$path" "$canonical_query"

  local url="${BASE_URL}${path}"
  if [ -n "$query" ]; then url="${url}?${query}"; fi

  curl -s -w "%{http_code}" -o "$outfile" "$url" \
    -H "X-Agent-Wallet-Address: $HEADER_WALLET" \
    -H "X-Agent-Chain-Id: $HEADER_CHAIN_ID" \
    -H "X-Agent-Timestamp: $HEADER_TIMESTAMP" \
    -H "X-Agent-Nonce: $HEADER_NONCE" \
    -H "X-Agent-Signature: $HEADER_SIGNATURE"
}

# --- Helper: authenticated POST request ---
make_authenticated_post() {
  local path="$1"
  local body="$2"
  local query="${3:-}"

  local canonical_query
  canonical_query="$(canonicalize_query_string "$query")"

  sign_request "POST" "$path" "$canonical_query" "$body"

  local url="${BASE_URL}${path}"
  if [ -n "$query" ]; then url="${url}?${query}"; fi

  curl -s "$url" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-Agent-Wallet-Address: $HEADER_WALLET" \
    -H "X-Agent-Chain-Id: $HEADER_CHAIN_ID" \
    -H "X-Agent-Timestamp: $HEADER_TIMESTAMP" \
    -H "X-Agent-Nonce: $HEADER_NONCE" \
    -H "X-Agent-Signature: $HEADER_SIGNATURE" \
    -d "$body"
}

# --- Usage ---
make_authenticated_request "/api/agents/v1/shop/albums" "page=1&pageSize=20&inStock=true" | jq .
```

## Security Details

### Timestamp Tolerance

The server accepts timestamps within **5 minutes** (300,000 ms) of the server's current time. Requests outside this window are rejected with `AGENT_AUTH_INVALID_TIMESTAMP`.

### Nonce Replay Protection

Each nonce is stored in Redis with a **5-minute TTL**, scoped per wallet address (`agent:auth:nonce:{wallet}:{nonce}`). Reusing a nonce within that window returns `AGENT_AUTH_REPLAY_DETECTED`.

Best practices:
- Use a cryptographically random value (e.g., `openssl rand -hex 16`)
- Never reuse nonces across requests
- Length must be 8-128 characters

### Signature Verification

The server uses `ethers.verifyMessage(payload, signature)` for EOA signatures and ERC-1271 validation for smart wallets, both bound to the exact `X-Agent-Chain-Id` value provided in the request. No cross-chain fallback is attempted.

## Authentication Error Codes

| Code | HTTP | Description |
|------|------|-------------|
| `AGENT_AUTH_MISSING_HEADER` | 401 | One or more required `X-Agent-*` headers are missing |
| `AGENT_AUTH_INVALID_CHAIN` | 401 | `X-Agent-Chain-Id` is missing, malformed, or unsupported |
| `AGENT_AUTH_INVALID_WALLET` | 401 | Wallet address is not a valid EVM address |
| `AGENT_AUTH_INVALID_TIMESTAMP` | 401 | Timestamp is not a number or outside the 5-minute window |
| `AGENT_AUTH_INVALID_NONCE` | 401 | Nonce length is not between 8-128 characters |
| `AGENT_AUTH_INVALID_SIGNATURE` | 401 | Signature is malformed or does not match the wallet |
| `AGENT_AUTH_REPLAY_DETECTED` | 401 | Nonce has already been used within the TTL window |

See [errors.md](./errors.md) for the full error reference.
