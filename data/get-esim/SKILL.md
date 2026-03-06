---
name: Get eSIM Skill
description: Purchase eSIM data packages using USDC on Base Mainnet (or testnet
  for testing) via the x402 protocol.
---

# Get eSIM Skill

Purchase eSIM data packages using USDC on Base Mainnet (or testnet for testing) via the x402 protocol.

## Description

This skill enables AI agents to purchase eSIM data packages for users. It uses the x402 payment protocol to pay with USDC on Base Mainnet (default) or Base Sepolia testnet (for testing), then delivers the eSIM installation page.

**Default Network**: Base Mainnet (production - real eSIMs)
**Test Network**: Base Sepolia (testing - mock eSIMs)

## Prerequisites

- A wallet skill or USDC-capable wallet on Base (Mainnet or Sepolia)
- USDC balance for purchases
- ETH for gas (if using `transfer` scheme)

Suggested wallets: Coinbase Agentic Wallet, any x402-compatible wallet, or any wallet that supports Base USDC transfers.

## Network Selection

By default, purchases happen on **Base Mainnet** (real eSIMs). For testing, explicitly specify the testnet network.

### When to Use Each Network

| Network | Use Case | eSIM Type |
|---------|----------|-----------|
| **Base Mainnet** (default) | Production purchases | Real eSIMs |
| **Base Sepolia** | Development/testing | Mock eSIMs |

### Specifying Network

The user can indicate their preference by:
- Saying "testnet", "testing", "mock", or "demo" → Use Sepolia testnet
- Not specifying, or saying "mainnet", "production", "real" → Use Base mainnet (default)

## Invocation

Use this skill when a user:
- Asks for an eSIM or mobile data
- Needs cellular data for travel
- Wants to buy a data plan for a specific country
- Mentions needing connectivity abroad
- Requests "test" or "mock" eSIM for development

## Important: Transaction Timing

Crypto and eSIM transactions are NOT instant. Expect:
- **USDC transfer**: 5-15 seconds for on-chain confirmation
- **Purchase completion**: Additional 3-30 seconds for API to verify the transaction on-chain
- **Total purchase flow**: Can take 30-60 seconds from payment initiation to eSIM delivery

Inform the user that the purchase is processing and to wait for confirmation.

## Workflow

1. **Determine network**: Ask or detect if user wants mainnet (real) or testnet (testing)
2. **Discover needs**: Ask which country they need data for
3. **Search packages**: Query esimqr.link for available packages
4. **Present options**: Show available data plans with prices
5. **Get selection**: User picks a package
6. **Confirm purchase**: Show price, network (mainnet/testnet), and wallet balance, get confirmation
7. **Execute x402 flow**:
   - POST to /api/agent/purchase (mainnet) or /api/agent-testnet/purchase (testnet) → receive 402 with payment details
   - Pay using your wallet
   - Retry POST with payment proof header
8. **Deliver eSIM**: Return the `esimPageUrl` - a user-friendly page with QR code and install buttons

## Example Conversation

### Mainnet (Real eSIM)
```
User: I need an eSIM for my trip to USA

Agent: I can help you get an eSIM! This will be a real eSIM on Base Mainnet.

[Agent searches packages]

I found these options for USA:
- US_100MB_7: 100MB / 7 Days - $0.50
- US_1_7: 1GB / 7 Days - $1.18
- US_3_7: 3GB / 7 Days - $2.50
- US_5_30: 5GB / 30 Days - $4.42

Which package would you like?

User: 1GB 7 days

Agent: The US 1GB 7-Day plan costs $1.18 USDC on Base Mainnet.

My wallet balance: $30.00 USDC

Shall I purchase this eSIM now?

User: Yes

Agent: Initiating purchase on Base Mainnet...

✓ Payment sent: 1.18 USDC
✓ Transaction: 0xabc123...

Your eSIM is ready! Install it here:
https://esimqr.link/web3/esim/agent_1707184523_abc123
```

### Testnet (Mock eSIM for Testing)
```
User: Get me a test eSIM for USA

Agent: I'll get you a test eSIM on Base Sepolia testnet (mock eSIM for testing).

[Agent searches packages on testnet]

I found test packages for USA:
- US_1_7: 1GB / 7 Days - $1.18 (testnet)
- US_5_30: 5GB / 30 Days - $4.42 (testnet)

Which would you like?

User: 1GB

Agent: The US 1GB 7-Day test plan costs $1.18 testnet USDC.

My wallet balance: 10.00 testnet USDC

Shall I purchase this test eSIM?

User: Yes

Agent: Initiating testnet purchase...

✓ Test payment sent: 1.18 USDC
✓ Transaction: 0xdef456...

Your mock eSIM is ready! (For testing only):
https://esimqr.link/web3/esim/mockagent_1707184523_abc123
```

## API Endpoints

Base URL: `https://esimqr.link`

### Mainnet Endpoints (Production)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/agent/quote` | GET | Get price quote |
| `/api/agent/purchase` | POST | Initiate/complete purchase |
| `/api/agent/esim/{id}` | GET | Get eSIM status |

### Testnet Endpoints (Testing)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/agent-testnet/quote` | GET | Get price quote |
| `/api/agent-testnet/purchase` | POST | Initiate/complete purchase |
| `/api/agent-testnet/esim/{id}` | GET | Get eSIM status |

### Shared Endpoints (Both Networks)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/web3/packages?q={country}` | GET | Search packages (works for both) |

### Rate Limiting

