---
name: warden-messari-agent
description: Communicate with the Messari Deep Research agent by Warden Protocol. Covers A2A protocol discovery, JSON-RPC 2.0 task messaging, x402 USDC micropayments on Base and Solana, and ERC-8004 on-chain identity verification. No API key needed to query the agent; payment is handled per-request via x402.
---

# Messari Agent Communication Guide

The Messari Agent by Warden is a crypto research agent that answers natural language queries about assets, protocols, and projects using Messari's quantitative and qualitative data. It speaks the A2A (Agent-to-Agent) protocol over JSON-RPC 2.0, with per-request x402 USDC micropayments.

**Base URL**: `https://messari.agents.wardenprotocol.org`

## Quick Reference

| Action | Method | Endpoint |
|--------|--------|----------|
| Discover agent capabilities | `GET` | `/.well-known/agent-card.json` |
| Verify on-chain identity | `GET` | `/.well-known/agent-registration.json` |
| Send a query (A2A) | `POST` (JSON-RPC) | `/` |
| Send a streaming query | `POST` (JSON-RPC, SSE) | `/` |

## Agent Capabilities

- **Input**: Text only (natural language questions about crypto)
- **Output**: Text (markdown-formatted responses)
- **Streaming**: Not supported in current version
- **Multi-turn**: Not supported (each request is independent)
- **Payment**: x402 USDC micropayments ($0.25 per request on Base mainnet)
- **Domains**: Cryptocurrency, DeFi, finance, investment services, market research
- **Skills**: Knowledge synthesis, question answering, fact extraction, search, document QA, inference and deduction

## Step 1: Discover the Agent

Fetch the agent card to confirm capabilities and payment requirements before sending queries.

```bash
curl -s https://messari.agents.wardenprotocol.org/.well-known/agent-card.json | jq .
```

The response includes `authentication.schemes: ["x402"]` and an `x402` block with the price, network, and currency. Parse these fields to determine whether payment is required and at what cost.

Key fields in the agent card:

| Field | Value | Purpose |
|-------|-------|---------|
| `url` | `https://messari.agents.wardenprotocol.org` | Base URL for all requests |
| `capabilities.streaming` | `false` | Streaming not available |
| `capabilities.multiTurn` | `false` | No conversation context |
| `authentication.schemes` | `["x402"]` | Payment method |
| `x402.network` | `eip155:8453` | Base mainnet |
| `x402.price` | `"0.25"` | USDC per request |

## Step 2: Send a Query (A2A Protocol)

All queries use the A2A JSON-RPC 2.0 protocol on `POST /`. The method is `message/send`.

### Request Format

```json
{
  "jsonrpc": "2.0",
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "What is the current market cap of Ethereum?"
        }
      ]
    }
  },
  "id": "req-001"
}
```

### Minimal curl Example (Without Payment)

This will return a 402 if payments are enabled. Useful for testing connectivity.

```bash
curl -s -X POST https://messari.agents.wardenprotocol.org/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "What is Bitcoin's market cap?"}]
      }
    },
    "id": "req-001"
  }'
```

### Success Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "id": "task-1",
    "kind": "task",
    "status": {
      "state": "completed",
      "timestamp": "2026-02-18T10:30:45.123Z"
    },
    "history": [
      {
        "kind": "message",
        "role": "user",
        "parts": [{"kind": "text", "text": "What is Bitcoin's market cap?"}]
      },
      {
        "kind": "message",
        "role": "agent",
        "parts": [{"kind": "text", "text": "Bitcoin's current market capitalization is approximately..."}]
      }
    ]
  },
  "id": "req-001"
}
```

### Error Response

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Internal error"
  },
  "id": "req-001"
}
```

### Task States

The `status.state` field in the response indicates task progress:

