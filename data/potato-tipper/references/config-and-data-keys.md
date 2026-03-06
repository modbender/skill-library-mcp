# Config + data keys (🆙 setup)

## Goal

To “connect” PotatoTipper to a user’s Universal Profile (🆙), you set ERC725Y data on the 🆙 so that:

1) Follow/unfollow notifications route to PotatoTipper (as an LSP1 delegate)
2) PotatoTipper can read the user’s tip settings from the 🆙

## The 3 relevant data keys

### A) LSP1 delegate — react on FOLLOW (LSP26)

Key (bytes32):
- `LSP1UniversalReceiverDelegate:LSP26FollowerSystem_FollowNotification`
- `0x0cfc51aec37c55a4d0b1000071e02f9f05bcd5816ec4f3134aa2e5a916669537`

Value:
- the PotatoTipper contract address (encoded per LSP2 schema; typically `address` value content)

### B) LSP1 delegate — react on UNFOLLOW (LSP26)

Key (bytes32):
- `LSP1UniversalReceiverDelegate:LSP26FollowerSystem_UnfollowNotification`
- `0x0cfc51aec37c55a4d0b100009d3c0b4012b69658977b099bdaa51eff0f0460f4`

Value:
- the PotatoTipper contract address

### C) Tip settings stored on the user’s 🆙

LSP2 JSON Schema

```json
{
  "name": "PotatoTipper:Settings",
  "key": "0xd1d57abed02d4c2d7ce00000e8211998bb257be214c7b0997830cd295066cc6a",
  "keyType": "Mapping",
  "valueType": "(uint256,uint256,uint256)",
  "valueContent": "(Number,Number,Number)"
}
```

Key (bytes32):
- `PotatoTipper:Settings`
- `0xd1d57abed02d4c2d7ce00000e8211998bb257be214c7b0997830cd295066cc6a`

Value:
- ABI-encoded tuple: `(uint256 tipAmount, uint256 minimumFollowers, uint256 minimumPotatoBalance)`
- `tipAmount` and `minimumPotatoBalance` are in **wei units** (LSP7 token has 18 decimals).

Example:

encoded data: `0x0000000000000000000000000000000000000000000000000de0b6b3a764000000000000000000000000000000000000000000000000000000000000000000050000000000000000000000000000000000000000000000056bc75e2d63100000`

decode result as: `(1e18, 5, 100e18)` meaning:
- tipAmount = 1 🥔
- minimumFollowers = 5
- minimumPotatoBalance = 100 🥔

details:

```js
example: 0x0000000000000000000000000000000000000000000000000de0b6b3a764000000000000000000000000000000000000000000000000000000000000000000050000000000000000000000000000000000000000000000056bc75e2d63100000

- tipAmount (uint256) = 32 bytes long
// 0000000000000000000000000000000000000000000000000de0b6b3a7640000 (in hex) = 1,000,000,000,000,000,000 (in decimals)

- minimumFollowers (uint256) = 32 bytes long
// 0000000000000000000000000000000000000000000000000000000000000005

- minimumPotatoBalance (uint256) = 32 bytes long
// 0000000000000000000000000000000000000000000000056bc75e2d63100000 (in hex) = 100,000,000,000,000,000,000 (in decimals)

- Final decoded result
// => (1 $POTATO token as tip amount, 5 minimum followers, 100 $POTATO token minimum in follower balance)
```

## Preferred integration pattern (self-documenting helpers)

Rather than hardcoding these ERC725Y data keys in dApps codebase, use the on-chain helper views functions from `PotatoTipperConfig`:

- `configDataKeys()` — human-friendly struct with each key
- `configDataKeysList()` — `bytes32[]` keys for batch setting
- `encodeConfigDataKeysValues(tipSettings)` — returns `(keys[], values[])` for a single `setDataBatch`

This reduces docs drift: verified contract source becomes the canonical config reference.

