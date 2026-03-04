# Gigaverse Items Reference

Data source: `GET https://gigaverse.io/api/offchain/gameitems` → `.entities`

## Rarity Levels

| Rarity | Name | Alert |
|--------|------|-------|
| 1 | Common | - |
| 2 | Uncommon | - |
| 3 | Rare | - |
| 4 | Epic | - |
| 5 | **Legendary** | 🔥 Notify user |
| 6 | **Relic** | 🌟 Notify user |
| 7 | **Giga** | 💎 Notify user |

**Alert threshold:** `RARITY_CID >= 5`

## Notable Rare Items (Rarity ≥ 4)

### Legendary (5)
- Boss Head/Body (Crusader, Overseer, Athena, Archon, Foxglove, Summoner, Chobo)
- Bubble Nib, Warden Lamprey, Skellfin, Mobius Dickens
- Void Romling Head/Body
- Eggspeditor 5, USDC, Naughty Gift Box

### Relic (6)
- Seeker, Anemone, Geotle
- Garnish Head/Body, Char Head/Body, Dith Head/Body, Bunyoo Head/Body
- Aiz Head/Body, Harambe Head/Body
- Giga Romling Head/Body

### Giga (7)
- (Rarest tier - check for new additions)

## Fetching Item Data

```bash
# Get all items
curl -s "https://gigaverse.io/api/offchain/gameitems" | jq '.entities'

# Get item by ID
curl -s "https://gigaverse.io/api/offchain/gameitems" | jq '.entities[] | select(.ID_CID == 103)'
```

## Item Structure

```json
{
  "ID_CID": 103,
  "NAME_CID": "Crusader Head",
  "RARITY_CID": 5,
  "GAME_ITEM_TYPE_CID": 1,
  "OFFCHAIN_TYPE_CID": "equipment"
}
```

## Building Item Lookup Map

```javascript
async function buildItemMap() {
  const res = await fetch('https://gigaverse.io/api/offchain/gameitems');
  const data = await res.json();
  
  const items = {};
  for (const item of data.entities) {
    items[item.ID_CID] = {
      name: item.NAME_CID,
      rarity: item.RARITY_CID
    };
  }
  return items;
}

// Usage
const items = await buildItemMap();
const itemName = items[103]?.name; // "Crusader Head"
const isRare = items[103]?.rarity >= 4; // true
```
