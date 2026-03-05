# Subgraph Queries (Base)

Endpoints:
- `GOTCHIVERSE_SUBGRAPH_URL=https://api.goldsky.com/api/public/project_cmh3flagm0001r4p25foufjtt/subgraphs/gotchiverse-base/prod/gn`
- `CORE_SUBGRAPH_URL=https://api.goldsky.com/api/public/project_cmh3flagm0001r4p25foufjtt/subgraphs/aavegotchi-core-base/prod/gn`

Notes:
- Subgraph `Bytes` filters should use lowercase addresses.
- Use gotchiverse subgraph for parcel/installations/tiles state.
- Use core subgraph for supporting Aavegotchi/market context.

## Reachability Smoke Tests

```bash
curl -s "$GOTCHIVERSE_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{"query":"{ __schema { queryType { fields { name } } } }"}' \
  | python3 -c 'import json,sys; f=[x["name"] for x in json.load(sys.stdin)["data"]["__schema"]["queryType"]["fields"]]; print([n for n in ("parcel","parcels","installationTypes","tileTypes","parcelAccessRights") if n in f])'

curl -s "$CORE_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{"query":"{ __schema { queryType { fields { name } } } }"}' \
  | python3 -c 'import json,sys; f=[x["name"] for x in json.load(sys.stdin)["data"]["__schema"]["queryType"]["fields"]]; print([n for n in ("aavegotchi","erc721Listings","erc1155Listings") if n in f])'
```

## Parcel by ID

```bash
curl -s "$GOTCHIVERSE_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{
  "query":"query($id:ID!){ parcel(id:$id){ id tokenId parcelId owner coordinateX coordinateY district size surveyRound lastChanneledAlchemica lastClaimedAlchemica remainingAlchemica totalAlchemicaClaimed equippedInstallationsBalance equippedTilesBalance equippedInstallations{ id installationType name level alchemicaType capacity harvestRate craftTime prerequisites alchemicaCost } equippedTiles{ id tileType name width height craftTime alchemicaCost } } }",
  "variables":{"id":"59"}
}'
```

## Parcels by Owner

```bash
curl -s "$GOTCHIVERSE_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{
  "query":"query($owner:Bytes!){ parcels(first:50, orderBy: tokenId, orderDirection: asc, where:{owner:$owner}){ id tokenId parcelId owner size surveyRound remainingAlchemica equippedInstallationsBalance equippedTilesBalance } }",
  "variables":{"owner":"<FROM_ADDRESS_LOWERCASE>"}
}'
```

## Equipped Installations for a Parcel

```bash
curl -s "$GOTCHIVERSE_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{
  "query":"query($parcelId:String!){ installations(where:{parcel:$parcelId, equipped:true}){ id x y owner parcel{ id tokenId parcelId } type{ id name installationType level alchemicaType capacity harvestRate craftTime nextLevelId prerequisites alchemicaCost spillRate spillRadius } } }",
  "variables":{"parcelId":"59"}
}'
```

## Equipped Tiles for a Parcel

```bash
curl -s "$GOTCHIVERSE_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{
  "query":"query($parcelId:String!){ tiles(where:{parcel:$parcelId, equipped:true}){ id x y owner parcel{ id tokenId parcelId } type{ id name tileType width height craftTime alchemicaCost } } }",
  "variables":{"parcelId":"59"}
}'
```

## Installation and Tile Types

```bash
curl -s "$GOTCHIVERSE_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{
  "query":"{ installationTypes(first:1000){ id name installationType level alchemicaType craftTime harvestRate capacity nextLevelId upgradeQueueBoost prerequisites deprecated deprecatedAt alchemicaCost spillRate spillRadius amount } }"
}'

curl -s "$GOTCHIVERSE_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{
  "query":"{ tileTypes(first:1000){ id name tileType width height craftTime deprecated deprecatedAt alchemicaCost amount uri } }"
}'
```

## Parcel Access Rights

```bash
curl -s "$GOTCHIVERSE_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{
  "query":"query($parcelId:String!){ parcelAccessRights(where:{parcel:$parcelId}, orderBy:actionRight, orderDirection:asc){ id actionRight accessRight whitelistId parcel{ id tokenId owner } } }",
  "variables":{"parcelId":"59"}
}'
```

## Core Subgraph: Gotchi Context

```bash
curl -s "$CORE_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{
  "query":"query($id:ID!){ aavegotchi(id:$id){ id name kinship } }",
  "variables":{"id":"100"}
}'
```

## Core Subgraph: Active Parcel Listings (Optional Market Context)

```bash
curl -s "$CORE_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{
  "query":"query($parcelContract:Bytes!){ erc721Listings(first:50, orderBy:timeCreated, orderDirection:desc, where:{cancelled:false, timePurchased:\"0\", erc721TokenAddress:$parcelContract}){ id tokenId seller priceInWei timeCreated } }",
  "variables":{"parcelContract":"0x4b0040c3646d3c44b8a28ad7055cfcf536c05372"}
}'
```
