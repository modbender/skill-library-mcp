# Moralis Frequently Asked Questions

Common questions about Moralis capabilities, pricing, and implementation.

## General Questions

### What is Moralis?

Moralis is an enterprise-grade Web3 data infrastructure platform. It provides APIs to query blockchain data (balances, tokens, NFTs, transactions, prices) and monitor real-time events across 50+ chains.

**Not a blockchain.** Moralis reads data from blockchains but doesn't host one.

**Not a wallet.** Moralis provides data to build wallets, not wallet services.

### Who uses Moralis?

Major crypto companies including MetaMask, Trust Wallet, Ledger, Blockchain.com, Ronin Wallet, and Exodus. Powers 100M+ end users monthly.

### Is Moralis free?

Yes, there's a free tier with 40,000 Compute Units per day. Enough for development and small apps. Paid plans start at $49/month.

---

## API & Features

### What data can I get from Moralis?

| Category | Data Types |
|----------|------------|
| Wallet | Balances, tokens, NFTs, history, approvals, net worth |
| Token | Prices, metadata, holders, pairs, analytics, security |
| NFT | Metadata, traits, transfers, trades, floor prices |
| DeFi | Positions, protocols, liquidity, yields |
| Blockchain | Blocks, transactions, logs |
| Entity | Labeled addresses (exchanges, funds, whales) |

### What chains does Moralis support?

**50+ chains** including:
- **EVM:** Ethereum, Polygon, BSC, Arbitrum, Optimism, Base, Avalanche, Linea, Fantom, and more
- **Non-EVM:** Solana
- **Emerging:** Monad, Sei, Ronin

Full list: [SupportedApisAndChains.md](../moralis-data-api/references/SupportedApisAndChains.md)

### Does Moralis support testnet?

Yes. Major testnets supported:
- Ethereum Sepolia, Holesky
- Polygon Amoy
- BSC Testnet
- Base Sepolia
- And others

Note: Price data not available on testnets.

### Can Moralis decode transactions?

Yes. The `getWalletHistory` and `getTransactionVerbose` endpoints return human-readable decoded data including:
- Method names
- Parameter values
- Token transfers
- NFT transfers

---

## Real-Time & Streams

### What's the difference between Data API and Streams?

| Aspect | Data API | Streams |
|--------|----------|---------|
| Model | Request-response | Push via webhook |
| Use | Query current/historical state | React to events |
| Latency | Fast (varies by query complexity and chain) | 1-3s after block |
| Setup | API calls | Webhook endpoint required |

### Can I monitor wallets in real-time?

Yes, use @moralis-streams-api. Create a stream with the wallet address and receive webhooks for:
- Incoming/outgoing transactions
- Token transfers
- NFT transfers
- Contract interactions

### Does Streams guarantee delivery?

Yes. At-least-once delivery guarantee with:
- Automatic retries with exponential backoff on failure
- Payload backup and replay functionality
- Webhook handlers should be idempotent (duplicates possible)

### Can I get historical events from Streams?

Streams are for real-time events only. For historical data:
- Use @moralis-data-api queries
- Or Datashare for bulk export

---

## Pricing & Limits

### What are Compute Units (CUs)?

CUs measure API usage. Each endpoint costs different CUs based on complexity:
- Simple queries: 1-5 CUs
- Complex queries: 10-50 CUs
- Heavy queries: 50-100+ CUs

### What are the rate limits?

| Plan | Throughput |
|------|------------|
| Free | 1,000 CU/s |
| Starter | 1,000 CU/s |
| Pro | 2,000 CU/s |
| Business | 5,000 CU/s |
| Enterprise | Custom |

### What happens when I exceed limits?

- **Daily limit (Free):** API returns 429 until next day
- **Monthly limit (Paid):** Overage charges apply
- **Throughput:** Requests queued/delayed

### Can I pay with crypto?

Contact Moralis support for crypto payment options.

---

## Technical Questions

### What's the API authentication?

Single API key in header:
```
X-API-Key: $MORALIS_API_KEY
```

Get key at: https://admin.moralis.com

### What format are responses?

JSON. All responses use `snake_case` field names:
```json
{
  "token_address": "0x...",
  "block_number": 12345678
}
```

### How do I handle pagination?

Most list endpoints return max 100 items. Use cursor:
```
?limit=100&cursor=<cursor_from_response>
```

### Are there SDKs?

Yes, official SDKs for:
- JavaScript/TypeScript
- Python

But these skills use direct REST API calls via curl for simplicity.

### What response times should I expect?

Most Data API endpoints respond quickly. Response times vary depending on query complexity (decoded endpoints take longer), wallet size (large wallets need more processing), and chain. For production applications, set client-side timeouts to **30s** to safely handle edge cases. Use pagination with smaller `limit` values for wallets with large transaction histories. Implement exponential backoff for 429 (rate limit) responses.

See [PerformanceAndLatency.md](../moralis-data-api/references/PerformanceAndLatency.md) for full details.

### Is there a webhook secret?

Yes, for Streams webhooks. Different from API key:
- **API Key:** Authenticates your requests to Moralis
- **Streams Secret:** Verifies webhook payloads are from Moralis

---

## Common Issues

### "404 Not Found" error

Causes:
- Wrong base URL (Data API vs Streams)
- Incorrect endpoint path
- Token/contract doesn't exist

### "401 Unauthorized" error

Causes:
- Missing or invalid API key
- Key not activated yet (takes a few minutes)

### "429 Too Many Requests" error

Causes:
- Exceeded rate limit
- Exceeded daily/monthly quota

Solution: Implement exponential backoff, upgrade plan if needed.

### Empty response

Not an error. The address may have no activity. Check:
- Correct chain ID
- Address has activity on that chain
- Try `getWalletActiveChains` first

### Wrong data types

Common mistakes:
- Block numbers are decimal, not hex
- Balances are strings, not numbers
- Timestamps are ISO strings

See [DataTransformations.md](../moralis-data-api/references/DataTransformations.md)

---

## Integration Questions

### Can I use Moralis with any backend?

Yes. REST APIs work with any language/framework:
- Node.js
- Python
- Go
- Rust
- PHP
- Any HTTP client

### Do I need a database?

Moralis doesn't require a database. But you may want one to:
- Cache responses
- Store user preferences
- Track historical changes

### Can I use Moralis serverless?

Yes. Perfect for:
- AWS Lambda
- Vercel Functions
- Cloudflare Workers
- Google Cloud Functions

### How do I handle multi-chain?

1. Use `getWalletActiveChains` to find user's chains
2. Query each chain in parallel
3. Aggregate results

---

## Security & Compliance

### Is Moralis secure?

Yes:
- SOC 2 Type II certified
- ISO 27001 certified
- Data encrypted in transit and at rest

### Does Moralis store my data?

Moralis doesn't store your user data. You receive data and manage storage yourself.

### Is there an SLA?

Enterprise plans include custom SLAs. Contact Moralis for details.

---

## Support

### Where can I get help?

- **Docs:** https://docs.moralis.com
- **Discord:** Community support
- **Forum:** https://forum.moralis.io
- **Support:** https://moralis.com/support (paid plans)

### Is there 24/7 support?

Enterprise plans include 24/7 support. Other plans have community and business hours support.
