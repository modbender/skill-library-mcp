# Skills & Inventory Reference

## Overview

Noobs can level up skills by spending XP items. Each skill has multiple stats to allocate points into.

---

## Inventory

### Authenticated (Current User)

```bash
curl https://gigaverse.io/api/items/balances \
  -H "Authorization: Bearer $JWT"
```

Returns `entities[]` with item balances.

### Public Lookup (Any Wallet)

```bash
curl https://gigaverse.io/api/indexer/player/gameitems/0xADDRESS
```

No JWT required. Returns onchain balances.

---

## Skills

### Get Skill Definitions

```bash
curl https://gigaverse.io/api/offchain/skills
```

No JWT required. Returns all skills with:
- `docId` — Skill ID
- `GAME_ITEM_ID_CID` — XP item required for this skill
- `LEVEL_CID` — Max level
- `stats[]` — Stat definitions for allocation

### Get Noob's Skill Progress

```bash
curl https://gigaverse.io/api/offchain/skills/progress/NOOB_ID
```

No JWT required. Returns:
- `SKILL_CID` — Skill ID
- `LEVEL_CID` — Current skill level
- `LEVEL_CID_array` — Allocated stat levels per stat

---

## Level Up (Allocate Point)

```bash
curl -X POST https://gigaverse.io/api/game/skill/levelup \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "skillId": 1,
    "statId": 0,
    "noobId": 81087
  }'
```

**What happens:**
- Burns required XP item for next level
- Increments `LEVEL_CID`
- Increments `LEVEL_CID_array[statId]`

---

## Level Down (Respec)

```bash
curl -X POST https://gigaverse.io/api/game/skill/leveldown \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "skillId": 1,
    "statId": 0,
    "noobId": 81087
  }'
```

**Requirements:**
- Skill must allow respec (`allowLevelDown`)
- Burns respec input item (`INPUT_ID_CID` / `INPUT_AMOUNT_CID`)
- Spends respec energy cost
- Refunds portion of XP based on skill config

---

## Preflight Checklist

Before leveling up/down:

1. **Get Noob ID:**
   ```bash
   curl https://gigaverse.io/api/game/account/0xADDRESS
   ```

2. **Get skill definitions:**
   ```bash
   curl https://gigaverse.io/api/offchain/skills
   ```

3. **Get current progress:**
   ```bash
   curl https://gigaverse.io/api/offchain/skills/progress/NOOB_ID
   ```

4. **Get inventory:**
   ```bash
   curl https://gigaverse.io/api/items/balances \
     -H "Authorization: Bearer $JWT"
   ```

5. **Verify XP/input balance** for intended operation

---

## Common Errors

| Error | Cause |
|-------|-------|
| `Noob not found for user` | Wallet hasn't minted a noob |
| `Noob does not belong to player` | noobId doesn't match JWT wallet |
| `Skill doesn't exist` | Invalid skillId |
| `Skill at max level` | Already maxed |
| `Skill at min level` | Can't respec below 0 |
| `Stat index out of bounds` | Invalid statId |
| Insufficient balance | Not enough XP items or respec items |

---

## Endpoints Summary

| Endpoint | Auth | Description |
|----------|------|-------------|
| `GET /items/balances` | JWT | Current user's inventory |
| `GET /indexer/player/gameitems/{address}` | None | Public inventory lookup |
| `GET /offchain/skills` | None | All skill definitions |
| `GET /offchain/skills/progress/{noobId}` | None | Noob's skill progress |
| `POST /game/skill/levelup` | JWT | Allocate skill point |
| `POST /game/skill/leveldown` | JWT | Respec skill point |
