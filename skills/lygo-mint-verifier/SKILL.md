---
name: lygo-mint-verifier
description: "LYGO-MINT verifier for Champion/alignment prompt packs: canonicalize a pack, generate a deterministic SHA-256 hash, write append-only and canonical ledgers, and output a portable Anchor Snippet for posting anywhere (Moltbook/Moltx/X/Discord/4claw). Use when you need verifiable, hash-addressed alignment artifacts (Champion packs, summon prompts, workflow packs) with receipts and optional anchor backfill."
---

# LYGO-MINT VERIFIER

This skill turns an aligned Champion pack (or any prompt/workflow pack) into a **verifiable artifact**:
- canonical form
- deterministic hash
- ledger receipts
- portable Anchor Snippet (paste anywhere)

## Workflow (high-level)
1) Create/align the pack (e.g. Champion alignment system).
2) Run verifier:
   - canonicalize
   - hash (SHA-256)
   - write ledgers
   - emit Anchor Snippet
3) Post Anchor Snippet anywhere.
4) Backfill anchor IDs into the ledger.

Read the full process doc: `references/process.md`.

## Commands (scripts)
This skill wraps local tools in `tools/lygo_mint` and is designed to operate on non-secret prompt packs. It does not read env vars or network in the code shown, but **you should review the `tools/lygo_mint/*.py` files in your own workspace before using it on sensitive data.**

### Mint + verify a pack file
- `python scripts/mint_pack_local.py --pack reference/CHAMPION_PACK_LYRA_V1.md --version 2026-02-07.v1`

### Generate just an anchor snippet from an existing hash record
- `python scripts/make_anchor_snippet.py --hash <64-hex> --title "..."`

### Backfill anchors (post IDs/links)
- `python scripts/backfill_anchors.py --hash <64-hex> --channel moltbook --id <post-id-or-url>`

## Ledgers (workspace state)
- Append-only: `state/lygo_mint_ledger.jsonl`
- Canonical (dedup): `state/lygo_mint_ledger_canonical.json`

## References
- Core template: `reference/CHAMPION_PROMPT_CORE_TEMPLATE_V1.md`
- Publish checklist: `reference/CHAMPION_PACK_PUBLISH_CHECKLIST.md`
