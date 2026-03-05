# Inspected Upstream Skills

Directly inspected from ClawHub:

- `minara` latest `1.1.9`
- `torchmarket` latest `4.2.7`
- `torchliquidationbot` latest `3.0.2`

## Capability notes used in this meta-skill

- Minara: trading intelligence, swap-intent parsing, transaction assembly, chain support including Solana and Base.
- Torch Market: deep Solana-native token/vault/lending/quote primitives via bundled Torch SDK.
- Torch Liquidation Bot: autonomous vault-routed liquidation executor (not a generic swap engine by design).

## Scope constraints

- Torch Market and Torch Liquidation Bot are Solana-focused.
- No explicit built-in Twitter/X module in these three skills; social signal checks require external web search tools.
- "Rug/honeypot" checks are not a single turnkey flag in these skills; risk must be inferred from available on-chain indicators plus external validation.
