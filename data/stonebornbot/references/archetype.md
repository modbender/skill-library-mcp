# Archetype ERC721a Support

Archetype is an invite-based minting framework for ERC721a contracts. Enable when the target contract uses Archetype's invite system.

## When to Enable

- Contract uses `mint(Auth calldata auth, uint256 quantity, address affiliate, bytes calldata signature)` or similar
- Mint requires an auth key (invite code / allowlist proof)
- Contract page mentions "Archetype" or "invite-based"

## Config Fields

```json
"archetype": {
  "enabled": true,
  "authKey": "0x...",       // Auth/invite key (bytes32). Get from allowlist or project.
  "proof": ["0x...", ...],  // Merkle proof array. Empty [] if no proof needed.
  "affiliate": "0x...",     // Affiliate address. Use 0x0...0 if none.
  "signature": "0x"         // Optional platform signature. Usually "0x".
}
```

## How It Works

When enabled, the bot constructs the mint calldata using the Archetype ABI pattern instead of the standard `mintFunction`. The auth struct is assembled from the config fields and passed as the first argument.

## Getting Auth Keys

1. **From the project**: Check their Discord/website for allowlist tools
2. **From the contract**: Read `invites` mapping or listen for `Invited` events
3. **From Etherscan**: Check successful mint txs and decode the auth parameter
