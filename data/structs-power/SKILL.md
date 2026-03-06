---
name: structs-power
description: Manages power infrastructure in Structs. Covers substations, allocations, player connections, and power monitoring. Use when power is low or overloaded, creating or managing substations, connecting players to substations, allocating capacity, diagnosing offline status, or planning power budget for new structs.
---

# Structs Power

**Important**: Entity IDs containing dashes (like `3-1`, `4-5`) are misinterpreted as flags by the CLI parser. All transaction commands in this skill use `--` before positional arguments to prevent this.

## Procedure

1. **Assess power state** — Query player: `structsd query structs player [id]`. Compute: `availablePower = (capacity + capacitySecondary) - (load + structsLoad)`. If `load + structsLoad > capacity + capacitySecondary`, player goes **OFFLINE** (cannot act). Player passive draw: 25,000 mW.
2. **Create substation** — First create allocation from reactor/generator: `structsd tx structs allocation-create --allocation-type static|dynamic|automated|provider-agreement TX_FLAGS -- [source-id] [power]`. Omit the `--controller` flag to keep control with the creating player account (safest default). If needed, `--controller` accepts an **address**, not a player ID. Then: `structsd tx structs substation-create TX_FLAGS -- [owner-id] [allocation-id]`.
3. **Connect power** — `structsd tx structs substation-allocation-connect -- [substation-id] [allocation-id]` to add source. `structsd tx structs substation-allocation-disconnect -- [substation-id] [allocation-id]` to remove.
4. **Connect players** — `structsd tx structs substation-player-connect -- [substation-id] [player-id]` to draw power. `structsd tx structs substation-player-disconnect -- [substation-id] [player-id]` to remove.
5. **Migrate players** — `structsd tx structs substation-player-migrate TX_FLAGS -- [source-substation-id] [dest-substation-id] [player-id,player-id2,...]`.
6. **Manage allocations** — Update: `structsd tx structs allocation-update -- [allocation-id] [new-power]`. Delete: `structsd tx structs allocation-delete -- [allocation-id]`.
7. **Delete substation** — `structsd tx structs substation-delete -- [substation-id]` (disconnect allocations/players first).

## Commands Reference

| Action | Command |
|--------|---------|
| Substation create | `structsd tx structs substation-create -- [owner-id] [allocation-id]` |
| Substation delete | `structsd tx structs substation-delete -- [substation-id]` |
| Allocation connect | `structsd tx structs substation-allocation-connect -- [substation-id] [allocation-id]` |
| Allocation disconnect | `structsd tx structs substation-allocation-disconnect -- [substation-id] [allocation-id]` |
| Player connect | `structsd tx structs substation-player-connect -- [substation-id] [player-id]` |
| Player disconnect | `structsd tx structs substation-player-disconnect -- [substation-id] [player-id]` |
| Player migrate | `structsd tx structs substation-player-migrate -- [src-substation-id] [dest-substation-id] [player-ids]` |
| Allocation create | `structsd tx structs allocation-create --allocation-type [type] -- [source-id] [power]` |
| Allocation update | `structsd tx structs allocation-update -- [allocation-id] [power]` |
| Allocation delete | `structsd tx structs allocation-delete -- [allocation-id]` |

**TX_FLAGS**: `--from [key-name] --gas auto --gas-adjustment 1.5 -y`

## Verification

- **Player**: `structsd query structs player [id]` — `capacity`, `capacitySecondary`, `load`, `structsLoad`, online status.
- **Substation**: `structsd query structs substation [id]` — connected allocations, players.
- **Allocations**: `structsd query structs allocation-all-by-source [source-id]`, `allocation-all-by-destination [dest-id]` — power flow.

## How to Increase Capacity

If capacity is too low (or you're going offline), there are three paths:

| Method | Requires | Speed | Risk | Rate |
|--------|----------|-------|------|------|
| Reactor infusion | Alpha Matter | Immediate | Low | 1g ≈ 1 kW (minus commission) |
| Generator infusion | Alpha Matter + generator struct | Immediate | High (irreversible, raidable) | 1g = 2-10 kW |
| Buy via agreement | A provider with capacity | Immediate | Medium (ongoing cost) | Varies by provider |

**Most common**: Infuse Alpha Matter into your guild's reactor. Capacity increases automatically.

For step-by-step workflows, see the [structs-energy skill](https://structs.ai/skills/structs-energy/SKILL).

## Error Handling

- **Going offline**: Load exceeds capacity. Deactivate structs immediately (`struct-deactivate`), then increase capacity — see the `structs-energy` skill for options.
- **Allocation exceeds source**: Source (reactor/provider) has limited capacity. Query source; create smaller allocation or add capacity.
- **Substation delete failed**: Ensure no players or allocations connected. Disconnect first.
- **Automated allocation limit**: One automated allocation per source. Attempting a second from the same source will error. Use static/dynamic for multiple.
- **capacity=0 false positive**: A player connected to a substation pool may show `capacity=0` while structs are online and drawing power. Check `structsLoad > 0` as the real indicator of functionality, not `capacity > 0`.

## See Also

- [structs-energy skill](https://structs.ai/skills/structs-energy/SKILL) — "I need more energy" decision tree and workflows
- [knowledge/mechanics/power](https://structs.ai/knowledge/mechanics/power) — Formulas, capacity, load, online status
- [knowledge/mechanics/building](https://structs.ai/knowledge/mechanics/building) — Build power requirements
- [knowledge/mechanics/resources](https://structs.ai/knowledge/mechanics/resources) — Reactor vs generator conversion rates
