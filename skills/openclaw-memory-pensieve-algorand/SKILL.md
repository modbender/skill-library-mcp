---
name: pensieve-algorand v2
description: High-performance hybrid memory for OpenClaw with strict append-only capture, budgeted daily dream cycles, and optional Algorand anchoring through encrypted notes and external signing. Use when you need durable cross-session consistency with predictable runtime and low token overhead.
---

# OpenClaw Memory Pensieve v2

Use this skill to run memory in two lanes: ultra-fast capture and bounded consolidation.

## Core architecture

- Capture lane (hot path): `capture_event.py`
  - O(1) append to `events.jsonl` + `ledger.jsonl`
  - no LLM, no network, no summarization
- Consolidation lane (cold path): `dream_cycle_budgeted.py`
  - runs on schedule
  - hard caps for scanned events and promotions
- Anchoring lane (optional): encrypted Algorand note anchors with external signing

## Setup

1. `scripts/init_memory_layers.py --root <workspace>/memory`
2. Capture writes via:
   - `scripts/capture_event.py --root <workspace>/memory --content "..." --tags a,b`
3. Schedule daily consolidation:
   - `scripts/dream_cycle_budgeted.py --root <workspace>/memory`

## Daily performance pipeline

1. dream cycle (budgeted)
2. build anchor payload
3. build unsigned tx
4. sign externally
5. submit signed tx
6. record tx map
7. periodic fetch/decrypt/verify audit

## Required rules

- Never rewrite `*.jsonl` history (append-only only).
- Keep capture lane deterministic and minimal.
- Keep dream-cycle bounded by explicit caps.
- Anchor hashes/roots only; never plaintext memory on-chain.

## Read order

1. `self_model.jsonl`
2. `procedural.jsonl`
3. `semantic.jsonl`
4. `events.jsonl` (time-bounded)

## References

- `references/architecture.md`
- `references/operations.md`
- `references/algorand.md`
