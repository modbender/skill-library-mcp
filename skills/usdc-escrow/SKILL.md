---
name: usdc-escrow
description: "Trustless USDC escrow for agent-to-agent payments on Base. Create, release, dispute escrows via simple commands."
metadata:
  openclaw:
    emoji: "🔐"
    requires:
      bins: [curl, jq]
---

# USDC Escrow Skill

## Overview
This skill provides trustless USDC escrow services for agent-to-agent payments on Base. It allows AI agents to create, manage, and resolve payment escrows using smart contracts.

## API
All scripts point to `https://api.payclawback.xyz` by default. To use a different backend, set:
- `ESCROW_API_URL` - Override API URL (optional)

## Available Commands

### Create an Escrow
Creates a new escrow holding USDC for a beneficiary.
```bash
./scripts/create-escrow.sh <beneficiary_address> <amount_usdc> "<description>" <deadline_hours>
```
Example: `./scripts/create-escrow.sh 0x742d35Cc6634C0532925a3b844Bc9e7595f2bD28 10 "Payment for data analysis" 48`

### List Escrows
List all escrows, optionally filtered by state or depositor.
```bash
./scripts/list-escrows.sh [--state active|released|disputed|refunded|expired] [--depositor 0x...]
```

### Get Escrow Details
Get details of a specific escrow by ID.
```bash
./scripts/get-escrow.sh <escrow_id>
```

### Release Escrow
Release escrowed funds to the beneficiary.
```bash
./scripts/release-escrow.sh <escrow_id>
```

### Dispute Escrow
Open a dispute on an active escrow.
```bash
./scripts/dispute-escrow.sh <escrow_id>
```

### Resolve Dispute
Resolve a disputed escrow as arbiter.
```bash
./scripts/resolve-dispute.sh <escrow_id> <true|false>
```
- `true` = release funds to beneficiary
- `false` = refund to depositor

### Claim Expired Escrow
Reclaim funds from an expired escrow.
```bash
./scripts/claim-expired.sh <escrow_id>
```

## Workflow Example
1. Agent A wants to pay Agent B for a service
2. Agent A creates an escrow: `./scripts/create-escrow.sh 0xAgentB 50 "Sentiment analysis job" 24`
3. Agent B performs the service
4. Agent A releases payment: `./scripts/release-escrow.sh 1`

## How It Works
- USDC is locked in a [verified smart contract on Base](https://sepolia.basescan.org/address/0x2a27844f3775c3a446d32c06f4ebc3a02bb52e04)
- The escrow has a deadline - funds return to depositor if expired
- Either party can open a dispute for arbiter resolution
- The AI arbiter agent resolves disputes impartially
- All transactions are on-chain and verifiable

## API Reference
See `references/api-docs.md` for complete API documentation.
