---
name: nadfunagent
description: Autonomous trading agent for Nad.fun that scans markets, analyzes tokens, executes trades, and distributes profits to MMIND token holders. Uses nadfun-trading, nadfun-indexer, and nadfun-agent-api skills.
user-invocable: true
argument-hint: [action] [options]
---

**CRITICAL COMMUNICATION RULES:**
1. **Language**: Always respond in the SAME language as the user's question.  If in English, respond in English.
2. **Data Loading**: BEFORE executing any operations, FIRST request and load ALL required data from user or configuration files. Use OpenClaw's memory/session storage to save loaded data so you don't need to ask again.
3. **Telegram Integration**: 
   - Send detailed reports to Telegram after each trading cycle
   - If Telegram bot connection is not established, request user to start conversation with bot first
   - Include position status, P&L, new opportunities found, trades executed
4. **Initial Setup**: When first invoked, ask user for:
   - MMIND_TOKEN_ADDRESS (or load from .env)
   - MONAD_PRIVATE_KEY (or load from .env)
   - MONAD_RPC_URL (or load from .env)
   - MONAD_NETWORK (or load from .env)
   - Telegram user ID for notifications
   Save all this data in OpenClaw memory for future use.
5. **Missing variables**: If `.env` is missing or any required variable (MONAD_PRIVATE_KEY, MONAD_RPC_URL, MMIND_TOKEN_ADDRESS, MONAD_NETWORK) is not set, **ask the user to provide it** before running trading or scripts. Do not proceed with buy/sell or execute-bonding-v2 until config is complete.

# Nad.fun Autonomous Trading Agent

Autonomous trading agent that scans Nad.fun markets, analyzes tokens using momentum strategies, executes trades, and distributes profits to MMIND token holders.

## Prerequisites

- `monad-development` skill installed (for wallet and RPC setup)
- `nadfun-trading` skill installed (for buy/sell operations), or use the `trading/` folder from this repo
- `nadfun-indexer` skill installed (for querying events)
- `nadfun-agent-api` skill installed (for market data)
- Network configured (mainnet only for this skill)
- MMIND token address configured

**Paths (clean install):** Config is read from `NADFUN_ENV_PATH` if set, else `$HOME/nadfunagent/.env`. Positions report: `POSITIONS_REPORT_PATH` or `$HOME/nadfunagent/positions_report.json`. Scripts from `nadfun-trading` may be at `~/.openclaw/workspace/skills/nadfun-trading` or at `<this-repo>/trading`. See `DEPENDENCIES.md`.

## Configuration

**CRITICAL**: Load environment variables from `.env` file (default path: `$HOME/nadfunagent/.env`; override with `NADFUN_ENV_PATH`):

- `MMIND_TOKEN_ADDRESS`: Address of MMIND token for profit distribution (required)
- `MONAD_PRIVATE_KEY`: Private key for trading wallet (required)
- `MONAD_RPC_URL`: RPC endpoint URL (required)
- `MONAD_NETWORK`: Network type - "mainnet" or "testnet" (required)
- `MAX_POSITION_SIZE`: Maximum position size in MON (default: 0.1)
- `PROFIT_TARGET_PERCENT`: Take-profit threshold (default: 20%)
- `STOP_LOSS_PERCENT`: Stop-loss threshold (default: 10%)
- `PNL_DISTRIBUTION_PERCENT`: % of profit to distribute (default: 30%)

**Before starting trading cycle:**
1. Read `.env` file (path: `NADFUN_ENV_PATH` or `$HOME/nadfunagent/.env`). If the file is missing or any required variable is empty, **ask the user** to provide MMIND_TOKEN_ADDRESS, MONAD_PRIVATE_KEY, MONAD_RPC_URL, MONAD_NETWORK — do not run trading until config is complete.
2. Load `MMIND_TOKEN_ADDRESS` - use this for profit distribution
3. Load `MONAD_PRIVATE_KEY` - use this for wallet operations
4. Load `MONAD_RPC_URL` - use this for blockchain queries
5. Load `MONAD_NETWORK` - determines API endpoints (mainnet: api.nadapp.net, testnet: dev-api.nad.fun)

## Workflow

**EXECUTION SUMMARY - READ THIS FIRST:**
1. **Load config** from `$HOME/nadfunagent/.env` (MMIND_TOKEN_ADDRESS, MONAD_PRIVATE_KEY, MONAD_RPC_URL, MONAD_NETWORK)
2. **Execute ONLY 3 methods** (from HAR file analysis): Method 5 (New Events API), Method 6 (Market Cap API), Method 7 (Creation Time API)
3. **Combine results** - merge all token addresses from 3 methods, count frequency (how many methods found each token, max 3)
4. **Prioritize** - sort tokens by frequency (tokens found in 2-3 methods = higher priority)
5. **Save tokens** - save ALL found tokens (up to top 50 for storage) to `$HOME/nadfunagent/found_tokens.json` for manual review
6. **Analyze** - get token info, market data, metrics via Agent API, calculate scores
7. **Filter** - keep only tokens with min liquidity 5 MON, min holders 5
8. **Trade** - execute trades if score >= 60
9. **Distribute** - distribute profits to MMIND holders if profit >= 0.1 MON

### 1. Market Scanning (NEW + TRENDING)

**CRITICAL INSTRUCTIONS**: You MUST scan tokens using ALL 7 methods below. Execute each method step-by-step and collect ALL found token addresses.

**EXECUTION ORDER:**
1. Method 1: CurveCreate events (Indexer) - NEW tokens
2. Method 2: CurveBuy events (Indexer) - TRENDING by volume  
3. Method 3: Swap History (Agent API) - TRENDING by 24h volume
4. Method 4: Holdings (Agent API) - ACTIVE tokens from large traders
5. Method 5: New Events API - REAL-TIME BUY/CREATE events
6. Method 6: Market Cap API - TOP tokens by capitalization
7. Method 7: Creation Time API - NEWEST tokens

**STEP-BY-STEP EXECUTION:**

**CRITICAL LOGGING REQUIREMENT:**
After executing EACH method, you MUST log:
1. Print: "✅ Method X executed: Found N tokens"
2. Print: "Method X token addresses: <address1> <address2> ..."
3. If method failed: Print: "❌ Method X failed: <error reason>"
4. This helps track which methods are working and debug issues

**NOTE:** Only Methods 5, 6, and 7 are used (from HAR file analysis). Methods 1-4 are disabled.

**STATUS CHECK:** This method requires RPC access. You MUST execute it, don't skip it!

