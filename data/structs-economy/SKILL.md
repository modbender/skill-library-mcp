---
name: structs-economy
description: Manages economic operations in Structs. Covers reactor staking, energy providers, agreements, allocations, generator infusion, and token transfers. Use when staking Alpha Matter in reactors, creating or managing energy providers, negotiating agreements, allocating energy, infusing generators, transferring tokens, or managing economic infrastructure.
---

# Structs Economy

## Procedure

1. **Assess position** — Query player, reactor, provider, agreement state via `structsd query structs player/reactor/provider/agreement [id]`.
2. **Reactor staking** — Stake Alpha Matter: `structsd tx structs reactor-infuse [player-address] [reactor-address] [amount] TX_FLAGS`. The `amount` **must include the denomination**, e.g. `60000000ualpha` (not just `60000000`). This **automatically increases the player's capacity** — no allocation setup needed. The reactor's commission rate determines the split: player receives `power * (1 - commission)`, reactor keeps the rest. Unstake: `reactor-defuse [reactor-id]` (cooldown applies). Cancel cooldown: `reactor-cancel-defusion [reactor-id]`. Migrate: `reactor-begin-migration [player-address] [source-validator-address] [dest-validator-address] [amount]`.
3. **Generator infusion** — `structsd tx structs struct-generator-infuse [struct-id] [amount] TX_FLAGS`. **IRREVERSIBLE** — Alpha cannot be recovered. Higher conversion rates than reactors (2-10x) but generator is vulnerable to raids.
4. **Provider lifecycle** — Create: `provider-create [substation-id] [rate] [access-policy] [provider-penalty] [consumer-penalty] [cap-min] [cap-max] [dur-min] [dur-max] TX_FLAGS`. Valid `access-policy` values: `open-market` (anyone can buy), `guild-market` (guild members only), `closed-market` (invite-only via `provider-guild-grant`). Update capacity/duration/access via `provider-update-capacity-maximum`, `provider-update-duration-minimum`, etc. Delete: `provider-delete [provider-id]`. Withdraw earnings: `provider-withdraw-balance [provider-id]`. Grant/revoke guild access: `provider-guild-grant`, `provider-guild-revoke`.
5. **Agreements** — Open: `agreement-open [provider-id] [duration] [capacity] TX_FLAGS`. Close: `agreement-close [agreement-id]`. Adjust: `agreement-capacity-increase/decrease`, `agreement-duration-increase`.
6. **Allocations** — Create: `allocation-create [source-id] [power] --allocation-type static|dynamic|automated TX_FLAGS`. Omit the `--controller` flag to keep control with the creating player account (safest default). If needed, `--controller` accepts an **address** (not a player ID). Update: `allocation-update [allocation-id] [new-power]`. Delete: `allocation-delete [allocation-id]` — only the controlling address can delete an allocation. Transfer: `allocation-transfer [allocation-id] [new-owner]`.

### Allocation Type Comparison

| Type | Updatable | Deletable | Auto-grows | Limit | Use Case |
|------|-----------|-----------|------------|-------|----------|
| `static` | No | No (while connected) | No | Unlimited | Fixed capacity routing |
| `dynamic` | Yes | Yes | No | Unlimited | Flexible, managed routing |
| `automated` | Yes | No | Yes (scales with source capacity) | One per source | Energy commerce (recommended) |
| `provider-agreement` | System-managed | System-managed | System-managed | System-created | Auto-created when agreements open; never create manually |

**Automated allocation limit**: Only one automated allocation per source is allowed. Attempting to create a second from the same source will error. Use `dynamic` type if you need multiple allocations from one source.

**Recommended for energy sales**: Use `automated` allocations. When you infuse more alpha into a reactor, your capacity grows, and automated allocations proportionally increase energy flowing to your substations with no manual intervention.
7. **Token transfer** — `player-send [from-address] [to-address] [amount] TX_FLAGS`.

## Commands Reference

| Action | Command |
|--------|---------|
| Reactor infuse | `structsd tx structs reactor-infuse [player-addr] [validator-addr] [amount]` (validator = `structsvaloper1...`, NOT reactor ID) |
| Reactor defuse | `structsd tx structs reactor-defuse [reactor-id]` |
| Reactor migrate | `structsd tx structs reactor-begin-migration [player-addr] [src-validator-addr] [dest-validator-addr] [amount]` |
| Reactor cancel defusion | `structsd tx structs reactor-cancel-defusion [reactor-id]` |
| Generator infuse | `structsd tx structs struct-generator-infuse [struct-id] [amount]` |
| Provider create | `structsd tx structs provider-create [substation-id] [rate] [access] [prov-penalty] [cons-penalty] [cap-min] [cap-max] [dur-min] [dur-max]` |
| Provider delete | `structsd tx structs provider-delete [provider-id]` |
| Provider withdraw | `structsd tx structs provider-withdraw-balance [provider-id]` |
| Agreement open | `structsd tx structs agreement-open [provider-id] [duration] [capacity]` |
| Agreement close | `structsd tx structs agreement-close [agreement-id]` |
| Allocation create | `structsd tx structs allocation-create [source-id] [power] --allocation-type [type]` |
| Allocation update | `structsd tx structs allocation-update [allocation-id] [power]` |
| Allocation delete | `structsd tx structs allocation-delete [allocation-id]` |
| Player send | `structsd tx structs player-send [from] [to] [amount]` |

**TX_FLAGS**: `--from [key-name] --gas auto --gas-adjustment 1.5 -y`

**Important**: Entity IDs containing dashes (like `3-1`, `4-5`) are misinterpreted as flags by the CLI parser. Always place `--` between flags and positional args: `structsd tx structs command TX_FLAGS -- [entity-id] [other-args]`

## Verification

- **Reactor**: `structsd query structs reactor [id]` — check `infusedAmount`, `defusionCooldown`.
- **Provider**: `structsd query structs provider [id]` — verify capacity, rate, active agreements.
- **Agreement**: `structsd query structs agreement [id]` — check status, capacity, duration.
- **Allocation**: `structsd query structs allocation [id]` — confirm power, source, destination.
- **Player balance**: `structsd query structs player [id]` — verify Alpha Matter after transfers.

## Error Handling

- **Insufficient balance**: Check player Alpha Matter before infuse/send. Refine ore first.
- **Provider capacity exceeded**: Query provider `capacityMaximum`; reduce agreement capacity or create new provider.
- **Defusion cooldown**: Use `reactor-cancel-defusion` to re-stake during cooldown, or wait.
- **Generator infuse failed**: Cannot undo. Verify struct is a generator type and amount is correct before submitting.

## See Also

- [structs-energy skill](https://structs.ai/skills/structs-energy/SKILL) — "I need more energy" decision tree and workflows
- [knowledge/economy/energy-market](https://structs.ai/knowledge/economy/energy-market) — Provider/agreement flow, pricing
- [knowledge/economy/guild-banking](https://structs.ai/knowledge/economy/guild-banking) — Central Bank tokens
- [knowledge/mechanics/resources](https://structs.ai/knowledge/mechanics/resources) — Alpha Matter, conversion rates
- [knowledge/mechanics/power](https://structs.ai/knowledge/mechanics/power) — Capacity, load, online status
