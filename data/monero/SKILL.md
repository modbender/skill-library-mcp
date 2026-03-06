---
name: Monero
description: Assist with Monero XMR transactions, privacy features, wallet management, and security practices.
metadata: {"clawdbot":{"emoji":"🔒","os":["linux","darwin","win32"]}}
---

## Privacy by Default
- All transactions are private — sender, receiver, and amount hidden by default
- Ring signatures hide sender — your transaction mixed with decoys
- Stealth addresses hide receiver — one-time addresses for each transaction
- RingCT hides amounts — transaction values encrypted
- No transparent mode — unlike Zcash, privacy isn't optional

## Address Types
- Standard addresses start with "4" — 95 characters long
- Subaddresses start with "8" — recommended for receiving, unlinkable to main address
- Integrated addresses include payment ID — for exchanges, starts with "4"
- Never reuse addresses — generate new subaddress for each transaction

## Transaction Characteristics
- Confirmations take ~2 minutes per block — 10 confirmations recommended for security
- Transactions are larger than Bitcoin — more data for privacy features
- Fees based on transaction size — typically $0.01-0.05
- No RBF — can't speed up stuck transactions
- Unlock time: 10 blocks — funds locked for ~20 minutes after receiving

## Wallet Types
- Monero GUI — official desktop wallet, full or remote node
- Monero CLI — power users, scripting
- Feather Wallet — lightweight desktop, recommended for most users
- Cake Wallet — mobile, iOS and Android
- Hardware: Ledger supports XMR — via Monero GUI or Feather

## Node Considerations
- Running own node = maximum privacy — no one sees your queries
- Remote nodes see your IP and query patterns — use Tor for privacy
- Trusted remote nodes: community-maintained lists exist
- Node sync takes days — hundreds of GB storage required
- Pruned nodes save space — ~50GB vs ~150GB+ for full

## View Keys and Audit
- View key allows seeing incoming transactions — but not outgoing or balances
- Useful for accounting without spending access
- Proving payments requires tx key — generated per transaction
- No public explorer can track you — unlike Bitcoin

## Exchange Considerations
- Some exchanges delisted XMR — regulatory pressure
- KuCoin, Kraken, others still support — verify current status
- Withdrawals may require extra confirmations — exchanges are cautious
- No memo/tag needed — address only
- Atomic swaps available — decentralized BTC-XMR swaps

## Mining
- CPU mineable by design — ASIC resistant RandomX algorithm
- Solo mining possible — GUI has built-in miner
- Pool mining for consistent rewards — many pools available
- P2Pool for decentralized mining — no pool operator trust needed

## Common Issues
- "Wallet not synced" — wait for blockchain sync to complete
- Balance shows 0 — wallet scanning blockchain, be patient
- "Unlock time" — received funds locked for 10 blocks
- Transaction stuck — wait, Monero doesn't have RBF
- "Daemon not connected" — node connection issue, check settings

## Security Best Practices
- Use subaddresses — main address should rarely be shared
- Run own node or use Tor — remote nodes see your IP
- Verify wallet software — download from getmonero.org only
- Hardware wallet for large amounts — Ledger integration available
- Keep seed phrase offline — standard crypto security

## Payment Verification
- Provide tx key + tx ID + recipient address — proves payment
- Receiver can verify without revealing their view key
- Block explorers can't verify — privacy preserved
- Useful for disputes — cryptographic proof of payment

## Regulatory Awareness
- Banned or restricted in some jurisdictions — check local laws
- Some exchanges refuse XMR — regulatory compliance
- Travel rule compliance impossible — by design
- Not illegal in most countries — but scrutinized
