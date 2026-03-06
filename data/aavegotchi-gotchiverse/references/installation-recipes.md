# Installation Recipes (Foundry cast)

## Read / Verify Installation Context

Installation diamond wired addresses:
```bash
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" 'getAddresses()(address,address,address,address,address,bytes)' --rpc-url "$BASE_MAINNET_RPC"
```

Installation type data:
```bash
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" \
  'getInstallationType(uint256)((uint8,uint8,uint16,uint8,uint8,uint32,uint16,uint8,uint32,uint32,bool,uint256[4],uint256,uint256,uint256[],string))' \
  "<INSTALLATION_ID>" \
  --rpc-url "$BASE_MAINNET_RPC"

~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" \
  'getInstallationTypes(uint256[])(((uint8,uint8,uint16,uint8,uint8,uint32,uint16,uint8,uint32,uint32,bool,uint256[4],uint256,uint256,uint256[],string))[])' \
  "[<ID_1>,<ID_2>]" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Craft queue view:
```bash
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" 'getCraftQueue(address)((address,uint16,bool,uint40,uint256)[])' "$FROM_ADDRESS" --rpc-url "$BASE_MAINNET_RPC"
```

Owned balances (wallet + parcel):
```bash
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" 'installationsBalances(address)((uint256,uint256)[])' "$FROM_ADDRESS" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" 'installationBalancesOfToken(address,uint256)((uint256,uint256)[])' "$REALM_DIAMOND" "<PARCEL_ID>" --rpc-url "$BASE_MAINNET_RPC"
```

## Craft Installations

Single craft path (`uint16[] ids`, `uint40[] gltr`):
```bash
# simulate
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" 'craftInstallations(uint16[],uint40[])' "[<INSTALLATION_ID>]" "[<GLTR_BLOCKS>]" \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"

# broadcast
~/.foundry/bin/cast send "$INSTALLATION_DIAMOND" 'craftInstallations(uint16[],uint40[])' "[<INSTALLATION_ID>]" "[<GLTR_BLOCKS>]" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Batch craft path (`(uint16 installationID,uint16 amount,uint40 gltr)[]`):
```bash
# simulate
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" 'batchCraftInstallations((uint16,uint16,uint40)[])' \
  '[(10,1,0),(55,2,0)]' \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"

# broadcast
~/.foundry/bin/cast send "$INSTALLATION_DIAMOND" 'batchCraftInstallations((uint16,uint16,uint40)[])' \
  '[(10,1,0),(55,2,0)]' \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Claim crafted installations:
```bash
# simulate
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" 'claimInstallations(uint256[])' "[<QUEUE_ID_1>,<QUEUE_ID_2>]" \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"

# broadcast
~/.foundry/bin/cast send "$INSTALLATION_DIAMOND" 'claimInstallations(uint256[])' "[<QUEUE_ID_1>,<QUEUE_ID_2>]" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Reduce craft time with GLTR burn:
```bash
# simulate
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" 'reduceCraftTime(uint256[],uint40[])' "[<QUEUE_ID>]" "[<BLOCKS_TO_REDUCE>]" \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"

# broadcast
~/.foundry/bin/cast send "$INSTALLATION_DIAMOND" 'reduceCraftTime(uint256[],uint40[])' "[<QUEUE_ID>]" "[<BLOCKS_TO_REDUCE>]" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Upgrade Installations

Upgrade queue reads:
```bash
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" 'getParcelUpgradeQueue(uint256)((address,uint16,uint16,uint40,bool,uint256,uint256)[],uint256[])' "<PARCEL_ID>" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" 'getUserUpgradeQueueNew(address)((address,uint16,uint16,uint40,bool,uint256,uint256)[],uint256[])' "$FROM_ADDRESS" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" 'parcelQueueEmpty(uint256)(bool)' "<PARCEL_ID>" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" 'getUpgradeQueueId(uint256)((address,uint16,uint16,uint40,bool,uint256,uint256))' "<UPGRADE_INDEX>" --rpc-url "$BASE_MAINNET_RPC"
```

Queued upgrade (`UpgradeQueue` tuple):
- Tuple: `(owner, coordinateX, coordinateY, readyBlock, claimed, parcelId, installationId)`
- `readyBlock` and `claimed` are ignored on input and overwritten by contract.

```bash
# simulate
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" \
  'upgradeInstallation((address,uint16,uint16,uint40,bool,uint256,uint256),uint256,bytes,uint40)' \
  "($FROM_ADDRESS,<X>,<Y>,0,false,<PARCEL_ID>,<CURRENT_INSTALLATION_ID>)" "<GOTCHI_ID>" 0x "<GLTR_BLOCKS>" \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"

