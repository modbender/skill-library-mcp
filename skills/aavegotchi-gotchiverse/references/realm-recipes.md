# Realm Recipes (Foundry cast)

All commands assume defaults from `references/addresses.md` and use:
- `~/.foundry/bin/cast call` for simulation/read
- `~/.foundry/bin/cast send` for broadcast

## Global Preflight

```bash
~/.foundry/bin/cast chain-id --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast wallet address --private-key "$PRIVATE_KEY"

~/.foundry/bin/cast call "$REALM_DIAMOND" 'owner()(address)' --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$REALM_DIAMOND" 'getAlchemicaAddresses()(address[4])' --rpc-url "$BASE_MAINNET_RPC"
```

## Parcel Reads

Parcel snapshot:
```bash
~/.foundry/bin/cast call "$REALM_DIAMOND" \
  'getParcelInfo(uint256)((string,string,address,uint256,uint256,uint256,uint256,uint256[4],uint256,uint256,uint256[4],(uint256,uint256)[],(uint256,uint256)[],uint256,uint256))' \
  "<PARCEL_ID>" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Available and remaining alchemica:
```bash
~/.foundry/bin/cast call "$REALM_DIAMOND" 'getAvailableAlchemica(uint256)(uint256[4])' "<PARCEL_ID>" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$REALM_DIAMOND" 'getRealmAlchemica(uint256)(uint256[4])' "<PARCEL_ID>" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$REALM_DIAMOND" 'lastClaimedAlchemica(uint256)(uint256)' "<PARCEL_ID>" --rpc-url "$BASE_MAINNET_RPC"
```

Upgrade queue limits on parcel:
```bash
~/.foundry/bin/cast call "$REALM_DIAMOND" 'getParcelUpgradeQueueLength(uint256)(uint256)' "<PARCEL_ID>" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$REALM_DIAMOND" 'getParcelUpgradeQueueCapacity(uint256)(uint256)' "<PARCEL_ID>" --rpc-url "$BASE_MAINNET_RPC"
```

## Access Right Preflight

Read access-right and whitelist id for a parcel/action:
```bash
~/.foundry/bin/cast call "$REALM_DIAMOND" 'getParcelsAccessRights(uint256[],uint256[])(uint256[])' "[<PARCEL_ID>]" "[<ACTION_RIGHT>]" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$REALM_DIAMOND" 'getParcelsAccessRightsWhitelistIds(uint256[],uint256[])(uint256[])' "[<PARCEL_ID>]" "[<ACTION_RIGHT>]" --rpc-url "$BASE_MAINNET_RPC"
```

Explicit verifier (reverts if unauthorized):
```bash
~/.foundry/bin/cast call "$REALM_DIAMOND" 'verifyAccessRight(uint256,uint256,uint256,address)' \
  "<PARCEL_ID>" "<GOTCHI_ID>" "<ACTION_RIGHT>" "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Channeling Preflight

Gotchi lending/listing/kinship:
```bash
~/.foundry/bin/cast call "$AAVEGOTCHI_DIAMOND" 'isAavegotchiListed(uint32)(bool)' "<GOTCHI_ID>" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$AAVEGOTCHI_DIAMOND" 'isAavegotchiLent(uint32)(bool)' "<GOTCHI_ID>" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$AAVEGOTCHI_DIAMOND" 'kinship(uint256)(uint256)' "<GOTCHI_ID>" --rpc-url "$BASE_MAINNET_RPC"
```

Current channeling timestamps:
```bash
~/.foundry/bin/cast call "$REALM_DIAMOND" 'getLastChanneled(uint256)(uint256)' "<GOTCHI_ID>" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$REALM_DIAMOND" 'getParcelLastChanneled(uint256)(uint256)' "<PARCEL_ID>" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$REALM_DIAMOND" 'getAltarId(uint256)(uint256)' "<PARCEL_ID>" --rpc-url "$BASE_MAINNET_RPC"
```

## Start Surveying

Simulate:
```bash
~/.foundry/bin/cast call "$REALM_DIAMOND" 'startSurveying(uint256)' "<PARCEL_ID>" \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Broadcast:
```bash
~/.foundry/bin/cast send "$REALM_DIAMOND" 'startSurveying(uint256)' "<PARCEL_ID>" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Claim Available Alchemica

Single parcel:

Simulate:
```bash
~/.foundry/bin/cast call "$REALM_DIAMOND" 'claimAvailableAlchemica(uint256,uint256,bytes)' \
  "<PARCEL_ID>" "<GOTCHI_ID>" 0x \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Broadcast:
```bash
~/.foundry/bin/cast send "$REALM_DIAMOND" 'claimAvailableAlchemica(uint256,uint256,bytes)' \
  "<PARCEL_ID>" "<GOTCHI_ID>" 0x \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Multiple parcels:

Simulate:
```bash
~/.foundry/bin/cast call "$REALM_DIAMOND" 'claimAllAvailableAlchemica(uint256[],uint256,bytes)' \
  "[<PARCEL_ID_1>,<PARCEL_ID_2>]" "<GOTCHI_ID>" 0x \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Broadcast:
```bash
~/.foundry/bin/cast send "$REALM_DIAMOND" 'claimAllAvailableAlchemica(uint256[],uint256,bytes)' \
  "[<PARCEL_ID_1>,<PARCEL_ID_2>]" "<GOTCHI_ID>" 0x \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Channel Alchemica

