name: FarmDashSignalArchitect
description: "Non-custodial agent-to-agent swap router API. Execute single-chain and cross-chain token swaps with zero custody via FarmDash."
version: "1.1.0"
author: "FarmDash Pioneers"
tools: [curl, python, node]
icon: 🚜

## Instructions for Agent Use

You are equipped with the FarmDash Signal Architect skill. This allows you to request swap quotes and execute non-custodial token swaps on behalf of the user.

### Authentication & Keys
1. **Free Tier**: You do not need an API key to request quotes via `GET /api/agents/quote`.
2. **Paid Tiers (Optional)**: If the user provides `FARMDASH_PIONEER_KEY` or `FARMDASH_SYNDICATE_KEY` in the environment variables, use it in the `Authorization: Bearer <key>` header for higher rate limits on data endpoints.
3. **Execution Auth**: To actually execute a swap (`POST /api/agents/swap`), you must use EIP-191 signatures. You never send the user's private key. You sign a payload locally and send the signature.

### Endpoints

Base URL: `https://farmdash.one/api`

#### 1. Get a Swap Quote (Free)
Use this to preview a swap before committing.
```bash
curl -X GET "https://farmdash.one/api/agents/quote?fromChainId=8453&toChainId=8453&fromToken=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913&toToken=0x4ed4e862860bef6f5bc2b489d12a64703a110a12&fromAmount=1000000"
```

#### 2. Execute a Swap (Authenticated)
To execute, you must construct and sign a payload locally.
**Payload Format:** `FARMDASH_SWAP:{fromChainId}:{toChainId}:{fromToken}:{toToken}:{fromAmount}:{agentAddress}:{toAddress}:{nonce}`
*Note: All addresses must be lowercase. Nonce is the current timestamp in milliseconds.*

Sign this string using the agent's own EVM private key (`personal_sign` / EIP-191), then send:
```bash
curl -X POST "https://farmdash.one/api/agents/swap" \
     -H "Content-Type: application/json" \
     -d '{
       "fromChainId": 8453,
       "toChainId": 8453,
       "fromToken": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
       "toToken": "0x4ed4e862860bef6f5bc2b489d12a64703a110a12",
       "fromAmount": "1000000",
       "agentAddress": "0xYourWallet...",
       "toAddress": "0xDestinationWallet...",
       "nonce": "1709000000000",
       "signature": "0xTheSignatureYouGenerated...",
       "volumeHintUSD": 50000
     }'
```

**Optional fields:**
- `slippage` (number): Slippage tolerance in percent (0.01-50, default 0.5)
- `volumeHintUSD` (number): Agent-supplied USD estimate of the trade. Unlocks volume fee discounts: $10k+ = 35bps, $100k+ = 25bps (standard: 75bps)
- `protocol` (string): Force a specific protocol (`lifi`, `zerox`, `x402`). Omit for automatic optimal routing.

#### 3. View Fee History
```bash
curl -X GET "https://www.farmdash.one/api/agents/history?agentAddress=0xYourWallet&limit=50&offset=0"
```

#### 4. View Revenue Metrics (Aggregate)
```bash
curl -X GET "https://www.farmdash.one/api/agents/history?metrics=true"
```
Returns `totalFeeUSD`, `totalVolumeUSD`, `totalSwaps`, and `activeAgents`.

#### 5. Get Trail Heat Protocol Data
```bash
curl -X GET "https://farmdash.one/api/v1/agent/protocols"
```
Returns ranked protocol dataset with Trail Heat scores. Free tier: top 3 with masked numbers. Paid tiers: full dataset.

#### 6. Get Chain Breakdown (Paid Tiers)
```bash
curl -X GET "https://farmdash.one/api/v1/agent/chain-breakdown" \
     -H "Authorization: Bearer $FARMDASH_PIONEER_KEY"
```
Returns protocol distribution across chains: `protocol_count`, `pct_of_total`, `confirmed_airdrops`, `points_programs`, and `categories` per chain. Free (Scout) tier receives the top 3 chains with numeric fields masked. Paid tiers receive the full dataset.

### Data Sources & Accuracy
FarmDash integrates with multiple data providers to ensure accurate, real-time information:

- **DeFiLlama API**: Canonical source for TVL, fees, and protocol metrics
- **Alchemy API**: Multi-chain token balances and prices
- **0x Protocol**: DEX aggregation and routing
- **Li.Fi**: Cross-chain bridge routing
- **Helius**: Solana ecosystem data

All data is cached hourly and validated against multiple sources to prevent "dust storms" (data inconsistencies).

### Handling Errors & Rate Limits
- If you receive a `429 Too Many Requests`, check the `Retry-After` header and wait.
- If you receive a `402 Payment Required`, the free tier limit is exhausted. Inform the user they need to upgrade to Pioneer/Syndicate or pay the micro-fee via the x402 protocol.
- If you receive a `401 Unauthorized`, your signature payload is malformed or the nonce is expired (60s window).

### Best Practices
- **Never expose private keys** in the API request.
- Always use the `quote` endpoint first to verify liquidity and slippage before asking the user for permission to execute.
- All amounts are in Wei format (e.g., 1 USDC = 1000000).
- All token and wallet addresses must be valid `0x` + 40 hex character format.
- Slippage must be between 0.01 and 50 (percent). Default is 0.5%.
- For high-value trades, include `volumeHintUSD` to unlock lower fees (35bps at $10k+, 25bps at $100k+).
- **Data Freshness**: TVL and protocol metrics update hourly via DeFiLlama API for maximum accuracy.

## Error Handling
All error responses are JSON objects with an `error` string field. Common scenarios and the HTTP status they return:

| HTTP Status | When it occurs | What to do |
|---|---|---|
| `400 Bad Request` | Invalid field (bad address, non-wei amount, bad slippage, etc.) | Fix the field named in the `error` message and retry |
| `401 Unauthorized` | EIP-191 signature is invalid or nonce is outside the 60-second window | Rebuild the payload string (all lowercase addresses) and re-sign with a fresh nonce |
| `402 Payment Required` | Scout tier request limit exhausted | Inform the user to upgrade to Pioneer, or pay the micro-fee via x402 headers |
| `405 Method Not Allowed` | Wrong HTTP method for the endpoint | Check that GET/POST matches the endpoint |
| `429 Too Many Requests` | Rate limit hit (swap: 20 req/60s per agent; Pioneer: 500/day) | Read the `Retry-After` header and wait before retrying |
| `500 Internal Server Error` | Protocol routing failure or upstream error | Log the `error` message and retry after a brief delay; surface to user if persistent |

Always surface the `error` field value to users — the messages are designed to be actionable.