# broadcast
~/.foundry/bin/cast send "$INSTALLATION_DIAMOND" \
  'upgradeInstallation((address,uint16,uint16,uint40,bool,uint256,uint256),uint256,bytes,uint40)' \
  "($FROM_ADDRESS,<X>,<Y>,0,false,<PARCEL_ID>,<CURRENT_INSTALLATION_ID>)" "<GOTCHI_ID>" 0x "<GLTR_BLOCKS>" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Instant upgrade (`InstantUpgradeParams` tuple):
- Tuple: `(coordinateX, coordinateY, targetInstallationIds[], parcelId, realmDiamond)`

```bash
# simulate
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" \
  'instantUpgrade((uint16,uint16,uint256[],uint256,address),uint256,uint256,bytes)' \
  "(<X>,<Y>,[<CURRENT_ID>,<NEXT_ID>,<NEXT2_ID>],<PARCEL_ID>,$REALM_DIAMOND)" "<TOTAL_GLTR_BLOCKS>" "<GOTCHI_ID>" 0x \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"

# broadcast
~/.foundry/bin/cast send "$INSTALLATION_DIAMOND" \
  'instantUpgrade((uint16,uint16,uint256[],uint256,address),uint256,uint256,bytes)' \
  "(<X>,<Y>,[<CURRENT_ID>,<NEXT_ID>,<NEXT2_ID>],<PARCEL_ID>,$REALM_DIAMOND)" "<TOTAL_GLTR_BLOCKS>" "<GOTCHI_ID>" 0x \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Reduce queued upgrade time:
```bash
# simulate
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" 'reduceUpgradeTime(uint256,uint256,uint40,bytes)' \
  "<UPGRADE_INDEX>" "<GOTCHI_ID>" "<BLOCKS_TO_REDUCE>" 0x \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"

# broadcast
~/.foundry/bin/cast send "$INSTALLATION_DIAMOND" 'reduceUpgradeTime(uint256,uint256,uint40,bytes)' \
  "<UPGRADE_INDEX>" "<GOTCHI_ID>" "<BLOCKS_TO_REDUCE>" 0x \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Finalize ready upgrades:
```bash
# simulate
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" 'finalizeUpgrades(uint256[])' "[<UPGRADE_INDEX_1>,<UPGRADE_INDEX_2>]" \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"

# broadcast
~/.foundry/bin/cast send "$INSTALLATION_DIAMOND" 'finalizeUpgrades(uint256[])' "[<UPGRADE_INDEX_1>,<UPGRADE_INDEX_2>]" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Selector Sanity (No Funds)

```bash
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" 'craftInstallations(uint16[],uint40[])' '[]' '[]' --from "$FROM_ADDRESS" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" 'batchCraftInstallations((uint16,uint16,uint40)[])' '[]' --from "$FROM_ADDRESS" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" 'claimInstallations(uint256[])' '[]' --from "$FROM_ADDRESS" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" 'finalizeUpgrades(uint256[])' '[]' --from "$FROM_ADDRESS" --rpc-url "$BASE_MAINNET_RPC"
```

