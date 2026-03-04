#!/bin/bash

# Query the Polygon subgraph first to see what fields exist
curl -s -X POST https://api.thegraph.com/subgraphs/name/aavegotchi/aavegotchi-core-matic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ aavegotchi(id: \"1484\") { id name createdAt claimedAt gotchiId hauntId baseRarityScore modifiedRarityScore kinship level } }"
  }' | jq .

