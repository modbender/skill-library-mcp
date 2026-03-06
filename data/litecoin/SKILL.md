---
name: Litecoin
description: Assist with Litecoin LTC transactions, address formats, fees, and MWEB privacy features.
metadata: {"clawdbot":{"emoji":"Ł","os":["linux","darwin","win32"]}}
---

## Network Basics
- Bitcoin fork with faster blocks — 2.5 minute block time vs Bitcoin's 10
- Scrypt proof of work — different mining algorithm than Bitcoin
- 84 million max supply — 4x Bitcoin's 21 million cap
- Often called "silver to Bitcoin's gold" — similar but lighter for payments

## Address Formats
- Legacy addresses start with "L" — oldest format, widely supported
- SegWit addresses start with "M" or "3" — lower fees, better efficiency
- Native SegWit (bech32) starts with "ltc1" — lowest fees, recommended
- MWEB addresses for privacy — special addresses for confidential transactions
- Verify address format before sending — wrong format may not work on all exchanges

## Transaction Characteristics
- Confirmations faster than Bitcoin — 2.5 minutes per block
- 6 confirmations for high value — ~15 minutes vs Bitcoin's ~1 hour
- Fees very low — typically under $0.01
- RBF (Replace-By-Fee) supported — can speed up stuck transactions
- SegWit reduces transaction size — use SegWit addresses for lower fees

## MWEB (MimbleWimble)
- Optional privacy extension — confidential transactions
- MWEB addresses start with different prefix — separate from regular addresses
- Peg-in to MWEB, peg-out to main chain — move funds between layers
- Some exchanges don't support MWEB — check before using
- Privacy not default — must explicitly use MWEB

## Wallet Options
- Litecoin Core full node — most secure, downloads full blockchain
- Electrum-LTC light wallet — faster setup, SPV security
- Ledger and Trezor support — hardware wallet integration
- Trust Wallet, Exodus — multi-coin with LTC support
- Litewallet mobile — official mobile wallet

## Fees and Speed
- Fees based on transaction size — not amount sent
- SegWit transactions smaller — lower fees
- Priority fees for faster inclusion — rarely needed given fast blocks
- Mempool usually not congested — transactions confirm quickly
- Consolidating UTXOs costs fees — plan during low activity

## Exchange Considerations
- Nearly universal exchange support — high liquidity
- Fast deposits/withdrawals — 6 confirmations typical
- No memo/tag required — simple address only
- Some exchanges group LTC with Bitcoin — similar handling
- MWEB deposits may not be supported — verify exchange compatibility

## Common Issues
- Transaction unconfirmed — check fee, use RBF if enabled
- Balance not showing — wallet not synced, wait or use light wallet
- Sent to wrong address type — some services only support certain formats
- MWEB funds not recognized — exchange doesn't support MWEB, peg-out first
- Dust outputs — small UTXOs may not be economical to spend

## Merged Mining
- Merged mined with Dogecoin — shares Scrypt hashpower
- Increases security for both networks — shared mining work
- No action required from users — happens at protocol level
- Benefits from Dogecoin's popularity — more miners securing Litecoin

## Use Cases
- Faster payments than Bitcoin — practical for transactions
- Lower fees for transfers — cheaper to move between exchanges
- Testing ground for Bitcoin features — SegWit activated first on Litecoin
- Privacy with MWEB — optional confidential transactions
- Established history — one of oldest cryptocurrencies, since 2011

## Security
- Same UTXO model as Bitcoin — similar security considerations
- Seed phrase is everything — 12 or 24 words depending on wallet
- Verify addresses character by character — clipboard malware exists
- Use SegWit addresses — better security and efficiency
- Cold storage for large amounts — hardware wallet or paper backup
