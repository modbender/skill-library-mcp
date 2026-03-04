---
name: blindoracle
display_name: BlindOracle - Privacy-First Agent Infrastructure
version: 1.0.1
author: Craig M. Brown
homepage: https://craigmbrown.com/blindoracle
license: Proprietary
category: infrastructure
tags:
  - forecasting
  - identity
  - payments
  - privacy
  - x402
  - micropayments
  - agent-infrastructure
  - settlement
min_sdk_version: "0.1.0"
---

# BlindOracle

Privacy-first agent infrastructure providing forecasting, credential verification, settlement, and cross-rail transfers via x402 micropayments.

## Description

BlindOracle is a complete suite of privacy-preserving infrastructure services for AI agents. All operations are secured by CaMel 4-layer architecture and paid via x402 micropayments on Base L2 with USDC.

### Service Tracks

1. **Forecasting Platform** - Create and resolve privacy-preserving forecast markets with anonymous position submission
2. **Credential Verification** - Decentralized agent identity scoring with anti-synthetic detection
3. **Account & Settlement** - Multi-rail balance management and value transfer (instant ~3s, on-ledger ~30s)
4. **Cross-Rail Transfers** - Atomic transfers between payment rails with free fee quotes

## Capabilities

| Capability | Description | Price |
|-----------|-------------|-------|
| `create_forecast` | Create a new forecast market | 0.001 USDC |
| `submit_position` | Submit anonymous position | 0.0005 USDC + 0.1% |
| `resolve_forecast` | Resolve forecast and distribute payouts | 0.002 USDC |
| `verify_credential` | Verify agent credentials and reputation | 0.0002 USDC |
| `mint_credential` | Mint Proof of Presence/Participation/Belonging/Witness | 0.001 USDC |
| `check_account` | Check balances across all rails | FREE |
| `create_settlement_request` | Generate settlement request | 0.0001 USDC |
| `settle_instant` | Instant rail settlement (~3s) | 0.0005 USDC + 0.1% |
| `settle_onchain` | On-chain rail settlement (~30s) | 0.001 USDC + 0.05% |
| `transfer_cross_rail` | Cross-rail transfer execution | 0.001 USDC + 0.1% |
| `convert_private_to_stable` | Convert private tokens to stablecoins | 0.0005 USDC + 0.05% |
| `get_transfer_quote` | Get fee estimates and route plans | FREE |

## Usage

```javascript
// Check account balances (FREE)
const balance = await gateway.invoke("blindoracle", {
  capability: "check_account",
  params: { rail: "all" }
});

// Create a forecast
const forecast = await gateway.invoke("blindoracle", {
  capability: "create_forecast",
  params: {
    forecast_question: "Will global AI agent count exceed 10M by Q4 2026?",
    forecast_deadline: "2026-12-31T23:59:59Z",
    initial_stake_units: 10000,
    resolution_oracle: "chainlink_data_feed"
  },
  payment_proof: { /* x402 proof */ }
});

// Verify agent credentials
const creds = await gateway.invoke("blindoracle", {
  capability: "verify_credential",
  params: {
    agent_public_key: "ba3eefec0e795362230f869461ea16e20b782e11eef6107edeed0d3d19e7651b"
  }
});
```

## Security

All operations protected by CaMel 4-Layer Security:
- **Layer 1**: Rate limiting (60 req/min) + input sanitization
- **Layer 2**: Byzantine consensus (67% threshold, 80% for high-value)
- **Layer 3**: Anti-persuasion detection (30% deviation threshold)
- **Layer 4**: Authority validation + immutable audit trail

## Privacy

- Zero-identity-linkage via guardian federation bridge
- Commitment scheme: sha256(secret || stance || amount)
- Depositor and position holder are unlinkable
- Decentralized credentials without central authority

## API Endpoints

- Base URL: `https://craigmbrown.com/api/v2`
- Agent Card: `https://craigmbrown.com/a2a/v1`
- Health: `https://craigmbrown.com/api/v2/health`

## Payment

All payments via HTTP 402 (x402) micropayment protocol on Base L2 (chain ID 8453) with USDC.

## Requirements

- x402-compatible payment client
- Base L2 USDC for paid capabilities
- No dependencies for free capabilities (check_account, get_transfer_quote)

## Support

- Homepage: https://craigmbrown.com/blindoracle
- Repository: https://github.com/craigmbrown/blindoracle-docs
