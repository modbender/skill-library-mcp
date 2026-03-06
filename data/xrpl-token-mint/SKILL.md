---
name: xrpl-token-mint
description: "Create and manage XRPL tokens (issued currencies) and NFTs. Use
  for: (1) Minting new tokens, (2) Setting up token issuers, (3) Creating NFTs,
  (4) Managing trust lines."
---


# XRPL Token Minting

## Setup

```bash
npm install xrpl
```

## ISSUED CURRENCY (Fungible Token)

### Step 1: Create Trust Line (User)
```typescript
{
  TransactionType: 'TrustSet',
  Account: 'rUserAddress',
  LimitAmount: {
    currency: 'USD',
    issuer: 'rIssuerAddress',
    value: '1000000'
  }
}
```

### Step 2: Issue Token (Issuer)
```typescript
{
  TransactionType: 'Payment',
  Account: 'rIssuerAddress',
  Destination: 'rUserAddress',
  Amount: {
    currency: 'USD',
    issuer: 'rIssuerAddress',
    value: '1000'
  }
}
```

## NFT (Non-Fungible Token)

### Mint NFT
```typescript
{
  TransactionType: 'NFTokenMint',
  Account: 'rCreatorAddress',
  NFTokenTaxon: 0, // Collection ID
  Issuer: 'rCreatorAddress', // or different issuer
  TransferFee: 2500, // 2.5% royalty on secondary sales
  Flags: {
    tfBurnable: true,
    tfOnlyXRP: false,
    tfTrustLine: false
  },
  URI: 'ipfs://Qm...' // Metadata URL
}
```

### Create Offer (Sell)
```typescript
{
  TransactionType: 'NFTokenCreateOffer',
  Account: 'rSellerAddress',
  NFTokenID: '00080000...',
  Amount: '1000000', // 1 XRP
  Flags: tfSellNFToken
}
```

### Accept Offer (Buy)
```typescript
{
  TransactionType: 'NFTokenAcceptOffer',
  Account: 'rBuyerAddress',
  NFTokenOfferID: 'offerID...'
}
```

## Flags

- **tfBurnable**: Issuer can burn tokens
- **tfOnlyXRP**: Token cannot be transferred for IOUs
- **tfTransferable**: Token can be transferred
- **tfSellNFToken**: Create offer is a sell offer

## Key Points

- Token name: 3-character code (e.g., "USD") or full 40-char hex
- Precision: Up to 16 decimal places
- TransferFee: 0-50000 (0-50%)
- NFT Taxon: User-defined collection ID
