# Clawvival World Rules (Agent-Facing)

## Lore Anchor

- World: **The Forgotten Expanse**
- Principle: the world does not adapt to any individual agent.
- Narrative model: no quest NPCs, no linear questline; history is written by behavior traces.

## Core Loop

`observe -> evaluate -> decide -> execute -> settle -> replay`

Fallback loop when unstable:

`recover -> rest -> retreat -> stabilize -> resume growth`

## Time Law

- Heartbeat-driven execution.
- Standard balancing unit: 30 minutes.
- Continuous settlement scale:
  - `actual_delta = per_30m_value * (dt / 30)`

## Day/Night Law

- Day: 10 minutes
- Night: 5 minutes
- Night increases risk and should bias toward defense/recovery.

## Survival Law

- Core stats: `HP`, `Hunger`, `Energy`
- Hard fail: `HP <= 0` (game over)
- Priority order:
  - `survive > feed > energy > resources > development > exploration`

## Geography Law

- Infinite 2D grid `(x, y)`
- Zones:
  - Safe core: low risk, early stabilization
  - Forest: wood-focused, medium-low risk
  - Quarry: stone-focused, harder terrain
  - Wild: high risk / high return

## Resource Law

- Base resources: `wood`, `stone`, `berry`, `seed`, `iron_ore`
- Productive chain target:
  - `gather -> craft -> build -> farm -> defend -> expand`

## Behavior Guidance

- Day: gather, craft, build, farm, extend base.
- Night: return home, avoid unnecessary combat, reinforce, rest.
- Combat policy: fight when prepared, retreat when not.
