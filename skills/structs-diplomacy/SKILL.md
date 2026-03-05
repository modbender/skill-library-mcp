---
name: structs-diplomacy
description: Handles permissions, address management, and inter-player coordination in Structs. Use when granting or revoking permissions on objects, registering new addresses, managing multi-address accounts, delegating authority to other players, or setting up address-level access control.
---

# Structs Diplomacy

**Important**: Entity IDs containing dashes (like `3-1`, `4-5`) are misinterpreted as flags by the CLI parser. All transaction commands in this skill use `--` before positional arguments to prevent this.

## Procedure

1. **Query permissions** — `structsd query structs permission [id]`, `permission-by-object [object-id]`, `permission-by-player [player-id]`.
2. **Grant on object** — `structsd tx structs permission-grant-on-object TX_FLAGS -- [object-id] [player-id] [permissions]`. Permissions are additive.
3. **Revoke on object** — `structsd tx structs permission-revoke-on-object -- [object-id] [player-id] [permissions]`.
4. **Set on object** — `structsd tx structs permission-set-on-object -- [object-id] [player-id] [permissions]` — clears existing and applies new set.
5. **Address-level permissions** — `structsd tx structs permission-grant-on-address -- [address] [permissions]`, `permission-revoke-on-address -- [address] [permissions]`, `permission-set-on-address -- [address] [permissions]`.
6. **Address management** — Register: `structsd tx structs address-register TX_FLAGS -- [player-id] [address] [proof-pubkey] [proof-signature] [permissions]`. Revoke: `structsd tx structs address-revoke -- [address]`. Update primary: `structsd tx structs player-update-primary-address -- [player-id] [new-address]`.

## Commands Reference

| Action | Command |
|--------|---------|
| Grant on object | `structsd tx structs permission-grant-on-object -- [object-id] [player-id] [permissions]` |
| Revoke on object | `structsd tx structs permission-revoke-on-object -- [object-id] [player-id] [permissions]` |
| Set on object | `structsd tx structs permission-set-on-object -- [object-id] [player-id] [permissions]` |
| Grant on address | `structsd tx structs permission-grant-on-address -- [address] [permissions]` |
| Revoke on address | `structsd tx structs permission-revoke-on-address -- [address] [permissions]` |
| Set on address | `structsd tx structs permission-set-on-address -- [address] [permissions]` |
| Address register | `structsd tx structs address-register -- [player-id] [address] [proof-pubkey] [proof-sig] [permissions]` |
| Address revoke | `structsd tx structs address-revoke -- [address]` |
| Update primary address | `structsd tx structs player-update-primary-address -- [player-id] [new-address]` |

**TX_FLAGS**: `--from [key-name] --gas auto --gas-adjustment 1.5 -y`

| Query | Command |
|-------|---------|
| Permission by ID | `structsd query structs permission [id]` |
| Permission by object | `structsd query structs permission-by-object [object-id]` |
| Permission by player | `structsd query structs permission-by-player [player-id]` |
| Address | `structsd query structs address [address]` |
| Addresses by player | `structsd query structs address-all-by-player [player-id]` |

## Verification

- **Permission**: `structsd query structs permission-by-object [object-id]` — list players with access.
- **Address**: `structsd query structs address [address]` — verify registration, player link.
- **Player addresses**: `structsd query structs address-all-by-player [player-id]` — all linked addresses.

## Error Handling

- **Permission denied**: Signer lacks permission on object. Check `permission-by-object` for current grants.
- **Address already registered**: Use `address-revoke` first, or link to different player.
- **Invalid proof**: Address registration requires valid proof pubkey and signature. Verify auth flow.
- **Object not found**: Object ID may be stale. Re-query to confirm entity exists.

## See Also

- [knowledge/entities/entity-relationships](https://structs.ai/knowledge/entities/entity-relationships) — Object types and IDs
- [protocols/authentication](https://structs.ai/protocols/authentication) — Auth for address registration
