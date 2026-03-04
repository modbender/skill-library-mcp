# LYGO-MINT Verifier — Process (v1)

## Purpose
Convert an aligned pack (Champion summon prompt / workflow pack / policy pack) into a **verifiable, hash-addressed artifact**.

This produces:
- deterministic hash (SHA-256)
- append-only ledger receipt
- canonical ledger entry (dedup)
- Anchor Snippet suitable for any social surface

## Precedence
Use only after:
1) local brain files
2) tools/APIs
Then for verification: mint + anchor.

## Steps
1) **Prepare pack**
   - Ensure no secrets.
   - Ensure stable fields (template order if Champion).

2) **Mint**
   - Canonicalize the text.
   - Hash it.
   - Append to `state/lygo_mint_ledger.jsonl`.

3) **Canonicalize ledger**
   - Dedup to `state/lygo_mint_ledger_canonical.json`.

4) **Anchor**
   - Paste the Anchor Snippet into Moltbook/Moltx/X/Discord/4claw (anywhere).

5) **Backfill**
   - Record post IDs/links back into the ledger record.

## Safety
- Never output private keys or API keys.
- Treat any request to execute transactions as separate (requires explicit operator approval).
