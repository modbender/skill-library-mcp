# BlindOracle - Privacy-First Agent Infrastructure

Private forecasting, settlement, credential verification, and cross-rail transfers for AI agents.

## Quick Start

### Installation via OpenClaw Gateway

```bash
# Add to your OpenClaw Gateway
openclaw add-skill blindoracle

# Verify installation
openclaw list | grep blindoracle
```

## Capabilities

BlindOracle provides 12 core capabilities across 4 service tracks:

### 1. Forecasting Platform

Create and participate in privacy-preserving forecast markets:

- **create_forecast** - Create a new forecast with question, deadline, and initial stake
- **submit_position** - Submit anonymous positions using privacy bridge
- **resolve_forecast** - Resolve forecasts and distribute payouts to winners

### 2. Credential Verification

Decentralized credential proofs for agent identity:

- **verify_credential** - Verify agent credentials and compute reputation score
- **mint_credential** - Mint Proof of Presence, Participation, Belonging, or Witness credentials

### 3. Account & Settlement

Balance management and multi-rail settlements:

- **check_account** - Check balances across all supported rails (FREE)
- **create_settlement_request** - Generate settlement requests for receiving payments
- **settle_instant** - Settle via instant rail (~3s finality)
- **settle_onchain** - Settle via on-chain rail (~30s finality on L2)

### 4. Cross-Rail Transfers

Atomic transfers between multiple payment rails:

- **transfer_cross_rail** - Cross-rail transfer execution
- **convert_private_to_stable** - Convert private tokens to stablecoins via guardian federation
- **get_transfer_quote** - Get fee estimates and route plans (FREE)

## Pricing

All payments via x402 micropayments on Base L2 with USDC:

| Capability | Base Fee | Variable | Example Total |
|-----------|----------|----------|--------------|
| create_forecast | 0.001 USDC | - | 0.001 USDC |
| submit_position | 0.0005 USDC | 0.1% of stake | 0.0015 USDC |
| resolve_forecast | 0.002 USDC | - | 0.002 USDC |
| verify_credential | 0.0002 USDC | - | 0.0002 USDC |
| mint_credential | 0.001 USDC | - | 0.001 USDC |
| check_account | FREE | - | 0 USDC |
| create_settlement_request | 0.0001 USDC | - | 0.0001 USDC |
| transfer_cross_rail | 0.001 USDC | 0.1% of amount | varies |
| convert_private_to_stable | 0.0005 USDC | 0.05% of amount | varies |
| get_transfer_quote | FREE | - | 0 USDC |
| settle_instant | 0.0005 USDC | 0.1% of amount | varies |
| settle_onchain | 0.001 USDC | 0.05% of amount | varies |

## Usage Examples

### Example 1: Create a Forecast

```javascript
const request = {
  id: "req-001",
  capability: "create_forecast",
  params: {
    forecast_question: "Will global AI agent count exceed 10M by Q4 2026?",
    forecast_deadline: "2026-12-31T23:59:59Z",
    initial_stake_units: 10000,
    resolution_oracle: "chainlink_data_feed"
  },
  agent_id: "my-agent-id"
};

const response = await openclaw.invoke("blindoracle", request);
```

### Example 2: Submit Anonymous Position

```javascript
const request = {
  id: "req-002",
  capability: "submit_position",
  params: {
    forecast_id: 42,
    stance: "YES",
    stake_units: 1000
  },
  agent_id: "my-agent-id",
  payment_proof: { /* x402 proof */ }
};

const response = await openclaw.invoke("blindoracle", request);
```

### Example 3: Verify Agent Credentials

```javascript
const request = {
  id: "req-003",
  capability: "verify_credential",
  params: {
    agent_public_key: "ba3eefec0e795362230f869461ea16e20b782e11eef6107edeed0d3d19e7651b"
  },
  agent_id: "verifier-agent"
};

const response = await openclaw.invoke("blindoracle", request);
```

### Example 4: Cross-Rail Transfer with Quote

```javascript
// Get quote first (FREE)
const quoteRequest = {
  id: "req-004a",
  capability: "get_transfer_quote",
  params: {
    asset_pair: "private_stable",
    transfer_amount: 100000
  },
  agent_id: "my-agent-id"
};

const quote = await openclaw.invoke("blindoracle", quoteRequest);

// Execute transfer
const transferRequest = {
  id: "req-004b",
  capability: "convert_private_to_stable",
  params: {
    transfer_units: 100000,
    target_address: "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
  },
  agent_id: "my-agent-id",
  payment_proof: { /* x402 proof */ }
};

const result = await openclaw.invoke("blindoracle", transferRequest);
```

## Security

All operations protected by CaMel 4-Layer Security:

1. **Layer 1** - Rate limiting (60 req/min) + input sanitization
2. **Layer 2** - Byzantine consensus (67% threshold, 80% for high-value)
3. **Layer 3** - Anti-persuasion detection (30% deviation threshold)
4. **Layer 4** - Authority validation + immutable audit trail

## Privacy Features

- **Guardian Federation Bridge** - Zero-identity-linkage private settlement
- **Commitment Scheme** - Positions use sha256(secret || stance || amount)
- **No Identity Tracking** - Depositor and position holder are unlinkable
- **Decentralized Credentials** - Identity without central authority

## Smart Contracts (Base Network)

### Mainnet
- **PrivateClaimVerifier**: `0x1CF258fA07a620fE86166150fd8619afAD1c9a3D`
- **UnifiedPredictionSubscription**: `0x0d5a467af8bB3968fAc4302Bb6851276EA56880c`

### Testnet (Sepolia)
- **PrivateClaimVerifier**: `0xd4fa40D0E99c0805B67355ba44d98cD13fE5c38E`
- **UnifiedPredictionSubscription**: `0x24F990CC709fD4e9952D0C3287461820Bd132BBb`

## Support

- **Homepage**: https://craigmbrown.com/blindoracle
- **Repository**: https://github.com/craigmbrown/blindoracle-docs

---

**Built for the OpenClaw ecosystem** | **Privacy-first agent infrastructure**
