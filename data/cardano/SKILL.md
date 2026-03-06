---
name: Cardano
description: Assist with Cardano ADA transactions, staking, native tokens, and UTxO model.
metadata: {"clawdbot":{"emoji":"₳","os":["linux","darwin","win32"]}}
---

## UTxO Model (Critical Difference)
- Cardano uses UTxO like Bitcoin, not accounts like Ethereum — each transaction consumes and creates outputs
- Wallet balance is sum of all UTxOs — not a single account balance
- Transaction fees depend on size — more inputs/outputs = higher fee
- Change outputs created automatically — transactions consume full UTxOs and return change
- Minimum UTxO value required — can't create outputs below threshold (currently ~1 ADA)

## Transaction Characteristics
- Transactions are deterministic — you know exact fee before submitting
- No failed transactions that consume fees — if it fails, no fee charged
- Multi-asset transactions native — send ADA and tokens in same transaction
- Metadata can be attached — up to 16KB of arbitrary data

## Native Tokens
- Tokens are first-class citizens — not smart contracts, native protocol support
- Minting requires policy script — defines who can mint/burn and when
- Tokens must be sent with minimum ADA — tokens can't exist alone in UTxO
- Policy ID identifies the token — verify policy ID for authenticity
- Burning requires same policy script — time-locked policies can't burn after deadline

## Staking
- Non-custodial staking — ADA stays in your wallet, fully liquid
- Delegate to stake pools — no minimum, no lockup
- Rewards every epoch (5 days) — automatic, no claiming required
- First rewards appear after 15-20 days — registration and reward delay
- Pool saturation affects rewards — overly popular pools give diminishing returns

## Choosing Stake Pools
- Pool margin is operator's cut — lower isn't always better, quality matters
- Fixed cost (340 ADA minimum) taken before margin — affects small delegators more
- Pledge shows operator commitment — higher pledge often indicates reliability
- Check pool uptime and block production — missed blocks mean missed rewards
- Avoid pools near saturation — rewards decrease above saturation point

## Wallets
- Daedalus is full node wallet — downloads entire blockchain, most secure
- Yoroi is light wallet — faster, browser extension available
- Hardware wallet support — Ledger and Trezor via compatible software
- 15 or 24 word seed phrases — don't mix formats between wallets
- Staking key separate from spending key — can stake without exposing full access

## Smart Contracts (Plutus)
- eUTxO model extends UTxO with data and scripts — different from Ethereum EVM
- Transactions must be built off-chain — then submitted to chain
- Deterministic execution — same inputs always produce same outputs
- Higher collateral requirements — locked ADA returned if transaction succeeds
- Script size affects fees — optimize for smaller scripts

## Common Transaction Issues
- "Insufficient funds for fee" — need more ADA than just transfer amount
- "Minimum UTxO not met" — output too small, must include more ADA
- "UTxO too fragmented" — many small UTxOs, consolidate with self-transfer
- "Collateral required" — smart contract interaction needs collateral UTxO
- "Transaction too large" — too many inputs, split into multiple transactions

## Network and Epochs
- Epoch is 5 days — staking rewards and protocol updates follow epoch boundaries
- Slot every 1 second — blocks approximately every 20 seconds
- Hard forks via Hard Fork Combinator — seamless upgrades without chain splits
- Testnet (preprod, preview) for development — free test ADA from faucets

## Security
- Seed phrase is everything — never share, never enter online
- Verify transaction details on hardware wallet screen — software can lie
- Check policy IDs for tokens — scam tokens can have same name as legitimate ones
- DApp connections don't expose seed — only public key and signing requests
- Stake pool changes take effect after epoch boundary — not instant

## NFTs and Metadata
- NFTs are native tokens with quantity 1 — no special contract needed
- CIP-25 standard for NFT metadata — JSON metadata with image links
- Metadata stored on-chain — permanent and verifiable
- IPFS commonly used for images — verify IPFS pinning is permanent
- jpg.store, cnft.io for marketplace — verify NFT policies before buying

## Governance
- Voltaire era introducing on-chain governance — ADA holders vote on proposals
- Project Catalyst for treasury funding — community-voted grants
- Constitutional Committee, DReps — delegated representation coming
- Staking and governance participation can overlap — same ADA, different roles
