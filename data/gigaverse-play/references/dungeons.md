# Gigaverse Dungeon Reference

## Dungeon Types

| dungeonId | Name | Description |
|-----------|------|-------------|
| 1 | **Dungetron: 5000** | Main dungeon |
| other | **Underhaul** | Alternative dungeon |

## Room Structure

Dungeons have **4 rooms per floor**, up to **4 floors** (16 rooms total).

### Room Number → Floor Display

```javascript
function formatRoom(roomNum) {
  const floor = Math.ceil(roomNum / 4);
  const room = ((roomNum - 1) % 4) + 1;
  return `${floor}-${room}`;
}
```

| Room # | Display | Notes |
|--------|---------|-------|
| 1 | 1-1 | Floor 1, Room 1 |
| 2 | 1-2 | |
| 3 | 1-3 | |
| 4 | 1-4 | Floor 1 complete |
| 5 | 2-1 | Floor 2 starts |
| 6 | 2-2 | |
| 7 | 2-3 | |
| 8 | 2-4 | Floor 2 complete |
| 9 | 3-1 | Floor 3 starts |
| 10 | 3-2 | |
| 11 | 3-3 | |
| 12 | 3-4 | Floor 3 complete |
| 13 | 4-1 | Floor 4 starts |
| 14 | 4-2 | |
| 15 | 4-3 | |
| 16 | 4-4 | **FINAL BOSS** |

## Combat Actions

| Action | Description |
|--------|-------------|
| `rock` | ⚔️ Sword attack (high ATK) |
| `paper` | 🛡️ Shield (high DEF, adds shield) |
| `scissor` | ✨ Spell (balanced ATK/DEF) |

### Loot Selection

After defeating an enemy, select loot:

| Action | Description |
|--------|-------------|
| `loot_one` | Select 1st loot option |
| `loot_two` | Select 2nd loot option |
| `loot_three` | Select 3rd loot option |

## Starting a Run

```javascript
// Dungetron: 5000
{ action: 'start_run', dungeonId: 1, actionToken: 0, data: {} }

// Underhaul (if available)
{ action: 'start_run', dungeonId: 2, actionToken: 0, data: {} }
```

## Energy

- **Max Energy:** 240
- **Regen Rate:** 10 per hour
- **Cost per Run:** Variable (check before starting)