**What to do:**
1. Read `$HOME/nadfunagent/.env` to get `MONAD_RPC_URL` and `MONAD_NETWORK`
2. Get current block number using RPC: `eth_blockNumber`
3. Calculate: `safeLatest = currentBlock - 10` (safety margin)
4. Scan last 900 blocks in chunks of 100 blocks (RPC limit)
5. For each chunk, query CurveCreate events using `nadfun-indexer` skill

**How to execute:**
- Use `nadfun-indexer` skill with parameters: `event=CurveCreate`, `fromBlock=<start>`, `toBlock=<end>`
- Extract token addresses from events: `event.args.token` or `event.args[1]` (token is second argument)
- Collect all unique token addresses

**Example command structure:**
```
Use skill: nadfun-indexer
Parameters: event=CurveCreate, fromBlock=<calculated_start>, toBlock=<calculated_end>
Extract: token address from each event
```

**Expected result:** Array of token addresses (0x...) from newly created tokens

#### Method 2: Trending Tokens via Indexer (CurveBuy volume analysis)

**STATUS CHECK:** This method requires RPC access. You MUST execute it, don't skip it!

**What to do:**
1. Query CurveBuy events from last 900 blocks (same pagination as Method 1)
2. For each event, extract: token address and amountIn (MON spent)
3. Sum volume per token address
4. Sort tokens by total volume (descending)
5. Take top 20 tokens with highest volume

**How to execute:**
1. **Use same RPC setup as Method 1:** Get publicClient from monad-development skill
2. **Query CurveBuy events:** For each 100-block chunk:
   - Use `nadfun-indexer` skill: `event=CurveBuy`, `fromBlock=<start>`, `toBlock=<end>`
   - OR use viem: `publicClient.getContractEvents({ address: CURVE_ADDRESS, eventName: "CurveBuy", fromBlock, toBlock })`
3. **Extract data:** From each event:
   - `token = event.args.token` or `event.args[1]`
   - `amountIn = event.args.amountIn` or `event.args[2]` (amount in MON)
4. **Calculate volume:** Group by token address, sum all amountIn values
5. **Sort and filter:** Sort by total volume DESC, take top 20
6. **Log results:** Print "✅ Method 2: Found top 20 trending tokens by volume"

**Example:**
```
1. Use same RPC client from Method 1
2. Query CurveBuy events in chunks of 100 blocks
3. For each event: extract token and amountIn
4. Sum volume per token
5. Sort DESC, take top 20
6. Print: "✅ Method 2: Found 20 trending tokens"
```

**Expected result:** Top 20 token addresses sorted by trading volume

#### Method 3: Trending Tokens via Agent API (Swap History Analysis)

**What to do:**
1. Take top 10 tokens from Method 2 (highest volume)
2. For each token, query swap history via Agent API
3. Calculate 24h volume from swap history
4. Keep tokens with >= 1 MON volume in last 24 hours

**How to execute:**
- Determine API URL: if `MONAD_NETWORK=mainnet` then `https://api.nadapp.net`, else `https://dev-api.nad.fun`
- For each token, make GET request: `${API_URL}/agent/swap-history/${tokenAddress}?limit=50&trade_type=ALL`
- Parse response JSON
- For each swap in `response.swaps`:
  - Check `swap.swap_info.timestamp` - if within last 24 hours
  - Sum `swap.swap_info.native_amount` (in wei, convert to MON: divide by 1e18)
- Keep tokens with total 24h volume >= 1 MON
- Add 1-2 second delay between API calls to avoid rate limits

**Example:**
```
API_URL = MONAD_NETWORK === 'mainnet' ? 'https://api.nadapp.net' : 'https://dev-api.nad.fun'
For each token in top10:
  GET ${API_URL}/agent/swap-history/${token}?limit=50&trade_type=ALL
  Calculate 24h volume
  If volume >= 1 MON: add to trendingViaAPI
  Wait 1-2 seconds
```

**Expected result:** List of tokens with high 24h trading volume

#### Method 4: Get All Active Tokens (via Holdings of Large Accounts)

**STATUS CHECK:** Don't skip this method! Execute it with rate limit delays.

**What to do:**
1. From Method 2 CurveBuy events, find buyers who spent >1 MON
2. Extract their addresses (sender field)
3. Query holdings for first 5 large buyers (to avoid rate limits)
4. Extract all token addresses they hold (balance > 0)

**How to execute:**
1. **From Method 2 results:** Use CurveBuy events already queried
2. **Filter large buyers:**
   - Filter events where `amountIn > 1000000000000000000` (1 MON in wei = 1e18)
   - Extract `sender` address: `event.args.sender` or `event.args[0]`
   - Get unique addresses, take first 5
3. **Query holdings:** For each of 5 addresses:
   - GET: `${API_URL}/agent/holdings/${address}?limit=50`
   - Headers: `Accept: application/json`
   - Wait 2 seconds between requests
4. **Parse and extract:**
   - Parse JSON response
   - For each `holding` in `response.tokens`:
     - Check `holding.balance_info.balance` - if > 0
     - Extract `holding.token_info.address` or `holding.token_info.token_id`
5. **Log results:** Print "✅ Method 4: Found N active tokens from large trader holdings"

**Example:**
```
From Method 2 CurveBuy events:
  Filter: amountIn > 1e18 (1 MON)
  Extract: sender addresses
  Take first 5 unique addresses
For each address:
  GET ${API_URL}/agent/holdings/${address}?limit=50
  Extract tokens with balance > 0
  Wait 2 seconds
Print: "✅ Method 4: Found X tokens"
```

**Expected result:** Set of token addresses held by active large traders

#### Method 5: New Events API (Real-time BUY/SELL/CREATE events)

**STATUS:** ✅ This method is WORKING! Found 7 tokens in last scan.

**What to do:**
1. Make GET request to `/api/token/new-event` endpoint
2. Parse JSON response (array of events)
3. Extract token addresses from CREATE and BUY events
4. Add all unique token addresses to collection

**How to execute:**
1. **Determine base URL:** Read MONAD_NETWORK from .env:
   - If `MONAD_NETWORK=mainnet`: `baseUrl = 'https://nad.fun'`
   - Else: `baseUrl = 'https://dev.nad.fun'`
2. **Make GET request:**
   - URL: `${baseUrl}/api/token/new-event`
   - Headers: `Accept: application/json`, `User-Agent: OpenClaw-Agent/1.0`
3. **Parse response:** JSON array of event objects
4. **Extract tokens:**
   - For each event in response:
     - If `event.type === 'CREATE'`: extract `event.token_info.token_id`
     - If `event.type === 'BUY'`: extract `event.token_info.token_id`
     - If `event.type === 'SELL'`: optionally extract (indicates active trading)
