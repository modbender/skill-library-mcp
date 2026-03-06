---
name: firstledger-snipe
description: "Snipe new token launches on XRPL via FirstLedger. Use for: (1)
  Detecting new token issuances, (2) Monitoring mempool for fresh offers, (3)
  Front-running token buys, (4) Managing XRP reserves."
---


# FirstLedger Sniping

## Overview

Monitor XRPL for new token launches and execute fast purchases before others.

## FirstLedger Endpoints

- **WebSocket**: `wss://xlrps-1.xrpl.link/`
- **REST**: `https://xlrps-1.xrpl.link/api/v1/`

## Detect New Tokens

### Subscribe to Transactions
```typescript
const ws = new WebSocket('wss://xlrps-1.xrpl.link/');

ws.send(JSON.stringify({
  command: 'subscribe',
  transactions: true
}));

// Watch for Payment transactions with new tokens
ws.onmessage = (msg) => {
  const tx = JSON.parse(msg.data);
  if (tx.TransactionType === 'Payment' && tx.Amount?.currency) {
    console.log('New token:', tx.Amount);
  }
};
```

### Check Issuer Flags
```typescript
// Key flags to audit before buying:
const flags = {
  lsfDisableMaster: 0x00080000,  // CANNOT mint more - SAFE
  lsfRipple: 0x00020000,         // Default ripple
  lsfDefaultRipple: 0x00040000,  // Trustline default
  lsfRequireAuth: 0x00010000      // Must be authorized
};

// SKIP if:
- lsfDisableMaster is NOT set (issuer can rug)
- No requireAuth (anyone can hold)
```

## Execute Buy

```typescript
const { Client, Wallet } = require('xrpl');
const client = new Client('wss://xrplcluster.com');

const tx = {
  TransactionType: 'Payment',
  Account: wallet.address,
  Destination: issuerAddress,
  Amount: {
    currency: tokenCode, // e.g., 'SYM123'
    issuer: issuerAddress,
    value: '100' // Amount to buy
  },
  DestinationTag: 1 // For tracking
};

const result = await client.submit(tx, { wallet });
```

## Safety Checks

✅ **MUST VERIFY**:
1. `lsfDisableMaster` flag set (no more minting)
2. Contract ownership renounced
3. Liquidity added (check trustlines)
4. Not a honeypot (can sell after buying)

❌ **SKIP IF**:
- No audit
- No liquidity
- Non-renounced contract

## Risk Profile

- **High risk** - Only trade what you can lose
- Always audit token flags before buying
- Keep XRP reserve for fees (~10 XRP)
