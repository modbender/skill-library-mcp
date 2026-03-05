---
name: Sui
description: Assist with SUI transactions, object model, staking, and Move smart contracts.
metadata: {"clawdbot":{"emoji":"💧","os":["linux","darwin","win32"]}}
---

## Object Model (Critical Difference)
- Sui uses objects, not accounts — everything is an object with unique ID
- Objects are owned or shared — owned objects enable parallel transactions
- Coins are objects too — SUI balance is sum of coin objects you own
- Object IDs are permanent — address doesn't change but objects move
- Different from Ethereum's account model — requires different mental model

## SUI Token
- Native gas token — required for all transactions
- Total supply fixed at creation — no inflation, but distribution ongoing
- Gas fees burned — deflationary pressure
- Staking rewards from fees — validators and delegators earn from gas

## Transaction Characteristics
- Sub-second finality — extremely fast confirmation
- Parallel execution for owned objects — independent transactions don't wait
- Gas is predictable — know exact cost before submitting
- Transactions are atomic — all or nothing, no partial execution
- Sponsored transactions possible — someone else pays gas

## Address Format
- Addresses start with "0x" — 64 hex characters
- One address per wallet — but many objects owned
- Not the same as Ethereum addresses — different derivation
- Same seed gives different addresses than other chains

## Wallet Options
- Sui Wallet (official) — browser extension
- Suiet, Ethos — alternative wallets with good UX
- Ledger support coming — check current status
- Mobile wallets available — Sui Wallet has mobile app

## Staking
- Delegate to validators — no minimum to stake
- Epoch-based rewards — epochs are ~24 hours
- Staking locks SUI — but liquid staking options exist
- Choose validators carefully — commission rates vary
- Rewards compound automatically — unless you withdraw

## Gas and Fees
- Gas denominated in MIST — 1 SUI = 10^9 MIST
- Gas budget set per transaction — unused gas refunded
- Storage fees separate — pay for object storage
- Gas prices stable — reference gas price updated per epoch
- Very cheap transactions — fractions of a cent

## Move Language
- Smart contracts written in Move — not Solidity
- Object-centric programming — different from EVM
- Strong safety guarantees — resources can't be copied or lost
- Abilities system — controls what objects can do
- Package upgrades possible — but original stays on chain

## DeFi and NFTs
- Cetus, Turbos for DEX — major decentralized exchanges
- NFTs are objects — natural fit for Sui's model
- Kiosk standard for NFT trading — built-in marketplace primitives
- SuiFrens and other NFT collections — active NFT ecosystem
- Dynamic NFTs easy — objects can change over time

## Common Issues
- "Insufficient gas" — need more SUI for transaction
- Object not found — object was consumed or transferred
- Transaction failed — check error message, often gas or permission
- Coins fragmented — many small coin objects, merge them
- Staking delayed — rewards start next epoch after staking

## Coin Management
- Coins are separate objects — can have many coin objects
- Merge coins to simplify — combine into fewer objects
- Split coins for exact amounts — needed for some dApps
- Gas paid from one coin object — automatically selected
- Wallet usually manages this — but understand the model

## Cross-Chain
- Wormhole bridge available — connect to other chains
- Bridged assets are wrapped — not native on other chains
- Bridge verification important — verify official bridge addresses
- Native USDC coming — Circle deploying natively

## Security
- Seed phrase controls everything — standard 12/24 word recovery
- Transaction preview shows effects — review before signing
- dApp permissions matter — revoke unused connections
- Objects can have transfer restrictions — check before assuming transferable
- Verify package addresses — scam dApps exist
