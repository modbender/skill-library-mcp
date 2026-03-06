# Tator x402 Payment & Integration Reference

Complete implementation guide for all wallet types, payment flows, transaction verification, and advanced patterns. Most agents should start with SKILL.md — this reference is for manual integration, debugging, or advanced use cases.

> **⚠️ Security Notice:** For programmatic signing patterns (viem, ethers.js, Solana), refer to the x402 protocol documentation at https://www.x402.org. If you need to handle signing directly, **always use a dedicated hot wallet with minimal funds ($1-5 USDC)**. Never use your main wallet or any wallet holding significant assets. Managed wallet services (Sponge, AgentWallet, Vincent, Lobster.cash) are preferred as they never expose raw keys to your agent.

## x402 Payment Flow

```
1. POST to endpoint → 2. Get 402 response → 3. Sign payment → 4. Retry with header → 5. Get trade result
```

The 402 response contains a `PAYMENT-REQUIRED` header (base64 JSON) with accepted payment networks, amounts, and signing parameters.

## Payment Networks (14)

| Network | CAIP-2 ID | Token | Address |
|---------|-----------|-------|---------|
| Base | `eip155:8453` | USDC | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| Ethereum | `eip155:1` | USDC | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` |
| Arbitrum | `eip155:42161` | USDC | `0xaf88d065e77c8cC2239327C5EDb3A432268e5831` |
| Optimism | `eip155:10` | USDC | `0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85` |
| Polygon | `eip155:137` | USDC | `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` |
| Avalanche | `eip155:43114` | USDC | `0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E` |
| Unichain | `eip155:130` | USDC | `0x078D782b760474a361dDA0AF3839290b0EF57AD6` |
| Linea | `eip155:59144` | USDC | `0x176211869cA2b568f2A7D4EE941E073a821EE1ff` |
| Sonic | `eip155:146` | USDC | `0x29219dd400f2Bf60E5a23d13Be72B486D4038894` |
| HyperEVM | `eip155:999` | USDC | `0xb88339CB7199b77E23DB6E890353E22632Ba630f` |
| Ink | `eip155:57073` | USDC | `0x2D270e6886d130D724215A266106e6832161EAEd` |
| Monad | `eip155:143` | USDC | `0x754704Bc059F8C67012fEd69BC8a327a5aafb603` |
| MegaETH | `eip155:6342` | USDM | `0xFAfDdbb3FC7688494971a79cc65DCa3EF82079E7` |
| Solana | `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` | USDC | Native USDC SPL |

**Cost:** $0.20 USDC/USDM (200000 atomic units with 6 decimals) on any network. Base recommended for lowest fees.

## PAYMENT-SIGNATURE Payload Structure (Critical)

### EVM Payload (Decoded from base64)

```json
{
  "x402Version": 2,
  "scheme": "exact",
  "network": "eip155:8453",
  "payload": {
    "signature": "0x804f6127...1b",
    "authorization": {
      "from": "0xYourWalletAddress",
      "to": "0xPayToAddressFrom402Response",
      "value": "200000",
      "validAfter": "0",
      "validBefore": "1771454085",
      "nonce": "0xa1b2c3d4...bytes32hex"
    }
  }
}
```

### Solana Payload (Decoded from base64)

```json
{
  "x402Version": 2,
  "scheme": "exact",
  "network": "solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp",
  "payload": {
    "transaction": "base64-encoded-partially-signed-solana-transaction"
  }
}
```

### Field Rules

| Field | Type | Notes |
|-------|------|-------|
| `x402Version` | Number | **Must be `2`** |
| `scheme` | String | Always `"exact"` |
| `network` | String | CAIP-2 ID from 402 response |
| `signature` | String | **Direct child of `payload`, NOT inside `authorization`** |
| `value` | String | **Decimal string** (e.g., `"200000"`) — not hex, not BigInt |
| `validAfter` | String | **Decimal string** Unix timestamp. Use `"0"` for immediate |
| `validBefore` | String | **Decimal string** Unix timestamp. Set ~1 hour future |
| `nonce` | String | `0x`-prefixed bytes32 hex. Must be unique per payment |

### Common Mistakes That Cause Payment Failures

**1. `signature` nested inside `authorization`**
```json
// ❌ WRONG — causes "Cannot read properties of undefined"
{ "payload": { "authorization": { "signature": "0x...", "from": "0x..." } } }

// ✅ CORRECT — signature is a SIBLING of authorization
{ "payload": { "signature": "0x...", "authorization": { "from": "0x..." } } }
```

**2. Missing `x402Version`**
```json
// ❌ WRONG
{ "scheme": "exact", "network": "eip155:8453", "payload": { ... } }

