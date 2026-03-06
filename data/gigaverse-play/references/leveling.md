# Leveling Guide

Between dungeon runs, check for XP items (scrap) and level up your Noob's skills.

## Overview

- Each dungeon has its own skill tree and XP item
- Spending XP allocates points to stats (ATK, DEF, HP, Armor)
- Higher levels cost more XP (exponential scaling)
- Stats improve starting combat power for that dungeon

---

## Dungeons & XP Items

| Dungeon | Skill Name | XP Item ID | Item Name |
|---------|------------|------------|-----------|
| 1 | Dungetron 5000 | 2 | Dungeon Scrap |
| 2 | Gigus Dungeon | - | (disabled) |
| 3 | Dungetron Underhaul | 3 | (TBD) |

---

## Available Stats (Dungetron 5000)

| Stat ID | Name | Effect |
|---------|------|--------|
| 0 | Sword ATK | +1 starting Sword attack |
| 1 | Sword DEF | +1 starting Sword defense |
| 2 | Shield ATK | +1 starting Shield attack |
| 3 | Shield DEF | +1 starting Shield defense |
| 4 | Spell ATK | +1 starting Spell attack |
| 5 | Spell DEF | +1 starting Spell defense |
| 6 | Max HP | +2 starting max health |
| 7 | Max Armor | +1 starting max armor |

---

## Strategy-Based Allocation

Based on your combat strategy, prioritize different stats:

### 🗡️ Aggressive (Glass Cannon)
Priority: Sword ATK > Spell ATK > Shield ATK
- Maximize damage output
- Accept lower survivability
- Best for: Fast clears, skilled players

### 🛡️ Defensive (Tank)
Priority: Max HP > Max Armor > Shield DEF > Sword DEF
- Maximize survivability
- Accept slower fights
- Best for: New players, longer runs

### ⚖️ Balanced (Treasure Hunter)
Priority: Max HP > Sword ATK > Shield DEF > Spell ATK
- Mix of survivability and damage
- Well-rounded approach
- Best for: General use

### 🎲 Random (Chaos Agent)
Priority: Random distribution
- Unpredictable builds
- For experimentation only

---

## Pre-Run Leveling Check

**Before EVERY dungeon run**, agents should:

1. Check XP item balance:
```bash
curl https://gigaverse.io/api/items/balances \
  -H "Authorization: Bearer $JWT"
```

2. Check XP needed for next level:
```bash
curl https://gigaverse.io/api/offchain/skills
# Look at xpPerLvl array for your current level
```

3. If XP >= next level cost → Level up!

---

## Level Up Request

```bash
curl -X POST https://gigaverse.io/api/game/skill/levelup \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "skillId": 1,
    "statId": 6,
    "noobId": YOUR_NOOB_ID
  }'
```

Parameters:
- `skillId`: 1 = Dungetron 5000
- `statId`: 0-7 (see stat table above)
- `noobId`: Your Noob's ID

---

## XP Cost Table (Dungetron 5000)

| Level | XP Required | Cumulative |
|-------|-------------|------------|
| 1 | 11 | 11 |
| 2 | 14 | 25 |
| 3 | 18 | 43 |
| 4 | 22 | 65 |
| 5 | 25 | 90 |
| 6 | 29 | 119 |
| 7 | 33 | 152 |
| 8 | 37 | 189 |
| 9 | 41 | 230 |
| 10 | 45 | 275 |

*Level 10+ costs increase significantly (91+ per level)*

---

## Autonomous Behavior

In autonomous mode, agents should:

1. After each run, check scrap balance
2. If scrap >= next level cost:
   - Pick stat based on strategy config
   - Level up automatically
   - Log: "Leveled up! +1 Sword ATK (Level 3)"
3. Repeat until scrap < next level cost

### Stat Selection by Strategy

```javascript
function pickStat(strategy) {
  const priorities = {
    aggressive: [0, 4, 2, 6],  // Sword ATK, Spell ATK, Shield ATK, HP
    defensive: [6, 7, 3, 1],   // HP, Armor, Shield DEF, Sword DEF
    balanced: [6, 0, 3, 4],    // HP, Sword ATK, Shield DEF, Spell ATK
    random: () => Math.floor(Math.random() * 8)
  };
  // Rotate through priorities based on current level distribution
}
```

---

## Interactive Mode

If not autonomous, prompt user:

```
📊 LEVEL UP AVAILABLE!
XP: 25 scrap (need 18 for Level 3)

Choose stat to upgrade:
0: Sword ATK
1: Sword DEF
2: Shield ATK
3: Shield DEF
4: Spell ATK
5: Spell DEF
6: Max HP (+2)
7: Max Armor (+1)
```

---

## Check Current Progress

```bash
curl https://gigaverse.io/api/offchain/skills/progress/YOUR_NOOB_ID
```

Response:
```json
{
  "SKILL_CID": 1,
  "LEVEL_CID": 2,
  "LEVEL_CID_array": [1, null, null, null, null, null, 1]
}
```

This shows: Level 2, with +1 Sword ATK (stat 0) and +1 Max HP (stat 6).

---

## Respec (Optional)

To reallocate points (costs respec items):

```bash
curl -X POST https://gigaverse.io/api/game/skill/leveldown \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "skillId": 1,
    "statId": 0,
    "noobId": YOUR_NOOB_ID
  }'
```

Refunds 75% of XP spent.

---

## Integration with Run Loop

```
┌─────────────────┐
│ Check Energy    │
└────────┬────────┘
         │
    < 40 energy?
         │
    ┌────┴────┐
    │ YES     │ NO
    ▼         ▼
┌─────────┐ ┌─────────────┐
│ Wait    │ │ Check Scrap │
└─────────┘ └──────┬──────┘
                   │
              enough for level?
                   │
              ┌────┴────┐
              │ YES     │ NO
              ▼         ▼
         ┌─────────┐ ┌─────────────┐
         │Level Up │ │ Start Run   │
         └────┬────┘ └─────────────┘
              │
              └──► (repeat check)
```
