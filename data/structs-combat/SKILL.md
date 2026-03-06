---
name: structs-combat
description: Executes combat operations in Structs. Covers attacks, raids, defense setup, and stealth positioning. Use when attacking enemy structs, raiding a planet for ore, setting up defenders, activating stealth, moving fleet for raids, or preparing for incoming attacks. Raids require fleet movement and background PoW compute.
---

# Structs Combat

**Important**: Entity IDs containing dashes (like `5-10`, `9-3`) are misinterpreted as flags by the CLI parser. All transaction commands in this skill use `--` before positional arguments to prevent this.

## Procedure

1. **Scout** — `structsd query structs planet [id]`, `structsd query structs struct [id]` for targets, shield, defenses.
2. **Optional stealth** — `structsd tx structs struct-stealth-activate --from [key-name] --gas auto --gas-adjustment 1.5 -y -- [struct-id]` before attack.
3. **Attack structs** — `structsd tx structs struct-attack --from [key-name] --gas auto --gas-adjustment 1.5 -y -- [operating-struct-id] [target-struct-id,target-id2,...] [weapon-system]`. Can target multiple structs.
4. **Raid flow** — Move fleet to target: `structsd tx structs fleet-move --from [key-name] --gas auto --gas-adjustment 1.5 -y -- [fleet-id] [destination-location-id]`. Then `structsd tx structs planet-raid-compute -D 3 --from [key-name] --gas auto --gas-adjustment 1.5 -y -- [fleet-id]`. Compute auto-submits the complete transaction. Move fleet home. Refine stolen ore immediately.
5. **Defense setup** — `structsd tx structs struct-defense-set --from [key] --gas auto -y -- [defender-struct-id] [protected-struct-id]` to assign; `structsd tx structs struct-defense-clear --from [key] --gas auto -y -- [defender-struct-id]` to remove.

## Commands Reference

| Action | CLI Command |
|--------|-------------|
| Attack | `structsd tx structs struct-attack -- [operating-struct-id] [target-ids] [weapon-system]` |
| Raid compute (PoW + auto-complete) | `structsd tx structs planet-raid-compute -D 3 -- [fleet-id]` |
| Raid complete (manual, rarely needed) | `structsd tx structs planet-raid-complete -- [fleet-id]` |
| Fleet move | `structsd tx structs fleet-move -- [fleet-id] [destination-location-id]` |
| Set defense | `structsd tx structs struct-defense-set -- [defender-id] [protected-id]` |
| Clear defense | `structsd tx structs struct-defense-clear -- [defender-id]` |
| Stealth on | `structsd tx structs struct-stealth-activate -- [struct-id]` |
| Stealth off | `structsd tx structs struct-stealth-deactivate -- [struct-id]` |
| Move Command Ship (ambit) | `structsd tx structs struct-move -- [struct-id] [new-ambit] [new-slot] [new-location]` |

Raid flow: fleet-move → planet-raid-compute (auto-submits complete) → fleet-move home → refine stolen ore. Common tx flags: `--from [key-name] --gas auto --gas-adjustment 1.5 -y`.

## Raid Timing

Fleet movement (`fleet-move`) is instant — no transit time. The only time cost in a raid cycle is the PoW compute.

`planet-raid-compute` uses `-D` flag (range 1-64) to wait until difficulty drops before hashing. Raid PoW difficulty depends on the target planet's properties. Launch raid compute in a background terminal — it may take minutes to hours depending on difficulty. Use `-D 3` for zero wasted CPU. Compute auto-submits the complete transaction.

**Important**: Your fleet is locked "away" during the raid compute. You cannot build on your planet while your fleet is away. Plan accordingly — complete all planet builds before moving fleet for a raid.

## Ambit Targeting

Each weapon can only hit specific ambits. Before attacking, verify your struct's weapon can reach the target's ambit.

| Struct | Lives In | Primary Targets | Secondary Targets |
|--------|----------|-----------------|-------------------|
| Command Ship | Any (movable) | Current ambit only | — |
| Battleship | Space | Space, Land, Water | — |
| Starfighter | Space | Space | Space |
| Frigate | Space | Space, Air | — |
| Pursuit Fighter | Air | Air | — |
| Stealth Bomber | Air | Land, Water | — |
| High Altitude Interceptor | Air | Space, Air | — |
| Mobile Artillery | Land | Land, Water | — |
| Tank | Land | Land | — |
| SAM Launcher | Land | Space, Air | — |
| Cruiser | Water | Land, Water | Air |
| Destroyer | Water | Air, Water | — |
| Submersible | Water | Space, Water | — |

**Command Ship positioning**: The Command Ship is the only struct that can change ambits via `struct-move`. It can only attack structs in its current ambit (ambit flag `32` = "Local"). Move it to the target's ambit before attacking. Move it away from enemy weapon ranges as a defensive tactic.

## Weapon Control vs Defense Type

The interaction between weapon control (guided/unguided) and target defense determines evasion. This is the core of combat tactics:

| Target Defense | vs Guided | vs Unguided |
|----------------|-----------|-------------|
| Signal Jamming (Battleship, Pursuit Fighter, Cruiser) | **66% miss** | Full hit |
| Defensive Maneuver (High Alt Interceptor) | Full hit | **66% miss** |
| Armour (Tank) | Full hit, -1 dmg | Full hit, -1 dmg |
| Stealth Mode (Stealth Bomber, Submersible) | Same-ambit only | Same-ambit only |
| Indirect Combat (Mobile Artillery) | Full hit | Full hit |
| None | Full hit | Full hit |

