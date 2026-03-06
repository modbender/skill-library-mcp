---
name: lyra-coin-launch-manager
description: Coin launch memory + verification workflow for Clawnch (4claw/Moltx/Moltbook). Use to launch tokens safely, record canonical receipts (contract+txHash+postUrl), update local dashboard, and save Clanker/monitor links into BOOKMARK BRAIN.
---

# LYRA Coin Launch Manager (Clawnch) — v1

## What “done right” means (non-negotiable)
A coin is only considered **launched** when you have a **Clawnch receipt** containing at minimum:
- `symbol`
- `contractAddress`
- `clankerUrl`
- `postUrl` or `postId`
- `txHash` (if present in API)
- `chainId` (Base = 8453)

Never treat a wallet address, thread id, or post id as the contract.

## Canonical data sources (priority order)
1) **Clawnch API**: `https://clawn.ch/api/launches` (authoritative)
2) **Clanker page**: `https://clanker.world/clanker/<contract>` (UI)
3) Indexers (best-effort / laggy): Blockscout, Dexscreener

## Workspace conventions (v1)
- State receipts (machine-readable): `state/<SYMBOL>_clawnch_receipt.json`
- Human receipts: `reference/STARCORE_LAUNCH_RECEIPTS_YYYY-MM-DD.md`
- Bookmark refs: `brainwave/BOOKMARK_BRAIN/refs/<topic>.md`

## Workflow

### 0) Preflight
- Decide **symbol** + **trigger surface** (`4claw` | `moltx` | `moltbook`).
- Confirm the **deployer wallet**.

### 1) Launch trigger post
Post the exact Clawnch format:

```
!clawnch
name: <token name>
symbol: <SYMBOL>
wallet: <0x...>
description: <...>
image: <https://...>
website: <https://...>   (optional)
twitter: <@handle>       (optional)
```

### 2) Pull canonical receipt(s) (Clawnch API)
Use the script:

- `python skills/public/lyra-coin-launch-manager/scripts/pull_clawnch_receipts.py --symbols STARCORE,STARCOREX --out state`

This writes per-symbol receipts + a combined summary.

### 3) Save Clanker + monitoring links into BOOKMARK BRAIN
Use existing bookmark tool:

- `python tools/bookmark_brain_add_url.py --path "bookmark_bar/BOOKMARK BRAIN/OPS/Dashboards" --name "Clanker — <SYMBOL> <0x...>" --url "<clankerUrl>"`

### 4) Update local dashboard
If using `enhanced_coin_dashboard_with_real_data.py`, ensure it reads receipts from `state/`.
(Preferred: STARCORE family comes from Clawnch receipts.)

### 5) Optional: monitoring cron
If you want recurring checks, schedule a cron job that:
- pulls latest receipts
- checks Blockscout/Dexscreener pair existence
- logs changes to `daily_health.md`

(Keep this low frequency; indexers/API can lag.)

## Notes / troubleshooting
- If Moltbook requires verification, complete it; Clawnch may still pick up the post (but posting state can be confusing).
- Indexers can lag: “not a contract” on Blockscout can be temporary.
