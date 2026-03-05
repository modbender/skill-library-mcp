#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/CJ42/potato-tipper-contracts.git"
REPO_DIR="${POTATO_TIPPER_REPO_DIR:-$(mktemp -d)/potato-tipper-contracts}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Clone repo if not already present
if [[ ! -d "$REPO_DIR/.git" ]]; then
  echo "Cloning Potato Tipper contracts into $REPO_DIR..."
  git clone "$REPO_URL" "$REPO_DIR"
fi

# Usage check
if [[ $# -lt 2 ]]; then
  cat <<EOF
Usage: setup_potato_tipper.sh <network> <up-address>

  network: luksoTestnet | lukso
  up-address: your Universal Profile address (0x...)

Required env vars:
  PRIVATE_KEY: EOA controller private key (must have ADDUNIVERSALRECEIVERDELEGATE + CALL permissions)
  TIP_AMOUNT: tip per follower in wei (e.g., "42000000000000000000" = 42 POTATO)
  MIN_FOLLOWERS: minimum follower count (e.g., "5")
  MIN_POTATO_BALANCE: minimum POTATO balance in wei (e.g., "100000000000000000000" = 100 POTATO)
  TIPPING_BUDGET: total POTATO budget in wei (e.g., "1000000000000000000000" = 1000 POTATO)

Optional env vars:
  POTATO_TIPPER_REPO_DIR: path to an existing clone of the repo (skips cloning)

Example:
  TIP_AMOUNT=42000000000000000000 \\
  MIN_FOLLOWERS=5 \\
  MIN_POTATO_BALANCE=100000000000000000000 \\
  TIPPING_BUDGET=1000000000000000000000 \\
  PRIVATE_KEY=0x... \\
  ./setup_potato_tipper.sh luksoTestnet 0xYourUPAddress
EOF
  exit 1
fi

NETWORK="$1"
UP_ADDRESS="$2"

# Network-specific addresses
if [[ "$NETWORK" == "luksoTestnet" ]]; then
  POTATO_TIPPER_ADDRESS="0xB844b12313A2D702203109E9487C24aE807e1d66"
  POTATO_TOKEN_ADDRESS="0xE8280e7f0d54daE39725dC5f500F567Af2854A13"
  RPC_URL="${LUKSO_TESTNET_RPC_URL:-https://rpc.testnet.lukso.network}"
elif [[ "$NETWORK" == "lukso" ]]; then
  POTATO_TIPPER_ADDRESS="0x5eed04004c2D46C12Fe30C639A90AD5d6F5D573d"
  POTATO_TOKEN_ADDRESS="0x80D898C5A3A0B118a0c8C8aDcdBB260FC687F1ce"
  RPC_URL="${LUKSO_MAINNET_RPC_URL:-https://rpc.mainnet.lukso.network}"
else
  echo "Unknown network: $NETWORK"
  exit 1
fi

# Validate env vars
: "${PRIVATE_KEY:?Missing PRIVATE_KEY}"
: "${TIP_AMOUNT:?Missing TIP_AMOUNT}"
: "${MIN_FOLLOWERS:?Missing MIN_FOLLOWERS}"
: "${MIN_POTATO_BALANCE:?Missing MIN_POTATO_BALANCE}"
: "${TIPPING_BUDGET:?Missing TIPPING_BUDGET}"

echo "Setting up PotatoTipper for UP: $UP_ADDRESS on $NETWORK"
echo "Repo: $REPO_DIR"
echo "RPC: $RPC_URL"
echo ""

cd "$REPO_DIR"

export UP_ADDRESS
export POTATO_TIPPER_ADDRESS
export POTATO_TOKEN_ADDRESS

forge script "$SCRIPT_DIR/SetupPotatoTipper.s.sol:SetupPotatoTipper" \
  --rpc-url "$RPC_URL" \
  --broadcast \
  --private-key "$PRIVATE_KEY"
