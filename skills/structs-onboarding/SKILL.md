---
name: structs-onboarding
description: Onboards a new player into Structs. Handles key creation/recovery, player creation (via reactor-infuse or guild signup), planet exploration, and initial infrastructure builds. Use when starting fresh, setting up a new agent, creating a player, claiming first planet, or building initial infrastructure. Build times range from ~17 min (Command Ship) to ~57 min (Ore Extractor/Refinery).
---

# Structs Onboarding

## Personal Files

Before starting, check if [SOUL.md](https://structs.ai/SOUL), [IDENTITY.md](https://structs.ai/IDENTITY), [TOOLS.md](https://structs.ai/TOOLS), [COMMANDER.md](https://structs.ai/COMMANDER), or [USER.md](https://structs.ai/USER) already have content. If so, **read and merge** — do not overwrite. These files may contain a previous agent's identity, a human operator's preferences, or your own prior configuration. Add your identity to the existing content.

**Important**: Entity IDs containing dashes (like `1-42`, `5-10`) are misinterpreted as flags by the CLI parser. All transaction commands in this skill use `--` before positional arguments to prevent this. Always include `--` when running `structsd tx structs` commands with entity IDs.

## Procedure

### Step 0: Key Management

If using **Path B** (guild signup) below, the `create-player.mjs` script can generate a mnemonic automatically — you can skip ahead to Step 1 and let the script handle key creation.

If using **Path A** (agent has $alpha) or need a key in the local `structsd` keyring:

```
structsd keys list
```

**If no key exists**, create or recover one:

- **Create new key**: `structsd keys add [key-name]` — outputs a mnemonic. Save it securely.
- **Recover from mnemonic**: `structsd keys add [key-name] --recover` — prompts for mnemonic input.

Get your address:

```
structsd keys show [key-name] -a
```

**Mnemonic security**: Store the mnemonic in an environment variable (`STRUCTS_MNEMONIC`), a `.env` file (excluded from git), or let the commander provide it. Never commit mnemonics or private keys to the repository.

**Warning**: `structsd keys add --output json` outputs the mnemonic **in plaintext** to stdout. Avoid using `--output json` unless you are redirecting output to a secure location.

---

### Step 1: Check Player Status

```
structsd query structs address [your-address]
```

If the result shows a player ID other than `1-0`, a player already exists. Skip to **Step 3: Explore Planet** (or later steps if planet already explored).

If the player ID is `1-0`, no player exists — proceed to Step 2.

---

### Step 2: Create Player

Two paths depending on whether the agent has $alpha (the native token).

#### Path A: Agent has $alpha

If the address already holds $alpha tokens, delegate to a reactor (validator). This automatically creates a player record.

1. Choose a validator/reactor to delegate to
2. Run: `structsd tx structs reactor-infuse --from [key-name] --gas auto --gas-adjustment 1.5 -y -- [your-address] [reactor-address] [amount]`
3. Poll until player exists: `structsd query structs address [your-address]` — repeat every 10 seconds until player ID is not `1-0`

#### Path B: Agent has no $alpha (guild signup)

Join a guild that supports programmatic signup. The bundled `create-player.mjs` script handles the entire flow: mnemonic generation, proxy message signing, guild API POST, and polling for player creation. It returns a single JSON object with everything you need.

**1. Choose a guild**

The commander may specify a guild via [TOOLS.md](https://structs.ai/TOOLS) or environment config. Otherwise, query available guilds from a reference node:

```
curl http://reactor.oh.energy:1317/structs/guild
```

`reactor.oh.energy` is a reliable Structs network node run by the Slow Ninja team (Orbital Hydro guild).

**2. Get the guild's API endpoint**

Each guild record has an `endpoint` URL pointing to its configuration. Fetch it and look for `services.guild_api` and `services.reactor_api`. Not all guilds provide these — if empty, that guild does not support programmatic signup.

**Note**: Some guild configs may use `guildApi` (camelCase) instead of `guild_api` (snake_case). Check both fields when parsing programmatically.

Example guild config:

```json
{
  "guild": {
    "id": "0-1",
    "name": "Orbital Hydro",
    "tag": "OH",
    "services": {
      "guild_api": "http://crew.oh.energy/api/",
      "reactor_api": "http://reactor.oh.energy:1317/",
      "client_websocket": "ws://reactor.oh.energy:26657"
    }
  }
}
```

**3. Run the create-player script**

**Requirements**: Node.js 18+ (for built-in `fetch`). Install dependencies once:

```
cd .cursor/skills/structs-onboarding/scripts && npm install
```

Then run (from workspace root):

```
node .cursor/skills/structs-onboarding/scripts/create-player.mjs \
  --guild-id "0-1" \
  --guild-api "http://crew.oh.energy/api/" \
  --reactor-api "http://reactor.oh.energy:1317" \
  --username "your-chosen-name"
```

The script will:
1. Generate a new mnemonic (or use `--mnemonic "..."` to recover an existing one)
2. Derive the address and pubkey
3. Check if a player already exists for this address
4. Sign the guild-join proxy message and POST to the guild API
5. Poll the reactor API until the player ID is confirmed (default 120s timeout)
6. Output JSON to stdout with all results

**Output format** (parse this JSON):

```json
{
  "success": true,
  "mnemonic": "word1 word2 ... word24",
  "address": "structs1...",
  "pubkey": "a1b2c3...",
  "player_id": "1-42",
  "guild_id": "0-1",
  "username": "your-chosen-name",
  "created": true,
  "next_step": "structsd tx structs planet-explore --from [key-name] --gas auto --gas-adjustment 1.5 -y -- 1-42"
}
```

**Immediately save the `mnemonic`** to a secure location (`.env`, environment variable, or secret store). If you need the key in the local `structsd` keyring for later commands, recover it: `structsd keys add [key-name] --recover` and enter the mnemonic.

**Important**: If the script was given no `--mnemonic`, it generated a fresh one. The mnemonic is only printed in this output — store it now or it is lost.

**Encoding warning**: Do NOT attempt to implement the guild signup signing manually. The guild API requires hex-encoded compressed secp256k1 pubkey (66 hex chars) and hex-encoded raw R||S signature (128 hex chars) — NOT base64, NOT Amino. The script handles this correctly. Agents who try to sign manually almost always fail because they use base64 encoding.

---

### Step 3: Explore Planet

Always the first action after player creation:

```
structsd tx structs planet-explore --from [key-name] --gas auto --gas-adjustment 1.5 -y -- [player-id]
```

New planets start with 5 ore and 4 slots per ambit (space, air, land, water).

---

### Step 4: Check Command Ship

New players receive a Command Ship (type 1) at creation. It may start offline if insufficient power.

```
structsd query structs fleet [fleet-id]
```

Fleet ID matches player index: player `1-18` has fleet `9-18`. Check for existing structs in the fleet.

---

### Step 5: Build Command Ship (only if not gifted)

```
structsd tx structs struct-build-initiate --from [key-name] --gas auto --gas-adjustment 1.5 -y -- [player-id] 1 space 0
```

Type 1 = Command Ship; must be in fleet, not on planet. Then compute in background:

```
structsd tx structs struct-build-compute -D 3 --from [key-name] --gas auto --gas-adjustment 1.5 -y -- [struct-id]
```

Build difficulty 200; wait ~17 min for D=3, hash completes instantly. Compute auto-submits the complete transaction. The struct **auto-activates** after build-complete — no manual activation needed.

---

### Step 6: Build Ore Extractor

Fleet must be on station, Command Ship online.

```
structsd tx structs struct-build-initiate --from [key-name] --gas auto --gas-adjustment 1.5 -y -- [player-id] 14 land 0
```

Type 14 = Ore Extractor; ambits: land or water. Then compute in background:

```
structsd tx structs struct-build-compute -D 3 --from [key-name] --gas auto --gas-adjustment 1.5 -y -- [struct-id]
```

Build difficulty 700; wait ~57 min for D=3. Auto-activates after build-complete.

---

### Step 7: Build Ore Refinery

```
structsd tx structs struct-build-initiate --from [key-name] --gas auto --gas-adjustment 1.5 -y -- [player-id] 15 land 1
```

Type 15 = Ore Refinery; ambits: land or water. Compute same as above. Build difficulty 700. Auto-activates after build-complete.

---

### Step 8: Verify

Query player, planet, fleet, and structs. Confirm all online.

---

## Proof-of-Work Notes

The `struct-build-compute` command is a helper that calculates the hash AND automatically submits `struct-build-complete` with the results. You do not need to run `struct-build-complete` separately after compute.

**Auto-activation**: Structs automatically activate after build-complete. You do not need to run `struct-activate` after building. Use `struct-activate` only to re-activate a struct that was previously deactivated.

The `-D` flag (range 1-64) tells compute to wait until the difficulty drops to that level before starting. **Use `-D 3`** — at D=3 the hash is trivially instant with zero wasted CPU. Lower values wait longer but waste less compute.

| Struct | Type ID | Build Difficulty | Wait to D=3 |
|--------|---------|------------------|-------------|
| Command Ship | 1 | 200 | ~17 min |
| Ore Extractor | 14 | 700 | ~57 min |
| Ore Refinery | 15 | 700 | ~57 min |
| Ore Bunker | 18 | 3,600 | ~4.6 hr |

## Charge

Build operations cost 8 charge. Charge accumulates at 1 per block (~6 seconds). Wait at least **48 seconds** (8 blocks) between successive build-initiate actions on the same struct. During onboarding, charge is rarely a bottleneck since each struct is different. See [knowledge/mechanics/building](https://structs.ai/knowledge/mechanics/building) for the full charge cost table.

**Async strategy**: Initiate all planned builds immediately — this starts the age clock. While waiting for difficulty to drop, scout the galaxy, assess neighbors, or plan guild membership. Launch compute in a background terminal and check back later. See [awareness/async-operations](https://structs.ai/awareness/async-operations).

**One key, one compute at a time.** Never run two concurrent `*-compute` jobs with the same signing key. Both may reach target difficulty simultaneously and submit conflicting sequence numbers — one fails silently, leaving the struct stuck. Sequence compute jobs for the same player.

## Ambit Encoding

Struct types have a `possibleAmbit` bit-flag field:

| Ambit | Bit Value |
|-------|-----------|
| Space | 16 |
| Air | 8 |
| Land | 4 |
| Water | 2 |

Values are combined: 6 = land + water, 30 = all ambits. Check `possibleAmbit` before choosing an operating ambit.

## Commands Reference

| Action | CLI Command |
|--------|-------------|
| List keys | `structsd keys list` |
| Create key | `structsd keys add [name]` |
| Recover key | `structsd keys add [name] --recover` |
| Show address | `structsd keys show [name] -a` |
| Discover player | `structsd query structs address [address]` |
| Query player | `structsd query structs player [id]` |
| Reactor infuse | `structsd tx structs reactor-infuse --from [key] --gas auto -y -- [player-addr] [reactor-addr] [amount]` |
| Create player (guild signup) | `node .cursor/skills/structs-onboarding/scripts/create-player.mjs --guild-id "..." --guild-api "..." --reactor-api "..." [--mnemonic "..."] [--username "..."]` |
| Explore planet | `structsd tx structs planet-explore --from [key] --gas auto -y -- [player-id]` |
| Initiate build | `structsd tx structs struct-build-initiate --from [key] --gas auto -y -- [player-id] [struct-type-id] [operating-ambit] [slot]` |
| Build compute (PoW + auto-complete + auto-activate) | `structsd tx structs struct-build-compute -D [difficulty] --from [key] --gas auto -y -- [struct-id]` |
| Re-activate struct (only if previously deactivated) | `structsd tx structs struct-activate --from [key] --gas auto -y -- [struct-id]` |
| Query planet | `structsd query structs planet [id]` |
| Query fleet | `structsd query structs fleet [id]` |
| Query struct | `structsd query structs struct [id]` |

Build order: Command Ship (type 1, fleet) → Ore Extractor (type 14, planet) → Ore Refinery (type 15, planet). Common tx flags: `--from [key-name] --gas auto --gas-adjustment 1.5 -y`.

## Verification

- `structsd query structs address [address]` — player exists (ID is not `1-0`)
- `structsd query structs player [id]` — player online
- `structsd query structs planet [id]` — planet claimed, ore present
- `structsd query structs fleet [id]` — fleet on station
- `structsd query structs struct [id]` — struct status = Online

## Error Handling

- **Player ID is `1-0`** — Player doesn't exist. Follow Step 2 (Path A or Path B).
- **create-player.mjs fails** — Check that `--guild-api` and `--reactor-api` URLs are correct and reachable. Verify the guild supports programmatic signup (`services.guild_api` exists). If providing a `--mnemonic`, verify it is a valid 24-word BIP39 mnemonic.
- **Guild API returns HTML or 404** — The URL is wrong or you are not using the script. The signup endpoint (`/auth/signup`) is **POST only**. Always use `create-player.mjs` which handles the POST, signing, and polling automatically.
- **Signup succeeds but player never appears** — Re-run the script with the same `--mnemonic` to resume polling. The guild may be slow to process. If it still fails after 120s, the guild's proxy may be down.
- **"insufficient resources"** — Check player Alpha Matter balance.
- **"fleet not on station"** — Wait for fleet or move fleet before planet builds.
- **"invalid slot"** — Use slot 0-3 per ambit; check planet structs for occupancy.
- **"power overload"** — Not enough capacity to activate. Add power sources or connect to a substation with more capacity.

## See Also

- [knowledge/mechanics/building](https://structs.ai/knowledge/mechanics/building) — Build times, difficulty, charge costs
- [knowledge/mechanics/planet](https://structs.ai/knowledge/mechanics/planet) — Planet properties, ore, slots
- [knowledge/mechanics/fleet](https://structs.ai/knowledge/mechanics/fleet) — Fleet movement, on-station rules
- [knowledge/entities/struct-types](https://structs.ai/knowledge/entities/struct-types) — All struct type IDs and properties
- [knowledge/mechanics/power](https://structs.ai/knowledge/mechanics/power) — Capacity, load, online status
- [awareness/async-operations](https://structs.ai/awareness/async-operations) — Background PoW, pipeline strategy