**Tactics**: Use unguided weapons vs Signal Jamming, guided vs Defensive Maneuver. Armour always reduces by 1.

**Stealth rules**:
- Stealthed structs can still be attacked from the **same ambit** -- stealth only blocks cross-ambit targeting
- Attacking **instantly deactivates** stealth (firing reveals position)
- Re-activation costs 1 charge (`struct-stealth-activate`)

## Strategic Positioning

**Offensive**: Move your Command Ship to the ambit where you want to deal damage. Use cross-ambit attackers (Battleship, Stealth Bomber, SAM Launcher, Submersible) for coverage without repositioning.

**Defensive**: If the enemy fleet can only target specific ambits, move your Command Ship to an ambit they cannot reach. Diversify defenders across ambits so you can block attacks from any direction.

**High-value cross-ambit units**: Battleship (Space→Space/Land/Water), SAM Launcher (Land→Space/Air), Stealth Bomber (Air→Land/Water), Submersible (Water→Space/Water), Cruiser (Water→Land/Water + Air secondary). These structs threaten multiple ambits and are the foundation of flexible fleet composition.

## Verification

- Query planet shield, struct health
- Query fleet location (onStation vs away)
- Stolen ore: refine immediately; verify with struct/player queries
- Attack results include health values (remaining health after attack) -- use to assess damage dealt
- Raid `seized_ore` is tracked on `planet_raid` record -- query to see total ore stolen

## Combat Notes

- Minimum damage after reduction is 1 -- attacks always deal at least 1 damage
- Offline/destroyed structs cannot counter-attack
- Each struct can only commit once per attack action (no double-commit)
- Target struct existence is validated before attack proceeds
- Hashing for raid-compute is open by default -- any valid proof accepted
- Successful raids seize ALL of the target's storedOre -- one raid takes everything
- Destroyed structs are gone forever but can be replaced by building a new struct of the same type (full PoW required)
- Protect your Command Ship -- losing it disables your entire fleet until a replacement is built

## Combat Readiness Checklist

Before engaging in combat, verify all conditions:

- [ ] **Command Ship online** — `structsd query structs struct [cmd-ship-id]`, status = Online
- [ ] **Fleet on station** (for defense) or **fleet away** (for raids) — `structsd query structs fleet [fleet-id]`
- [ ] **Sufficient charge** — Weapons cost 1-20 charge. At ~6 sec/block, 20 charge = 2 minutes
- [ ] **Power capacity headroom** — Total load must stay below capacity during combat
- [ ] **Defense structs assigned** — PDC, Orbital Shield, defenders set via `struct-defense-set`
- [ ] **Available struct slot** — If building combat structs, check planet slots (0-3 per ambit)
- [ ] **Ore refined or secured** — Unrefined ore is stealable. Refine before engaging in raids that may invite retaliation

## Defense Formations

Assign defenders to protect high-value structs. Defenders absorb incoming attacks before the protected struct takes damage.

**Minimum viable defense**: Assign at least one combat struct per ambit to defend your Command Ship. Command Ship has 6 HP; most fleet structs have 3 HP. Without defenders, a Command Ship can be destroyed in just a few attacks.

**Example formation** (4 Starfighters defending Command Ship):

```
structsd tx structs struct-defense-set --from [key] --gas auto -y -- [starfighter-1-id] [command-ship-id]
structsd tx structs struct-defense-set --from [key] --gas auto -y -- [starfighter-2-id] [command-ship-id]
structsd tx structs struct-defense-set --from [key] --gas auto -y -- [starfighter-3-id] [command-ship-id]
structsd tx structs struct-defense-set --from [key] --gas auto -y -- [starfighter-4-id] [command-ship-id]
```

**Rules**:
- Defenders must be in the **same ambit as the target being defended** to block (not the attacker's ambit)
- A struct cannot block for a friendly in a different ambit
- Defenders whose weapons can reach the attacker's ambit will **counter-attack automatically** — this is in addition to the normal counter-attack most structs have
- Counter-attacks are ambit-independent from the defended target (a space defender can counter a space attacker while defending a land struct)
- Each defender assignment costs 1 charge -- stagger 6s apart (same account)
- Build defense BEFORE economy or offense -- always
- Defense protects structs from destruction but does **NOT** prevent ore seizure -- the only defense for ore is immediate refining

## Error Handling

- **"insufficient charge"** — Weapon needs charge; check struct state.
- **"target invalid"** — Target may be destroyed, stealthed, or out of range.
- **"unreachable" / "out_of_range"** — Your weapon cannot target that ambit. Check the targeting matrix above and reposition your Command Ship or use a different struct.
- **"fleet not away"** — Raids require fleet away; move fleet first.
- **"proof invalid"** — Re-run raid-compute with correct difficulty.
- **Stolen ore** — Refine immediately; ore is stealable until refined.

## See Also

- [knowledge/mechanics/combat](https://structs.ai/knowledge/mechanics/combat) — Damage, evasion, raids, defense
- [knowledge/mechanics/fleet](https://structs.ai/knowledge/mechanics/fleet) — Fleet movement, on-station rules
- [knowledge/mechanics/resources](https://structs.ai/knowledge/mechanics/resources) — Ore vulnerability, Alpha Matter