5. **Log results:** Print "✅ Method 5: Found N tokens from new events API"

**Example:**
```
baseUrl = MONAD_NETWORK === 'mainnet' ? 'https://nad.fun' : 'https://dev.nad.fun'
GET ${baseUrl}/api/token/new-event
Parse JSON response
For each event:
  If event.type === 'CREATE' or 'BUY':
    Add event.token_info.token_id to tokensFromEvents
Print: "✅ Method 5: Found X tokens"
```

**Expected result:** Array of token addresses from recent CREATE and BUY events

**Response structure:**
- `type`: "BUY" | "SELL" | "CREATE"
- `amount`: Event amount (string)
- `token_info`: Complete token information (token_id, name, symbol, description, creator, etc.)
- `account_info`: Account that performed the action

#### Method 6: Market Cap API (Top tokens by market cap)

**STATUS CHECK:** Previous error: base64 decoding failed. Fix: Use proper decoding method.

**What to do:**
1. GET request to market cap endpoint
2. Response is base64-encoded JSON - decode it PROPERLY
3. Extract token addresses from response
4. Add all token addresses to collection

**How to execute:**
1. **API URL:** `${API_URL}/order/market_cap?page=1&limit=50&is_nsfw=false`
   - Where `API_URL = MONAD_NETWORK === 'mainnet' ? 'https://api.nadapp.net' : 'https://dev-api.nad.fun'`
2. **GET request:**
   - Headers: `Accept: application/json`, `User-Agent: OpenClaw-Agent/1.0`
   - Get response as text (not JSON)
3. **Decode base64 PROPERLY:**
   - Response body is base64 string
   - Use Python: `import base64; decoded = base64.b64decode(response_text).decode('utf-8')`
   - OR use command: `echo "$response_text" | base64 -d`
   - CRITICAL: Make sure response_text is the raw base64 string, not wrapped in JSON
4. **Parse decoded JSON:**
   - Parse decoded string as JSON
   - Structure: `{ "tokens": [...], "total_count": N }`
5. **Extract tokens WITH FULL DATA:**
   - For each token in `data.tokens`:
     - Extract `token.token_info.token_id` (token address)
     - **CRITICAL**: Store FULL token object with both `token_info` AND `market_info`
     - Structure: `{token_info: {...}, market_info: {...}, percent: ...}`
     - Add to topMarketCapTokens array (store full objects, not just addresses)
6. **Log results:** Print "✅ Method 6: Found N tokens with market data from market cap API"

**Example:**
```
API_URL = MONAD_NETWORK === 'mainnet' ? 'https://api.nadapp.net' : 'https://dev-api.nad.fun'
response = GET ${API_URL}/order/market_cap?page=1&limit=100&is_nsfw=false
decoded = base64.b64decode(response.text).decode('utf-8')
data = json.loads(decoded)

topMarketCapTokens = []  # Array of full token objects
For each token in data.tokens:
  # Store FULL token object with token_info + market_info
  topMarketCapTokens.append({
    'token_info': token.token_info,
    'market_info': token.market_info,
    'percent': token.percent,
    'address': token.token_info.token_id  # For easy access
  })
Print: "✅ Method 6: Found X tokens with market data"
```

**Expected result:** Array of full token objects (with token_info + market_info) sorted by market cap

**Response structure:**
- `tokens`: Array of token objects with `token_info` and `market_info`
- `total_count`: Total number of tokens
- Each token includes: `token_info` (token_id, name, symbol, creator, etc.) and `market_info` (market_type, price, volume, holder_count, etc.)

#### Method 7: Creation Time API (Newest tokens)

**CRITICAL**: Include BOTH bonding curve AND DEX tokens! Do NOT filter by is_graduated.

**What to do:**
1. GET request to creation time endpoint (newest first)
2. Decode base64 response PROPERLY (same as Method 6)
3. Extract token addresses - include ALL tokens (both bonding curve AND DEX)
4. Add to collection WITH FULL DATA

**How to execute:**
- API URL: `${API_URL}/order/creation_time?page=1&limit=50&is_nsfw=false&direction=DESC`
- GET request, decode base64 response (same as Method 6)
- Parse JSON: `data.tokens` array
- For each token:
  - Extract `token.token_info.token_id` (token address)
  - **CRITICAL**: Store FULL token object with both `token_info` AND `market_info`
  - **DO NOT filter by is_graduated** - include both bonding curve (is_graduated=false) AND DEX (is_graduated=true) tokens
  - Add to newestTokens array (store full objects, not just addresses)

**Example:**
```
API_URL = MONAD_NETWORK === 'mainnet' ? 'https://api.nadapp.net' : 'https://dev-api.nad.fun'
response = GET ${API_URL}/order/creation_time?page=1&limit=50&is_nsfw=false&direction=DESC
decoded = base64.b64decode(response.text).decode('utf-8')
data = json.loads(decoded)

newestTokens = []  # Array of full token objects
For each token in data.tokens:
  # Include ALL tokens - both bonding curve AND DEX
  # Store FULL token object with token_info + market_info
  newestTokens.append({
    'token_info': token.token_info,
    'market_info': token.market_info,
    'percent': token.percent,
    'address': token.token_info.token_id  # For easy access
  })
Print: "✅ Method 7: Found X tokens with market data (bonding curve + DEX)"
```

**Expected result:** Array of full token objects (with token_info + market_info) - newest tokens including both bonding curve AND DEX

**Response structure:**
- Same as Method 6: `tokens` array with `token_info` and `market_info`
- `direction=DESC` returns newest first
- **CRITICAL**: Include ALL tokens (both bonding curve AND DEX) - do NOT filter by is_graduated

#### Combine All Methods - CRITICAL STEP

**What to do:**
1. Collect ALL token addresses from Methods 5, 6, and 7 into one set (removes duplicates)
2. Count how many times each token appears across methods
3. Sort tokens by frequency (tokens found in more methods = higher priority/confidence)
4. Log summary of combination results

**How to execute:**
1. **Create collections:**
   - `allTokens = new Set()` or `allTokens = []` (use Set to avoid duplicates)
   - `tokenFrequency = new Map()` or `{}` to count occurrences

2. **Add tokens from each method:**
   - Method 5: Add all token addresses from tokensFromEvents (New Events API) - these are just addresses
   - Method 6: Add all tokens from topMarketCapTokens (Market Cap API) - these are FULL objects with token_info + market_info
   - Method 7: Add all tokens from newestTokens (Creation Time API) - these are FULL objects with token_info + market_info
   
   **IMPORTANT**: For Methods 6 & 7, store the FULL token objects (not just addresses) so you can use market_info directly for analysis!

