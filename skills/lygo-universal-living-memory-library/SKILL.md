---
name: lygo-universal-living-memory-library
description: Universal LYGO Living Memory Library upgrade. Provides a strict, low-noise memory index (max 20 files), fragile tagging, and audit/compression workflows so Champions can retain continuity and verify integrity via LYGO-MINT. Pure advisor; not a controller.
---

# LYGO Universal Living Memory Library (v1.1)

## What this is
A **universal upgrade skill** for LYGO systems that defines a minimal, durable memory library:
- **Max 20 files** in the active index (small context footprint)
- {FRAGILE} tagging for manual review
- An **audit workflow** (integrity + drift checks)
- A **compression workflow** (pure signal)
- Provenance via **LYGO‑MINT** hashes + anchors

This skill is **pure advisor**: it does nothing unless invoked.

## When to use
Use when you want to:
- define what files are “the living core”
- run an audit on those files
- compress a large archive into a clean Master Archive
- mint+anchor a living memory snapshot

## How to invoke (copy/paste)
- “Run **Living Memory Audit** (max20 index) and report drift/fragile flags.”
- “Compress these logs into **Master Archive** using Living Memory rules.”
- “Mint the Master Archive with LYGO‑MINT and output an Anchor Snippet.”

## Core verifier (install)
- https://clawhub.ai/DeepSeekOracle/lygo-mint-verifier

## References
- `references/library_spec.md` (rules + file roles)
- `references/core_files_index.json` (the Max20 index)
- `references/audit_protocol.md`
- `references/compression_protocol.md`
- `references/seal_220cupdate_excerpt.md`

## Scripts
- `scripts/audit_library.py` (runs the audit against the index)
- `scripts/self_check.py` (pack sanity)