// ✅ CORRECT
{ "x402Version": 2, "scheme": "exact", "network": "eip155:8453", "payload": { ... } }
```

**3. Wrong value format**
```json
// ❌ WRONG — hex or raw numbers
{ "value": "0x30D40" }
{ "value": 200000 }

// ✅ CORRECT — decimal string
{ "value": "200000" }
```

**4. Wrong endpoint**
```
❌ /v1/tator/api/v1/prompt  (internal route)
✅ /v1/tator/prompt          (correct public endpoint)
```

## x402 Headers Reference

| Header | Direction | Description |
|--------|-----------|-------------|
| `PAYMENT-REQUIRED` | Response (402) | Base64 JSON with payment requirements |
| `PAYMENT-SIGNATURE` | Request (retry) | Base64 JSON with signed payment proof |
| `PAYMENT-RESPONSE` | Response (200) | Base64 JSON with settlement tx hash |

Legacy `X-PAYMENT` header accepted for v1 backward compatibility.

## Payment-Identifier (Idempotency)

At $0.20 per request, prevent double-charging on retries:

```javascript
const paymentPayload = {
  x402Version: 2,
  scheme: 'exact',
  network: 'eip155:8453',
  payload: { /* ... */ },
  extensions: {
    'payment-identifier': {
      paymentId: 'pay_' + crypto.randomUUID().replace(/-/g, '')
    }
  }
};
```

IDs must be 16-128 characters, alphanumeric with hyphens and underscores.

## Wallet Integration Patterns

### Pattern 1: Sponge Wallet (Recommended — No Raw Keys)

See SKILL.md Pattern A.

### Pattern 2: AgentWallet (No Raw Keys)

See SKILL.md Pattern B.

### Pattern 3: @x402/fetch (Programmatic Signing)

> For programmatic signing with `@x402/fetch`, `viem`, or `ethers.js`, refer to the x402 protocol documentation at https://www.x402.org and the EVM signing spec at https://github.com/coinbase/x402/blob/main/specs/schemes/exact/scheme_exact_evm.md. Use the PAYMENT-SIGNATURE payload structure documented above in this file to construct the correct payment header. Always use a dedicated hot wallet with minimal funds.

### Pattern 4: Manual EVM Signing (viem / ethers.js)

For manual EVM signing, use the PAYMENT-SIGNATURE payload structure documented above and follow the x402 EVM signing spec: https://github.com/coinbase/x402/blob/main/specs/schemes/exact/scheme_exact_evm.md

The flow is:
1. POST to the Tator endpoint → receive 402 with `PAYMENT-REQUIRED` header
2. Parse the `accepts` array to find your preferred network
3. Sign an EIP-712 `TransferWithAuthorization` message using the parameters from the 402 response
4. Build the PAYMENT-SIGNATURE payload (see structure above — note `signature` is a sibling of `authorization`)
5. Base64-encode the payload and retry the request with the `PAYMENT-SIGNATURE` header
6. Verify and sign the returned trade transactions

> ⚠️ Always use a dedicated hot wallet with minimal funds for x402 payments. Never use your main wallet.

### Pattern 5: Solana Wallet (SVM)

For Solana payment signing, use `@x402/svm` and `@x402/fetch`. The Solana flow differs from EVM — you build an SPL `TransferChecked` transaction with the gateway's `feePayer` address, partially sign it, and send it in the payload.

See the x402 SVM spec and `@x402/svm` package documentation for implementation details.

### Pattern 6: Vincent Wallet (heyvincent.ai)

```javascript
const paymentAuth = await vincent.createX402Payment({
  network: 'eip155:8453',
  amount: '200000',
  token: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'
});

