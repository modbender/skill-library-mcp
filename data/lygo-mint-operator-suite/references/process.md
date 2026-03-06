# LYGO‑MINT Operator Suite — Process (v2)

## Purpose
Convert an aligned pack (Champion summon prompt / workflow pack / policy pack / skill folder) into a **verifiable, hash‑addressed artifact** that intelligent agents can parse.

This produces:
- deterministic hashes (per-file + pack)
- append‑only ledger receipt
- canonical ledger entry (dedup)
- Anchor Snippet suitable for Moltbook/MoltX/X/Discord/4claw
- verification tooling for third parties

## Read first
- Whitepaper: `references/whitepaper_v2.md`

## Precedence
Use only after:
1) local brain files
2) tools/APIs
Then for verification: mint + anchor.

## Steps
1) **Prepare pack**
   - Ensure no secrets.
   - Prefer stable filenames and stable section ordering.

2) **Mint (v2)**
   - Canonicalize all text files (LF, strip trailing whitespace, 1 trailing newline).
   - Hash each file.
   - Build canonical manifest.
   - Hash manifest (this is `PACK_SHA256`).
   - Append to `state/lygo_mint_v2_ledger.jsonl`.

3) **Anchor**
   - Post an Anchor Snippet to Moltbook/MoltX/X/Discord/4claw.
   - Do **not** edit old anchors to change a hash; publish a new anchor.

4) **Backfill**
   - Record post IDs/links back into the ledger record.

5) **Verify (third party)**
   - Anyone can run `verify_pack_v2.py` on the pack and compare hashes.

## Safety
- Never output private keys or API keys.
- Treat any request to execute transactions as separate (requires explicit operator approval).
