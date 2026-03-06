# Tile Recipes (Foundry cast)

## Read / Verify Tile Context

Tile type data:
```bash
~/.foundry/bin/cast call "$TILE_DIAMOND" \
  'getTileType(uint256)((uint8,uint8,bool,uint16,uint32,uint256[4],string))' \
  "<TILE_ID>" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Tile craft queue:
```bash
~/.foundry/bin/cast call "$TILE_DIAMOND" 'getCraftQueue(address)((uint256,uint40,uint16,bool,address)[])' "$FROM_ADDRESS" --rpc-url "$BASE_MAINNET_RPC"
```

Owned balances (wallet + parcel):
```bash
~/.foundry/bin/cast call "$TILE_DIAMOND" 'tilesBalances(address)((uint256,uint256)[])' "$FROM_ADDRESS" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$TILE_DIAMOND" 'tileBalancesOfToken(address,uint256)((uint256,uint256)[])' "$REALM_DIAMOND" "<PARCEL_ID>" --rpc-url "$BASE_MAINNET_RPC"
```

## Craft Tiles

Craft path (`uint16[]`):
```bash
# simulate
~/.foundry/bin/cast call "$TILE_DIAMOND" 'craftTiles(uint16[])' "[<TILE_ID>]" \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"

# broadcast
~/.foundry/bin/cast send "$TILE_DIAMOND" 'craftTiles(uint16[])' "[<TILE_ID>]" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Batch craft (`(uint16 tileID,uint16 amount,uint40 gltr)[]`):
```bash
# simulate
~/.foundry/bin/cast call "$TILE_DIAMOND" 'batchCraftTiles((uint16,uint16,uint40)[])' \
  '[(27,1,0),(26,2,0)]' \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"

# broadcast
~/.foundry/bin/cast send "$TILE_DIAMOND" 'batchCraftTiles((uint16,uint16,uint40)[])' \
  '[(27,1,0),(26,2,0)]' \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Claim crafted tiles:
```bash
# simulate
~/.foundry/bin/cast call "$TILE_DIAMOND" 'claimTiles(uint256[])' "[<QUEUE_ID_1>,<QUEUE_ID_2>]" \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"

# broadcast
~/.foundry/bin/cast send "$TILE_DIAMOND" 'claimTiles(uint256[])' "[<QUEUE_ID_1>,<QUEUE_ID_2>]" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Reduce craft time with GLTR:
```bash
# simulate
~/.foundry/bin/cast call "$TILE_DIAMOND" 'reduceCraftTime(uint256[],uint40[])' "[<QUEUE_ID>]" "[<BLOCKS_TO_REDUCE>]" \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"

# broadcast
~/.foundry/bin/cast send "$TILE_DIAMOND" 'reduceCraftTime(uint256[],uint40[])' "[<QUEUE_ID>]" "[<BLOCKS_TO_REDUCE>]" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Build on Parcel with Tiles (Realm)

Tile equip/unequip/move are called through `REALM_DIAMOND`:
- `equipTile(uint256,uint256,uint256,uint256,uint256,bytes)`
- `unequipTile(uint256,uint256,uint256,uint256,uint256,bytes)`
- `moveTile(uint256,uint256,uint256,uint256,uint256,uint256)`

Use `references/realm-recipes.md` commands for those flows.

## Selector Sanity (No Funds)

```bash
~/.foundry/bin/cast call "$TILE_DIAMOND" 'craftTiles(uint16[])' '[]' --from "$FROM_ADDRESS" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$TILE_DIAMOND" 'batchCraftTiles((uint16,uint16,uint40)[])' '[]' --from "$FROM_ADDRESS" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$TILE_DIAMOND" 'claimTiles(uint256[])' '[]' --from "$FROM_ADDRESS" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$TILE_DIAMOND" 'reduceCraftTime(uint256[],uint40[])' '[]' '[]' --from "$FROM_ADDRESS" --rpc-url "$BASE_MAINNET_RPC"
```

