# Potato Tipper contracts — repo overview

Repo: `CJ42/potato-tipper-contracts` (Foundry)

## Purpose

A contract system that enables a Universal Profile (🆙) to automatically tip LSP7 $POTATO tokens to **new** followers. It plugs into the LUKSO standards via:

- **LSP1** Universal Receiver Delegate (hook)
- **LSP26** Follower System notifications (follow / unfollow)
- **LSP7** Digital Asset transfers (operator transfer from followed user to follower)
- **ERC725Y** storage on the user’s 🆙 for user settings

## Key files

- `src/PotatoTipper.sol`
  - Implements `ILSP1UniversalReceiverDelegate`.
  - Entry point: `universalReceiverDelegate(sender, value, typeId, data)`.
  - Validates calls come from the LSP26 Follower Registry.
  - Enforces: follower must be an LSP0 account (🆙), not an EOA.
  - Tracks state:
    - `_tippedFollowers[follower][user]` — prevent double tips.
    - `_postInstallFollowers[follower][user]` — “APT” (after install) followers.
    - `_existingFollowersUnfollowedPostInstall[follower][user]` — “BPT” (before install) followers that later unfollow, not eligible on re-follow.

- `src/PotatoTipperConfig.sol`
  - “Self-documenting” config helpers for dApps/users:
    - `configDataKeys()`
    - `configDataKeysList()`
    - `encodeConfigDataKeysValues(...)`

- `src/PotatoTipperSettingsLib.sol`
  - Loads/decodes tip settings stored in ERC725Y.

- `src/Constants.sol`
  - Addresses for `_FOLLOWER_REGISTRY` and `_POTATO_TOKEN` (network-specific).