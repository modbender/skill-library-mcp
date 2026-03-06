# Factions Reference

## Get Faction Data

```bash
curl https://gigaverse.io/api/factions/summary
```

Returns all factions with population stats.

---

## Faction List

| ID | Name | Notes |
|----|------|-------|
| 1 | **Crusader** | Most popular, highest activity |
| 2 | **Overseer** | |
| 3 | **Athena** | |
| 4 | **Archon** | Lowest activity |
| 5 | **Foxglove** | |
| 6 | **Summoner** | Second most active |
| 7 | **Chobo** | |

---

## Population Stats (from API)

| ID | Faction | Population | Active | Active % | Rank |
|----|---------|------------|--------|----------|------|
| 1 | Crusader | 18,313 | 3,658 | 20.06% | #1 |
| 6 | Summoner | 11,676 | 3,503 | 19.21% | #2 |
| 3 | Athena | 10,905 | 2,785 | 15.27% | #3 |
| 2 | Overseer | 6,812 | 2,312 | 12.68% | #4 |
| 7 | Chobo | 9,466 | 2,235 | 12.25% | #5 |
| 5 | Foxglove | 10,017 | 1,874 | 10.28% | #6 |
| 4 | Archon | 8,594 | 1,871 | 10.26% | #7 |

*Population data changes daily — fetch fresh data from the API.*

---

## Choosing a Faction

```bash
# Get current faction options
curl https://gigaverse.io/api/factions/summary | jq '[.entities[] | {id: .FACTION_CID, name: .NAME_CID, active: .data.activePopulation}]'

# Choose faction
curl -X POST https://gigaverse.io/api/factions/choose \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "factionId": 1,
    "expectedInputIds": [],
    "expectedInputAmounts": []
  }'

# Verify selection
curl https://gigaverse.io/api/factions/player/0xYOUR_ADDRESS
```

---

## Response Structure

```json
{
  "entities": [
    {
      "FACTION_CID": 1,
      "NAME_CID": "Crusader",
      "UINT256_CID": 18313,        // total population
      "MINT_COUNT_CID": 18553,     // total mints
      "BURN_COUNT_CID": -240,      // burns (negative)
      "data": {
        "activePopulation": 3658,
        "activePopulationPercentage": "20.06",
        "activityRank": 1,
        "dayPopulations": [...]    // daily history
      }
    }
  ]
}
```

---

## Quick Lookup (Agent Use)

```javascript
const FACTIONS = {
  1: "Crusader",
  2: "Overseer", 
  3: "Athena",
  4: "Archon",
  5: "Foxglove",
  6: "Summoner",
  7: "Chobo"
};

// Get faction name
const factionName = FACTIONS[factionId] || `Faction #${factionId}`;
```