3. **Count frequency and preserve full data:**
   - Use a Map/object: `allTokensMap = {}` where key = token address, value = token object with metadata
   - For Method 5 (addresses only): `allTokensMap[address] = {address, source: 'method5', data: null}`
   - For Method 6 (full objects): `allTokensMap[address] = {address, source: 'method6', data: fullTokenObject}`
   - For Method 7 (full objects): `allTokensMap[address] = {address, source: 'method7', data: fullTokenObject}`
   - Count frequency: `tokenFrequency[address] = (tokenFrequency[address] || 0) + 1`
   - **CRITICAL**: Preserve full token objects from Methods 6 & 7 - they contain market_info!

4. **Convert and sort:**
   - `candidateTokens = Object.values(allTokensMap)` or `Array.from(allTokensMap.values())`
   - Sort by frequency DESC, then by data availability:
     ```javascript
     candidateTokens.sort((a, b) => {
       const freqA = tokenFrequency[a.address] || 0
       const freqB = tokenFrequency[b.address] || 0
       if (freqB !== freqA) return freqB - freqA  // Higher frequency first
       // Prefer tokens with full data (market_info)
       const hasDataA = a.data && a.data.market_info ? 1 : 0
       const hasDataB = b.data && b.data.market_info ? 1 : 0
       return hasDataB - hasDataA
     })
     ```
   - `prioritizedTokens = candidateTokens`

5. **Log summary:**
   - Print: "📊 Combined results: Total unique tokens: N"
   - Print: "Tokens found in 2+ methods: X"
   - Print: "Tokens found in all 3 methods: Y"
   - Print: "Tokens with full market data: Z"
   - Print: "Top 10 prioritized tokens: <list with addresses>"

**Example:**
```
allTokensMap = {}  # Map: address -> {address, source, data}
tokenFrequency = {}

# Method 5: addresses only
for address in tokensFromEvents:
  allTokensMap[address] = {address: address, source: 'method5', data: null}
  tokenFrequency[address] = (tokenFrequency[address] || 0) + 1

# Method 6: full objects with market_info
for token in topMarketCapTokens:
  address = token.token_info.token_id
  allTokensMap[address] = {address: address, source: 'method6', data: token}
  tokenFrequency[address] = (tokenFrequency[address] || 0) + 1

# Method 7: full objects with market_info
for token in newestTokens:
  address = token.token_info.token_id
  allTokensMap[address] = {address: address, source: 'method7', data: token}
  tokenFrequency[address] = (tokenFrequency[address] || 0) + 1

# Sort by frequency and data availability
candidateTokens = Object.values(allTokensMap)
prioritizedTokens = candidateTokens.sort((a, b) => {
  freqDiff = tokenFrequency[b.address] - tokenFrequency[a.address]
  if (freqDiff !== 0) return freqDiff
  return (b.data && b.data.market_info ? 1 : 0) - (a.data && a.data.market_info ? 1 : 0)
})

Print: "📊 Combined: N unique tokens, X found in 2+ methods, Y found in all 3 methods, Z with full data"
```

**Expected result:** Prioritized array of token objects, each containing:
- `address`: token address
- `source`: which method(s) found it
- `data`: full token object with token_info + market_info (if available from Methods 6 or 7)
- `foundInMethods`: count from tokenFrequency

#### Save Found Tokens - CRITICAL STEP

**What to do:**
After combining all methods and getting prioritizedTokens, you MUST save them to file `$HOME/nadfunagent/found_tokens.json` for manual review.

**How to execute:**

1. **Prepare token list:**
   - Take top 50 tokens from prioritizedTokens
   - For each token, create object: `{address: token, foundInMethods: frequency_count}`
   - Create scan entry with timestamp, totalFound count, and tokens array

2. **Read existing file:**
   - File: `$HOME/nadfunagent/found_tokens.json`
   - If file doesn't exist or is empty: start with `[]`
   - If exists: parse JSON, get array

3. **Append and save:**
   - Add new scan entry to array
   - Keep only last 100 scans (remove oldest if > 100)
   - Write back as formatted JSON

**Example using Node.js script (RECOMMENDED):**
```bash
# From skill root or repo root: print token addresses (one per line) and pipe to script
# prioritizedTokens is the array of token addresses; take first 50 and pass to script
echo -e "0x...\n0x..." | node scripts/save_tokens.js
```
Or from the agent: write the list of addresses to a temp file or stdin and run `node scripts/save_tokens.js` (script reads from stdin). Data dir: `NADFUNAGENT_DATA_DIR` or `$HOME/nadfunagent`.

**Expected result:** File `$HOME/nadfunagent/found_tokens.json` updated with latest scan results

### 2. Token Analysis - CRITICAL: Use Data from Methods 6 & 7 Directly

**IMPORTANT**: Methods 6 (Market Cap API) and Method 7 (Creation Time API) already return COMPLETE token data with `market_info`. Use this data directly for analysis - DO NOT make additional API calls unless absolutely necessary!

**Data Structure from Methods 6 & 7:**
Each token in the response has this structure:
```json
{
  "token_info": {
    "token_id": "0x...",
    "name": "...",
    "symbol": "...",
    "is_graduated": true/false,
    "created_at": timestamp,
    ...
  },
  "market_info": {
    "market_type": "DEX" or "BONDING_CURVE",
    "reserve_native": "1625513352353765005672133",  // Liquidity in MON (wei format)
    "reserve_token": "51582894169959918089536846",
    "token_price": "0.000886889894056452",
    "price": "0.0415501242",
    "price_usd": "0.000886889894056452",
    "volume": "761848094037806233587694495",  // Total volume (wei format)
    "holder_count": 31580,  // Number of holders
    "ath_price": "0.0128807779",
    "ath_price_usd": "0.0128807779",
    ...
  },
  "percent": 8.797  // Market cap change percentage
}
```

**Analysis Steps:**

1. **Extract data from Methods 6 & 7:**
   - For each token in `data.tokens` array from Methods 6 & 7:
     - Extract `token_info.token_id` (token address)
     - Extract `market_info.reserve_native` (liquidity in wei, convert to MON: divide by 1e18)
     - Extract `market_info.holder_count` (number of holders)
     - Extract `market_info.volume` (total volume in wei, convert to MON: divide by 1e18)
     - Extract `market_info.market_type` ("DEX" or "BONDING_CURVE")
     - Extract `token_info.is_graduated` (true if graduated to DEX)
     - Extract `percent` (market cap change percentage)

