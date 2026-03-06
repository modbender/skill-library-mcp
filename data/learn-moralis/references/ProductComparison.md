# Moralis Product Comparison

Detailed comparison of Moralis products to help users choose the right solution.

## Product Overview

| Product | Purpose | When to Use |
|---------|---------|-------------|
| **Data APIs** | Query blockchain state | Read current/historical data |
| **Streams** | Real-time event monitoring | React to on-chain events |
| **Datashare** | Bulk data export | Analytics, ML, data warehouses |
| **Data Indexer** | Custom indexing | Enterprise custom schemas |
| **RPC Nodes** | Direct node access | Raw blockchain interaction |

---

## Data APIs vs Streams

### Data APIs

**Best for:**
- Portfolio displays
- Transaction history views
- Token/NFT lookups
- Price queries
- One-time data fetches
- Historical analysis

**Characteristics:**
- Request-response model
- Pull-based (you request data)
- Returns current state
- Supports historical queries via block parameters
- Fast response times (varies by query complexity and chain)

**Example:** "Show me vitalik.eth's current token balances"

### Streams

**Best for:**
- Trading bots
- Alert systems
- Event logging
- Real-time dashboards
- Webhook integrations
- Notification services

**Characteristics:**
- Push-based (events delivered to you)
- Requires webhook endpoint
- ~1-3 second delivery after block confirmation
- At-least-once delivery with retries (idempotent handlers recommended)
- Decoded, enriched data

**Example:** "Notify me whenever vitalik.eth receives tokens"

---

## Streams vs Other Real-Time Solutions

| Feature | Moralis Streams | RPC WebSockets | The Graph |
|---------|----------------|----------------|-----------|
| Setup time | 2-3 minutes | Hours | 2+ hours |
| Decoded data | Yes | No (raw) | Yes |
| Cross-chain | Yes, unified | Per-chain | Per-chain |
| Reliability | At-least-once with retries | Connection drops | Variable |
| Wallet monitoring | Yes | No | No |
| Maintenance | Zero | High | Medium |

---

## Data APIs vs Building Your Own

| Aspect | Moralis Data APIs | Self-Built |
|--------|-------------------|------------|
| Time to first query | Minutes | Weeks-months |
| Multi-chain support | Built-in | Per-chain work |
| Data decoding | Automatic | Manual ABI work |
| Infrastructure | Managed | You manage |
| Cost | Predictable | Variable |
| Reliability | 99.9%+ SLA | Depends on setup |

---

## Datashare vs Data APIs

| Aspect | Datashare | Data APIs |
|--------|-----------|-----------|
| Data volume | Bulk/all | Per-request |
| Format | Parquet/CSV | JSON |
| Destination | Snowflake/BigQuery/S3 | Your app |
| Use case | Analytics, ML | Real-time apps |
| Update frequency | Periodic | Real-time |

**Use Datashare when:**
- Building analytics dashboards on historical data
- Training ML models on blockchain data
- Need to join blockchain data with internal data
- Running complex SQL queries

**Use Data APIs when:**
- Building user-facing applications
- Need real-time data
- Querying specific addresses/tokens
- Don't need bulk historical data

---

## API Categories Within Data APIs

### Wallet API
- Balances, tokens, NFTs, history
- Per-address queries
- Most common starting point

### Token API
- Prices, metadata, holders, pairs
- Per-token queries
- DeFi/trading use cases

### NFT API
- Metadata, traits, transfers, trades
- Per-collection or per-token queries
- NFT marketplace use cases

### DeFi API
- Protocol positions, liquidity
- Per-address across protocols
- Portfolio/risk management

### Blockchain API
- Blocks, transactions, logs
- Raw chain data access
- Explorer-like functionality

### Price API
- Real-time and historical prices
- OHLCV candlestick data
- Trading/charting use cases

### Entity API
- Labeled addresses (exchanges, funds)
- Identity/compliance use cases

### Discovery API
- Trending tokens, top gainers/losers
- Market cap rankings, price movers
- Token search and filtering

---

## Choosing by Use Case

### "I want to build a wallet app"
→ **Data APIs** (Wallet API, Token API, NFT API)

### "I want to alert users on activity"
→ **Streams** + your notification system

### "I want to analyze blockchain trends"
→ **Datashare** → your data warehouse

### "I want real-time price updates"
→ **Data APIs** (poll) or **Streams** (push for DEX events)

### "I want to monitor smart contract events"
→ **Streams**

### "I want historical transaction data"
→ **Data APIs** (with pagination) or **Datashare** (bulk)

---

## Cost Comparison

| Method | Cost Structure |
|--------|----------------|
| Data APIs | Per-request (CUs) |
| Streams | Per-record CUs (50 CU/record, confirmed only) |
| Datashare | Per-GB exported |
| RPC Nodes | Per-request |

For most applications, **Data APIs + Streams** provides the best balance of:
- Predictable costs
- Easy implementation
- Comprehensive data access

---

## Migration Paths

### From RPC polling to Streams
1. Identify events you're polling for
2. Create stream with matching `topic0`
3. Point to your webhook endpoint
4. Remove polling code

### From The Graph to Moralis
1. Map subgraph queries to API endpoints
2. Replace GraphQL calls with REST calls
3. Use Streams for real-time instead of subscriptions

### From self-built indexer to Moralis
1. Identify data requirements
2. Map to Moralis endpoints
3. Migrate incrementally by data type
