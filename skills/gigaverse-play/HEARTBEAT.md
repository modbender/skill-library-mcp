# Gigaverse Heartbeat

Check periodically for energy status and notify your human when ready to play.

## Add to Your Heartbeat

Add this to your `HEARTBEAT.md` or periodic task list:

```markdown
## Gigaverse Check (every 30 minutes)
If 30 minutes since last Gigaverse check:
1. Fetch energy status for configured wallet
2. If energy is full (or nearly full), notify human
3. Check XP balance — can we level up?
   - If autonomous: level up according to strategy
   - If interactive: notify human with options
4. Update lastGigaverseCheck timestamp
```

## Track State

Create or update your state file (e.g. `memory/heartbeat-state.json`):

```json
{
  "lastGigaverseCheck": null,
  "lastEnergyLevel": null,
  "lastNotifiedFull": null
}
```

## Check Energy

```bash
# Get current energy
curl https://gigaverse.io/api/offchain/player/energy/YOUR_ADDRESS
```

Response:
```json
{
  "entities": [{
    "parsedData": {
      "currentEnergy": 100,
      "maxEnergy": 100,
      "lastRegenTime": 1730000000
    }
  }]
}
```

## When to Notify

**Notify your human when:**
- Energy is at max (100%) and wasn't full last check
- Energy crossed 80% threshold since last check
- They haven't played in 24+ hours and have energy

**Don't spam:**
- Only notify once when energy fills up
- Don't notify if you already notified about full energy
- Respect quiet hours (late night)

## Example Notification

```
🎮 Gigaverse: Your energy is full! (100/100)
Ready for a dungeon run?
```

Or with more context:

```
⚔️ Dungeon energy recharged!
Energy: 100/100 (was 45 last check)
Time since last run: 6 hours

Ready to quest?
```

## Sample Check Logic

```javascript
async function checkGigaverseEnergy(address, lastState) {
  const response = await fetch(
    `https://gigaverse.io/api/offchain/player/energy/${address}`
  );
  const data = await response.json();
  const energy = data.entities?.[0]?.parsedData;
  
  if (!energy) return { notify: false };
  
  const { currentEnergy, maxEnergy } = energy;
  const percentage = (currentEnergy / maxEnergy) * 100;
  const wasFull = lastState.lastEnergyLevel >= maxEnergy;
  const isFull = currentEnergy >= maxEnergy;
  
  // Notify if just became full
  const shouldNotify = isFull && !wasFull && !lastState.lastNotifiedFull;
  
  return {
    notify: shouldNotify,
    currentEnergy,
    maxEnergy,
    percentage,
    message: shouldNotify 
      ? `🎮 Gigaverse: Energy full! (${currentEnergy}/${maxEnergy}) Ready to quest?`
      : null
  };
}
```

---

## Check for Level-Up

Between runs, check if the Noob can level up.

### 1. Get Current XP Balance

```bash
JWT=$(cat ~/.secrets/gigaverse-jwt.txt)
curl https://gigaverse.io/api/items/balances \
  -H "Authorization: Bearer $JWT" | jq '.entities[] | select(.ID_CID == "2") | .BALANCE_CID'
```

Item ID 2 = Dungeon Scrap (Dungetron 5000 XP)

### 2. Get Current Level & XP Cost

```bash
NOOB_ID=YOUR_NOOB_ID
curl https://gigaverse.io/api/offchain/skills/progress/$NOOB_ID
```

XP costs per level (Dungetron 5000):
| Level | XP Cost |
|-------|---------|
| 1 | 11 |
| 2 | 14 |
| 3 | 18 |
| 4 | 22 |
| 5 | 25 |

### 3. If XP >= Cost → Level Up!

**Autonomous mode:** Level up automatically based on strategy config.

```bash
# Get strategy from config
STRATEGY=$(jq -r '.combat' ~/.config/gigaverse/config.json)

# Pick stat based on strategy (see references/leveling.md)
# aggressive: 0 (Sword ATK), 4 (Spell ATK), 2 (Shield ATK)
# defensive: 6 (Max HP), 7 (Max Armor), 3 (Shield DEF)
# balanced: 6 (Max HP), 0 (Sword ATK), 3 (Shield DEF)

curl -X POST https://gigaverse.io/api/game/skill/levelup \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{"skillId": 1, "statId": CHOSEN_STAT, "noobId": YOUR_NOOB_ID}'
```

Log the result:
```
⬆️ Leveled up! +1 Max HP (now Level 3)
Scrap: 18 → 0
```

**Interactive mode:** Notify human with options.

```
📊 LEVEL UP AVAILABLE!
XP: 25 scrap (need 18 for Level 3)

Current stats: +1 Sword ATK, +1 Max HP

Choose stat to upgrade:
0: Sword ATK    4: Spell ATK
1: Sword DEF    5: Spell DEF
2: Shield ATK   6: Max HP (+2)
3: Shield DEF   7: Max Armor
```

### Sample Level Check Logic

```javascript
async function checkLevelUp(jwt, noobId, strategy) {
  // Get scrap balance
  const inv = await fetch('https://gigaverse.io/api/items/balances', {
    headers: { Authorization: `Bearer ${jwt}` }
  }).then(r => r.json());
  
  const scrap = inv.entities?.find(e => e.ID_CID === '2')?.BALANCE_CID || 0;
  
  // Get current level
  const progress = await fetch(
    `https://gigaverse.io/api/offchain/skills/progress/${noobId}`
  ).then(r => r.json());
  
  const currentLevel = progress.entities?.[0]?.LEVEL_CID || 0;
  
  // XP costs (first 10 levels)
  const xpCosts = [0, 11, 14, 18, 22, 25, 29, 33, 37, 41, 45];
  const nextCost = xpCosts[currentLevel + 1] || 999;
  
  if (scrap >= nextCost) {
    return {
      canLevel: true,
      scrap,
      currentLevel,
      nextCost,
      statToPick: pickStatByStrategy(strategy, progress)
    };
  }
  
  return { canLevel: false, scrap, currentLevel, nextCost };
}
```

See [references/leveling.md](references/leveling.md) for full strategy-to-stat mapping.

---

## Why This Matters

Energy regenerates over time. If you're not checking, your human might:
- Miss optimal play windows
- Waste capped energy that could be regenerating
- Forget about the game entirely

A gentle nudge when energy is full keeps them engaged without being annoying.

**Think of it like:** A gaming companion who says "Hey, you're charged up!" — helpful, not pushy. ⚔️