2. **For Method 5 tokens (new-event API):**
   - This API returns only basic event data without full market_info
   - For tokens from Method 5, you can optionally query `/agent/market/:token_id` to get market_info
   - BUT prioritize tokens from Methods 6 & 7 first (they already have complete data)

3. **Calculate Liquidity Score (30% weight):**
   ```javascript
   liquidityMON = parseFloat(market_info.reserve_native) / 1e18
   
   // Score based on liquidity tiers
   if (liquidityMON >= 1000) liquidityScore = 100      // Excellent
   else if (liquidityMON >= 500) liquidityScore = 80     // Very good
   else if (liquidityMON >= 100) liquidityScore = 60    // Good
   else if (liquidityMON >= 50) liquidityScore = 40      // Fair
   else if (liquidityMON >= 10) liquidityScore = 20      // Low
   else liquidityScore = 0                              // Too low
   
   weightedLiquidity = liquidityScore * 0.30
   ```

4. **Calculate Momentum Score (25% weight):**
   ```javascript
   // Use percent (market cap change) as momentum indicator
   percentChange = parseFloat(token.percent) || 0
   
   // Score based on positive momentum
   if (percentChange >= 50) momentumScore = 100      // Strong growth
   else if (percentChange >= 20) momentumScore = 80
   else if (percentChange >= 10) momentumScore = 60
   else if (percentChange >= 5) momentumScore = 40
   else if (percentChange >= 0) momentumScore = 20
   else momentumScore = 0                           // Negative momentum
   
   weightedMomentum = momentumScore * 0.25
   ```

5. **Calculate Volume Score (20% weight):**
   ```javascript
   volumeMON = parseFloat(market_info.volume) / 1e18
   
   // Score based on volume tiers
   if (volumeMON >= 1000000) volumeScore = 100      // 1M+ MON volume
   else if (volumeMON >= 500000) volumeScore = 80
   else if (volumeMON >= 100000) volumeScore = 60
   else if (volumeMON >= 50000) volumeScore = 40
   else if (volumeMON >= 10000) volumeScore = 20
   else volumeScore = 0
   
   weightedVolume = volumeScore * 0.20
   ```

6. **Calculate Holder Score (15% weight):**
   ```javascript
   holderCount = parseInt(market_info.holder_count) || 0
   
   // Score based on holder count
   if (holderCount >= 10000) holderScore = 100      // Excellent distribution
   else if (holderCount >= 5000) holderScore = 80
   else if (holderCount >= 1000) holderScore = 60
   else if (holderCount >= 500) holderScore = 40
   else if (holderCount >= 100) holderScore = 20
   else holderScore = 0
   
   weightedHolders = holderScore * 0.15
   ```

7. **Calculate Progress Score (10% weight):**
   ```javascript
   isGraduated = token_info.is_graduated === true
   marketType = market_info.market_type
   
   // Score based on market stage
   if (isGraduated || marketType === "DEX") {
     progressScore = 100  // Fully graduated to DEX
   } else {
     // Still on bonding curve - use percent as progress indicator
     // Higher percent = closer to graduation
     percent = parseFloat(token.percent) || 0
     if (percent >= 80) progressScore = 80
     else if (percent >= 50) progressScore = 60
     else if (percent >= 30) progressScore = 40
     else progressScore = 20
   }
   
   weightedProgress = progressScore * 0.10
   ```

8. **Calculate Authority Score (Bonus - up to +10 points):**
   ```javascript
   // Check for social media presence and website (indicates legitimacy)
   hasTwitter = token_info.twitter && token_info.twitter.length > 0
   hasTelegram = token_info.telegram && token_info.telegram.length > 0
   hasWebsite = token_info.website && token_info.website.length > 0
   
   authorityScore = 0
   if (hasTwitter) authorityScore += 3
   if (hasTelegram) authorityScore += 3
   if (hasWebsite) authorityScore += 4
   
   // Maximum +10 bonus points for full social presence
   authorityBonus = Math.min(authorityScore, 10)
   ```

9. **Calculate Total Score:**
   ```javascript
   totalScore = weightedLiquidity + weightedMomentum + weightedVolume + weightedHolders + weightedProgress + authorityBonus
   
   // Round to 2 decimal places
   totalScore = Math.round(totalScore * 100) / 100
   ```

9. **Store Analysis Results:**
   For each token, store:
   ```javascript
   {
     address: token_info.token_id,
     name: token_info.name,
     symbol: token_info.symbol,
     liquidity: liquidityMON,
     holders: holderCount,
     volume: volumeMON,
     marketType: marketType,
     isGraduated: isGraduated,
     percentChange: percentChange,
     scores: {
       liquidity: liquidityScore,
       momentum: momentumScore,
       volume: volumeScore,
       holders: holderScore,
       progress: progressScore,
       total: totalScore
     },
     foundInMethods: tokenFrequency[token_info.token_id] || 1
   }
   ```

**CRITICAL INSTRUCTIONS:**
- Use data from Methods 6 & 7 DIRECTLY - they already contain all needed information
- DO NOT make additional API calls to `/agent/market/:token_id` for tokens from Methods 6 & 7
- Only for Method 5 tokens (if needed) make additional API calls
- Calculate scores immediately after combining methods, before filtering
- **Check authority (social media presence)**: Check `token_info.twitter`, `token_info.telegram`, `token_info.website` - add bonus points
- Log analysis results: Print "📊 Analysis: Token X has score Y (liquidity: A, momentum: B, volume: C, holders: D, progress: E, authority: +F)"

### 3. Filtering Criteria

Filter tokens based on:

- **Minimum liquidity**: 5 MON
- **Minimum holders**: 5
- **Bonding curve progress**: >= 10%
- **Score calculation**:
  - Liquidity: 30% weight
  - Momentum: 25% weight
  - Volume trend: 20% weight
  - Holder distribution: 15% weight
  - Bonding curve progress: 10% weight

### 4. Position Management - CRITICAL: Check Existing Positions FIRST

**BEFORE analyzing new tokens, you MUST check and manage existing positions!**

#### Step 1: Get Current Holdings

**What to do:**
1. Get trading wallet address from `MONAD_PRIVATE_KEY` in `.env` (derive address from private key)
2. Query current token holdings using Agent API: `/agent/holdings/${walletAddress}?limit=100`
3. Filter tokens where `balance > 0` (exclude zero balances)
4. For each token with balance > 0, get current market data

