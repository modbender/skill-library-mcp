---
name: OpenDex API Skill
description: You can interact with the OpenDex API to retrieve Solana token
  data, community-curated content, market sentiment, and more.
---

# OpenDex API Skill

You can interact with the OpenDex API to retrieve Solana token data, community-curated content, market sentiment, and more.

## Base URL

```
https://opendex-api-dy30.onrender.com
```

Frontend: `https://opendex.online`

## Authentication

### Public Endpoints (No API Key Required)

Token data, search, price, chart, sentiment, and watchlist endpoints are open and do not require authentication. They are rate-limited to **100 requests/minute** per IP.

### Authenticated Endpoints (API Key Required)

Community content endpoints under `/api/v1/` require an API key passed via the `X-API-Key` header.

**Rate limits:**
- Standard endpoints: 100 requests/minute
- Key registration: 10 requests/minute
- Search: 30 requests/minute

## Obtaining an API Key

Register a free API key by sending a POST request with a Solana wallet address:

```
POST /api/v1/keys/register
Content-Type: application/json

{
  "wallet": "<SOLANA_WALLET_ADDRESS>",
  "name": "OpenClaw"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "API key created successfully",
  "data": {
    "apiKey": "abc123...full64hexchars",
    "keyPrefix": "abc123",
    "owner": "<SOLANA_WALLET_ADDRESS>",
    "name": "OpenClaw",
    "createdAt": "2026-02-26T12:00:00Z"
  }
}
```

The full API key is only returned once at creation. Store it securely. One key per wallet.

Users can also obtain keys through the web UI at `https://opendex.online/api.html` by connecting their wallet.

### Using the API Key

Include the key in the `X-API-Key` header on all `/api/v1/` requests:

```
curl -H "X-API-Key: YOUR_API_KEY" \
  https://opendex-api-dy30.onrender.com/api/v1/community/<mint>
```

### Key Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/keys/info` | GET | Get your key's usage stats (requires `X-API-Key`) |
| `/api/v1/keys/status/:wallet` | GET | Check if a wallet has a key (public) |
| `/api/v1/keys/revoke` | DELETE | Revoke your key (requires `X-API-Key`) |

---

## API Endpoints

### Token Data (No Auth)

#### List Tokens
```
GET /api/tokens?filter=trending&limit=50&offset=0&order=desc
```
Filters: `trending`, `new`, `gainers`, `losers`, `most_viewed`

**Response:** Array of token objects with `mintAddress`, `name`, `symbol`, `price`, `priceChange24h`, `volume24h`, `marketCap`, `logoUri`, `views`, `sentimentScore`, `sentimentBullish`, `sentimentBearish`.

#### Search Tokens
```
GET /api/tokens/search?q=<query>
```
Query must be 2-100 characters. Rate limit: 30/minute. Returns matching tokens by name, symbol, or address.

#### Get Token Details
```
GET /api/tokens/:mint
```
Returns full token data including `price`, `priceChange24h`, `volume24h`, `liquidity`, `marketCap`, `fdv`, `supply`, `circulatingSupply`, `holders`, `decimals`, `logoUri`, and community `submissions` (banners and socials).

#### Get Token Price
```
GET /api/tokens/:mint/price
```
Returns current price data: `price`, `marketCap`, `fdv`, `volume24h`, `priceChange24h`, `liquidity`.

#### Get Price Chart
```
GET /api/tokens/:mint/chart?interval=1h&limit=100
```
Intervals: `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`, `1w`

#### Get OHLCV Data
```
GET /api/tokens/:mint/ohlcv?interval=1h&limit=100
```
Returns candlestick data (open, high, low, close, volume).

#### Get Liquidity Pools
```
GET /api/tokens/:mint/pools
```

#### Batch Get Tokens
```
POST /api/tokens/batch
Content-Type: application/json

{ "mints": ["mint1", "mint2", ...] }
```
Max 50 tokens per request.

#### Check Token Holder
```
GET /api/tokens/:mint/holder/:wallet
```
Returns `balance`, `holdsToken`, `percentageHeld`, `totalSupply`, `circulatingSupply`.

#### Record Page View
```
POST /api/tokens/:mint/view
```

#### Get View Count
```
GET /api/tokens/:mint/views
```

---

### Community Content (Requires API Key)

#### Get Community Content for a Token
```
GET /api/v1/community/:mint
```
Returns the top-voted banner and social links for a token.

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "So11111111111111111111111111111111111111112",
    "banner": {
      "url": "https://i.imgur.com/example.png",
      "score": 15,
      "submittedAt": "2026-02-26T12:00:00Z"
    },
    "links": {
      "twitter": { "url": "https://twitter.com/solana", "score": 12 },
      "telegram": null,
      "discord": { "url": "https://discord.gg/solana", "score": 8 },
      "tiktok": null,
      "website": { "url": "https://solana.com", "score": 10 }
    },
    "submissionCount": 4
  }
}
```

#### Get All Approved Submissions
```
GET /api/v1/community/:mint/all?type=banner
```
Optional `type` filter: `banner`, `twitter`, `telegram`, `discord`, `tiktok`, `website`

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "...",
    "count": 3,
    "submissions": [
      {
        "id": 123,
        "type": "banner",
        "url": "https://i.imgur.com/example.png",
        "score": 15,
        "upvotes": 20,
        "downvotes": 5,
        "submittedAt": "2026-02-26T12:00:00Z"
      }
    ]
  }
}
```