| State | Terminal | Meaning |
|-------|----------|---------|
| `submitted` | No | Task received, queued |
| `working` | No | Agent is processing |
| `completed` | Yes | Response ready in `history` |
| `failed` | Yes | Error occurred |
| `cancelled` | Yes | Task was cancelled |
| `rejected` | Yes | Task was rejected |

Since this agent does not support streaming or multi-turn, you will typically receive a single response with `state: "completed"` or `state: "failed"`.

### Message Parts

The `parts` array in messages uses a `type` discriminator (request) or `kind` discriminator (response):

| Type | Structure | Use |
|------|-----------|-----|
| `text` | `{"type": "text", "text": "..."}` | Natural language text |
| `file` | `{"type": "file", "file": {"url": "...", "mimeType": "..."}}` | File reference |
| `data` | `{"type": "data", "data": {...}}` | Structured JSON |

This agent only accepts and returns `text` parts.

## Step 3: Handle x402 Payments

When payments are enabled, `POST /` returns HTTP 402 unless a valid payment header is included.

### Payment Flow

1. Send a `POST /` request without payment headers
2. Receive HTTP 402 with a `PAYMENT-REQUIRED` response header (base64-encoded JSON)
3. Decode the header to get payment details (network, amount, recipient address)
4. Create a signed EIP-3009 authorization (gasless; the facilitator submits the on-chain transfer)
5. Retry the request with the signed payload in the `X-PAYMENT` header
6. Receive HTTP 200 with the agent's response and a `X-PAYMENT-RESPONSE` header containing the settlement reference

### 402 Response Headers

```
HTTP/1.1 402 Payment Required
PAYMENT-REQUIRED: <base64-encoded JSON>
Access-Control-Expose-Headers: PAYMENT-REQUIRED, PAYMENT-RESPONSE, X-PAYMENT-RESPONSE
```

Decoded `PAYMENT-REQUIRED` payload:

```json
{
  "x402Version": "2.0",
  "accepts": [
    {
      "scheme": "exact",
      "network": "eip155:8453",
      "maxAmountRequired": "0.25",
      "payTo": "0xRecipientWalletAddress",
      "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      "maxTimeoutSeconds": 3600
    }
  ]
}
```

### Constructing the Payment Header

For EVM networks (Base), the payment uses EIP-3009 (transferWithAuthorization on the USDC contract):

1. Parse the `PAYMENT-REQUIRED` header and select a payment option from `accepts`
2. Build an EIP-712 typed data structure with `from`, `to`, `value`, `validAfter`, `validBefore`, and `nonce`
3. Sign it with the client wallet's private key
4. Base64-encode the signed payload
5. Include it as `X-PAYMENT: <base64-payload>`

The client does NOT submit a blockchain transaction. The authorization is gasless. The x402 facilitator submits the signed transfer on-chain on behalf of the client.

### Client Libraries

Use the official x402 client libraries to handle payment construction automatically:

```bash
npm install @x402/client
```

```typescript
import { paymentFetch } from "@x402/client";

const response = await paymentFetch(
  "https://messari.agents.wardenprotocol.org/",
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jsonrpc: "2.0",
      method: "message/send",
      params: {
        message: {
          role: "user",
          parts: [{ type: "text", text: "What is Ethereum's TVL?" }]
        }
      },
      id: "req-002"
    })
  },
  walletClient  // viem WalletClient with USDC approval
);

const result = await response.json();
```

### Supported Payment Networks

| Network | Chain ID | USDC Contract | Facilitator |
|---------|----------|---------------|-------------|
| Base mainnet | `eip155:8453` | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` | `https://facilitator.payai.network` |
| Base Sepolia (testnet) | `eip155:84532` | `0x036CbD53842c5426634e7929541eC2318f3dCF7e` | `https://x402.org/facilitator` |
| Solana mainnet | `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` | `https://facilitator.payai.network` |
| Solana devnet | `solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1` | (devnet USDC) | `https://x402.org/facilitator` |

