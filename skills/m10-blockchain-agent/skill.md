---
name: m10-blockchain-agent
description: >-
  Ask natural language questions about Ethereum blockchain data. Covers
  historical on-chain activity (events, transactions, blocks, token transfers,
  NFTs), live chain state (balances, gas prices, transaction lookups), and
  smart contract bytecode analysis (function selectors, ABIs for unverified
  contracts). Powered by a multi-agent pipeline over 5.8B+ indexed records.
compatibility: Requires network access. Paid endpoint (HTTP 402 / x402 protocol).
metadata:
  openclaw:
    homepage: https://onesource.io
---

# M10 Blockchain Agent

Ask a question in plain English. Get a structured analysis backed by live
blockchain data — no query language, no SDKs, no index knowledge required.

|              |                                           |
| ------------ | ----------------------------------------- |
| **Base URL** | `https://agent.onesource.io`              |
| **Auth**     | HTTP 402 (x402 protocol, no API keys)     |
| **Price**    | $0.04 USDC per query                      |
| **Networks** | Ethereum mainnet · Sepolia · Avalanche    |

---

## Payment

This is a paid endpoint. Requests without payment receive **HTTP 402** with a
`payment-required` header describing the price, network, and recipient. Paid
requests include a `payment-signature` header and are processed normally.

Payment uses the [x402 protocol](https://github.com/coinbase/x402) — an open
standard for HTTP-native payments. The skill itself does not manage wallets
or signing; it only returns standard HTTP 402 responses. Payment handling is
the responsibility of the calling client or platform.

---

## Privacy & Data Handling

- **Queries are sent to `https://agent.onesource.io`** — an external service
  operated by [OneSource](https://onesource.io). Your natural-language query
  text and any addresses you include are transmitted.
- **`query_traces`** in the response contains an audit trail of internal data
  lookups. This may echo parts of your query. Omit it from user-facing output
  if not needed.
- **No data is stored** beyond what is needed to process the request.

---

## Capabilities

### Indexed Historical Data
5.8 billion+ records across Ethereum mainnet, Sepolia testnet, and Avalanche C-Chain.

**Events & Activity**
- "How many Transfer events happened in the last 24 hours?"
- "What events did 0xdead... emit this week?"
- "Top 10 contracts by event count over the last 30 days"
- "Show me all Approval events for USDC in the last hour"

**Transactions**
- "What's the average gas used per transaction on mainnet today?"
- "How many transactions did 0xabc... send in the last 30 days?"
- "Show the 5 highest-value transactions in block range 21000000–21001000"
- "What's the transaction volume trend week over week for the last month?"

**Blocks**
- "What was the average block time last week?"
- "Which blocks had the highest gas utilization in the past 24 hours?"
- "How many blocks were produced per hour yesterday?"

**Token Transfers (ERC-20 / ERC-721 / ERC-1155)**
- "What ERC-20 tokens did 0xabc... receive in the last month?"
- "Top 5 ERC-20 tokens by transfer volume this week"
- "Show all mint events for USDC in the last 7 days"
- "How many unique wallets received WETH in the last 24 hours?"

**NFTs**
- "Show me BAYC token #4321 — name, image, and attributes"
- "What were the last 5 CryptoPunks sales and their prices?"
- "How many NFTs did 0xabc... receive this month?"
- "Top 10 NFT collections by transfer count today"

**Contracts**
- "When was Uniswap V3 deployed and who deployed it?"
- "How many contracts were deployed on mainnet in the last 7 days?"
- "Is 0xabc... a contract or an EOA?"

---

### Live Chain State
Real-time lookups directly from Ethereum archive nodes — no indexing lag.

- "What's the current ETH balance of 0xabc...?"
- "What's the current gas price on mainnet?"
- "Did transaction 0x123... succeed or revert?"
- "What's the latest block number right now?"
- "What's the USDC balance of 0xabc... at the current block?"
- "How much ETH does Vitalik's address hold?"
- "What's the current EIP-1559 base fee and priority fee?"

---

### Smart Contract Analysis
Analyze any deployed contract's bytecode — including unverified contracts —
to extract its interface without needing source code.

- "What functions does 0xabc... expose?"
- "Decompile 0xabc... and show me the function selectors"
- "Compare the public functions of these two contracts: 0xabc... and 0xdef..."
- "Does 0xabc... implement ERC-721?"

---

## Pricing

Requests are priced per-query at **$0.04 USDC** via the x402 payment protocol
(see [Payment](#payment) above).

| Network | Asset | Scheme  | Endpoint |
| ------- | ----- | ------- | -------- |
| Base    | USDC  | `exact` | `https://agent.onesource.io` |

The `usage.estimated_cost_usd` field in every response shows exactly what
each query cost.

---

## Request

```
POST /
Content-Type: application/json

{
  "query":      "string — required. Your natural language question.",
  "session_id": "string — optional. Custom ULID. Auto-generated if omitted."
}
```

## Response

```json
{
  "session_id": "01JMQX7K3N...",
  "status":     "completed | error | processing",
  "summary":    "Plain text summary, 1–3 sentences. Present on success.",
  "response":   "Full Markdown analysis with tables, headers, code blocks.",
  "steps": [
    {
      "agent":       "router | opensearch | rpc | evmole",
      "action":      "Description of what was queried",
      "status":      "completed | failed"
    }
  ],
  "usage": {
    "total_tokens":       5820,
    "estimated_cost_usd": 0.0018
  },
  "query_traces": [...],
  "error": "string | null"
}
```

**`summary`** — plain text, 1–3 sentences. Display this prominently.
**`response`** — full Markdown. Render it, don't parse it as structured data.
**`query_traces`** — raw audit trail of every data query made internally.

---

## Error Codes

| Code | Meaning                | Fix                                   |
| ---- | ---------------------- | ------------------------------------- |
| 402  | Payment required       | Include `payment-signature` header    |
| 409  | Session already exists | Omit `session_id` or use a new one    |
| 422  | Malformed request      | Check `query` field is present        |
| 500  | Pipeline error         | Try rephrasing the query              |

---

## What M10 Won't Answer

The agent rejects queries requiring unbounded full-index scans with no filter:

- "List every transaction ever"
- "Give me all NFTs"
- "Show everything in the last year"

Add a filter (address, time range, event type, contract) and it works:

- "List the last 10 transactions from 0xabc..."
- "Top 10 NFT collections by mint count in the last 24 hours"
- "How many transactions happened last year?" (aggregation — fine)
