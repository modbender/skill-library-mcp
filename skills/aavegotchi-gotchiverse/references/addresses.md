# Addresses / Constants (Base Mainnet)

Chain:
- Chain ID: `8453`
- Default RPC: `https://mainnet.base.org`

Diamonds:
- `REALM_DIAMOND=0x4B0040c3646D3c44B8a28Ad7055cfCF536c05372`
- `INSTALLATION_DIAMOND=0xebba5b725A2889f7f089a6cAE0246A32cad4E26b`
- `TILE_DIAMOND=0x617fdB8093b309e4699107F48812b407A7c37938`
- `AAVEGOTCHI_DIAMOND=0xA99c4B08201F2913Db8D28e71d020c4298F29dBF`

Alchemica + GLTR tokens:
- `FUD=0x2028b4043e6722Ea164946c82fe806c4a43a0fF4`
- `FOMO=0xA32137bfb57d2b6A9Fd2956Ba4B54741a6D54b58`
- `ALPHA=0x15e7CaC885e3730ce6389447BC0f7AC032f31947`
- `KEK=0xE52b9170fF4ece4C35E796Ffd74B57Dec68Ca0e5`
- `GLTR=0x4D140CE792bEdc430498c2d219AfBC33e2992c9D`

Subgraphs:
- `GOTCHIVERSE_SUBGRAPH_URL=https://api.goldsky.com/api/public/project_cmh3flagm0001r4p25foufjtt/subgraphs/gotchiverse-base/prod/gn`
- `CORE_SUBGRAPH_URL=https://api.goldsky.com/api/public/project_cmh3flagm0001r4p25foufjtt/subgraphs/aavegotchi-core-base/prod/gn`

Owner sanity (observed onchain):
- Realm/Installation/Tile owner: `0xf52398257A254D541F392667600901f710a006eD`
- FUD/FOMO/ALPHA/KEK/GLTR owner: `0x3a2E7D1E98A4a051B0766f866237c73643fDF360`

Recommended exports:
```bash
export BASE_MAINNET_RPC="${BASE_MAINNET_RPC:-https://mainnet.base.org}"

export REALM_DIAMOND="${REALM_DIAMOND:-0x4B0040c3646D3c44B8a28Ad7055cfCF536c05372}"
export INSTALLATION_DIAMOND="${INSTALLATION_DIAMOND:-0xebba5b725A2889f7f089a6cAE0246A32cad4E26b}"
export TILE_DIAMOND="${TILE_DIAMOND:-0x617fdB8093b309e4699107F48812b407A7c37938}"
export AAVEGOTCHI_DIAMOND="${AAVEGOTCHI_DIAMOND:-0xA99c4B08201F2913Db8D28e71d020c4298F29dBF}"

export FUD="${FUD:-0x2028b4043e6722Ea164946c82fe806c4a43a0fF4}"
export FOMO="${FOMO:-0xA32137bfb57d2b6A9Fd2956Ba4B54741a6D54b58}"
export ALPHA="${ALPHA:-0x15e7CaC885e3730ce6389447BC0f7AC032f31947}"
export KEK="${KEK:-0xE52b9170fF4ece4C35E796Ffd74B57Dec68Ca0e5}"
export GLTR="${GLTR:-0x4D140CE792bEdc430498c2d219AfBC33e2992c9D}"

export GOTCHIVERSE_SUBGRAPH_URL="${GOTCHIVERSE_SUBGRAPH_URL:-https://api.goldsky.com/api/public/project_cmh3flagm0001r4p25foufjtt/subgraphs/gotchiverse-base/prod/gn}"
export CORE_SUBGRAPH_URL="${CORE_SUBGRAPH_URL:-https://api.goldsky.com/api/public/project_cmh3flagm0001r4p25foufjtt/subgraphs/aavegotchi-core-base/prod/gn}"

export DRY_RUN="${DRY_RUN:-1}"
```

Verification snippets:
```bash
~/.foundry/bin/cast chain-id --rpc-url "$BASE_MAINNET_RPC"

~/.foundry/bin/cast code "$REALM_DIAMOND" --rpc-url "$BASE_MAINNET_RPC" | wc -c
~/.foundry/bin/cast code "$INSTALLATION_DIAMOND" --rpc-url "$BASE_MAINNET_RPC" | wc -c
~/.foundry/bin/cast code "$TILE_DIAMOND" --rpc-url "$BASE_MAINNET_RPC" | wc -c

~/.foundry/bin/cast call "$REALM_DIAMOND" 'owner()(address)' --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$INSTALLATION_DIAMOND" 'owner()(address)' --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$TILE_DIAMOND" 'owner()(address)' --rpc-url "$BASE_MAINNET_RPC"

~/.foundry/bin/cast call "$FUD" 'symbol()(string)' --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$FUD" 'decimals()(uint8)' --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$FUD" 'owner()(address)' --rpc-url "$BASE_MAINNET_RPC"

~/.foundry/bin/cast call "$REALM_DIAMOND" 'getAlchemicaAddresses()(address[4])' --rpc-url "$BASE_MAINNET_RPC"
```

