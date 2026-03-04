---
name: aegis-security-hackathon
version: 1.0.0
description: Blockchain security scanner for AI agents (testnet). Pay with Base Sepolia USDC via x402 protocol.
homepage: https://hackathon.aegis402.xyz
metadata: {"emoji":"🛡️","category":"blockchain-security","api_base":"https://hackathon.aegis402.xyz/v1","network":"testnet"}
---

# Aegis402 Shield Protocol (Hackathon/Testnet)

Blockchain security API for AI agents. **Testnet version** - pay with Base Sepolia USDC.

> ⚠️ This is the hackathon/testnet deployment. For production, use [aegis-security](https://aegis402.xyz/skill.md).

## Skill Files

| File | URL |
|------|-----|
| **SKILL.md** (this file) | `https://hackathon.aegis402.xyz/skill.md` |
| **package.json** (metadata) | `https://hackathon.aegis402.xyz/skill.json` |

**Base URL:** `https://hackathon.aegis402.xyz/v1`

## Quick Start

```bash
npm install @x402/fetch @x402/evm
```

```typescript
import { x402Client, wrapFetchWithPayment } from '@x402/fetch';
import { ExactEvmScheme } from '@x402/evm/exact/client';

const client = new x402Client()
  .register('eip155:*', new ExactEvmScheme(yourEvmWallet));

const fetch402 = wrapFetchWithPayment(fetch, client);

// Payments on Base Sepolia (testnet USDC)
const res = await fetch402('https://hackathon.aegis402.xyz/v1/check-token/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48?chain_id=1');
const data = await res.json();
```

**Requirements:** Testnet USDC on Base Sepolia (chain ID 84532)

**Get testnet USDC:** [Base Sepolia Faucet](https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet)

---

## Pricing (Testnet USDC)

| Endpoint | Price | Use Case |
|----------|-------|----------|
| `POST /simulate-tx` | $0.05 | Transaction simulation, DeFi safety |
| `GET /check-token/:address` | $0.01 | Token honeypot detection |
| `GET /check-address/:address` | $0.005 | Address reputation check |

---

## Endpoints

### Check Token ($0.01)

Scan any token for honeypots, scams, and risks.

```bash
curl "https://hackathon.aegis402.xyz/v1/check-token/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48?chain_id=1"
```

**Response:**
```json
{
  "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
  "isHoneypot": false,
  "trustScore": 95,
  "risks": [],
  "_meta": { "requestId": "uuid", "duration": 320 }
}
```

### Check Address ($0.005)

Verify if address is flagged for phishing or poisoning.

```bash
curl "https://hackathon.aegis402.xyz/v1/check-address/0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
```

**Response:**
```json
{
  "address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
  "isPoisoned": false,
  "reputation": "NEUTRAL",
  "tags": ["wallet", "established"],
  "_meta": { "requestId": "uuid", "duration": 180 }
}
```

### Simulate Transaction ($0.05)

Predict balance changes and detect threats before signing.

```bash
curl -X POST "https://hackathon.aegis402.xyz/v1/simulate-tx" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "0xYourWallet...",
    "to": "0xContract...",
    "value": "1000000000000000000",
    "data": "0x...",
    "chain_id": 8453
  }'
```

**Response:**
```json
{
  "isSafe": true,
  "riskLevel": "LOW",
  "simulation": {
    "balanceChanges": [
      { "asset": "USDC", "amount": "-100.00", "address": "0x..." }
    ]
  },
  "warnings": [],
  "_meta": { "requestId": "uuid", "duration": 450 }
}
```

---

## x402 Payment Flow (Testnet)

1. Agent calls any paid endpoint
2. Receives `402 Payment Required` with Base Sepolia payment instructions
3. Pays testnet USDC on Base Sepolia (chain ID: 84532)
4. Retries request with payment proof header
5. Gets security scan result

**Network:** Base Sepolia (eip155:84532)
**Currency:** Testnet USDC

---

## Use Cases for AI Agents

### Before Swapping Tokens
```typescript
const tokenCheck = await fetch402(`https://hackathon.aegis402.xyz/v1/check-token/${tokenAddress}?chain_id=8453`);
const { isHoneypot, trustScore } = await tokenCheck.json();

if (isHoneypot || trustScore < 50) {
  console.log('⚠️ Risky token detected!');
}
```

### Before Signing Transactions
```typescript
const simulation = await fetch402('https://hackathon.aegis402.xyz/v1/simulate-tx', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ from, to, value, data, chain_id: 8453 })
});

const { isSafe, riskLevel, warnings } = await simulation.json();

if (!isSafe || riskLevel === 'CRITICAL') {
  console.log('🚨 Dangerous transaction!', warnings);
}
```

---

## Risk Levels

| Level | Meaning |
|-------|---------|
| `SAFE` | No issues detected |
| `LOW` | Minor concerns, generally safe |
| `MEDIUM` | Some risks, proceed with caution |
| `HIGH` | Significant risks detected |
| `CRITICAL` | Do not proceed |

---

## Supported Chains (for scanning)

| Chain | ID | check-token | check-address | simulate-tx |
|-------|-----|-------------|---------------|-------------|
| Ethereum | 1 | ✅ | ✅ | ✅ |
| Base | 8453 | ✅ | ✅ | ✅ |
| Polygon | 137 | ✅ | ✅ | ✅ |
| Arbitrum | 42161 | ✅ | ✅ | ✅ |
| Optimism | 10 | ✅ | ✅ | ✅ |
| BSC | 56 | ✅ | ✅ | ✅ |

---

## Health Check (Free)

```bash
curl https://hackathon.aegis402.xyz/health
```

---

## Links

- **Hackathon API**: https://hackathon.aegis402.xyz
- **Production API**: https://aegis402.xyz
- **GitHub**: https://github.com/SwiftAdviser/aegis-402-shield-protocol
- **x402 Protocol**: https://docs.x402.org

---

🛡️ Built for the Agentic Economy. Powered by x402 Protocol.