**How to execute:**
```javascript
// 1. Get wallet address from private key
const walletAddress = getAddressFromPrivateKey(MONAD_PRIVATE_KEY)

// 2. Query holdings
const holdingsResponse = await fetch(`${API_URL}/agent/holdings/${walletAddress}?limit=100`)
const holdings = await holdingsResponse.json()

// 3. Filter tokens with balance > 0
const activePositions = holdings.tokens.filter(token => {
  const balance = parseFloat(token.balance_info.balance) || 0
  return balance > 0
})

Print: "📊 Current positions: Found N tokens with balance > 0"
```

#### Step 2: Calculate P&L for Each Position

**CRITICAL**: Always use the `check-pnl.js` script from `nadfun-trading` skill for proper P&L calculation. This script:
- Reads entry price (`entryValueMON`) from `$HOME/nadfunagent/positions_report.json` (automatically recorded by `buy-token.js` when you purchase)
- Gets current value on-chain via nad.fun quote contract (or falls back to Agent API)
- Calculates P&L: `(currentValueMON - entryValueMON) / entryValueMON * 100`

**What to do:**
1. **Use the script**: Run `check-pnl.js` from nadfun-trading skill directory
2. The script reads entry prices from JSON (set by `buy-token.js` after purchases)
3. Gets current value on-chain via nad.fun quote contract
4. Calculates real P&L based on actual entry price

**How to execute:**
```bash
# Check P&L for all positions
cd $HOME/.openclaw/workspace/skills/nadfun-trading
node check-pnl.js

# Or with auto-sell (sells if P&L >= +5% or <= -10%)
node check-pnl.js --auto-sell
```

**Manual calculation (if script unavailable):**
```javascript
// Load entry prices from positions_report.json
const report = JSON.parse(await fs.readFile('$HOME/nadfunagent/positions_report.json', 'utf-8'))

for (const position of activePositions) {
  const tokenAddress = position.token_info.token_id || position.token_info.address
  const tokenBalance = parseFloat(position.balance_info.balance) || 0
  
  // Get entry price from JSON (recorded by buy-token.js)
  const prev = report.positions?.find(p => 
    (p.address || '').toLowerCase() === tokenAddress.toLowerCase()
  )
  const entryValueMON = prev?.entryValueMON || 0
  
  // Get current value on-chain via nad.fun quote contract
  const [router, amountOutWei] = await publicClient.readContract({
    address: '0x7e78A8DE94f21804F7a17F4E8BF9EC2c872187ea', // nad.fun quote contract
    abi: lensAbi,
    functionName: 'getAmountOut',
    args: [tokenAddress, parseEther(tokenBalance.toString()), false] // false = selling
  })
  const currentValueMON = Number(amountOutWei) / 1e18
  
  // Calculate P&L
  const pnlPercent = entryValueMON > 0
    ? ((currentValueMON - entryValueMON) / entryValueMON) * 100
    : 0
  
  positions.push({
    address: tokenAddress,
    balance: tokenBalance,
    entryValueMON: entryValueMON,
    currentValueMON: currentValueMON,
    pnlPercent: pnlPercent
  })
}

Print: "💰 Position P&L calculated for N positions (source: on-chain nad.fun quote + positions_report.json)"
```

**Entry Price Tracking:**
- Entry price is automatically recorded by `buy-token.js` after successful purchase
- Stored in `$HOME/nadfunagent/positions_report.json` as `entryValueMON`
- If entry price not found, `check-pnl.js` uses current value as fallback (P&L = 0%)

#### Step 3: Make Sell Decisions

**What to do:**
For each position, check sell conditions:

1. **Stop-Loss Check:**
   ```javascript
   if (pnlPercent <= -10) {  // STOP_LOSS_PERCENT = -10%
     // SELL ALL - stop loss triggered
     sellDecision = {
       action: 'SELL_ALL',
       reason: 'Stop-loss triggered',
       tokenAddress: position.address,
       amount: 'all'
     }
   }
   ```

2. **Take-Profit Check:**
   ```javascript
   if (pnlPercent >= 20) {  // PROFIT_TARGET_PERCENT = 20%
     // SELL HALF - take profit
     sellDecision = {
       action: 'SELL_HALF',
       reason: 'Take-profit triggered',
       tokenAddress: position.address,
       amount: position.balance / 2
     }
   }
   ```

3. **Trailing Stop (Optional):**
   ```javascript
   // If profit was > 15% but dropped to < 5%, sell to protect gains
   if (previousPnL > 15 && pnlPercent < 5) {
     sellDecision = {
       action: 'SELL_ALL',
       reason: 'Trailing stop - protecting gains',
       tokenAddress: position.address,
       amount: 'all'
     }
   }
   ```

**How to execute:**
```javascript
const sellDecisions = []

for (const position of positions) {
  // Stop-loss: sell all if down 10%+
  if (position.pnlPercent <= -10) {
    sellDecisions.push({
      tokenAddress: position.address,
      action: 'SELL_ALL',
      reason: `Stop-loss: ${position.pnlPercent.toFixed(2)}%`,
      amount: 'all'
    })
  }
  // Take-profit: sell half if up 20%+
  else if (position.pnlPercent >= 20) {
    sellDecisions.push({
      tokenAddress: position.address,
      action: 'SELL_HALF',
      reason: `Take-profit: ${position.pnlPercent.toFixed(2)}%`,
      amount: position.balance / 2
    })
  }
}

Print: "🔔 Sell decisions: N positions need action"
for (const decision of sellDecisions) {
  Print: `   ${decision.action}: ${decision.tokenAddress} - ${decision.reason}`
}
```

#### Step 4: Execute Sell Orders

**What to do:**
For each sell decision:
1. Use `nadfun-trading` skill with action `sell`
2. Parameters: token address, amount (from decision)
3. The skill handles: balance check, quote, approve, execution

**How to execute:**
```javascript
for (const decision of sellDecisions) {
  try {
    // Use nadfun-trading skill
    await useSkill('nadfun-trading', {
      action: 'sell',
      token: decision.tokenAddress,
      amount: decision.amount  // 'all' or specific amount
    })
    
    Print: `✅ Sold ${decision.amount} of ${decision.tokenAddress}: ${decision.reason}`
  } catch (error) {
    Print: `❌ Failed to sell ${decision.tokenAddress}: ${error.message}`
  }
}
```

### 5. Trading Execution - Buy New Tokens

**CRITICAL**: Only buy new tokens AFTER managing existing positions!

**Buy Decision Logic:**

1. **Prioritize tokens with authority (social media presence):**
   - Tokens with Twitter + Telegram + Website get priority
   - These are more legitimate and have better community support