const response = await fetch('https://x402.quickintel.io/v1/tator/prompt', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'PAYMENT-SIGNATURE': paymentAuth.encoded
  },
  body: JSON.stringify({
    prompt: 'Bridge 50 USDC from Base to Arbitrum',
    walletAddress: vincentWalletAddress,
    provider: 'my-agent'
  })
});
const result = await response.json();
// Verify and broadcast via Vincent
```

### Other Compatible Wallets

Any wallet supporting x402 or EIP-3009 works, including Lobster.cash (Crossmint-powered agent wallets with Visa card integration). See their respective documentation.

## Transaction Verification Checklist

**Every transaction Tator returns should be inspected before signing.**

### Quick Checks (Every Time)

1. **`to` address** — Known DEX router, bridge contract, or the address YOU specified
2. **`value` field** — Matches your requested ETH/native amount (for ERC-20 swaps, usually `"0"`)
3. **Approval transactions** (`0x095ea7b3`) — Spender should be a known protocol contract
4. **`chainId`** — Matches the chain you requested
5. **`description`** — Aligns with your original prompt

### Deep Checks (Large Trades)

6. **Decode calldata** — Use openchain.xyz/signatures or 4byte.directory
7. **Verify contracts** — Look up `to` on block explorer (BaseScan, Etherscan, etc.)
8. **Simulate** — Use Tenderly, Blocknative, or wallet simulation

### Common Function Selectors

| Selector | Function |
|----------|----------|
| `0x095ea7b3` | `approve(address,uint256)` |
| `0x38ed1739` | `swapExactTokensForTokens` (Uniswap V2) |
| `0x5ae401dc` | `multicall` (Uniswap V3) |
| `0x3593564c` | `execute` (Uniswap Universal Router) |

### Automated Verification (For Agents)

```javascript
function verifyTatorTransaction(tx, originalPrompt, expectedChainId) {
  const warnings = [];

  if (tx.chainId !== expectedChainId) {
    warnings.push(`CHAIN MISMATCH: Expected ${expectedChainId}, got ${tx.chainId}`);
  }

  const MAX_VALUE_WEI = BigInt('1000000000000000000'); // 1 ETH
  if (BigInt(tx.value || '0') > MAX_VALUE_WEI) {
    warnings.push(`HIGH VALUE: ${tx.value} wei exceeds safety threshold`);
  }

  const KNOWN_ROUTERS = new Set([
    '0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad', // Uniswap Universal Router (Base)
    '0x2626664c2603336e57b271c5c0b26f421741e481', // Uniswap V3 Router (Base)
    '0x6131b5fae19ea4f9d964eac0408e4408b66337b5', // Kyberswap (Base)
  ]);

  if (!KNOWN_ROUTERS.has(tx.to.toLowerCase())) {
    warnings.push(`UNKNOWN CONTRACT: ${tx.to} — verify on block explorer`);
  }

  if (tx.data?.startsWith('0x095ea7b3')) {
    const spender = '0x' + tx.data.slice(34, 74);
    if (!KNOWN_ROUTERS.has(spender.toLowerCase())) {
      warnings.push(`APPROVAL TO UNKNOWN SPENDER: ${spender}`);
    }
  }

  return { safe: warnings.length === 0, warnings };
}
```

> **For automated agents:** Never enable fully automatic signing without verification checks. Human-in-the-loop for high-value transactions is strongly recommended.

## Complete Example: Scan Then Buy

Pseudocode showing the recommended flow using your wallet integration of choice:

```
1. SCAN the token using quickintel-scan skill ($0.03)
   POST https://x402.quickintel.io/v1/scan/full
   Body: { chain: "base", tokenAddress: "0x..." }

2. CHECK scan results:
   - If is_Honeypot == true → STOP, do not buy
   - If has_Scams == true → STOP, do not buy
   - If liquidity == false → WARN, verify on DEX aggregator
   - If contract_Renounced == false → CAUTION, owner retains control

3. TRADE using Tator ($0.20)
   POST https://x402.quickintel.io/v1/tator/prompt
   Body: {
     prompt: "Buy 0.1 ETH worth of 0x... on base",
     walletAddress: "your-public-address",
     provider: "your-agent-name"
   }

4. VERIFY each returned transaction:
   - Check `to` address against known DEX routers
   - Check `value` matches your requested amount
   - Check `chainId` matches your requested chain
   - Check `description` aligns with your prompt

5. SIGN and broadcast each transaction in order

Total cost: $0.23 for a scanned, verified trade.
```

For working code implementations of this flow using Sponge or AgentWallet, combine Pattern A or B from SKILL.md with the quickintel-scan skill.

## Full Response Schema

### Transaction Response

```json
{
  "type": "transaction",
  "transactions": [
    {
      "to": "0xContractAddress",
      "data": "0xCalldata...",
      "value": "100000000000000000",
      "chainId": 8453,
      "description": "Buy PEPE with 0.1 ETH on Base"
    }
  ],
  "message": "Transaction ready. Sign and broadcast to complete."
}
```

### Info Response

```json
{
  "type": "info",
  "message": "PEPE is currently trading at $0.00001234 on Base.",
  "data": { "price": "0.00001234", "volume24h": "5200000" }
}
```

### Error Response

```json
{
  "type": "error",
  "message": "Insufficient balance.",
  "code": "INSUFFICIENT_BALANCE"
}
```

### Async Pending Response

```json
{
  "type": "pending",
  "jobId": "job_abc123",
  "message": "Request queued. Poll for result."
}
```

Poll (free): `GET https://x402.quickintel.io/v1/tator/jobs/{jobId}`

## Resources

- Tator Docs: https://docs.quickintel.io/tator
- x402 Protocol: https://www.x402.org
- x402 EVM Spec: https://github.com/coinbase/x402/blob/main/specs/schemes/exact/scheme_exact_evm.md
- Gateway Discovery: https://x402.quickintel.io/accepted
- Quick Intel: https://quickintel.io
- Support: https://t.me/tatortrader