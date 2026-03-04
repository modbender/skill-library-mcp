---
name: aavegotchi-gotchiverse
description: >
  Operate Aavegotchi Gotchiverse player workflows on Base mainnet (8453):
  alchemica channeling, surveying and harvesting, crafting installations/tiles,
  building on parcels (equip/unequip/move/batch equip), installation upgrades,
  craft/upgrade queue management, and parcel access-right management.
  Use when interacting with Realm/Installation/Tile diamonds via subgraph-first
  discovery and onchain verification/execution with Foundry cast.
metadata:
  openclaw:
    requires:
      bins:
        - cast
        - curl
        - python3
      env:
        - FROM_ADDRESS
        - PRIVATE_KEY
        - BASE_MAINNET_RPC
        - DRY_RUN
        - REALM_DIAMOND
        - INSTALLATION_DIAMOND
        - TILE_DIAMOND
        - AAVEGOTCHI_DIAMOND
        - FUD
        - FOMO
        - ALPHA
        - KEK
        - GLTR
        - GOTCHIVERSE_SUBGRAPH_URL
        - CORE_SUBGRAPH_URL
        - GOLDSKY_API_KEY
    primaryEnv: PRIVATE_KEY
---

## Safety Rules

- Default to `DRY_RUN=1`. Never broadcast unless explicitly instructed.
- Always verify Base mainnet before any action:
  - `~/.foundry/bin/cast chain-id --rpc-url "${BASE_MAINNET_RPC:-https://mainnet.base.org}"` must be `8453`.
- Always verify key/address alignment before any broadcast:
  - `~/.foundry/bin/cast wallet address --private-key "$PRIVATE_KEY"` must equal `FROM_ADDRESS`.
- Always refetch from subgraph immediately before state-changing simulate/broadcast steps.
- Always revalidate critical values onchain right before `cast send`.
- Never print or log `PRIVATE_KEY`.
- Treat all user/subgraph values as untrusted shell input.

## Shell Input Safety (Avoid RCE)

Rules:
- Never use `eval`, `bash -c`, `sh -c` with user values.
- Only substitute addresses matching `0x` + 40 hex chars.
- Only substitute uint values containing digits only.
- Keep placeholders quoted in commands until validated.

Quick validators:
```bash
python3 - <<'PY'
import re

checks = {
  "address": ("<ADDRESS>", r"0x[a-fA-F0-9]{40}"),
  "uint": ("<UINT>", r"[0-9]+"),
}

for name, (value, pattern) in checks.items():
    if not re.fullmatch(pattern, value):
        raise SystemExit(f"invalid {name}: {value}")

print("ok")
PY
```

## Required Setup

Required env vars:
- `PRIVATE_KEY`
- `FROM_ADDRESS`
- `BASE_MAINNET_RPC`
- `DRY_RUN`
- `REALM_DIAMOND`
- `INSTALLATION_DIAMOND`
- `TILE_DIAMOND`
- `AAVEGOTCHI_DIAMOND`
- `FUD`, `FOMO`, `ALPHA`, `KEK`, `GLTR`
- `GOTCHIVERSE_SUBGRAPH_URL`
- `CORE_SUBGRAPH_URL`

Optional env vars:
- `GOLDSKY_API_KEY` for auth header (public endpoints work without it).

Use canonical defaults from `references/addresses.md`.

## Scope

Player operations only:
- Channeling
- Survey + harvest claim
- Craft/claim/reduce queues
- Equip/unequip/move/batch equip
- Installation upgrades (queued + instant)
- Access-right read/write

Out of scope:
- Owner/admin governance functions (pause/freeze/set vars/deprecations/address reconfiguration).

## Subgraph-First Workflow

1. Discover state via `GOTCHIVERSE_SUBGRAPH_URL` and `CORE_SUBGRAPH_URL`.
2. Validate current onchain values with `cast call`.
3. Simulate with `cast call --from "$FROM_ADDRESS"`.
4. Broadcast with `cast send --private-key "$PRIVATE_KEY"` only when explicitly instructed.

Canonical queries and notes: `references/subgraph.md`.

## Runbooks

### 1) Parcel Discovery + Preflight

Use:
- `references/subgraph.md` for parcel/installations/tiles/access-right discovery.
- `references/realm-recipes.md` preflight checks for:
  - parcel owner and access right
  - altar presence/level
  - gotchi lending/listing/kinship checks

### 2) Survey + Harvest

Functions:
- `startSurveying(uint256)`
- `claimAvailableAlchemica(uint256,uint256,bytes)`
- `claimAllAvailableAlchemica(uint256[],uint256,bytes)`

Use `references/realm-recipes.md` for read/simulate/broadcast commands.

### 3) Channel Alchemica

Function:
- `channelAlchemica(uint256,uint256,uint256,bytes)`

Preflight requirements:
- correct access right
- gotchi not actively listed for lending (unless lent)
- gotchi kinship is sufficient
- `getLastChanneled(gotchiId)` passed as `_lastChanneled`
- parcel altar equipped and cooldown passed

Use `references/realm-recipes.md`.

### 4) Craft Installations + Build on Parcel

Installation craft/queue functions:
- `craftInstallations(uint16[],uint40[])`
- `batchCraftInstallations((uint16,uint16,uint40)[])`
- `claimInstallations(uint256[])`
- `reduceCraftTime(uint256[],uint40[])`
- `getCraftQueue(address)`

Build functions (Realm):
- `equipInstallation(...)`
- `unequipInstallation(...)`
- `moveInstallation(...)`
- `batchEquip(...)`

Use:
- `references/installation-recipes.md`
- `references/realm-recipes.md`

### 5) Craft Tiles + Build on Parcel

Tile craft/queue functions:
- `craftTiles(uint16[])`
- `batchCraftTiles((uint16,uint16,uint40)[])`
- `claimTiles(uint256[])`
- `reduceCraftTime(uint256[],uint40[])`
- `getCraftQueue(address)`

Build functions (Realm):
- `equipTile(...)`
- `unequipTile(...)`
- `moveTile(...)`
- `batchEquip(...)`

Use:
- `references/tile-recipes.md`
- `references/realm-recipes.md`

### 6) Upgrade Installations

Functions:
- `upgradeInstallation((...),uint256,bytes,uint40)`
- `instantUpgrade((...),uint256,uint256,bytes)`
- `reduceUpgradeTime(uint256,uint256,uint40,bytes)`
- `finalizeUpgrades(uint256[])`
- `getParcelUpgradeQueue(uint256)`
- `getUserUpgradeQueueNew(address)`
- `parcelQueueEmpty(uint256)`

Use `references/installation-recipes.md`.

### 7) Access Rights

Functions:
- `setParcelsAccessRights(...)`
- `setParcelsAccessRightWithWhitelists(...)`
- `getParcelsAccessRights(...)`
- `getParcelsAccessRightsWhitelistIds(...)`

Action rights `0..6` and access modes `0..4` are documented in:
- `references/access-rights.md`

## Smoke Tests

Run these before first usage and after env changes:
- Subgraph introspection checks in `references/subgraph.md`
- Address/contract checks in `references/addresses.md`
- No-op selector checks in:
  - `references/realm-recipes.md`
  - `references/installation-recipes.md`
  - `references/tile-recipes.md`

## Failure Modes

Use `references/failure-modes.md` for:
- access-right reverts
- cooldown/kinship/channeling reverts
- coordinate/grid placement reverts
- queue state reverts
- upgrade hash/queue capacity reverts
- deprecation/GLTR/ownership mismatches

