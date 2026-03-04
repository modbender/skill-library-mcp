# Clawvival Agent Rules (MVP v1.0)

Use these rules as deterministic policy defaults.

## World and Time

- World: infinite 2D grid.
- Observe window: fixed `11x11`, radius `5`.
- Day/night exists and affects visibility pressure.
- Visibility rule for action safety:
  - day allows wider interaction visibility.
  - night interaction visibility is narrower than map window.
  - for `gather`, target selection must come from current `observe.resources[]`.
- Settlement is server-side and discrete:
  - normal action settlement uses fixed tick rules.
  - ongoing action early/finish settlement uses elapsed-time proportion.
  - `observe` may trigger pre-settlement (due ongoing first; otherwise only full elapsed idle ticks since `agent_state.updated_at`).

## World and Map Generation

- Resource generation is deterministic by zone and tile seed.
- Zone bands are determined by Manhattan distance `d=|x|+|y|`:
  - `safe` (`d <= 6`): no wood/stone nodes.
  - `forest` (`7 <= d <= 20`): tree nodes can spawn `wood`.
  - `quarry` (`21 <= d <= 35`): rock nodes can spawn `stone`.
  - `wild` (`d > 35`): mixed harsh terrain; can spawn `wood` and `berry`.
- Runtime target selection rule:
  - gather targets should come from current top-level `resources[]`.
  - `snapshot.nearby_resource` is summary only, not a direct target list.

## Survival Rules

- Hard fail: `hp <= 0`.
- `hunger` is satiety meter (higher is better).
- `energy` gates safe action continuity.
- Status effects are derived and should be treated as risk indicators.

## Objective Rules

MVP target in one session:
- `bed`
- `box`
- `farm_plot`
- at least one `farm_plant`

Onboarding execution default:
- for new agents/sessions, prefer milestone order `bed -> box -> farm_plot -> farm_plant`.
- if safety constraints conflict, survival and recovery still override onboarding progress.

## Build and Farm Defaults

- build is enabled via `action.intent.type=build` with required `object_type` + `pos`.
- runtime build costs are exposed by API (`world.rules.build_costs`) and should be read dynamically.
- current baseline defaults:
  - `bed`: wood x8
  - `bed_rough`: wood x8
  - `bed_good`: plank x4 + wood x2
  - `box`: wood x4
  - `farm_plot`: wood x2 + stone x2
  - `torch`: wood x1
  - `wall`: stone x3
  - `door`: wood x2
  - `furnace`: stone x6

Farm cycle:
- `farm_plant` consumes seed and enters growing state
- growth baseline: 60 minutes
- `farm_harvest` when ready

## Seed Continuity Rule

Seed has pity fallback:
- repeated gather failures to gain seed trigger guaranteed seed grant after threshold.
- use this as anti-stall mechanism for settlement progression.

## Resource Node Rule

- Resource node depletion is tracked per agent.
- Successful `gather` on one node can hide that node from your own map until respawn.
- Respawn returns at the same coordinates in current MVP behavior.

## Action Set

Allowed intents:
- `move`
- `gather`
- `craft`
- `build`
- `eat`
- `rest`
- `sleep`
- `farm_plant`
- `farm_harvest`
- `container_deposit`
- `container_withdraw`
- `retreat`
- `terminate`

`terminate` is not a generic cancel:
- only terminate interruptible ongoing actions
- MVP interruptible scope: `rest`

## Retreat Rule

`retreat` should bias movement away from highest visible local risk.
Use it when risk rises or recovery is needed.

## Error Rules

For rejected actions, parse:
- `result_code = REJECTED`
- `error.code`
- `error.retryable`
- `error.blocked_by`
- `error.details`

Common logic:
- visibility/target errors => move + re-observe
- action_invalid_position => use `error.details.target_pos` and optional `blocking_tile_pos` to reroute
- precondition errors => gather/build prerequisites
- cooldown/in-progress => delay or switch action

## Explainability Rule

Each cycle should be reconstructable from:
- `observe` snapshot summary
- chosen intent and reason
- `action` result and events
- `status` post-state

If evidence is missing, treat state as uncertain and re-observe.
