# Common Failure Modes and Fixes

## Chain / Env / Key

- `chain-id != 8453`
  - Fix: use Base mainnet RPC.
- `cast wallet address` does not equal `FROM_ADDRESS`
  - Fix: correct `PRIVATE_KEY` or `FROM_ADDRESS`.
- `Function does not exist`
  - Fix: verify contract address and function signature.

## Access and Ownership

- `LibRealm: Access Right - Only Owner`
  - Action not allowed under current parcel access mode.
  - Fix: use parcel owner wallet, or update access rights/whitelist.
- `RealmGettersAndSettersFacet: Only Parcel owner can call`
  - Setting access rights from a non-owner sender.
- `AppStorage: Only Parcel owner can call`
  - Owner-only route triggered (for example certain unequip/move flows).

## Channeling / Harvest

- `AlchemicaFacet: 8 hours claim cooldown`
  - Claim attempted too early after last claim.
- `AlchemicaFacet: Incorrect last duration`
  - `_lastChanneled` arg does not match `getLastChanneled(gotchiId)`.
- `AlchemicaFacet: Gotchi can't channel yet`
  - One channel per gotchi per day limit.
- `AlchemicaFacet: Parcel can't channel yet`
  - Parcel altar-level cooldown not elapsed.
- `AlchemicaFacet: Must equip Altar`
  - No altar on parcel.
- `AavegotchiDiamond: Gotchi CANNOT have active listing for lending`
  - Gotchi is listed and not currently lent.
- `Kinship too low to reduce`
  - Gotchi kinship cannot be reduced for channeling.

## Survey / Building Preconditions

- `AlchemicaFacet: Round not released`
  - Surveying round has not progressed.
- `AlchemicaFacet: Parcel already surveying`
  - Surveying already active for parcel.
- `RealmFacet: Must survey before equipping`
  - Harvester/reservoir equip attempted before survey progress.
- `RealmFacet: Lodge already equipped`
  - Only one lodge allowed.
- `RealmFacet: Maker already equipped or altar not equipped`
  - Buildqueue booster constraint.

## Grid / Coordinates

- `LibRealm: x exceeding width` or `LibRealm: y exceeding height`
  - Placement outside parcel dimensions.
- `LibRealm: Invalid spot`
  - Collision with existing installation/tile footprint.
- `LibRealm: wrong installationId` / `wrong tileId` / `wrong startPosition`
  - Unequip/move coordinates do not match currently placed object.

## Craft / Queue

- `InstallationFacet: Installation does not exist` / `TileFacet: Tile does not exist`
  - Invalid ID.
- `InstallationFacet: can only craft level 1`
  - Non-base level craft attempt.
- `InstallationFacet: Installation has been deprecated` / `TileFacet: Tile has been deprecated`
  - Deprecated type.
- `InstallationFacet: Too much GLTR` / `TileFacet: Too much GLTR`
  - Reduction exceeds craft time.
- `InstallationFacet: Not owner` / `TileFacet: not owner`
  - Queue is not owned by sender.
- `InstallationFacet: Installation not ready` / `TileFacet: tile not ready`
  - Queue `readyBlock` not reached.

## Upgrade

- `InstallationUpgradeFacet: Upgrade hash not unique`
  - Duplicate queued upgrade at same parcel+coords+installation.
- `LibInstallation: UpgradeQueue full`
  - Parcel queue capacity reached.
- `LibInstallation: Maximum upgrade reached`
  - No `nextLevelId`.
- `LibInstallation: Wrong installation type` / `Wrong alchemicaType` / `Wrong installation level`
  - Invalid upgrade path.
- `InstallationUpgradeFacet: Incorrect GLTR sent`
  - Instant upgrade `gltr` does not equal required total craft blocks.
- `InstallationUpgradeFacet: Failed GLTR transfer`
  - Missing GLTR balance/allowance.

## Troubleshooting Workflow

1. Re-fetch parcel/installations/tiles/access-rights from gotchiverse subgraph.
2. Re-run onchain reads (`getParcelInfo`, type getters, queue getters).
3. Re-simulate exact tx with `cast call --from "$FROM_ADDRESS"`.
4. Broadcast only after the simulation succeeds with the same arguments.

