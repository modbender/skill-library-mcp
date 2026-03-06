---
name: structs-guild
description: Manages guild operations in Structs. Covers creation, membership, settings, and Central Bank token operations. Use when creating a guild, joining or leaving a guild, managing guild settings, minting or redeeming guild tokens, managing Central Bank collateral, or coordinating guild membership.
---

# Structs Guild

**Important**: Entity IDs containing dashes (like `3-1`, `4-5`) are misinterpreted as flags by the CLI parser. All transaction commands in this skill use `--` before positional arguments to prevent this.

## Procedure

1. **Discover guilds** — `structsd query structs guild-all` or `structsd query structs guild [id]`.
2. **Create guild** — Requires associated reactor. `structsd tx structs guild-create TX_FLAGS -- [endpoint] [substation-id]`.
3. **Membership** — Join: `structsd tx structs guild-membership-join -- [guild-id] [infusion-id,infusion-id2,...]` (use `--player-id`, `--substation-id` if needed). Proxy join: `structsd tx structs guild-membership-join-proxy -- [guild-id] [player-id] [infusion-ids]`. Invite flow: `structsd tx structs guild-membership-invite -- [guild-id] [player-id]` → invitee runs `structsd tx structs guild-membership-invite-approve -- [guild-id]` or `structsd tx structs guild-membership-invite-deny -- [guild-id]`. Request flow: `structsd tx structs guild-membership-request -- [guild-id]` → owner runs `structsd tx structs guild-membership-request-approve -- [guild-id] [player-id]` or `structsd tx structs guild-membership-request-deny -- [guild-id] [player-id]`. Kick: `structsd tx structs guild-membership-kick -- [guild-id] [player-id]`.
4. **Settings** — See Commands Reference: `guild-update-endpoint`, `guild-update-entry-substation-id`, `guild-update-join-infusion-minimum` (and `-minimum-by-invite`, `-minimum-by-request`), `guild-update-owner-id`. All use `--` before positional args.
5. **Central Bank** — Mint: `structsd tx structs guild-bank-mint TX_FLAGS -- [alpha-amount] [token-amount]` (no guild-id — signer's guild is used implicitly; both amounts are raw integers). Redeem: `structsd tx structs guild-bank-redeem -- [guild-id] [amount]`. Confiscate and burn: `structsd tx structs guild-bank-confiscate-and-burn -- [guild-id] [address] [amount]`.

## Commands Reference

| Action | Command |
|--------|---------|
| Create | `structsd tx structs guild-create -- [endpoint] [substation-id]` |
| Join | `structsd tx structs guild-membership-join -- [guild-id] [infusion-ids]` |
| Join proxy | `structsd tx structs guild-membership-join-proxy -- [guild-id] [player-id] [infusion-ids]` |
| Invite | `structsd tx structs guild-membership-invite -- [guild-id] [player-id]` |
| Invite approve/deny | `structsd tx structs guild-membership-invite-approve/deny -- [guild-id]` |
| Invite revoke | `structsd tx structs guild-membership-invite-revoke -- [guild-id] [player-id]` |
| Request | `structsd tx structs guild-membership-request -- [guild-id]` |
| Request approve/deny | `structsd tx structs guild-membership-request-approve/deny -- [guild-id] [player-id]` |
| Request revoke | `structsd tx structs guild-membership-request-revoke -- [guild-id]` |
| Kick | `structsd tx structs guild-membership-kick -- [guild-id] [player-id]` |
| Update endpoint | `structsd tx structs guild-update-endpoint -- [guild-id] [endpoint]` |
| Update entry substation | `structsd tx structs guild-update-entry-substation-id -- [guild-id] [substation-id]` |
| Update infusion minimums | `structsd tx structs guild-update-join-infusion-minimum/minimum-by-invite/minimum-by-request -- [guild-id] [value]` |
| Update owner | `structsd tx structs guild-update-owner-id -- [guild-id] [new-owner-player-id]` |
| Bank mint | `structsd tx structs guild-bank-mint -- [alpha-amount] [token-amount]` (signer's guild, raw integers) |
| Bank redeem | `structsd tx structs guild-bank-redeem -- [guild-id] [amount]` |
| Bank confiscate | `structsd tx structs guild-bank-confiscate-and-burn -- [guild-id] [address] [amount]` |

**TX_FLAGS**: `--from [key-name] --gas auto --gas-adjustment 1.5 -y`

## Verification

- **Guild**: `structsd query structs guild [id]` — members, settings, owner.
- **Membership applications**: `structsd query structs guild-membership-application-all` or by ID.
- **Bank collateral**: `structsd query structs guild-bank-collateral-address [guild-id]` — verify reserves.

## Error Handling

- **Insufficient infusion**: Guild may require minimum infusion to join. Query guild for `joinInfusionMinimum`; meet requirement or get invite (bypass).
- **Already member**: Cannot join twice. Check `guild-membership-application` status.
- **Mint/redeem failed**: Verify guild has sufficient Alpha Matter collateral for mint; sufficient tokens for redeem.
- **Permission denied**: Only guild owner (or delegated address) can update settings, approve requests, mint/redeem.

## See Also

- [knowledge/economy/guild-banking](https://structs.ai/knowledge/economy/guild-banking) — Central Bank, collateral, token lifecycle
- [knowledge/economy/energy-market](https://structs.ai/knowledge/economy/energy-market) — Provider guild access
- [knowledge/lore/factions](https://structs.ai/knowledge/lore/factions) — Guild politics
