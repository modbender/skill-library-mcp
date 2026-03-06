---
name: htlc-trade
description: "HTLC (Hash Time Locked Contract) trading for inscriptions and NFTs
  on EVM chains. Use when: (1) Buying or selling inscriptions via atomic swap,
  (2) Trading NFTs peer-to-peer without intermediaries, (3) Setting up trustless
  escrow for any digital asset, (4) Implementing commit-reveal trading patterns.
  Supports Base, Ethereum, Arbitrum and other EVM chains."
---


# HTLC Trade

Atomic swap trading using Hash Time Locked Contracts.

## Quick Start

```bash
# Install dependencies
npm install ethers viem

# Set environment
export PRIVATE_KEY=0x...
export BASE_ETH_RPC=https://mainnet.base.org
```

## Commands

### Generate Preimage

```bash
node scripts/htlc.js preimage
```

### Lock Funds (Buyer)

```bash
node scripts/htlc.js lock <seller> <preimageHash> <timeout> <amountETH>
```

### Reveal (Seller)

```bash
node scripts/htlc.js reveal <lockHash> <preimage>
```

### Full Trade

```bash
node scripts/htlc.js trade <seller> <inscriptionTx> <amountETH>
```

## Contract

BaseTimelock: `0xa7f9f88e753147d69baf8f2fef89a551680dbac1`

## Flow

1. Seller generates preimage, shares hash + inscription
2. Buyer verifies inscription, calls lock() with ETH
3. Seller calls reveal() with preimage → ETH released
4. Buyer confirms receipt → trade complete
