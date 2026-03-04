# Architecture

## Memory files

Under `<workspace>/memory/`:
- events.jsonl
- semantic.jsonl
- procedural.jsonl
- self_model.jsonl
- consolidation-log.jsonl
- ledger.jsonl
- onchain-anchors.jsonl

## Why this structure

- events = raw append-only history
- semantic/procedural/self_model = consolidated, low-noise recall
- ledger = integrity chain for every write
- anchors = on-chain proof mapping

## Integrity chain

For each captured event:
- entry_hash = sha256(canonical entry)
- prev_hash = previous ledger chain_hash (or GENESIS)
- chain_hash = sha256(prev_hash + entry_hash)

Append ledger receipt for every write.

## Performance model

- Capture is always cheap and local.
- Consolidation is scheduled and capped.
- Anchoring is daily and idempotent.
