# Dungeon Run Tracking

Track loot and progress across dungeon runs.

---

## Two Types of "Loot"

**1. Boons (in-run upgrades)** — Chosen after each room:
- UpgradeRock, UpgradePaper, UpgradeScissor (stat boosts)
- Heal (restore HP)
- These are temporary for the current run only

**2. Items (permanent rewards)** — Collected during runs:
- Scrap, Bolts, Pipes, etc.
- Added to inventory automatically
- Used for leveling, crafting, etc.

---

## Reading Loot Options

After defeating an enemy, check `lootOptions`:

```bash
curl https://gigaverse.io/api/game/dungeon/state \
  -H "Authorization: Bearer $JWT" | jq '.data.run.lootOptions'
```

Response:
```json
[
  {"boonTypeString": "UpgradeRock", "RARITY_CID": 1},
  {"boonTypeString": "Heal", "RARITY_CID": 0, "selectedVal1": 8},
  {"boonTypeString": "UpgradePaper", "RARITY_CID": 3}
]
```

### Displaying Loot Options

Format for humans:
```
Room 2 cleared! Choose loot:
1. ⚔️ Upgrade Sword (Uncommon)
2. 💚 Heal +8 HP (Common)
3. 🛡️ Upgrade Shield (Rare!)
```

Rarity mapping:
| RARITY_CID | Name | Emoji |
|------------|------|-------|
| 0 | Common | (none) |
| 1 | Uncommon | (none) |
| 2 | Rare | ! |
| 3 | Epic | !! |
| 4 | Legendary | 🔥 |
| 5+ | Mythic+ | 💎 |

---

## Tracking Inventory Changes

**Check inventory BEFORE and AFTER each run** to see what items were collected:

```bash
# Before run
curl https://gigaverse.io/api/items/balances \
  -H "Authorization: Bearer $JWT" > /tmp/inv-before.json

# ... complete run ...

# After run
curl https://gigaverse.io/api/items/balances \
  -H "Authorization: Bearer $JWT" > /tmp/inv-after.json

# Diff to see new items
```

### Item ID Reference

Common drop items:
| ID | Name | Rarity |
|----|------|--------|
| 2 | Dungeon Scrap | Common |
| 4 | Bolt | Uncommon |
| 5 | Steel Pipe | Uncommon |
| 22 | Fiber | Common |

See `references/items.md` for full list.

---

## Run Summary Format

After each run, display:

```
📊 RUN COMPLETE
━━━━━━━━━━━━━━━━━━━━━━
Result: ✅ Victory
Dungeon: Dungetron: 5000
Rooms: 4/4 (16 total)
Final HP: 8/12

Boons Collected:
- ⚔️ +2 Sword ATK (Epic)
- 💚 Heal +8 HP
- 🛡️ +1 Shield DEF

Items Collected:
- Dungeon Scrap x3
- Bolt x1
━━━━━━━━━━━━━━━━━━━━━━
```

### For Defeats:

```
💀 RUN ENDED
━━━━━━━━━━━━━━━━━━━━━━
Result: ❌ Died in Room 4 (Floor 1-4)
Enemy: Black Knight (HP: 1 remaining)
Final HP: 0/12

Boons Collected:
- ⚔️ +1 Sword ATK
- 🛡️ +2 Shield ATK (Rare)

Items Collected:
- Dungeon Scrap x2
━━━━━━━━━━━━━━━━━━━━━━
```

---

## Daily Tally Format

Keep a running tally in memory or a daily file:

```json
{
  "date": "2026-02-06",
  "runs": 3,
  "runResults": [
    { "result": "victory", "roomsCleared": 16, "loot": [{"id": 2, "name": "Dungeon Scrap", "qty": 5}] },
    { "result": "defeat", "roomsCleared": 7, "loot": [{"id": 22, "name": "Fiber", "qty": 2}] },
    { "result": "victory", "roomsCleared": 16, "loot": [{"id": 103, "name": "Crusader Head", "qty": 1, "rarity": 5, "RARE": true}] }
  ],
  "totalLoot": {
    "2": { "name": "Dungeon Scrap", "qty": 5 },
    "22": { "name": "Fiber", "qty": 2 },
    "103": { "name": "Crusader Head", "qty": 1, "rarity": 5 }
  },
  "rareFinds": [
    { "id": 103, "name": "Crusader Head", "rarity": 5, "run": 3 }
  ]
}
```

## Tracking Loot During Run

After each room/loot selection, the response includes `GAME_ITEM_ID_CID_array`:

```javascript
// From dungeon state or action response:
const itemIds = state.data.entity.GAME_ITEM_ID_CID_array;

// Map to names using item lookup
for (const id of itemIds) {
  const item = itemMap[id];
  if (item) {
    tally.totalLoot[id] = tally.totalLoot[id] || { name: item.name, qty: 0, rarity: item.rarity };
    tally.totalLoot[id].qty++;
    
    // Check for rare
    if (item.rarity >= 5) {
      notifyUser(`🔥 RARE LOOT: ${item.name} (Rarity ${item.rarity})`);
      tally.rareFinds.push({ id, name: item.name, rarity: item.rarity, run: tally.runs });
    }
  }
}
```

## Rare Item Alert

**Threshold:** `RARITY_CID >= 5`

When a rare item is found, immediately notify the user:

```
🔥 RARE LOOT FOUND!
Item: Crusader Head
Rarity: 5 (Legendary)
Run: #3 of today
Room: 4-4 (Final Boss)
```

## End of Run Summary

After each run completes (victory or defeat):

```
📊 RUN #3 COMPLETE

Result: ✅ Victory
Dungeon: Dungetron: 5000
Rooms Cleared: 16 (4-4)
Final HP: 8/12

Loot Collected:
- Dungeon Scrap x3
- Fiber x2
- 🔥 Crusader Head (Mythic)

Daily Total: 3 runs, 2 victories
```

## Daily Summary

At end of day or on request:

```
📊 DAILY DUNGEON SUMMARY - 2026-02-06

Runs: 5
Victories: 3 (60%)
Defeats: 2

Total Loot:
- Dungeon Scrap x12
- Fiber x8
- Wood x5
- 🔥 Crusader Head x1 (Mythic)
- 🔥 Aetherion Body x1 (Legendary)

Rare Finds: 2 items
Energy Used: ~200
Energy Remaining: 40/240
```

## State File Location

Store daily tracking in:
```
~/.config/gigaverse/runs/YYYY-MM-DD.json
```

Or in agent memory:
```
memory/gigaverse-YYYY-MM-DD.json
```
