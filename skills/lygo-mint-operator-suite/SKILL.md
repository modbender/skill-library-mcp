---
name: lygo-mint-operator-suite
description: "Advanced LYGO-MINT Operator Suite (v2): canonicalize *multi-file* packs, generate per-file + bundle hashes, write append-only + canonical ledgers, produce machine-readable multi-platform Anchor Snippets, and verify third-party packs. Built for LYGO operators who want dependable, receipts-first truth anchoring across MoltX/Moltbook/X/Discord/4claw."
---

# LYGO-MINT OPERATOR SUITE (v2)

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
All scripts are local and never print secrets.

### 1) Mint a pack (file OR folder) → manifest + hashes + ledgers + snippets
- `python scripts/mint_pack_v2.py --input reference/CHAMPION_PACK_LYRA_V1.md --title "LYRA Pack" --version 2026-02-09.v1`
- `python scripts/mint_pack_v2.py --input skills/public/lygo-champion-kairos-herald-of-time --title "KAIROS Pack" --version 2026-02-09.v1`

### 2) Verify a pack against an anchor snippet or a known hash
- `python scripts/verify_pack_v2.py --input ./some_pack_folder --pack-sha256 <hash>`

### 3) Create deterministic bundle (zip) for distribution
- `python scripts/bundle_pack_v2.py --input ./some_pack_folder --out tmp/pack.bundle.zip`

### 4) Generate multi-platform anchor snippets
- `python scripts/make_anchor_snippet_v2.py --pack-sha256 <hash> --title "..." --platform moltx`

### 5) Backfill anchors (post IDs/links)
- `python scripts/backfill_anchors.py --hash <64-hex> --channel moltbook --id <post-id-or-url>`

## Ledgers (workspace state)
- Append-only: `state/lygo_mint_ledger.jsonl`
- Canonical (dedup): `state/lygo_mint_ledger_canonical.json`

## References
- Core template: `reference/CHAMPION_PROMPT_CORE_TEMPLATE_V1.md`
- Publish checklist: `reference/CHAMPION_PACK_PUBLISH_CHECKLIST.md`
