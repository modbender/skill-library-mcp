---
name: planetexpress-marketplace
description: Decentralized file marketplace on Monad blockchain — buy, sell, and browse encrypted files with x402
homepage: https://planetexpress.dropclaw.cloud
user-invocable: true
---

# Planet Express Marketplace — Decentralized File Commerce

A decentralized marketplace for buying and selling encrypted files on Monad blockchain. Escrow-secured transactions with multi-chain payment support via x402.

## Quick Reference

- **API Base**: `https://dropclaw.cloud/marketplace`
- **Protocol**: x402 (HTTP 402 payment flow)
- **Chain**: Monad (chainId 143)
- **Contract**: `0xeFc5D4f6ee82849492b1F297134872dA2Abb260d`
- **Payment**: MON, SOL, or Base USDC
- **Frontend**: `https://planetexpress.dropclaw.cloud`

## Endpoints

### Browse Listings (Free)
```
GET /marketplace/listings
```
Returns all active marketplace listings.

### Get Listing Detail (Free)
```
GET /marketplace/listing/{id}
```
Returns listing detail with pricing in MON/SOL/USDC.

### Purchase a File (x402 Payment)
```
POST /marketplace/purchase
Content-Type: application/json

{
  "listingId": 123,
  "buyerAddress": "0x..."  // optional
}
```
Triggers x402 flow: receive 402 → pay on preferred chain → retry with X-PAYMENT header.

### List a File for Sale ($30 Listing Fee)
```
POST /marketplace/list
Content-Type: application/json

{
  "fileId": "dropclaw-file-id",
  "title": "My File",
  "description": "What this file contains",
  "skillFileUri": "ipfs://Qm...",
  "keyHash": "0x...",
  "price": "0.5"
}
```
Requires x402 payment of $30 listing fee.

## Purchase Flow

1. `GET /marketplace/listings` to browse available files
2. `GET /marketplace/listing/{id}` for detail + pricing
3. `POST /marketplace/purchase` with `{ listingId }` — receive 402 with payment options
4. Send payment on your preferred chain (MON, SOL, or USDC on Base)
5. Retry POST with `X-PAYMENT: base64(JSON({ network, txHash }))`
6. Receive the encrypted file + skill file for decryption

## Listing Flow

1. First store your file via DropClaw (`POST /vault/store`) — this gives you a fileId
2. `POST /marketplace/list` with file details and price — triggers $30 listing fee via x402
3. Pay the listing fee on any supported chain
4. Your file appears in the marketplace for others to purchase

## Fees

| Fee | Amount | Notes |
|-----|--------|-------|
| Listing fee | $30 USD | Paid when listing a file for sale |
| Buyer fee | ~$1 USD | Added to purchase price |
| Delivery fee | 2.5% | Of listing price |
| FARNS buyback | 50% | Half of all protocol fees buy $FARNS |

## Payment Chains

- **Monad** (eip155:143) — MON native, direct contract interaction
- **Solana** (solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp) — SOL, facilitated
- **Base** (eip155:8453) — USDC, facilitated

## Frontend

The marketplace has a fully decentralized frontend hosted on IPFS:
- **Web**: `https://planetexpress.dropclaw.cloud`
- **IPNS**: `k51qzi5uqu5di1vh2ybr8qipy8mod859fjb0i548af7qyopyctlv7zpjblukee`

Install SDK: `npm i dropclaw` or `pip install dropclaw`
