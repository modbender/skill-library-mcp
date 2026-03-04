# Parcel Access Rights

Access-rights are stored on `REALM_DIAMOND` and checked by `LibRealm.verifyAccessRight`.

## Action Rights (`actionRight`)

- `0`: channel alchemica
- `1`: empty reservoir / claim available alchemica
- `2`: equip installations
- `3`: equip tiles
- `4`: unequip installations (legacy mapping)
- `5`: unequip tiles (legacy mapping)
- `6`: upgrade installations

## Access Modes (`accessRight`)

- `0`: only parcel owner
- `1`: owner or valid borrower of a lent gotchi
- `2`: whitelist only (`whitelistId` required)
- `3`: legacy blacklisted mode (no explicit enforcement branch in current library; treat as permissive/legacy)
- `4`: anyone

## Read Current Access Rights Onchain

```bash
~/.foundry/bin/cast call "$REALM_DIAMOND" 'getParcelsAccessRights(uint256[],uint256[])(uint256[])' \
  "[<PARCEL_ID>]" "[<ACTION_RIGHT>]" \
  --rpc-url "$BASE_MAINNET_RPC"

~/.foundry/bin/cast call "$REALM_DIAMOND" 'getParcelsAccessRightsWhitelistIds(uint256[],uint256[])(uint256[])' \
  "[<PARCEL_ID>]" "[<ACTION_RIGHT>]" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Read Access Rights from Subgraph

```bash
curl -s "$GOTCHIVERSE_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{
  "query":"query($parcelId:String!){ parcelAccessRights(where:{parcel:$parcelId}, orderBy:actionRight, orderDirection:asc){ actionRight accessRight whitelistId parcel{ tokenId owner } } }",
  "variables":{"parcelId":"<PARCEL_ID_AS_STRING>"}
}'
```

## Set Access Rights (No Whitelist)

Simulate:
```bash
~/.foundry/bin/cast call "$REALM_DIAMOND" 'setParcelsAccessRights(uint256[],uint256[],uint256[])' \
  "[<PARCEL_ID>]" "[<ACTION_RIGHT>]" "[<ACCESS_RIGHT>]" \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Broadcast:
```bash
~/.foundry/bin/cast send "$REALM_DIAMOND" 'setParcelsAccessRights(uint256[],uint256[],uint256[])' \
  "[<PARCEL_ID>]" "[<ACTION_RIGHT>]" "[<ACCESS_RIGHT>]" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Set Access Rights With Whitelist

Use when `accessRight = 2`.

Simulate:
```bash
~/.foundry/bin/cast call "$REALM_DIAMOND" 'setParcelsAccessRightWithWhitelists(uint256[],uint256[],uint256[],uint32[])' \
  "[<PARCEL_ID>]" "[<ACTION_RIGHT>]" "[2]" "[<WHITELIST_ID>]" \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Broadcast:
```bash
~/.foundry/bin/cast send "$REALM_DIAMOND" 'setParcelsAccessRightWithWhitelists(uint256[],uint256[],uint256[],uint32[])' \
  "[<PARCEL_ID>]" "[<ACTION_RIGHT>]" "[2]" "[<WHITELIST_ID>]" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Preflight Authorization Check

Use this to verify a sender/gotchi pair can execute an action:

```bash
~/.foundry/bin/cast call "$REALM_DIAMOND" 'verifyAccessRight(uint256,uint256,uint256,address)' \
  "<PARCEL_ID>" "<GOTCHI_ID>" "<ACTION_RIGHT>" "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"
```

