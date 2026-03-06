# Gigaverse Enemy Reference

Data source: `GET https://gigaverse.io/api/offchain/static` → `.enemies`

## Enemy List

| ID | Name | HP | Shield | Notes |
|----|------|----|----|-------|
| 1 | Red Robe | 4 | 2 | Early game |
| 2 | Black Robe | 2 | 5 | |
| 3 | Black Knight | 6 | 4 | |
| 4 | Dark Guard | 9 | 6 | |
| 5 | Paladin | 12 | 8 | |
| 6 | Fanatic | 14 | 5 | |
| 7 | Forest Robe | 15 | 5 | |
| 8 | Crimson Knight | 10 | 15 | |
| 9 | White Knight | 17 | 10 | |
| 10 | Impkin | 18 | 14 | |
| 11 | Nocturne | 22 | 15 | |
| 12 | Azure Guard | 26 | 18 | |
| 13 | Gryndor | 30 | 20 | |
| 14 | Aetherion | 30 | 20 | |
| 15 | Zyren | 30 | 20 | |
| 16 | Crusader | 48 | 30 | **Boss** - drops loot |
| 17 | Overseer | 48 | 30 | **Boss** - drops loot |
| 18 | Athena | 48 | 30 | **Boss** - drops loot |
| 19 | Archon | 48 | 30 | **Boss** - drops loot |
| 20 | Foxglove | 48 | 30 | **Boss** - drops loot |
| 21 | Summoner | 48 | 30 | **Boss** - drops loot |
| 22 | Chobo | 48 | 30 | **Boss** - drops loot |
| 23 | Dirtmaw | 8 | 5 | Underhaul |
| 24 | Grubhusk | 12 | 7 | Underhaul |
| 25 | Gobwark | 15 | 8 | Underhaul |
| 26 | Azure Aetherion | 20 | 12 | Underhaul - drops loot |
| 27 | Crimson Aetherion | 20 | 12 | Underhaul - drops loot |
| 28 | Bulwark | 24 | 12 | Underhaul |
| 29 | Ratsnout | 26 | 15 | Underhaul |
| 30 | Dighusk | 28 | 17 | Underhaul |
| 31 | Azure Gryndor | 28 | 18 | Underhaul - drops loot |
| 32 | Crimson Gryndor | 22 | 16 | Underhaul - drops loot |
| 33 | Minktrap | 26 | 20 | Underhaul |
| 34 | Ironhusk | 40 | 14 | Underhaul |
| 35 | Grimwark | 28 | 30 | Underhaul |
| 36 | Azure Zyren | 36 | 30 | Underhaul - drops loot |
| 37 | Crimson Zyren | 32 | 24 | Underhaul - drops loot |
| 38 | Skeltin | 35 | 35 | |
| 39 | Crimson Impkin | 35 | 38 | |
| 40 | Bryophytus | 40 | 45 | |
| 41 | Hand Of Bekda | 1 | 200 | **Special** |
| 42 | Gigian Dirtmaw | 6 | 2 | Gigian variant |
| 43 | Gigian Guard | 6 | 3 | |
| 44 | Gigian Knight | 8 | 2 | |
| 45 | Gigian Robe | 8 | 3 | |
| 46 | Gigian Paladin | 9 | 2 | |
| 47 | Gigian Impkin | 9 | 1 | |
| 48 | Gigian Fanatic | 12 | 4 | |
| 49 | Gigian Gobwark | 12 | 4 | |
| 50 | Gigian Skeltin | 14 | 0 | |
| 51 | Gigian Grubhusk | 14 | 3 | |
| 52 | Gigian Gryndor | 16 | 4 | |
| 53 | Gigian Nocturne | 16 | 4 | |
| 54 | Gigian Bryophytus | 19 | 4 | |
| 55 | Gigian Aetherion | 22 | 5 | |
| 56 | Gigian Zyren | 22 | 5 | |
| 57 | Garnish | 28 | 8 | |
| 58 | Char | 28 | 8 | |
| 59 | Bunyoo | 28 | 8 | |
| 60 | Dith | 28 | 8 | |
| 61 | Aiz | 28 | 8 | |
| 62 | Harambe | 28 | 8 | |

## Getting Enemy Name from State

The dungeon state returns `ENEMY_CID` which maps to enemy ID:

```javascript
// From state: entity.ENEMY_CID = 3
// Lookup: Enemy#3 → "Black Knight"

const enemyNames = {
  1: 'Red Robe',
  2: 'Black Robe', 
  3: 'Black Knight',
  // ... etc
};

const enemyName = enemyNames[state.data.entity.ENEMY_CID];
```

## Fetching Full Enemy Data

```bash
curl -s "https://gigaverse.io/api/offchain/static" | jq '.enemies'
```

Response includes:
- `ID_CID` - Enemy ID
- `NAME_CID` - Enemy name
- `MOVE_STATS_CID_array` - [rockATK, rockDEF, paperATK, paperDEF, scissorATK, scissorDEF, HP, Shield]
- `LOOT_ID_CID` - Loot drop ID (0 = no special loot)
