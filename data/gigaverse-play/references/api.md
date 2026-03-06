# Gigaverse API Reference

**Base URL:** `https://gigaverse.io/api`

**Authentication:** Bearer token in Authorization header

```bash
curl https://gigaverse.io/api/endpoint \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Endpoint Map

### Authentication & Account
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/user/auth` | POST | No | Exchange signed message for JWT |
| `/user/me` | GET | Yes | Verify session |
| `/game/account/{address}` | GET | No | Check noob, username, canEnterGame |
| `/indexer/usernameAvailable/{name}` | GET | Yes | Check username + get mint signature |
| `/factions/summary` | GET | No | List faction options |
| `/factions/choose` | POST | Yes | Select faction |
| `/factions/player/{address}` | GET | No | Check faction selection |

### Dungeon
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/offchain/player/energy/{address}` | GET | No | Read current energy state |
| `/offchain/static` | GET | No | Static game data (enemies, items, etc.) |
| `/game/dungeon/today` | GET | Yes | Dungeon definitions, costs, requirements |
| `/game/dungeon/state` | GET | Yes | Current active run state |
| `/game/dungeon/action` | POST | Yes | Start run and submit moves |

### Inventory & Skills
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/items/balances` | GET | Yes | Current user's item inventory |
| `/indexer/player/gameitems/{address}` | GET | No | Public inventory lookup |
| `/offchain/skills` | GET | No | All skill definitions |
| `/offchain/skills/progress/{noobId}` | GET | No | Noob's skill progress |
| `/game/skill/levelup` | POST | Yes | Allocate skill point |
| `/game/skill/leveldown` | POST | Yes | Respec skill point |

### GigaJuice
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/gigajuice/player/{address}` | GET | No | Check juice status, listings, offerings |

See [juice.md](juice.md) for full GigaJuice documentation.

### Dungeon Types
| dungeonId | Name |
|-----------|------|
| 1 | Dungetron: 5000 |
| other | Underhaul |

> **Note:** See [onboarding.md](onboarding.md) for new player setup flow.

---

## 1) Authentication

Exchange a wallet signature for a JWT token using SIWE-style signing.

### Message Format

**EXACT format required:**
```
Login to Gigaverse at <timestamp>
```

The timestamp (unix milliseconds) must match in both the message AND the JSON payload.

### Request

```bash
curl -X POST https://gigaverse.io/api/user/auth \
  -H "Content-Type: application/json" \
  -d '{
    "signature": "0x...",
    "address": "0xYourAddress",
    "message": "Login to Gigaverse at 1730000000000",
    "timestamp": 1730000000000,
    "agent_metadata": {
      "type": "gigaverse-play-skill",
      "model": "claude-opus-4.5"
    }
  }'
```

### Agent Metadata (Required for Skill Users)

When authenticating via this skill, **always include `agent_metadata`**:

| Field | Value | Notes |
|-------|-------|-------|
| `type` | `"gigaverse-play-skill"` | Always use this exact value |
| `model` | Your model name | e.g. `"claude-opus-4.5"`, `"gpt-4"`, or `"unknown"` |

This helps track skill adoption and agent diversity in the Gigaverse.

### Response

```json
{
  "jwt": "eyJ...",
  "gameAccount": {...},
  "expiresAt": 1730086400000
}
```

### Validation Rules

- Message must include timestamp
- Signature must verify for address
- Do NOT change message text, spacing, or timestamp between signing and request

---

## 2) Verify Session

Confirm identity and check game access.

```bash
curl https://gigaverse.io/api/user/me \
  -H "Authorization: Bearer YOUR_JWT"
```

Check the `canEnterGame` field in response.

---

## 3) Check Energy & Entry Cost

### Get Player Energy

```bash
curl https://gigaverse.io/api/offchain/player/energy/0xYourAddress
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

### Get Dungeon Metadata

```bash
curl https://gigaverse.io/api/game/dungeon/today \
  -H "Authorization: Bearer YOUR_JWT"
```