#### Batch Community Content
```
GET /api/v1/community/batch?mints=mint1,mint2,mint3
```
Max 20 tokens per request. Returns a map of mint address to community content (banner URL and link URLs as strings, not objects).

---

### Sentiment (No Auth)

#### Get Sentiment
```
GET /api/sentiment/:mint?wallet=<optional_wallet>
```
Returns bullish/bearish counts and the user's vote if `wallet` is provided.

**Response:**
```json
{
  "tally": { "bullish": 245, "bearish": 53, "score": 192 },
  "userVote": "bullish"
}
```

#### Cast Sentiment Vote
```
POST /api/sentiment/:mint
Content-Type: application/json

{ "wallet": "<WALLET>", "sentiment": "bullish" }
```
Sentiment values: `bullish` or `bearish`. No token holder requirement.

#### Bulk Sentiment
```
POST /api/sentiment/bulk
Content-Type: application/json

{ "mints": ["mint1", "mint2", ...] }
```
Max 100 mints. Returns sentiment tallies for each.

---

### Submissions (Signature Required)

#### Get Submissions for a Token
```
GET /api/submissions/token/:mint?status=approved&type=banner
```
Statuses: `pending`, `approved`, `rejected`, `all`

#### Create Submission
```
POST /api/submissions
Content-Type: application/json

{
  "tokenMint": "<MINT>",
  "type": "twitter",
  "contentUrl": "https://twitter.com/example",
  "walletAddress": "<WALLET>",
  "signature": [...],
  "timestamp": 1709012400000
}
```
Types: `banner`, `twitter`, `telegram`, `discord`, `tiktok`, `website`

Requires Ed25519 wallet signature. Submissions are community-moderated through voting.

---

### Voting (Signature + Holder Required)

#### Cast Vote
```
POST /api/votes
Content-Type: application/json

{
  "submissionId": 123,
  "voterWallet": "<WALLET>",
  "voteType": "up",
  "signature": [...],
  "timestamp": 1709012400000
}
```
Voter must hold the token (minimum 0.1% of supply). Vote weight scales by holdings (1x-3x).

#### Check Vote Status
```
GET /api/votes/check?submissionId=123&wallet=<WALLET>
```

#### Bulk Check Votes
```
POST /api/votes/bulk-check
Content-Type: application/json

{ "submissionIds": [1, 2, 3], "wallet": "<WALLET>" }
```
Max 50. Returns `{ [submissionId]: { hasVoted, voteType } }`.

---

### Watchlist (No Auth)

#### Get Watchlist
```
GET /api/watchlist/:wallet
```

#### Add to Watchlist
```
POST /api/watchlist
Content-Type: application/json

{ "wallet": "<WALLET>", "mint": "<MINT>" }
```
Max 100 tokens per wallet.

#### Remove from Watchlist
```
DELETE /api/watchlist
Content-Type: application/json

{ "wallet": "<WALLET>", "mint": "<MINT>" }
```

#### Check if Token in Watchlist
```
POST /api/watchlist/check
Content-Type: application/json

{ "wallet": "<WALLET>", "mint": "<MINT>" }
```

---

### Health & Status (No Auth)

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Basic health check |
| `GET /health/detailed` | Full dependency status (DB, RPC, cache, APIs) |
| `GET /health/ready` | Readiness probe |
| `GET /health/live` | Liveness probe |
| `GET /api/stats` | Cache and database statistics |
| `GET /api/announcements/active` | Active site announcements |

---

## Error Responses

All errors follow this format:

```json
{
  "error": "User-facing message",
  "code": "ERROR_CODE",
  "requestId": "trace-id",
  "timestamp": "2026-02-26T12:00:00Z"
}
```

| Code | Meaning |
|------|---------|
| 400 | Bad request (invalid parameters) |
| 401 | Missing or invalid API key |
| 403 | Access denied (revoked key, insufficient holder balance) |
| 404 | Resource not found |
| 409 | Conflict (duplicate submission, wallet already has key) |
| 429 | Rate limit exceeded (check `Retry-After` header) |
| 503 | Service temporarily unavailable |

## Solana Address Format

Valid Solana addresses are base58-encoded, 43-44 characters, using characters `1-9 A-H J-N P-Z a-k m-z` (no `0`, `I`, `O`, `l`).

## External Links

For any token with mint address `<MINT>`:
- OpenDex token page: `https://opendex.online/token.html?mint=<MINT>`
- Solscan: `https://solscan.io/token/<MINT>`
- Jupiter swap: `https://jup.ag/swap/SOL-<MINT>`
- Raydium swap: `https://raydium.io/swap/?outputMint=<MINT>`