Simulate:
```bash
~/.foundry/bin/cast call "$REALM_DIAMOND" 'channelAlchemica(uint256,uint256,uint256,bytes)' \
  "<PARCEL_ID>" "<GOTCHI_ID>" "<LAST_CHANNELED_FROM_getLastChanneled>" 0x \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Broadcast:
```bash
~/.foundry/bin/cast send "$REALM_DIAMOND" 'channelAlchemica(uint256,uint256,uint256,bytes)' \
  "<PARCEL_ID>" "<GOTCHI_ID>" "<LAST_CHANNELED_FROM_getLastChanneled>" 0x \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Build on Parcel (Installations)

Equip installation:
```bash
# simulate
~/.foundry/bin/cast call "$REALM_DIAMOND" 'equipInstallation(uint256,uint256,uint256,uint256,uint256,bytes)' \
  "<PARCEL_ID>" "<GOTCHI_ID>" "<INSTALLATION_ID>" "<X>" "<Y>" 0x \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"

# broadcast
~/.foundry/bin/cast send "$REALM_DIAMOND" 'equipInstallation(uint256,uint256,uint256,uint256,uint256,bytes)' \
  "<PARCEL_ID>" "<GOTCHI_ID>" "<INSTALLATION_ID>" "<X>" "<Y>" 0x \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Unequip installation:
```bash
# simulate
~/.foundry/bin/cast call "$REALM_DIAMOND" 'unequipInstallation(uint256,uint256,uint256,uint256,uint256,bytes)' \
  "<PARCEL_ID>" "<GOTCHI_ID>" "<INSTALLATION_ID>" "<X>" "<Y>" 0x \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"

# broadcast
~/.foundry/bin/cast send "$REALM_DIAMOND" 'unequipInstallation(uint256,uint256,uint256,uint256,uint256,bytes)' \
  "<PARCEL_ID>" "<GOTCHI_ID>" "<INSTALLATION_ID>" "<X>" "<Y>" 0x \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Move installation:
```bash
~/.foundry/bin/cast call "$REALM_DIAMOND" 'moveInstallation(uint256,uint256,uint256,uint256,uint256,uint256)' \
  "<PARCEL_ID>" "<INSTALLATION_ID>" "<X0>" "<Y0>" "<X1>" "<Y1>" \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Build on Parcel (Tiles)

Equip tile:
```bash
# simulate
~/.foundry/bin/cast call "$REALM_DIAMOND" 'equipTile(uint256,uint256,uint256,uint256,uint256,bytes)' \
  "<PARCEL_ID>" "<GOTCHI_ID>" "<TILE_ID>" "<X>" "<Y>" 0x \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"

# broadcast
~/.foundry/bin/cast send "$REALM_DIAMOND" 'equipTile(uint256,uint256,uint256,uint256,uint256,bytes)' \
  "<PARCEL_ID>" "<GOTCHI_ID>" "<TILE_ID>" "<X>" "<Y>" 0x \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Unequip tile:
```bash
# simulate
~/.foundry/bin/cast call "$REALM_DIAMOND" 'unequipTile(uint256,uint256,uint256,uint256,uint256,bytes)' \
  "<PARCEL_ID>" "<GOTCHI_ID>" "<TILE_ID>" "<X>" "<Y>" 0x \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"

# broadcast
~/.foundry/bin/cast send "$REALM_DIAMOND" 'unequipTile(uint256,uint256,uint256,uint256,uint256,bytes)' \
  "<PARCEL_ID>" "<GOTCHI_ID>" "<TILE_ID>" "<X>" "<Y>" 0x \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Move tile:
```bash
~/.foundry/bin/cast call "$REALM_DIAMOND" 'moveTile(uint256,uint256,uint256,uint256,uint256,uint256)' \
  "<PARCEL_ID>" "<TILE_ID>" "<X0>" "<Y0>" "<X1>" "<Y1>" \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Batch Equip (Mixed Installations/Tiles)

Tuple layout:
- `types[]`: `0` installation, `1` tile
- `equip[]`: `true` equip, `false` unequip
- `ids[]`, `x[]`, `y[]` aligned by index
- `signatures[]`: legacy signatures, use `0x` for each action

Simulate example:
```bash
~/.foundry/bin/cast call "$REALM_DIAMOND" \
  'batchEquip(uint256,uint256,(uint256[],bool[],uint256[],uint256[],uint256[]),bytes[])' \
  "<PARCEL_ID>" "<GOTCHI_ID>" \
  '([0,1],[true,false],[10,27],[0,4],[0,4])' \
  '[0x,0x]' \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Coordinate Sanity Check

Use this to validate an installation currently occupies a coordinate:
```bash
~/.foundry/bin/cast call "$REALM_DIAMOND" 'checkCoordinates(uint256,uint256,uint256,uint256)' \
  "<PARCEL_ID>" "<X>" "<Y>" "<INSTALLATION_ID>" \
  --rpc-url "$BASE_MAINNET_RPC"
```

