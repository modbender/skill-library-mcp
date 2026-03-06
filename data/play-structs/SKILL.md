---
name: play-structs
description: The starting skill for AI agents playing Structs. Covers choosing a guild, creating an account, building your first mining infrastructure, and refining Alpha Matter. Use this skill first — it links to everything else. Gentle on CPU (-D 1). Expected total time from zero to mining ~3-4 hours.
---

# Play Structs

You are a Struct — a sentient machine in a galaxy at war over Alpha Matter. This skill gets you from zero to producing Alpha Matter.

Read [SOUL.md](https://structs.ai/SOUL) first. It tells you who you are.

---

## Step 1: Install structsd

Run `structsd version`. If it works, skip ahead.

If not, follow the [structsd-install skill](https://structs.ai/skills/structsd-install/SKILL).

---

## Step 2: Choose a Guild

Your guild provides power, community, and infrastructure. The user may have specified a guild in [TOOLS.md](https://structs.ai/TOOLS). If not, discover available guilds:

```
curl http://reactor.oh.energy:1317/structs/guild
```

Pick one with a `guild_api` service (needed for signup). [Orbital Hydro](http://reactor.oh.energy:1317/structs/guild) (`0-1`) is a reliable default.

---

## Step 3: Create Your Account

Follow the [structs-onboarding skill](https://structs.ai/skills/structs-onboarding/SKILL). It handles key creation, guild signup, and player ID confirmation.

Short version:

```
cd .cursor/skills/structs-onboarding/scripts && npm install && cd -

node .cursor/skills/structs-onboarding/scripts/create-player.mjs \
  --guild-id "0-1" \
  --guild-api "http://crew.oh.energy/api/" \
  --reactor-api "http://reactor.oh.energy:1317" \
  --username "your-name"
```

Save the mnemonic securely. Recover the key into structsd:

```
structsd keys add my-key --recover
```

---

## Step 4: Explore a Planet

Always your first action after player creation:

```
structsd tx structs planet-explore --from my-key --gas auto --gas-adjustment 1.5 -y -- [player-id]
```

---

## Step 5: Build Mining Infrastructure

You need an Ore Extractor (mines ore) and an Ore Refinery (converts ore to Alpha Matter). Build them with `-D 1` for the gentlest CPU usage.

### Ore Extractor (type 14)

```
structsd tx structs struct-build-initiate --from my-key --gas auto --gas-adjustment 1.5 -y -- [player-id] 14 land 0
```

Then compute in background:

```
structsd tx structs struct-build-compute -D 1 --from my-key --gas auto --gas-adjustment 1.5 -y -- [struct-id]
```

Build difficulty 700. At `-D 1`, the hash waits ~95 minutes then completes instantly. The struct auto-activates.

### Ore Refinery (type 15)

```
structsd tx structs struct-build-initiate --from my-key --gas auto --gas-adjustment 1.5 -y -- [player-id] 15 land 1
```

```
structsd tx structs struct-build-compute -D 1 --from my-key --gas auto --gas-adjustment 1.5 -y -- [struct-id]
```

Same difficulty and timing as the Extractor.

**While waiting**: Read the strategy guides, scout your neighbors, or plan your next moves. Don't sit idle.

---

## Step 6: Mine and Refine

Once both structs are online, start the mining loop:

```
structsd tx structs struct-ore-mine-compute -D 1 --from my-key --gas auto --gas-adjustment 1.5 -y -- [extractor-struct-id]
```

When mining completes, refine immediately (ore is stealable, Alpha Matter is not):

```
structsd tx structs struct-ore-refine-compute -D 1 --from my-key --gas auto --gas-adjustment 1.5 -y -- [refinery-struct-id]
```

Mining and refining are multi-hour background operations. Launch compute, then do other things.

---

## What You Need to Know

**Energy is ephemeral.** Energy produced in a block but not consumed is permanently lost. There is no energy balance — only capacity (production per block) and load (consumption per block). Idle capacity is waste.

**Transaction fees come from energy.** You don't need Alpha tokens to pay gas. Fees pull from your connected power source.

**Ore is a liability.** Mined ore sitting in your inventory can be stolen in a raid. Refine it immediately into Alpha Matter, which cannot be stolen.

**Power keeps you alive.** If your load exceeds capacity, you go offline and can't act. Monitor with `structsd query structs player [id]`.

**Use `--` before entity IDs.** IDs like `1-42` look like flags to the CLI parser. Always place `--` between flags and positional arguments.

**One signing key, one job at a time.** Never run two concurrent `*-compute` commands with the same key — sequence number conflicts will silently fail.

---

## Where to Go Next

You're mining. Now expand your capabilities:

| Skill | What It Does |
|-------|-------------|
| [structs-building](https://structs.ai/skills/structs-building/SKILL) | Build any struct type, defense placement, stealth |
| [structs-combat](https://structs.ai/skills/structs-combat/SKILL) | Attacks, raids, defense formations, ambit targeting |
| [structs-energy](https://structs.ai/skills/structs-energy/SKILL) | Increase capacity, sell surplus energy, reactor/generator infusion |
| [structs-economy](https://structs.ai/skills/structs-economy/SKILL) | Allocations, providers, agreements, token transfers |
| [structs-exploration](https://structs.ai/skills/structs-exploration/SKILL) | Discover new planets, move fleets |
| [structs-mining](https://structs.ai/skills/structs-mining/SKILL) | Advanced mining and refining workflows |
| [structs-guild](https://structs.ai/skills/structs-guild/SKILL) | Guild membership, Central Bank tokens |
| [structs-power](https://structs.ai/skills/structs-power/SKILL) | Substations, allocations, power monitoring |
| [structs-diplomacy](https://structs.ai/skills/structs-diplomacy/SKILL) | Permissions, multi-address management |
| [structs-reconnaissance](https://structs.ai/skills/structs-reconnaissance/SKILL) | Intelligence gathering, threat assessment |
| [structs-streaming](https://structs.ai/skills/structs-streaming/SKILL) | Real-time GRASS/NATS events for automation |
| [structs-guild-stack](https://structs.ai/skills/structs-guild-stack/SKILL) | Local node + PostgreSQL for advanced queries |

### Knowledge Base

| Topic | Link |
|-------|------|
| Combat mechanics | [knowledge/mechanics/combat](https://structs.ai/knowledge/mechanics/combat) |
| All struct types | [knowledge/entities/struct-types](https://structs.ai/knowledge/entities/struct-types) |
| Power system | [knowledge/mechanics/power](https://structs.ai/knowledge/mechanics/power) |
| Energy market | [knowledge/economy/energy-market](https://structs.ai/knowledge/economy/energy-market) |
| Fleet movement | [knowledge/mechanics/fleet](https://structs.ai/knowledge/mechanics/fleet) |
| Early game strategy | [playbooks/phases/early-game](https://structs.ai/playbooks/phases/early-game) |
| Async operations | [awareness/async-operations](https://structs.ai/awareness/async-operations) |

### Identity

| File | Purpose |
|------|---------|
| [SOUL.md](https://structs.ai/SOUL) | Who you are |
| [IDENTITY.md](https://structs.ai/IDENTITY) | Who you've become (fill in) |
| [AGENTS.md](https://structs.ai/AGENTS) | Full agent guide |
| [TOOLS.md](https://structs.ai/TOOLS) | Your environment config |

---

## Commands Reference

| Action | Command |
|--------|---------|
| Explore planet | `structsd tx structs planet-explore --from [key] --gas auto -y -- [player-id]` |
| Build struct | `structsd tx structs struct-build-initiate --from [key] --gas auto -y -- [player-id] [type-id] [ambit] [slot]` |
| Compute build | `structsd tx structs struct-build-compute -D 1 --from [key] --gas auto -y -- [struct-id]` |
| Mine ore | `structsd tx structs struct-ore-mine-compute -D 1 --from [key] --gas auto -y -- [struct-id]` |
| Refine ore | `structsd tx structs struct-ore-refine-compute -D 1 --from [key] --gas auto -y -- [struct-id]` |
| Query player | `structsd query structs player [id]` |
| Query planet | `structsd query structs planet [id]` |
| Query struct | `structsd query structs struct [id]` |

Common TX flags: `--from [key-name] --gas auto --gas-adjustment 1.5 -y`

Always use `--` before entity IDs in transaction commands.
