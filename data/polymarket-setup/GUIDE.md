# Polymarket Trading API Guide

A practical guide for developers and AI agents building automated trading systems on Polymarket. This document covers the four API surfaces, authentication, market structure, order placement, real-time data feeds, and position management -- grounded in working production code patterns.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Contract Addresses](#2-contract-addresses)
3. [Wallet Setup and Authentication](#3-wallet-setup-and-authentication)
4. [Token Approvals](#4-token-approvals)
5. [Market Structure](#5-market-structure)
6. [Discovering and Filtering Markets](#6-discovering-and-filtering-markets)
7. [Placing Orders](#7-placing-orders)
8. [Real-Time Data (WebSocket)](#8-real-time-data-websocket)
9. [Position Management](#9-position-management)
10. [Getting Started Checklist](#10-getting-started-checklist)
11. [Common Pitfalls](#11-common-pitfalls)

---

## 1. Architecture Overview

Polymarket exposes four distinct API surfaces. Every trading bot needs to interact with at least three of them.

| API Surface | Base URL | Purpose |
|---|---|---|
| **Gamma API** | `https://gamma-api.polymarket.com` | Market discovery, event metadata, market questions, CLOB token IDs |
| **CLOB API** | `https://clob.polymarket.com` | Order placement, signing, API key derivation, order book REST endpoints |
| **Data API** | `https://data-api.polymarket.com` | Position queries, historical data, user balances |
| **WebSocket** | `wss://ws-subscriptions-clob.polymarket.com` | Real-time order book, price changes, trade confirmations |

### Chain and SDK

- **Chain ID:** `137` (Polygon mainnet)
- **Python SDK:** [`py-clob-client`](https://github.com/Polymarket/py-clob-client) >= 0.28.0 -- provides `ClobClient`, `OrderArgs`, `OrderType`, and order signing
- All trades settle on Polygon using USDC (the CTF Exchange contract)

### Data Flow

```
Gamma API          CLOB API              WebSocket
    |                  |                     |
events/slug  -->  create_order()      /ws/market (book updates)
markets[]    -->  sign + post         /ws/user  (trade lifecycle)
clobTokenIds      OrderType.FAK
    |                  |                     |
    v                  v                     v
Market           Order placed          Real-time fills
Discovery        on exchange           and confirmations
                      |
                 Data API
                      |
           /positions?user=0x...
                      |
           Position snapshots <-----+
```

---

## 2. Contract Addresses

These are the canonical Polymarket contract addresses on Polygon mainnet. Required for token approvals and on-chain debugging.

| Contract | Address |
|---|---|
| **USDC** | `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` |
| **CTF Exchange** | `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045` |
| **CLOB Exchange** | `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E` |
| **Neg Risk CTF Exchange** | `0xC5d563A36AE78145C45a50134d48A1215220f80a` |
| **Neg Risk Adapter** | `0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296` |

The CTF Exchange and CLOB Exchange both need USDC spend approval from your proxy wallet before any trading can occur.

---

## 3. Wallet Setup and Authentication

### Key Hierarchy

Polymarket uses a two-layer wallet system:

| Concept | What It Is |
|---|---|
| **Signing wallet** | The private key that signs orders. This is your `POLYMARKET_PRIVATE_KEY`. |
| **Proxy wallet** | A Polymarket-managed contract wallet tied to your account. This is where funds sit and where orders execute from. Set via `POLYMARKET_PROXY_ADDRESS`. |
| **Funder** | Same as proxy wallet address -- the address that "funds" (holds collateral for) orders. |

### Signature Types

| Type | Use Case |
|---|---|
| `0` | EOA wallet signing directly |
| `1` | Poly Gnosis Safe proxy |
| `2` | Browser-generated proxy wallet (most common for programmatic trading) |

### Initializing the Client

```python
from py_clob_client.client import ClobClient

host = "https://clob.polymarket.com"
private_key = "0x..."       # Your signing private key
chain_id = 137              # Polygon mainnet
funder = "0xYourProxyAddress"  # Your proxy wallet address
signature_type = 2          # Browser wallet proxy

client = ClobClient(
    host,
    key=private_key,
    chain_id=chain_id,
    signature_type=signature_type,
    funder=funder,
)
```

### Deriving and Persisting API Credentials

The CLOB API uses HMAC-based authentication. Credentials are derived from your wallet signature -- not generated in a dashboard. Derive once, then store and reuse.

```python
# Derive (one-time per wallet)
api_creds = client.derive_api_key()
client.set_api_creds(api_creds)

api_key = api_creds.api_key
api_secret = api_creds.api_secret
api_passphrase = api_creds.api_passphrase
```

`derive_api_key()` performs an on-chain signature. It is deterministic -- the same wallet always produces the same credentials. Calling it repeatedly is safe but wasteful; derive once and persist.

**Storing credentials** -- add to your `.env` file after first derivation:

```bash
POLYMARKET_API_KEY=<api_key>
POLYMARKET_API_SECRET=<api_secret>
POLYMARKET_API_PASSPHRASE=<api_passphrase>
```

**Loading on startup** -- skip derivation if credentials already exist:

```python
import os
from py_clob_client.clob_types import ApiCreds

api_key = os.getenv("POLYMARKET_API_KEY")
api_secret = os.getenv("POLYMARKET_API_SECRET")
api_passphrase = os.getenv("POLYMARKET_API_PASSPHRASE")

if api_key and api_secret and api_passphrase:
    client.set_api_creds(ApiCreds(
        api_key=api_key,
        api_secret=api_secret,
        api_passphrase=api_passphrase,
    ))
else:
    api_creds = client.derive_api_key()
    client.set_api_creds(api_creds)
    # Persist to .env or config
```

### WebSocket Authentication

The user feed (`/ws/user`) requires the same API credentials passed in the subscription message:

```python
ws_auth = {
    "apiKey": api_key,
    "secret": api_secret,
    "passphrase": api_passphrase,
}
```

### Required Environment Variables

```bash
POLYMARKET_PRIVATE_KEY=0x...        # Signing wallet private key
POLYMARKET_PUBLIC_ADDRESS=0x...     # Public address of your proxy wallet
POLYMARKET_PROXY_ADDRESS=0x...      # Same as public address for type 2
POLYMARKET_SIGNATURE_TYPE=2         # Signature type (0, 1, or 2)
POLYMARKET_WEBSOCKET_URL=wss://ws-subscriptions-clob.polymarket.com
POLYMARKET_DATA_API=https://data-api.polymarket.com

# After first credential derivation:
POLYMARKET_API_KEY=...
POLYMARKET_API_SECRET=...
POLYMARKET_API_PASSPHRASE=...
```

---

## 4. Token Approvals

Before any trading can occur, your proxy wallet must approve USDC spending for the Polymarket exchange contracts. This is typically done once when setting up a new wallet.

### Via the Polymarket UI (simplest)

Deposit USDC through the Polymarket web app. The deposit flow handles all necessary approvals automatically.

### Headless (programmatic, no browser)

For server deployments, approvals can be submitted programmatically using Polymarket's gasless relayer. This requires Builder API credentials (separate from CLOB API credentials -- request from Polymarket).

```python
from web3 import Web3
from eth_abi import encode

# Contract addresses (Polygon mainnet)
USDC = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
CTF_EXCHANGE = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"
CLOB_EXCHANGE = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"
NEG_RISK_CTF_EXCHANGE = "0xC5d563A36AE78145C45a50134d48A1215220f80a"
NEG_RISK_ADAPTER = "0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296"

w3 = Web3()

# Set approval amount appropriate for your use case.
# A bounded amount (e.g. your expected trading volume in USDC * 1e6) limits
# exposure if the contract is ever compromised. Unbounded approvals are
# convenient but grant the contract permanent spend rights.
approval_amount = ...  # e.g. int(1000 * 1e6) for $1,000 USDC

# Build approve(address,uint256) calldata for each contract
approve_selector = w3.keccak(text="approve(address,uint256)")[:4].hex()

contracts_to_approve = [
    CTF_EXCHANGE,
    CLOB_EXCHANGE,
    NEG_RISK_CTF_EXCHANGE,
    NEG_RISK_ADAPTER,
]

for contract_address in contracts_to_approve:
    params = encode(["address", "uint256"], [contract_address, approval_amount]).hex()
    calldata = approve_selector + params
    # Submit via gasless relayer or direct transaction
```

The relayer approach (via `py-builder-relayer-client`) batches all four approvals into a single gasless transaction from the Safe proxy. Direct transactions work too but require MATIC for gas.

---

## 5. Market Structure

### Hierarchy

```
Event
|-- Market 1
|   |-- CLOB Token (YES)  <-- clobTokenIds[0]
|   |-- CLOB Token (NO)   <-- clobTokenIds[1]
|
|-- Market 2
    |-- CLOB Token (YES)
    |-- CLOB Token (NO)
```

- **Event**: A real-world occurrence (e.g., "Bitcoin price on February 11")
- **Market**: A specific binary question within that event (e.g., "Will Bitcoin be above $97,000?")
- **CLOB Token Pair**: Each market has exactly two tokens -- YES and NO. These are the tradeable assets with unique `clobTokenId` strings.

### Price Relationship

YES and NO prices are complementary -- they always sum to approximately $1.00:

```
price(YES) + price(NO) ~ 1.00
```

A YES token priced at $0.65 means the market implies a 65% probability. The corresponding NO token trades at approximately $0.35. In a well-arbitraged book, the sum will be within a few cents of $1.00 (the spread represents the market maker's edge).

### CLOB Token IDs

Token IDs are long hex-like strings. Each market's `clobTokenIds` is a JSON-encoded array with exactly two elements:

```
clobTokenIds: ["71321044...95559976", "71321044...62393983"]
               ^-- YES token           ^-- NO token
```

The ordering is always `[YES, NO]`. This matters for correctly mapping positions and order sides.

---

## 6. Discovering and Filtering Markets

### Fetching Event Data (Gamma API)

Events are identified by their URL slug. The Gamma API returns full event metadata including all child markets.

```python
import httpx

GAMMA_API = "https://gamma-api.polymarket.com"

def fetch_event(slug):
    res = httpx.get(f"{GAMMA_API}/events/slug/{slug}")
    res.raise_for_status()
    return res.json()

# Example: extract slug from a Polymarket URL
url = "https://polymarket.com/event/bitcoin-up-or-down-on-february-11"
slug = url.split("/")[-1]  # "bitcoin-up-or-down-on-february-11"
event = fetch_event(slug)
```

### Gamma API Event Response Shape

The response contains the event wrapper and a `markets` array. Key fields per market:

```json
{
  "id": "event-uuid",
  "slug": "bitcoin-up-or-down-on-february-11",
  "title": "Bitcoin Up or Down on February 11?",
  "markets": [
    {
      "id": "market-uuid",
      "question": "Will the price of Bitcoin be greater than $97,000 on February 11?",
      "description": "This market will resolve according to the final Close price...",
      "clobTokenIds": "[\"71321044...95559976\", \"71321044...62393983\"]",
      "active": true,
      "closed": false,
      "volume": "125000.50",
      "outcomePrices": "[0.65, 0.35]"
    }
  ]
}
```

Note that `clobTokenIds` is a JSON string within JSON -- it requires a double parse:

```python
import json

for market in event["markets"]:
    token_ids = json.loads(market["clobTokenIds"])
    yes_token = token_ids[0]
    no_token = token_ids[1]
```

### Extracting Subscribable Token IDs

To subscribe to WebSocket feeds, you need a flat list of all CLOB token IDs across all markets in your events:

```python
clob_tokens_raw = [
    json.loads(mkt["clobTokenIds"])
    for mkt in event["markets"]
]
clob_tokens_subscribe = []
for tokens in clob_tokens_raw:
    clob_tokens_subscribe += tokens
# Result: flat list of all YES and NO token IDs
```

### Parsing Market Questions

Polymarket crypto markets follow predictable question formats. You need to parse these to understand what price thresholds and dates a market covers.

**Supported question formats:**

| Format | Example | Parsed Type |
|---|---|---|
| Greater than | "Will the price of Bitcoin be greater than $97,000 on February 11?" | `greater_than` |
| Less than | "Will the price of Ethereum be less than $2,500 on March 1?" | `less_than` |
| Range | "Will the price of Bitcoin be between $95,000 and $97,000 on February 11?" | `range` |
| Up or Down | "Bitcoin Up or Down on February 10?" | `updown` (resolved via reference price) |

**Parsing a threshold/range question:**

```python
import re
from datetime import datetime
from zoneinfo import ZoneInfo

def parse_prediction_question(question, description=""):
    # Extract asset name
    asset_match = re.search(r"Will the price of (\w+) be", question)
    asset = asset_match.group(1)  # "Bitcoin", "Ethereum", etc.

    # Extract date
    date_match = re.search(r"on ([A-Z][a-z]+ \d{1,2})\?", question)
    date_str = date_match.group(1)  # "February 11"

    # Detect question type and extract thresholds
    between_match = re.search(r"be between \$?([\d,]+) and \$?([\d,]+)", question)
    less_match = re.search(r"be less than \$?([\d,]+)", question)
    greater_match = re.search(r"be greater than \$?([\d,]+)", question)

    if between_match:
        low = float(between_match.group(1).replace(",", ""))
        high = float(between_match.group(2).replace(",", ""))
        question_type = "range"
    elif less_match:
        low, high = None, float(less_match.group(1).replace(",", ""))
        question_type = "less_than"
    elif greater_match:
        low, high = float(greater_match.group(1).replace(",", "")), None
        question_type = "greater_than"

    # Parse resolution time from description
    # Descriptions typically contain: "12:00 in the ET timezone"
    resolution_time = "12:00"
    resolution_tz = "UTC"
    if description:
        time_match = re.search(r"(\d{1,2}):(\d{2})", description)
        if time_match:
            resolution_time = f"{int(time_match.group(1)):02d}:{int(time_match.group(2)):02d}"

        tz_map = {
            "ET": "America/New_York",
            "EST": "America/New_York",
            "PT": "America/Los_Angeles",
            "CT": "America/Chicago",
            "UTC": "UTC",
            "GMT": "UTC",
        }
        for abbr, iana in tz_map.items():
            if re.search(rf"\b{abbr}\b", description):
                resolution_tz = iana
                break

    # Build expiration datetime
    # Try current year first; if the result is in the past, use next year.
    # This handles markets that expire in the following calendar year.
    tz = ZoneInfo(resolution_tz)
    current_year = datetime.now(tz).year
    for year in (current_year, current_year + 1):
        naive_dt = datetime.strptime(
            f"{date_str} {year} {resolution_time}", "%B %d %Y %H:%M"
        )
        expiration = naive_dt.replace(tzinfo=tz)
        if expiration > datetime.now(tz):
            break

    return {
        "asset": asset,
        "low": low,
        "high": high,
        "expiration": expiration,
        "question_type": question_type,
    }
```

**Example parsed outputs:**

```python
# "Will the price of Bitcoin be greater than $97,000 on February 11?"
{
    "asset": "Bitcoin",
    "low": 97000.0,
    "high": None,
    "expiration": datetime(2025, 2, 11, 12, 0, tzinfo=ZoneInfo("America/New_York")),
    "question_type": "greater_than"
}

# "Will the price of Bitcoin be between $95,000 and $97,000 on February 11?"
{
    "asset": "Bitcoin",
    "low": 95000.0,
    "high": 97000.0,
    "expiration": datetime(2025, 2, 11, 12, 0, tzinfo=ZoneInfo("America/New_York")),
    "question_type": "range"
}
```

### Filtering Tradable Markets

Not all markets are suitable for trading. Filter by expiration window:

```python
from datetime import datetime, UTC, timedelta

def filter_tradable_markets(markets):
    return [
        m for m in markets
        if timedelta(hours=1) < (m["expiration"] - datetime.now(UTC)) < timedelta(weeks=52)
    ]
```

Rules:
- **Minimum 1 hour to expiration** -- avoids trading markets about to resolve (thin liquidity, wide spreads)
- **Maximum 52 weeks to expiration** -- avoids long-dated markets with stale order books

---

## 7. Placing Orders

### OrderArgs Construction

The `py-clob-client` SDK uses `OrderArgs` to define an order before signing:

```python
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL

order = OrderArgs(
    price=0.55,                         # Limit price (probability)
    side=BUY,                           # BUY or SELL
    size=10,                            # Number of shares (integer)
    token_id="71321044...95559976"      # CLOB token ID (YES or NO)
)
```

### Price Rounding Rules

Polymarket enforces tick sizes that depend on the price level:

```python
if price > 0.96 or price < 0.04:
    price = round(price, 3)  # 3 decimal places for extreme prices
else:
    price = round(price, 2)  # 2 decimal places for normal range
```

Submitting a price with too many decimal places will cause the order to be rejected.

### Minimum Order Value

Polymarket enforces a **minimum order value of $1.00**:

```python
order_value = quantity * price
if order_value < 1.0:
    # Order will be rejected -- skip it
    pass
```

At a price of $0.10, you need at least 10 shares. At $0.50, you need at least 2 shares.

### Order Slicing

Large orders should be sliced into chunks to avoid moving the market and to stay within exchange limits:

```python
max_order_size = 40  # configurable per strategy

def slice_order(price, side, total_qty, token_id):
    orders = []
    # Full-sized chunks
    for _ in range(int(total_qty / max_order_size)):
        orders.append(OrderArgs(
            price=price,
            side=side,
            size=int(max_order_size),
            token_id=token_id,
        ))
    # Remainder
    remainder = total_qty % max_order_size
    if remainder > 0:
        orders.append(OrderArgs(
            price=price,
            side=side,
            size=int(remainder),
            token_id=token_id,
        ))
    return orders
```

### Order Lifecycle: Create, Sign, Post

The full flow from `OrderArgs` to a live order on the exchange:

```python
from py_clob_client.clob_types import OrderType
from py_clob_client.exceptions import PolyApiException

def place_order(client, order_args):
    # Step 1: Create (sign) the order
    # This produces an EIP-712 signed order object
    signed_order = client.create_order(order_args)

    # Step 2: Post the signed order to the CLOB
    # OrderType.FAK = Fill-And-Kill (immediate fill or cancel)
    try:
        resp = client.post_order(signed_order, OrderType.FAK)
        if resp.get("success"):
            return resp
        else:
            error_msg = resp.get("errorMsg", str(resp))
            raise Exception(f"Order rejected: {error_msg}")
    except PolyApiException as e:
        raise Exception(f"API error: {e.error_msg}")
```

### Order Types

| Type | Behavior |
|---|---|
| `OrderType.FAK` | **Fill-And-Kill.** Fills as much as possible immediately, cancels the rest. Standard for bot trading. No resting orders left on the book. |
| `OrderType.GTC` | **Good-Till-Cancelled.** Rests on the book until filled or explicitly cancelled. Useful for market-making. |
| `OrderType.FOK` | **Fill-Or-Kill.** Must fill the entire order immediately or nothing. |

FAK is preferred for aggressive/taker strategies because it guarantees no stale resting orders.

### Cancelling GTC Orders

For GTC orders, you must explicitly cancel if you want to pull them from the book:

```python
# Cancel a single order by order ID
client.cancel_order(order_id="0xabc123...")

# Cancel all open orders
client.cancel_all_orders()
```

Order IDs are returned in the `post_order` response (`resp["orderID"]`) and in order events from the user WebSocket feed.

### Bankroll Management on Order Failure

When an order fails, any bankroll reserved for that order must be returned:

```python
def update_bankroll(side, tx_value, trade_failed=False):
    if trade_failed:
        side = BUY if side == SELL else SELL
    if side == BUY:
        bankroll -= tx_value
    elif side == SELL:
        bankroll += tx_value
```

### Error Handling Response Shape

Successful:
```json
{ "success": true, "orderID": "0x...", "transactID": "...", "status": "matched" }
```

Failed:
```json
{ "success": false, "errorMsg": "insufficient balance" }
```

---

## 8. Real-Time Data (WebSocket)

Polymarket provides two WebSocket endpoints on the same base URL:

| Endpoint | Path | Auth Required | Purpose |
|---|---|---|---|
| Market Feed | `/ws/market` | No | Order book snapshots, price changes, last trade prices |
| User Feed | `/ws/user` | Yes | Your order placements, fills, trade lifecycle (MATCHED -> MINED) |

### Market Feed (`/ws/market`)

#### Subscription Message

```json
{
  "assets_ids": [
    "71321044...95559976",
    "71321044...62393983"
  ],
  "type": "market"
}
```

#### Initial Response

On subscription, the server sends a **JSON array** of current order book snapshots -- one per subscribed token. After the initial snapshot, subsequent messages arrive as individual JSON objects (not arrays).

```json
[
  {
    "event_type": "book",
    "asset_id": "71321044...95559976",
    "bids": [
      {"price": "0.55", "size": "150"},
      {"price": "0.54", "size": "300"}
    ],
    "asks": [
      {"price": "0.57", "size": "200"},
      {"price": "0.58", "size": "100"}
    ],
    "timestamp": "1707600000000"
  }
]
```

#### Event Type: `book`

Full order book update for a single asset. Bids sorted ascending (best bid is last element), asks sorted ascending (best ask is first element).

Extracting best bid/ask:

```python
best_bid = tick["bids"][-1]["price"] if len(tick["bids"]) > 0 else None
best_ask = tick["asks"][0]["price"] if len(tick["asks"]) > 0 else None
```

#### Event Type: `price_change`

Aggregated best-bid/best-ask updates across multiple assets:

```json
{
  "event_type": "price_change",
  "price_changes": [
    { "asset_id": "...", "best_bid": "0.56", "best_ask": "0.58" }
  ],
  "timestamp": "1707600002000"
}
```

#### Event Type: `last_trade_price`

Fires when a trade executes. Useful for tracking last-traded price (LTP):

```json
{
  "event_type": "last_trade_price",
  "asset_id": "71321044...95559976",
  "price": "0.56",
  "timestamp": "1707600003000"
}
```

#### Keep-Alive (Ping/Pong)

Send the raw string `"PING"` (not a JSON object). The server responds with `"PONG"`.

```python
# Send every 10 seconds
ws.send("PING")

# Filter in on_message:
def on_message(ws, message):
    if message == "PONG":
        return
    msg = json.loads(message)
    # ... process
```

Set `ping_interval` and `ping_timeout` at the WebSocket library level:

```python
ws.run_forever(ping_interval=30, ping_timeout=10)
```

Note: use either manual PING or `ping_interval`, not both -- double-pinging can cause connection issues.

### REST Order Book (No WebSocket)

To get a current order book snapshot without a WebSocket connection, use the CLOB REST endpoint:

```python
import httpx

def get_order_book(token_id):
    res = httpx.get(
        "https://clob.polymarket.com/book",
        params={"token_id": token_id}
    )
    res.raise_for_status()
    return res.json()
    # Returns same structure as WebSocket "book" event

book = get_order_book("71321044...95559976")
best_bid = book["bids"][-1]["price"] if book["bids"] else None
best_ask = book["asks"][0]["price"] if book["asks"] else None
```

Useful for initial bootstrapping, testing connectivity, and getting a one-off price check without maintaining a WebSocket.

### User Feed (`/ws/user`)

#### Subscription Message (Authenticated)

```json
{
  "type": "user",
  "auth": {
    "apiKey": "your-api-key",
    "secret": "your-api-secret",
    "passphrase": "your-api-passphrase"
  }
}
```

#### Trade Lifecycle

```
PLACEMENT --> MATCHED --> CONFIRMED --> MINED
                \--> FAILED
                \--> RETRYING
```

| Status | Meaning | Action |
|---|---|---|
| `PLACEMENT` | Order accepted by the CLOB matching engine | Informational only |
| `MATCHED` | Order matched with a counterparty | Log the match. Do NOT update positions yet. |
| `CONFIRMED` | Transaction submitted to Polygon | Informational only |
| `MINED` | Transaction confirmed on-chain | **Update positions and P&L now.** |
| `FAILED` | On-chain settlement failed | Revert bankroll reservation. |
| `RETRYING` | Settlement being retried | Wait for MINED or FAILED. |

#### Trade Event (`event_type: "trade"`)

```json
{
  "event_type": "trade",
  "asset_id": "71321044...95559976",
  "price": 0.55,
  "size": 10,
  "side": "BUY",
  "status": "MATCHED",
  "id": "28c4d2eb-bbea-40e7-a9f0-b2fdb56b2c2e",
  "taker_order_id": "0x06bc63e...",
  "maker_orders": [...],
  "timestamp": "1707600004000"
}
```

The same trade ID fires multiple times with different `status` values as it progresses.

#### Order Event (`event_type: "order"`)

```json
{
  "event_type": "order",
  "type": "PLACEMENT",
  "asset_id": "71321044...95559976",
  "price": "0.55",
  "side": "BUY",
  "original_size": "10",
  "size_matched": "10",
  "timestamp": "1707600004000"
}
```

For FAK orders: `PLACEMENT` followed by `CANCELLATION` for any unfilled portion.

### Reconnection Strategy

```python
def on_close(ws, close_status_code, close_msg):
    # Reset attempt counter if connection was stable (> 30 seconds)
    if connected_at and (time.time() - connected_at) > 30:
        reconnect_attempts = 0

    if reconnect_attempts >= max_reconnect_attempts:  # e.g., 5
        return  # Give up -- alert operator

    delay = min(2 ** (reconnect_attempts + 1), 60)  # 2s, 4s, 8s, 16s, 32s, 60s cap
    reconnect_attempts += 1
    time.sleep(delay)
    reconnect()
```

---

## 9. Position Management

### Fetching Positions (Data API)

```python
import httpx

DATA_API = "https://data-api.polymarket.com"
user_address = "0xYourProxyAddress"

response = httpx.get(
    f"{DATA_API}/positions",
    params={"user": user_address}
)
positions = response.json()
```

### Position Response Shape

```json
{
  "asset": "71321044...95559976",
  "size": 10.0,
  "avgPrice": 0.55,
  "initialValue": 5.5,
  "currentValue": 6.5,
  "unrealizedPnl": 1.0,
  "realizedPnl": 0.0,
  "curPrice": 0.65,
  "proxyWallet": "0xYourProxy...",
  "conditionId": "...",
  "title": "Will the price of Bitcoin be greater than $97,000?",
  "outcome": "Yes",
  "outcomeIndex": 0
}
```

`outcomeIndex` maps token position to outcome: `0` = YES (matches `clobTokenIds[0]`), `1` = NO (matches `clobTokenIds[1]`).

### Building a Position Book

```python
import pandas as pd

numerical_columns = [
    "size", "avgPrice", "initialValue", "currentValue",
    "unrealizedPnl", "realizedPnl", "curPrice",
    "idealSz", "FairPx", "tBid", "tAsk",
]

def build_position_book(raw_positions, tracked_asset_ids):
    empty_position = {col: 0.0 for col in numerical_columns}
    filtered = []
    seen = {}

    for pos in raw_positions:
        if pos["asset"] in tracked_asset_ids:
            row = {col: pos.get(col, 0.0) for col in numerical_columns}
            row["asset"] = pos["asset"]
            filtered.append(row)
            seen[pos["asset"]] = True

    for asset_id in tracked_asset_ids:
        if asset_id not in seen:
            filtered.append({**empty_position, "asset": asset_id})

    return pd.DataFrame(filtered).set_index("asset")
```

### Mark-to-Market Updates

```python
def update_position_mtm(book, token_id, bid, ask):
    if bid is None or ask is None:
        return
    mid_px = 0.5 * (bid + ask)
    book.loc[token_id, "curPrice"] = round(mid_px, 4)
    book.loc[token_id, "unrealizedPnl"] = round(
        book.loc[token_id]["size"] * (mid_px - book.loc[token_id]["avgPrice"]), 2
    )
```

### Updating Positions on Fills

Call this when a trade reaches `MINED` status on the user feed:

```python
from threading import Lock

position_lock = Lock()

def update_position(book, token_id, size, price, side):
    size = -size if side == "SELL" else size
    trade_value = size * price
    prev_size = book.loc[token_id]["size"]
    new_size = prev_size + size
    prev_value = book.loc[token_id]["initialValue"]
    position_value = prev_value + trade_value if new_size > 0 else 0
    prev_avg_px = book.loc[token_id]["avgPrice"]

    if side == "BUY":
        avg_px = position_value / new_size if new_size != 0 else 0
    elif side == "SELL":
        avg_px = prev_avg_px if new_size > 0 else 0

    realized_pnl_trade = abs(size) * (price - prev_avg_px) if side == "SELL" else 0
    total_realized_pnl = book.loc[token_id]["realizedPnl"] + realized_pnl_trade
    unrealized_pnl = new_size * (price - avg_px)

    with position_lock:
        book.loc[token_id, "size"] = round(new_size, 4)
        book.loc[token_id, "initialValue"] = round(position_value, 3)
        book.loc[token_id, "avgPrice"] = round(avg_px, 4)
        book.loc[token_id, "realizedPnl"] = round(total_realized_pnl, 4)
        book.loc[token_id, "unrealizedPnl"] = round(unrealized_pnl, 4)
```

### Pair-Level P&L

Because YES and NO tokens are complementary, P&L must be calculated at the pair level:

```python
def get_pnl_per_market(book, asset_id, complementary_asset_tokens):
    complementary_id = complementary_asset_tokens[asset_id]
    pnl = (
        book.loc[asset_id]["unrealizedPnl"]
        + book.loc[asset_id]["realizedPnl"]
        + book.loc[complementary_id]["realizedPnl"]
        + book.loc[complementary_id]["unrealizedPnl"]
    )
    return pnl
```

### Total Portfolio P&L

```python
def get_total_pnl(book):
    total_realized = book["realizedPnl"].sum()
    total_unrealized = book["unrealizedPnl"].sum()
    combined = total_realized + total_unrealized
    return total_realized, total_unrealized, combined
```

---

## 10. Getting Started Checklist

### Prerequisites

- [ ] **Python 3.10+** installed
- [ ] **Install dependencies:**
  ```bash
  pip install "py-clob-client>=0.28.0" httpx "websocket-client>=1.9.0" orjson pandas python-dotenv
  ```

### Wallet Setup

- [ ] **Create a wallet** -- generate or import an Ethereum-compatible private key
- [ ] **Fund with MATIC** on Polygon for gas fees
- [ ] **Fund with USDC** on Polygon for trading collateral
- [ ] **Set up a Polymarket account** via the web UI -- this creates your proxy wallet
- [ ] **Deposit USDC** into Polymarket through their UI (handles token approvals automatically)
  - For headless deployments: use the programmatic approval flow in [Section 4](#4-token-approvals)
- [ ] **Note your proxy wallet address** -- visible in your Polymarket account settings

### Configuration

- [ ] **Set environment variables:**
  ```bash
  export POLYMARKET_PRIVATE_KEY="0x..."
  export POLYMARKET_PUBLIC_ADDRESS="0x..."
  export POLYMARKET_PROXY_ADDRESS="0x..."
  export POLYMARKET_SIGNATURE_TYPE="2"
  export POLYMARKET_WEBSOCKET_URL="wss://ws-subscriptions-clob.polymarket.com"
  export POLYMARKET_DATA_API="https://data-api.polymarket.com"
  ```

### Derive and Persist API Credentials

- [ ] **Run credential derivation** (one-time per wallet):
  ```python
  from py_clob_client.client import ClobClient

  client = ClobClient(
      "https://clob.polymarket.com",
      key="0x...",
      chain_id=137,
      signature_type=2,
      funder="0x...",
  )
  creds = client.derive_api_key()
  # Write to .env — do not log or print credentials
  ```
- [ ] **Add credentials to your `.env` file:**
  ```bash
  POLYMARKET_API_KEY=...
  POLYMARKET_API_SECRET=...
  POLYMARKET_API_PASSPHRASE=...
  ```

### Test Connectivity

- [ ] **Fetch an event from the Gamma API** to verify network access
- [ ] **Get an order book snapshot via REST** (`GET /book?token_id=<id>`) to verify CLOB access without WebSocket
- [ ] **Connect to the market WebSocket** and confirm you receive book snapshots
- [ ] **Query the Data API** for your current positions (may be empty)
- [ ] **Place a small test order** (e.g., 2 shares at a far-from-market price) to verify the full signing and posting flow

### Build Your Strategy

- [ ] **Subscribe to market data** via WebSocket for your target markets
- [ ] **Implement a pricing model** -- determine your fair value vs. market price
- [ ] **Implement order logic** -- when to buy, sell, and at what size
- [ ] **Implement position tracking** -- update on confirmed fills, calculate P&L
- [ ] **Add risk controls** -- max position per market, max loss per market, bankroll limits

---

## 11. Common Pitfalls

### Proxy Address vs. Signing Address

The private key you sign orders with is NOT the address that holds your funds. Orders are signed with your EOA private key but execute from the proxy wallet. If you query positions, use the **proxy wallet address** (`POLYMARKET_PUBLIC_ADDRESS`), not the EOA address.

### Token Ordering in clobTokenIds

`clobTokenIds[0]` is always YES, `clobTokenIds[1]` is always NO. Swapping these means you are buying the opposite outcome. This is a silent logic error -- the exchange will happily fill your order on the wrong token.

### Price Is Probability, Not Dollar Amount

A price of `0.65` means 65% implied probability. When you buy 10 shares at 0.65, you pay $6.50 and receive 10 outcome tokens that pay $10.00 if the event resolves YES. Your maximum loss is $6.50; your maximum gain is $3.50.

### Partial Fills and FAK Orders

FAK orders fill what they can and cancel the rest. If you submit a 40-share order but only 15 shares of liquidity exist at your price, you get 15 shares. The user feed shows `PLACEMENT` with `size_matched` reflecting the actual fill, followed by `CANCELLATION` for the unfilled portion. Position tracking must handle partial fills.

### Silent WebSocket Disconnects

WebSocket connections can die without triggering `on_close`. Implement health monitoring:

```python
last_message_time = time.time()

def on_message(ws, message):
    global last_message_time
    last_message_time = time.time()
    # ... process

# In a monitoring thread:
def health_check():
    stale = (time.time() - last_message_time) > 120  # 2 minutes
    if stale:
        ws.close()  # Force reconnect
```

Do not send orders if your user feed is stale or disconnected:

```python
ack_stale = (time.time() - ack_feed.last_message_time) > 120
if not ack_feed.connected or ack_stale:
    return  # Skip -- won't receive fill confirmations
```

### Bankroll Revert on Failure

When you decide to place an order, deduct from bankroll immediately to prevent over-committing. If the order fails (`FAILED` from user feed or API error), add the value back:

```python
# On BUY order creation:
bankroll -= quantity * price
# If that order later fails:
bankroll += quantity * price  # revert
```

Failing to revert causes the bot to gradually "leak" bankroll to phantom orders.

### Minimum Order Value ($1.00)

| Price | Min Shares | Order Value |
|-------|-----------|-------------|
| $0.05 | 20 | $1.00 |
| $0.10 | 10 | $1.00 |
| $0.25 | 4 | $1.00 |
| $0.50 | 2 | $1.00 |

Orders below $1.00 will be rejected.

### Double-Parsing clobTokenIds

```python
# WRONG
token_ids = market["clobTokenIds"]  # Still a string

# CORRECT
import json
token_ids = json.loads(market["clobTokenIds"])  # Now a list
```

### Timestamp Units

WebSocket timestamps are in **milliseconds**. Convert to seconds for Python's `datetime`:

```python
from datetime import datetime, UTC
dt = datetime.fromtimestamp(int(tick["timestamp"]) / 1000, UTC)
```

### Rate Limiting

The CLOB API has rate limits. Add small delays between batched order submissions and implement exponential backoff on 429 responses.

### Order Size Is Integer

`OrderArgs.size` must be a whole number. Always use `int()`:

```python
OrderArgs(price=0.55, side=BUY, size=int(quantity), token_id=token_id)
```

### Market Expiration

Do not trade markets that have already expired:

```python
from datetime import datetime, UTC
if datetime.now(UTC) >= market_expiration:
    return
```

---

## Appendix: API Quick Reference

### Gamma API

| Endpoint | Method | Description |
|---|---|---|
| `/events/slug/{slug}` | GET | Fetch event metadata and all child markets |
| `/markets` | GET | List/search markets with query params |

### CLOB API (via py-clob-client)

| Method | Description |
|---|---|
| `client.derive_api_key()` | Derive HMAC credentials from wallet signature |
| `client.set_api_creds(creds)` | Set credentials for authenticated requests |
| `client.create_order(order_args)` | Sign an order locally (EIP-712) |
| `client.post_order(signed, order_type)` | Submit signed order to the exchange |
| `client.cancel_order(order_id)` | Cancel a specific GTC order by ID |
| `client.cancel_all_orders()` | Cancel all open orders |

### CLOB REST Endpoints

| Endpoint | Method | Params | Description |
|---|---|---|---|
| `/book` | GET | `token_id=<id>` | Current order book snapshot for a single token |

### Data API

| Endpoint | Method | Params | Description |
|---|---|---|---|
| `/positions` | GET | `user=0x...` | All positions for a given address |

### WebSocket Messages

| Direction | Endpoint | Message |
|---|---|---|
| Client -> Server | `/ws/market` | `{"assets_ids": [...], "type": "market"}` |
| Client -> Server | `/ws/user` | `{"type": "user", "auth": {...}}` |
| Client -> Server | Both | `"PING"` (raw string) |
| Server -> Client | Both | `"PONG"` (raw string) |

### Contract Addresses (Polygon Mainnet)

| Contract | Address |
|---|---|
| USDC | `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` |
| CTF Exchange | `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045` |
| CLOB Exchange | `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E` |
| Neg Risk CTF Exchange | `0xC5d563A36AE78145C45a50134d48A1215220f80a` |
| Neg Risk Adapter | `0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296` |
