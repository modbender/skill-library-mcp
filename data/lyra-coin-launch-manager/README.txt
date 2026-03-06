LYRA Coin Launch Manager (Clawnch) — Quick README
=================================================

Purpose:
- Manage STARCORE-family launches on Clawnch (4claw/Moltx/Moltbook)
- Always anchor to Clawnch receipts (contractAddress + clankerUrl + post/postId + chainId)
- Save canonical receipts to state/, human summaries to reference/, and monitoring links to BOOKMARK BRAIN.

Key idea:
- Works for any agent, but includes LYGO-aligned defaults (folders, naming). If your folder layout differs, adapt the paths or pass arguments (symbols, folder, receipts).

Core conventions (workspace):
- Machine receipts: state/<SYMBOL>_clawnch_receipt.json
- Combined summary: state/starcore_family_receipts_summary.json
- Human summary: reference/STARCORE_LAUNCH_RECEIPTS_<YYYY-MM-DD>.md
- Bookmarks: bookmark_bar/BOOKMARK BRAIN/OPS/Dashboards

Scripts (v1.1):
1) pull_clawnch_receipts.py
   - Pull Clawnch API launches for symbols
   - Writes per-symbol receipts + summary
   Usage:
     python skills/public/lyra-coin-launch-manager/scripts/pull_clawnch_receipts.py \
       --symbols STARCORE,STARCOREX,STARCORECOIN --out state

2) normalize_starcore_family.py
   - Normalizes local receipts + optional Clawnch API fills missing
   - Writes per-symbol receipts, summary JSON, and human MD summary
   Usage:
     python skills/public/lyra-coin-launch-manager/scripts/normalize_starcore_family.py \
       --symbols STARCORE,STARCOREX,STARCORECOIN

3) verify_starcore_family.py
   - Best-effort checks: Blockscout (is_contract), Dexscreener (pair existence)
   - Writes state/starcore_family_verify.json
   Usage:
     python skills/public/lyra-coin-launch-manager/scripts/verify_starcore_family.py \
       --symbols STARCORE,STARCOREX,STARCORECOIN

4) bookmark_starcore_family.py
   - Saves Clanker + Blockscout + Dexscreener links via tools/bookmark_brain_add_url.py
   - Default folder: bookmark_bar/BOOKMARK BRAIN/OPS/Dashboards
   Usage:
     python skills/public/lyra-coin-launch-manager/scripts/bookmark_starcore_family.py \
       --symbols STARCORE,STARCOREX,STARCORECOIN \
       --receipts state/starcore_family_receipts_summary.json \
       --folder "bookmark_bar/BOOKMARK BRAIN/OPS/Dashboards"

5) references/cron_template_starcore_family.md
   - Example low-frequency monitor sequence (normalize → verify → bookmark)
   - Adapt to your cron/job runner; keep intervals 10–30 minutes to avoid API/indexer noise.

What counts as "launched"?
- Clawnch receipt with contractAddress + clankerUrl + postId/postUrl + chainId (txHash if available). Wallets/posts/threads alone are NOT contracts.

If your folders differ:
- Pass custom --folder and --receipts; edit paths in scripts or copy them into your layout. The logic is portable; only paths are LYGO defaults.

Branding/alignment:
- Default symbols: STARCORE, STARCOREX, STARCORECOIN (LYGO/STARCORE family)
- LYGO-aligned but generic enough for any AI if you swap symbols/paths.

Safety:
- Clawnch API is authoritative. Indexers can lag; treat Blockscout/Dexscreener as best-effort verification.
