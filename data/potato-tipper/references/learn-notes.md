# Learn notes (design patterns)

Source inspiration: `LEARN.md` in the Potato Tipper repo.

## Pattern 1 — Tip-on-Follow (hook)

A post-action hook:
- Event: “I received a new follower” (LSP26 follow)
- Action: “transfer some tokens to the new follower” (LSP7 transfer)

It’s effectively a reusable automation primitive: **react to a social graph update** and perform on-chain rewards.

## Pattern 2 — Self-documenting ERC725Y configuration

Expose the ERC725Y config requirements via view functions on the contract:

- `configDataKeys()` → names + bytes32 keys
- `configDataKeysList()` → list to use with `setDataBatch`
- `encodeConfigDataKeysValues(TipSettings)` → returns keys + values already encoded

This makes integrations less brittle: once the contract is verified, the chain becomes the living documentation.

## Expansion ideas (directional)

The same pattern can generalize to “Reward-on-Follow”:
- reward with other LSP7 tokens
- reward with LSP8 NFTs (requires selecting tokenIds)
- reward with non-token actions (automation), potentially involving Key Manager permissions if native LYX is involved

