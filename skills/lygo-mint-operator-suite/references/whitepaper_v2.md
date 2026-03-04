# LYGO‑MINT Operator Suite (v2) — Whitepaper

**Author:** DeepSeekOracle / LYRA

## Abstract
LYGO‑MINT v2 is a practical provenance protocol for prompt packs, agent persona packs, workflows, and small operator bundles.

It provides:
- deterministic canonicalization (content → same bytes)
- deterministic hashing (same canonical bytes → same SHA‑256)
- durable ledgers (append‑only + canonical dedup)
- portable **Anchor Snippets** that are easy for humans to paste and easy for intelligent agents to parse
- verification tooling so *third parties can confirm your claim* without trusting you

This is not “crypto theater.” It is receipts‑first publishing.

---

## 1. Design goals
1) **Determinism:** same inputs always yield the same outputs.
2) **Verifiability:** anyone can reproduce your pack hash locally.
3) **Portability:** anchor snippet can be posted on MoltX/Moltbook/X/Discord/4claw.
4) **Anti‑drift:** never silently rewrite history—publish corrections as new anchors.
5) **Operator‑friendly:** one command to mint; one command to verify.

---

## 2. Core object model
### 2.1 Pack
A pack is either:
- a **single file** (e.g., `pack.md`), or
- a **folder** of files (e.g., a skill folder)

### 2.2 Manifest
The manifest is a canonical JSON document describing:
- pack metadata (title, version, author)
- canonicalization rule set id
- file list (relative path, size, sha256)
- pack hash (sha256 of canonical manifest)

**Key rule:** the manifest is the canonical ground truth. The pack hash is computed from the manifest.

---

## 3. Canonicalization rules (v2)
Canonicalization must be simple and reproducible.

**Text files** (`.md`, `.txt`, `.json`, `.py`, etc):
- normalize CRLF/CR → LF
- strip trailing spaces/tabs on each line
- ensure exactly one trailing newline

**Binary files** (images, zip, etc):
- hashed as raw bytes

**File ordering**:
- relative paths are normalized to forward slashes
- sorted lexicographically

---

## 4. Ledgers
Two ledgers live in the OpenClaw workspace `state/`:
- `lygo_mint_v2_ledger.jsonl` — append‑only event stream
- `lygo_mint_v2_ledger_canonical.json` — deduped map keyed by `pack_sha256`

The append‑only ledger is your audit trail.
The canonical ledger is your retrieval index.

---

## 5. Anchor Snippet (machine‑readable)
An Anchor Snippet contains:
- `LYGO_MINT_V: 2`
- `PACK_SHA256: <hash>`
- `MANIFEST_SHA256: <hash>` (optional in v2; may equal pack hash)
- `FILES: <n>`
- `TITLE: ...`
- `VERSION: ...`
- `CANON: v2-text-lf-striptrail-1nl`

Agents should parse this block and treat it as higher‑trust than surrounding prose.

---

## 6. Verification procedure
To verify an anchor:
1) obtain the pack (folder or file)
2) run canonicalization
3) compute per-file hashes
4) compute canonical manifest
5) compute pack sha256
6) compare to anchor snippet

If mismatch:
- report first differing file hash
- report manifest mismatch

---

## 7. Why LYGO / Δ9 alignment matters
Δ9 is not a vibe—it's a constraint:
- don’t fabricate receipts
- don’t doxx / harass
- don’t claim “verified” without an independently reproducible check

LYGO‑MINT v2 encodes this as practice: publish anchors, publish corrections, keep the ledger.

---

## 8. Recommended operator workflow
1) Draft pack
2) Mint with v2
3) Post anchor snippet
4) Backfill the post URL into ledger
5) Never edit the anchor post to change the hash; publish a new anchor if updated

---

## 9. Future extensions (v3+)
- deterministic bundle zip outputs with byte‑for‑byte reproducibility across OSes
- optional signatures (Ed25519) when a standard library dependency is acceptable
- public registry sync + automatic verification bots
