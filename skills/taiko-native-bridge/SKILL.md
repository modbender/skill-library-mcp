---
name: taiko-native-bridge
description: Use when an agent needs to bridge or claim ETH/ERC20/ERC721/ERC1155 across Taiko L1/L2 with send/wait-ready/claim workflows.
metadata: {"clawdbot":{"emoji":"🌉","requires":{"bins":["bridge-cli"]},"install":[{"id":"go-install","kind":"shell","label":"Install bridge-cli with go install","command":"go install github.com/davidcai/taiko-bridge-cli/cmd/bridge-cli@latest"}]}}
---

# taiko-bridge-cli

Use `bridge-cli` for Taiko bridge send/wait/claim flows in both directions (`L1->L2`, `L2->L1`).

## Install

Preferred (remote install):
- `go install github.com/davidcai/taiko-bridge-cli/cmd/bridge-cli@latest`

Local source build:
- `cd /path/to/taiko-bridge-cli`
- `go build -o bridge-cli ./cmd/bridge-cli`

Download binary (if release artifact is available):
- `curl -L -o bridge-cli <release-binary-url>`
- `chmod +x bridge-cli`

Quick sanity check:
- `./bridge-cli --help`
- `./bridge-cli schema`

## Environment

Set RPC and key vars once, then reuse in commands.

```bash
export BRIDGE_CLI_PRIVATE_KEY=0x...

# Direction A: L1 -> L2
export L1_RPC=https://l1-rpc
export L2_RPC=https://l2-rpc
```

Base flags template:

```bash
COMMON_FLAGS=(
  --src-rpc "$SRC_RPC"
  --dst-rpc "$DST_RPC"
  --private-key "$BRIDGE_CLI_PRIVATE_KEY"
)
```

Address override flags are optional and only needed for custom deployments.

### Missing env behavior (for agents)

Before running bridge commands, verify these required envs exist:
- `BRIDGE_CLI_PRIVATE_KEY`
- `SRC_RPC`
- `DST_RPC`

If any are missing, do not run the command. Ask the user for the missing values first.

Example prompt:
- `I’m missing required env vars: SRC_RPC, DST_RPC. Please provide them so I can continue.`

## Recommended flows

Pipeline (fastest for agents):
- ETH: `./bridge-cli claim-eth "${COMMON_FLAGS[@]}" --to 0x... --value 1 --fee 0 --gas-limit 1000000`
- ERC20: `./bridge-cli claim-erc20 "${COMMON_FLAGS[@]}" --token 0x... --amount 100 --to 0x... --fee 0`
- ERC721: `./bridge-cli claim-erc721 "${COMMON_FLAGS[@]}" --token 0x... --token-ids 1 --to 0x... --fee 0`
- ERC1155: `./bridge-cli claim-erc1155 "${COMMON_FLAGS[@]}" --token 0x... --token-ids 1 --amounts 1 --to 0x... --fee 0`

Low-level explicit (debuggable):
1. `send-*`
2. `wait-ready --tx-hash <send_tx_hash>`
3. `claim --tx-hash <send_tx_hash>`

Example ETH low-level:

```bash
SEND_JSON=$(./bridge-cli send-eth "${COMMON_FLAGS[@]}" \
  --to 0xRecipient \
  --value 1 \
  --fee 0 \
  --gas-limit 1000000)

TX_HASH=$(echo "$SEND_JSON" | jq -r '.tx_hash')

./bridge-cli wait-ready "${COMMON_FLAGS[@]}" \
  --tx-hash "$TX_HASH" \
  --timeout 20m \
  --poll-interval 5s

./bridge-cli claim "${COMMON_FLAGS[@]}" \
  --tx-hash "$TX_HASH" \
  --timeout 20m \
  --poll-interval 5s
```

## Direction switch

For `L2->L1`, swap source and destination values:
- `SRC_* = L2 values`
- `DST_* = L1 values`

Then run the exact same commands.

## Agent notes

- Default output is JSON; prefer parsing with `jq`.
- ETH gas limit safety:
  - `bridge-cli` auto-checks `getMessageMinGasLimit(len(data))`.
  - If `--gas-limit` is too low, it auto-bumps and returns:
    - `requested_gas_limit`
    - `min_gas_limit`
    - `effective_gas_limit`
    - `gas_limit_adjusted`
- `bridge-*` commands are legacy aliases of `claim-*`.
- If `claim` reverts but `status` shows `dest_message_status=2`, message was already processed (usually relayer race).

## Troubleshooting

- `wait-ready` never progresses:
  - verify you are using `signal_service` addresses, not inbox/anchor addresses.
- `execution reverted` on send:
  - check `effective_gas_limit` and bridge destination config.
- Timeouts:
  - keep polling with larger `--timeout`, then retry `claim`.