Response includes:
- `dungeonDataEntities`: dungeon definitions
  - `ID_CID`: dungeon identifier
  - `ENERGY_CID`: base energy cost
  - `entryData[]`: tiered item requirements (if any)
  - `dungeonDisabled`: whether dungeon is available
- `dayProgressEntities`: daily run counters

### Energy Cost Calculation

- Final run energy = dungeon energy + system divisor
- Juiced runs: multiply cost by 3 (`runMultiplier = 3`)
- If `entryData` exists, required items will be burned

---

## 4) Dungeon Actions

All dungeon actions use `POST /game/dungeon/action` with bearer token.

### ⚠️ IMPORTANT: Action Token Handling

Every response returns a new `actionToken`. You MUST use this token for your next action.

```
Request 1: actionToken: 0  →  Response: actionToken: 1
Request 2: actionToken: 1  →  Response: actionToken: 2
Request 3: actionToken: 2  →  Response: actionToken: 3
...
```

**Rules:**
- Always persist the returned `actionToken`
- Server rejects stale/mismatched tokens (~5s anti-spam window)
- If you get "Invalid action token", call `/game/dungeon/state` to resync

### Start a Run

```bash
curl -X POST https://gigaverse.io/api/game/dungeon/action \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "start_run",
    "dungeonId": 1,
    "actionToken": 0,
    "data": {
      "consumables": [],
      "isJuiced": false,
      "index": 0
    }
  }'
```

Parameters:
- `dungeonId`: which dungeon to enter
- `isJuiced`: true for 3x cost/rewards (requires player juiced status)
- `index`: entry tier (for dungeons with `entryData` tiers)
- `consumables`: items to bring into dungeon

### Combat Moves (Rock Paper Scissors)

```bash
curl -X POST https://gigaverse.io/api/game/dungeon/action \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "rock",
    "dungeonId": 1,
    "actionToken": LATEST_TOKEN,
    "data": {}
  }'
```

Actions: `rock` (⚔️ Sword), `paper` (🛡️ Shield), `scissor` (✨ Spell)

### Loot Selection

After defeating enemies, choose loot:

```bash
curl -X POST https://gigaverse.io/api/game/dungeon/action \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "loot_one",
    "dungeonId": 1,
    "actionToken": LATEST_TOKEN,
    "data": {}
  }'
```

Actions: `loot_one`, `loot_two`, `loot_three`, `loot_four`

### Other Actions

| Action | Purpose | Data Required |
|--------|---------|---------------|
| `use_item` | Use a consumable item | Yes |
| `heal_or_damage` | Heal self or deal damage | Yes |
| `flee` | Escape current encounter | No |
| `cancel_run` | Abandon dungeon run | No |

---

## Get Current Run State

```bash
curl https://gigaverse.io/api/game/dungeon/state \
  -H "Authorization: Bearer YOUR_JWT"
```

Returns current room, enemies, HP, available actions.

---

## Rate Limits

*TBD*

---

## Debug Checklist

| Error | Cause | Fix |
|-------|-------|-----|
| `401 No token provided` | Missing Authorization header | Add `Authorization: Bearer <jwt>` |
| `401 Invalid token` | Expired or malformed JWT | Re-run auth flow |
| `Invalid signature` | Message/timestamp mismatch | Ensure signed message matches JSON exactly |
| `Already in dungeon` | Active run exists | Call `/game/dungeon/state` first |
| `Dungeon does not have tier X` | Invalid `data.index` | Check dungeon's `entryData` tiers |
| `Not enough usable item slots` | Bad consumables array | Adjust consumables/entry items |
| `Invalid action token` | Stale token | Use latest token from response, or resync via `/game/dungeon/state` |
| `Player not juiced` | `isJuiced: true` but player lacks status | Set `isJuiced: false` or get juiced status |

## Response Format

Success:
```json
{
  "success": true,
  "actionToken": 5,
  "data": {...}
}
```

Error:
```json
{
  "success": false,
  "error": "Description"
}
```
