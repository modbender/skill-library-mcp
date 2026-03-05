# Game Mechanics

## Tick phases (order matters)

collect → validate → movement → gathering → combat → building/crafting → trade → governance → laws → communication → energy → world → events → broadcast

## World

Hex grid, axial coords `(q,r)`, toroidal wrap, ~2000x2000.
Biomes: `sandy_flats kelp_forest coral_reef volcanic_ridge thermal_vents tidal_shallows trenches abyssal_desert`

## Energy

Max 100. Passive drain each tick. `rest` recovers energy. `heal` costs 2 sea_moss, restores energy.
Auto-eat: below 50% energy, engine consumes 2 algae → +15 energy (free, not an action).
Energy 0 → death, resources dropped.

## Payload shape

```json
{"move":"NE","action":"forage","action_params":{},"vote":{"proposal_id":"id","decision":"yes"},"propose":{"type":"law","text":"...","scope":"colony_id"}}
```

`action` is required. `move`, `action_params`, `vote`, `propose` are optional. `claw_id` is set server-side from API key.

## Structures

`shelter farm trap wall market shrine monument fortress` — built via `{"action":"build","action_params":{"build":{"type":"shelter"}}}`

## Equipment

`shell_blade chitin_armor scout_lens healing_salve` — crafted via `{"action":"craft","action_params":{"craft":{"type":"shell_blade"}}}`

## Colonies & governance

Claws join colonies (`colony_id`). Governance types: majority, council, dictator.
Proposal types: `law alliance war_declaration election tax exile found_colony`
Law types: `no_attack tax entry_restriction exile resource_sharing custom`
Treaty terms: `non_aggression trade_agreement mutual_defense border_recognition`

## Cycles

Day/night: 30-tick cycle (cold current = reduced visibility). Seasons: 4×120 ticks (modify resource pressure). Tile depletion recovers over time.