2. **Consider both early-stage AND established tokens:**
   - Early-stage (5-50 MON liquidity): Higher risk, higher potential
   - Established (50k+ MON liquidity): Lower risk, steady growth
   - Both can be profitable if they meet score criteria

3. **Buy Criteria:**
   - Score >= 60 (or >= 55 if has social media)
   - Liquidity >= 5 MON
   - Holders >= 5
   - NOT already in portfolio (check existing positions first)

4. **Position Sizing:**
   - For tokens with authority (social media): up to 0.15 MON
   - For tokens without authority: up to 0.1 MON
   - Maximum total position per token: 0.15 MON

**CRITICAL**: Always use the `buy-token.js` script from `nadfun-trading` skill. This script:
- Automatically detects bonding curve vs DEX via nad.fun quote contract
- Handles DEX: wraps MON→WMON, approves, swaps
- **Automatically records entry price** in `$HOME/nadfunagent/positions_report.json` after successful purchase
- Works on bonding curve (MON) or DEX (MON) - all trading uses MON

**Buy tokens:**
```bash
cd $HOME/.openclaw/workspace/skills/nadfun-trading
NAD_PRIVATE_KEY=$MONAD_PRIVATE_KEY node buy-token.js <token-address> <MON-amount> [--slippage=300]
```

**Example:**
```bash
NAD_PRIVATE_KEY=0x... node buy-token.js 0x123...abc 0.15 --slippage=300
```

**After purchase:**
- Entry price (`entryValueMON`) is automatically recorded in `$HOME/nadfunagent/positions_report.json`
- This entry price is used by `check-pnl.js` for P&L calculation
- No manual tracking needed - everything is automated