- **Limit**: 10 requests per minute per IP
- **Response**: HTTP 429 with `Retry-After` header
- Handle rate limits gracefully by respecting the `Retry-After` value

## Network Configuration

### Base Mainnet (Default)
| Parameter | Value |
|-----------|-------|
| Network | Base Mainnet |
| Chain ID | 8453 |
| CAIP-2 | eip155:8453 |
| USDC Token | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| USDC Decimals | 6 |

### Base Sepolia (Testnet)
| Parameter | Value |
|-----------|-------|
| Network | Base Sepolia (testnet) |
| Chain ID | 84532 |
| CAIP-2 | eip155:84532 |
| USDC Token | `0x036CbD53842c5426634e7929541eC2318f3dCF7e` |
| USDC Decimals | 6 |

**Note**: Payment wallet addresses are returned dynamically by the API in quote and 402 responses. Do not hardcode payment addresses.

## Payment Schemes (x402)

The 402 response offers two payment options in the `accepts` array. Choose based on your wallet capabilities:

| Scheme | Header | Wallet Requirements | Gas |
|--------|--------|---------------------|-----|
| `exact` | `PAYMENT-SIGNATURE` | EIP-3009 signing (Circle, x402 SDK) | Gasless |
| `transfer` | `X-PAYMENT` | Standard USDC transfer | You pay gas |

### Which Scheme to Use

- **Use `exact` if**: Your wallet supports EIP-3009 `transferWithAuthorization` signing (Circle wallets, x402-compatible SDKs). Benefits: gasless - the facilitator broadcasts for you.

- **Use `transfer` if**: Your wallet can do standard USDC transfers but doesn't support EIP-3009. Works with any wallet that supports Base. You pay gas fees.

- **Not sure?**: The `transfer` scheme works with any USDC-capable wallet.

### Exact Scheme Flow (gasless):
1. POST `/api/agent/purchase` (mainnet) or `/api/agent-testnet/purchase` (testnet) → receive 402 with EIP-3009 parameters
2. Sign a `transferWithAuthorization` message (no on-chain tx needed)
3. Retry POST with header: `PAYMENT-SIGNATURE: <base64-encoded-payload>`
4. Facilitator broadcasts the transaction for you

### Transfer Scheme Flow:
1. POST `/api/agent/purchase` (mainnet) or `/api/agent-testnet/purchase` (testnet) → receive 402 with payment details
2. Transfer USDC on-chain to `payTo` address (on the correct network!)
3. Retry POST with header: `X-PAYMENT: txHash=0x...,nonce=...`

## API Response Examples

### Search Packages
```json
GET /api/web3/packages?q=US

{
  "packages": [
    {"packageCode": "US_1_7", "name": "United States 1GB 7Days", ...}
  ]
}
```

### Quote (Mainnet)
```json
GET /api/agent/quote?packageCode=US_1_7

{
  "packageCode": "PHAJHEAYP",
  "slug": "US_1_7",
  "planName": "United States 1GB 7Days",
  "usdcAmount": "1.18",
  "paymentDetails": {
    "recipient": "<payment-address-from-api>",
    "chainId": 8453,
    "network": "eip155:8453"
  }
}
```

### Quote (Testnet)
```json
GET /api/agent-testnet/quote?packageCode=US_1_7

{
  "packageCode": "PHAJHEAYP",
  "slug": "US_1_7",
  "planName": "United States 1GB 7Days",
  "usdcAmount": "1.18",
  "paymentDetails": {
    "recipient": "<payment-address-from-api>",
    "chainId": 84532,
    "network": "eip155:84532"
  },
  "isTestnet": true
}
```

### 402 Payment Required
```json
POST /api/agent/purchase
Body: {"packageCode": "US_1_7"}

{
  "x402Version": 2,
  "accepts": [
    {"scheme": "exact", ...},
    {"scheme": "transfer", "amount": "1180000", "payTo": "<payment-address-from-api>", "extra": {"nonce": "abc123"}}
  ]
}
```

**Important**: Always use the `payTo` address from the 402 response. Never hardcode payment addresses.

### Purchase Success
```json
POST /api/agent/purchase
Headers: X-PAYMENT: txHash=0x...,nonce=abc123
Body: {"packageCode": "US_1_7"}

{
  "success": true,
  "esimId": "agent_1707184523_abc123",
  "esimPageUrl": "https://esimqr.link/web3/esim/agent_1707184523_abc123",
  "esimDetails": {
    "iccid": "8901234...",
    "activationCode": "LPA:1$..."
  }
}
```

## Status Values

- `pending` - Order created, awaiting provisioning
- `processing` - eSIM being provisioned
- `ready` - eSIM ready for installation
- `activated` - eSIM installed on device
- `failed` - Order failed (contact support)
- `cancelled` - Mock eSIM auto-cancelled (testnet only)

## Documentation

- **Mainnet**: https://esimqr.link/api/agent/docs
- **Testnet**: https://esimqr.link/api/agent-testnet/docs
- **Landing**: https://esimqr.link/agents

## Files

- `esim_api.py` - API client for esimqr.link (supports both mainnet and testnet)

## Dependencies

```
requests>=2.28.0
```

## Hackathon Submission

- **Track**: Agentic Commerce
- **Protocol**: x402 (HTTP 402 Payment Required)
- **Networks**: Base Mainnet (production), Base Sepolia (testing)
- **Payment**: USDC

Submitted to: https://www.moltbook.com/m/usdc
