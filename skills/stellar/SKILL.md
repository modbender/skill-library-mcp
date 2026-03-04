---
name: Stellar
description: Assist with Stellar XLM transactions, anchors, memo requirements, and cross-border payments.
metadata: {"clawdbot":{"emoji":"🚀","os":["linux","darwin","win32"]}}
---

## Memo Field (Critical)
- Exchanges require memo for deposits — sending without memo loses funds
- Memo can be text, ID, or hash — use exactly what exchange provides
- Memo is NOT optional for exchanges — different from self-custody wallets
- Personal wallets don't need memo — only centralized services
- Verify memo type matches — text memo vs ID memo are different

## Account Requirements
- Minimum balance: 1 XLM base reserve — required to activate account
- Each trustline adds 0.5 XLM reserve — locked, not spendable
- Sending to new account must include 1+ XLM — creates the account
- Merging account recovers reserve — must remove all trustlines first

## XLM Token
- Native asset of Stellar network — used for fees and reserves
- Extremely low fees — 0.00001 XLM per operation (~$0.000001)
- Fast finality — 3-5 seconds
- No mining — Stellar Consensus Protocol (SCP)

## Trustlines
- Must trust an issuer before receiving their tokens — explicit opt-in
- Trustline costs 0.5 XLM reserve — locked until removed
- Remove trustlines to recover reserve — must have zero balance first
- Scam tokens can't be forced on you — trustlines required

## Anchors and Assets
- Anchors issue fiat-backed tokens — USDC, yXLM (yield), various fiats
- Stellar has native USDC — issued by Circle directly
- Verify anchor reputation — not all are trustworthy
- Path payments convert automatically — send USD, receive EUR

## Addresses
- Public keys start with "G" — 56 characters
- Secret keys start with "S" — never share
- Federated addresses: user*domain.com — human-readable, resolves to G address
- Muxed addresses encode account + memo — M prefix, newer format

## Transaction Features
- Multiple operations per transaction — batch actions
- Sequence number like Ethereum nonce — must be sequential
- Time bounds optional — transactions can expire
- Fee bumping available — increase fee on pending transaction

## DEX and Trading
- Built-in decentralized exchange — native to protocol
- Order book model — limit orders, not AMM
- Path payments find best route — automatic conversion
- Swap aggregators exist — StellarX, Lobstr markets

## Wallets
- Lobstr — most popular, mobile and web
- StellarTerm — web-based trading
- Solar Wallet — Keybase team, desktop
- Ledger support — hardware wallet via compatible apps
- Freighter — browser extension for dApps

## Common Issues
- "Destination account does not exist" — account not created, needs 1+ XLM
- "Missing memo" — exchange requires memo, transaction may be lost
- "Insufficient balance" — must keep minimum reserve
- "Trustline not established" — must add trustline before receiving token
- Transaction stuck — rare on Stellar, usually instant

## Cross-Border Payments
- Designed for remittances — fast and cheap
- Anchor network for fiat on/off ramps — varies by country
- MoneyGram partnership — cash pickup locations
- USDC corridors — stablecoin transfers between countries

## Soroban (Smart Contracts)
- Smart contract platform on Stellar — newer addition
- Different from traditional Stellar operations — Rust-based contracts
- Expanding Stellar capabilities — DeFi, NFTs becoming possible
- Still maturing — ecosystem growing

## Security
- Seed phrase standard — 24 words
- Multisig available — require multiple signatures
- Sep-10 authentication — standard for web auth
- Verify transaction details — XDR can be decoded before signing