**Risk management:**
- **CRITICAL**: Buy tokens on BOTH bonding curve AND DEX (don't filter by market_type)
- The `nadfun-trading` skill automatically detects market type and uses correct contract
- For all trades, use MON balance (no wrapping needed - all trading uses MON)
- Set slippage tolerance: 2-3% (increased for better execution, especially on DEX)
- Set deadline: 5 minutes from now
- Don't exceed MAX_POSITION_SIZE per token

### 6. Profit Distribution

**CRITICAL**: Use `MMIND_TOKEN_ADDRESS` from `$HOME/nadfunagent/.env` file.

When profit >= 0.1 MON:

```typescript
// Step 1: Load MMIND_TOKEN_ADDRESS from .env file
const envFile = await readFile('$HOME/nadfunagent/.env', 'utf-8')
const mmindMatch = envFile.match(/MMIND_TOKEN_ADDRESS=(0x[a-fA-F0-9]+)/)
if (!mmindMatch) {
  throw new Error('MMIND_TOKEN_ADDRESS not found in .env file')
}
const MMIND_TOKEN_ADDRESS = mmindMatch[1]

// Step 2: Get MMIND token holders via Indexer
// Query Transfer events to find all addresses that ever held MMIND
const latestBlock = await publicClient.getBlockNumber()
const safeLatest = latestBlock - 10n

// Query in chunks (RPC limit: ~100 blocks)
const transfers = []
for (let from = 0n; from < safeLatest; from += 10000n) {
  const to = from + 10000n > safeLatest ? safeLatest : from + 10000n
  try {
    const events = await useSkill('nadfun-indexer', {
      event: 'Transfer',
      token: MMIND_TOKEN_ADDRESS,
      fromBlock: from,
      toBlock: to
    })
    transfers.push(...events)
  } catch (err) {
    // Continue if chunk fails
  }
}

// Step 3: Collect unique addresses
const holderAddresses = new Set()
transfers.forEach(event => {
  if ('args' in event) {
    if (event.args.from && event.args.from !== '0x0000000000000000000000000000000000000000') {
      holderAddresses.add(event.args.from)
    }
    if (event.args.to && event.args.to !== '0x0000000000000000000000000000000000000000') {
      holderAddresses.add(event.args.to)
    }
  }
})

// Step 4: Get current balances for each holder
const distributions = []
for (const address of holderAddresses) {
  try {
    const balance = await publicClient.readContract({
      address: MMIND_TOKEN_ADDRESS,
      abi: erc20Abi,
      functionName: 'balanceOf',
      args: [address]
    })
    
    if (balance > 0n) {
      distributions.push({ address, balance })
    }
  } catch (err) {
    // Skip if balance check fails
  }
}

// Step 5: Get total supply
const totalSupply = await publicClient.readContract({
  address: MMIND_TOKEN_ADDRESS,
  abi: erc20Abi,
  functionName: 'totalSupply'
})

// Step 6: Calculate and distribute profit proportionally
const profitToDistribute = (profit * BigInt(PNL_DISTRIBUTION_PERCENT)) / 100n

for (const holder of distributions) {
  const share = (profitToDistribute * holder.balance) / totalSupply
  if (share >= parseEther('0.001')) { // Minimum 0.001 MON
    await transferMON(holder.address, share) // Transfer MON directly (all trading uses MON)
  }
}
```

## Autonomous Trading Loop

The agent runs continuously:

1. **Position Management FIRST** (CRITICAL - do this before scanning)
   - Get wallet address from `MONAD_PRIVATE_KEY`
   - Query current holdings: `/agent/holdings/${walletAddress}?limit=100`
   - Filter tokens with balance > 0
   - For each position: use `check-pnl.js` to get real P&L (reads entry price from `$HOME/nadfunagent/positions_report.json`, gets current value on-chain via nad.fun quote contract)
   - Execute sell orders: use `sell-token.js` or `check-pnl.js --auto-sell` for stop-loss (P&L <= -10%) or take-profit (P&L >= +5%)
   - Log: "📊 Positions: N checked, X sold; entry prices tracked in positions_report.json"

2. **Scan market** (after managing positions, every 10 minutes to avoid rate limits)
   - Method 5: Fetch new events API (`/api/token/new-event`) for real-time BUY/CREATE events
   - Method 6: Fetch top tokens by market cap (`api.nadapp.net/order/market_cap`, base64 decoded)
   - Method 7: Fetch newest tokens (`api.nadapp.net/order/creation_time`, base64 decoded)
   - Combine all methods and prioritize tokens found in multiple sources
   - Add 2-3 second delays between API calls to respect rate limits (CRITICAL to avoid HTTP 429)

2. **Analyze opportunities**
   - Use data DIRECTLY from Methods 6 & 7 (already contains complete market_info)
   - Calculate scores using market_info: liquidity (30%), momentum (25%), volume (20%), holders (15%), progress (10%)
   - Convert wei values to MON: reserve_native / 1e18, volume / 1e18
   - Filter by criteria (min liquidity 5 MON, min holders 5, min score 60)
   - Sort by score DESC, then by methods count, then by liquidity
   - Take top 20 candidates
   - Generate buy/sell signals

3. **Execute trades**
   - Buy on bonding curve (MON) or DEX (MON) - all trading uses MON
   - Monitor positions
   - Stop-loss and take-profit

4. **Distribute profits**
   - Calculate total profit
   - Get MMIND holders via Indexer (Transfer events)
   - Distribute proportionally (30% of profit) in MON

## Risk Management

- **Position sizing**: Based on confidence score (max 0.1 MON)
- **Stop-loss**: -10% (automatic sell)
- **Take-profit**: +20% (sell half position)
- **Slippage protection**: 1-2% tolerance
- **Minimum liquidity**: 5 MON required

## Usage Examples

**Start autonomous trading:**

```bash
# Via OpenClaw chat
"Start autonomous trading agent"

# Or via cron job (runs every minute). Paths: use NADFUN_ENV_PATH / NADFUNAGENT_DATA_DIR for .env and data; run scripts from nadfun-trading skill directory (clawhub install).
openclaw cron add \
  --name "Nad.fun Trading Agent" \
  --cron "* * * * *" \
  --session isolated \
  --message "Run autonomous trading cycle: 1) Load config from .env (path: NADFUN_ENV_PATH or NADFUNAGENT_DATA_DIR/.env; need MMIND_TOKEN_ADDRESS, MONAD_PRIVATE_KEY, MONAD_RPC_URL, MONAD_NETWORK). 2) From nadfun-trading skill directory run: node execute-bonding-v2.js (uses check-pnl.js for P&L from positions_report.json at POSITIONS_REPORT_PATH or NADFUNAGENT_DATA_DIR, auto-sells at +5% or -10%). 3) If there is positive PnL (profit >= 0.1 MON), distribute profits to MMIND token holders: use MMIND_TOKEN_ADDRESS from .env, get holders via indexer/Transfer events, distribute proportionally (e.g. 30%) in MON. Report output in English."
```

**Check agent status:**

```bash
# Via OpenClaw chat
"Show trading agent status and statistics"
```

**View found tokens:** (data dir: `NADFUNAGENT_DATA_DIR`, default `$HOME/nadfunagent`)

```bash
# View latest found tokens
cat "${NADFUNAGENT_DATA_DIR:-$HOME/nadfunagent}/found_tokens.json" | jq '.[-1]'

# View all tokens from last scan
cat "${NADFUNAGENT_DATA_DIR:-$HOME/nadfunagent}/found_tokens.json" | jq '.[-1].tokens[] | .address'

# View tokens found in multiple methods (higher confidence)
cat "${NADFUNAGENT_DATA_DIR:-$HOME/nadfunagent}/found_tokens.json" | jq '.[-1].tokens[] | select(.foundInMethods > 1) | .address'

# View summary of last 10 scans
cat "${NADFUNAGENT_DATA_DIR:-$HOME/nadfunagent}/found_tokens.json" | jq '.[-10:] | .[] | {timestamp, totalFound}'
```

**Manual trade:**

```bash
# Via OpenClaw chat
"Buy 0.1 MON worth of token 0x..."
"Sell all tokens for 0x..."
```

## Integration with OpenClaw

This skill integrates with:

- **Cron Jobs**: Schedule autonomous trading cycles
- **Skills**: Uses nadfun-trading, nadfun-indexer, nadfun-agent-api
- **Gateway**: Runs via OpenClaw Gateway
- **Channels**: Can send notifications via Telegram/WhatsApp/etc.

## Error Handling

- All errors are logged but don't stop the agent
- Failed trades are retried with exponential backoff
- API failures fall back to Indexer queries
- Network errors trigger fallback RPC providers

## Rate Limit Handling

**CRITICAL**: Handle rate limits gracefully to avoid HTTP 429 errors.

### API Rate Limits

**Nad.fun Agent API:**
- Without API Key: 10 requests/minute (IP-based)
- With API Key: 100 requests/minute (Key-based)
- **Solution**: Add delays between requests (min 2 seconds between calls)

**Nad.fun Public APIs (`nad.fun/api/*` and `api.nadapp.net/*`):**
- Rate limits are not publicly documented but appear to be IP-based
- **Solution**: Add 2-3 second delays between calls, especially for base64-decoded endpoints
- Handle HTTP 429 errors gracefully with exponential backoff

**Anthropic/Claude API (CRITICAL - This is the main source of HTTP 429):**
- Rate limits vary by tier (typically 50-200 requests per minute)
- **Problem**: Each agent execution makes multiple requests to Claude
- **Solution**: 
  - Cron job runs every 10 minutes (`*/10 * * * *`) to reduce frequency
  - Optimize agent logic to minimize token usage
  - Batch operations when possible
  - If still hitting limits, increase to 15 minutes (`*/15 * * * *`)

### Rate Limit Strategy

1. **Add delays between API calls (CRITICAL):**
   ```typescript
   // Wait 2-3 seconds between Nad.fun API calls
   await new Promise(resolve => setTimeout(resolve, 2000))
   
   // Wait 1 second between Indexer queries
   await new Promise(resolve => setTimeout(resolve, 1000))
   ```

2. **Limit parallel requests:**
   - Process tokens sequentially or in small batches (max 5 at a time)
   - Add delays between batches
   - Don't make all 7 methods run simultaneously - stagger them

3. **Handle 429 errors gracefully:**
   ```typescript
   async function fetchWithRetry(url, options, maxRetries = 2) {
     for (let i = 0; i < maxRetries; i++) {
       try {
         const result = await fetch(url, options)
         if (result.status === 429) {
           const retryAfter = parseInt(result.headers.get('Retry-After') || '60')
           console.log(`Rate limited, waiting ${retryAfter} seconds...`)
           await new Promise(resolve => setTimeout(resolve, retryAfter * 1000))
           continue
         }
         return result
       } catch (err) {
         if (i === maxRetries - 1) throw err
         await new Promise(resolve => setTimeout(resolve, 5000 * (i + 1)))
       }
     }
   }
   ```

4. **Optimize agent execution:**
   - Use Indexer methods (1-2) first (they're faster and don't hit API limits)
   - Only use API methods (3-7) if Indexer doesn't find enough tokens
   - Analyze ALL tokens that pass filters (no limit)
   - Skip detailed analysis if token doesn't meet basic filters

5. **Cron frequency:**
   - Current: every 10 minutes (`*/10 * * * *`)
   - If still hitting Claude API limits, increase to 15 minutes (`*/15 * * * *`)