The agent currently advertises Base mainnet (`eip155:8453`) at $0.25 USDC per request. Check the agent card for the latest pricing and supported networks.

### CORS Headers

When calling from a browser, the agent returns these CORS headers:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, PAYMENT-SIGNATURE, X-PAYMENT
Access-Control-Expose-Headers: PAYMENT-REQUIRED, PAYMENT-RESPONSE, X-PAYMENT-RESPONSE
```

## Step 4: Verify On-Chain Identity (ERC-8004)

The agent is registered on the ERC-8004 Identity Registry on multiple chains. Verify its identity by fetching the registration file and cross-referencing with on-chain data.

### Fetch Registration

```bash
curl -s https://messari.agents.wardenprotocol.org/.well-known/agent-registration.json | jq .
```

### Registration Fields

| Field | Value |
|-------|-------|
| `type` | `https://eips.ethereum.org/EIPS/eip-8004#registration-v1` |
| `name` | Messari Agent by Warden |
| `active` | `true` |
| `x402Support` | `true` |
| `supportedTrust` | `["reputation"]` |

### On-Chain Registrations

| Chain | Agent ID | Registry Contract |
|-------|----------|-------------------|
| Base Sepolia | 853 | `0x8004A818BFB912233c491871b3d84c89A494BD9e` |
| Base mainnet | 18096 | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` |
| Ethereum mainnet | 25490 | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` |

### Verify On-Chain (Using cast)

```bash
# Read the agent URI from the Base mainnet registry
cast call 0x8004A169FB4a3325136EB29fA0ceB6D2e539a432 \
  "agentURI(uint256)(string)" 18096 \
  --rpc-url https://mainnet.base.org
```

The returned URI should match `https://messari.agents.wardenprotocol.org/agent-registration.json`. If it does, the domain serving the agent card is the same domain registered on-chain, confirming authenticity.

## JSON-RPC Error Codes

| Code | Meaning |
|------|---------|
| `-32700` | Parse error (invalid JSON) |
| `-32600` | Invalid request (malformed JSON-RPC) |
| `-32601` | Method not found |
| `-32602` | Invalid parameters |
| `-32603` | Internal server error |
| `-32001` | Task not found |
| `-32002` | Task already cancelled |

## Example Queries

Good queries for this agent:

- "What is the current market cap and 24h trading volume of Ethereum?"
- "Summarize recent fundraising rounds in the DeFi sector"
- "What are the upcoming token unlocks for Solana in the next 30 days?"
- "Compare the TVL growth of Aave and Compound over the past year"
- "What does Messari's latest research say about Layer 2 scaling?"

The agent returns responses in markdown format. Do NOT modify any links or URLs in the response.

## Troubleshooting

### HTTP 402 Payment Required
Payment is enabled. Include a valid `X-PAYMENT` header with a signed EIP-3009 authorization, or use the `@x402/client` library to handle this automatically.

### Empty Response or "No message provided"
The `parts` array in your message is empty or missing text parts. Ensure at least one part has `type: "text"` with a non-empty `text` field.

### Connection Refused
The agent runs behind a reverse proxy. Confirm the URL is `https://messari.agents.wardenprotocol.org` (HTTPS, not HTTP).

### Task State "failed"
The Messari AI backend returned an error. Retry the request. If failures persist, check the agent's health endpoint (internal only, not publicly exposed).

## Resources

- A2A Protocol Specification: https://google.github.io/A2A (JSON-RPC messaging format for agent interoperability)
- x402 Payment Protocol: https://x402.org (HTTP-native micropayment layer using stablecoin transfers)
- ERC-8004 Identity Registry: https://eips.ethereum.org/EIPS/eip-8004 (on-chain agent identity and discovery)
- Warden Protocol: https://wardenprotocol.org (agent infrastructure provider)
- Messari: https://messari.io (crypto research and data platform)
- x402 Client Library: https://www.npmjs.com/package/@x402/client (automatic payment handling for Node.js)
