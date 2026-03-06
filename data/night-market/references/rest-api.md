# Nightmarket REST API

Call services directly through the Nightmarket proxy without the MCP server.

## Proxy URL Pattern

```
<METHOD> https://nightmarket.ai/api/x402/<endpoint_id>
Content-Type: application/json

<request body>
```

## x402 Payment Flow

1. **Initial request** — Call the proxy URL normally
2. **402 response** — Proxy returns `402 Payment Required` with a `PAYMENT-REQUIRED` header containing payment details (amount, recipient, network)
3. **Sign payment** — Use your wallet to sign the payment payload
4. **Retry with payment** — Resend the same request with the signed `payment-signature` header
5. **Response** — Proxy forwards to the seller's API and returns the response

## Important Details

- **Network**: Base (USDC settlement)
- **Protocol**: x402 — payment-per-request via HTTP headers
- **Currency**: USDC (on-chain)
- Prices are in USDC (e.g., `0.01` = one cent per call)
- The `PAYMENT-REQUIRED` header contains the full payment requirements (scheme, amount, recipient, network)
- The `PAYMENT-RESPONSE` header on successful calls contains settlement proof with transaction hash
