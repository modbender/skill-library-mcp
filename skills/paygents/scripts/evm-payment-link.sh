#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Generate a wallet deeplink for an EVM payment (native ETH or ERC20).

Usage:
  evm-payment-link.sh --to <0x...> --amount <decimal> [options]

Options:
  --to          Recipient address (required)
  --amount      Human-readable amount (required)
  --chain-id    Chain ID (default: 8453 = Base)
  --asset       ETH or ERC20 (default: ERC20)
  --token       ERC20 contract address (auto-detected for USDC on known chains)
  --decimals    Token decimals (default: 6 for ERC20, 18 for ETH)
  --symbol      Token symbol for display (default: USDC or ETH)
  --wallet      metamask | trust (default: metamask)

Supported wallets:
  metamask    MetaMask mobile (link.metamask.io deeplinks)
  trust       Trust Wallet (link.trustwallet.com deeplinks)
USAGE
}

TO=""
AMOUNT=""
CHAIN_ID="8453"
ASSET="ERC20"
TOKEN=""
DECIMALS=""
SYMBOL=""
WALLET="metamask"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --to) TO="${2:-}"; shift 2 ;;
    --amount) AMOUNT="${2:-}"; shift 2 ;;
    --chain-id) CHAIN_ID="${2:-}"; shift 2 ;;
    --asset) ASSET="$(echo "${2:-}" | tr '[:lower:]' '[:upper:]')"; shift 2 ;;
    --token) TOKEN="${2:-}"; shift 2 ;;
    --decimals) DECIMALS="${2:-}"; shift 2 ;;
    --symbol) SYMBOL="${2:-}"; shift 2 ;;
    --wallet) WALLET="$(echo "${2:-}" | tr '[:upper:]' '[:lower:]')"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ -z "$TO" || -z "$AMOUNT" ]]; then
  echo "Missing required args --to and --amount." >&2
  usage
  exit 1
fi

if [[ ! "$TO" =~ ^0x[a-fA-F0-9]{40}$ ]]; then
  echo "Invalid EVM address: $TO" >&2
  exit 1
fi

if [[ ! "$AMOUNT" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
  echo "Invalid amount: $AMOUNT" >&2
  exit 1
fi

if [[ ! "$CHAIN_ID" =~ ^[0-9]+$ ]]; then
  echo "Invalid chain id: $CHAIN_ID" >&2
  exit 1
fi

if [[ "$ASSET" != "ETH" && "$ASSET" != "ERC20" ]]; then
  echo "--asset must be ETH or ERC20" >&2
  exit 1
fi

if [[ "$WALLET" != "metamask" && "$WALLET" != "trust" ]]; then
  echo "--wallet must be metamask or trust" >&2
  exit 1
fi

# Defaults based on asset type
if [[ "$ASSET" == "ETH" ]]; then
  DECIMALS="${DECIMALS:-18}"
  SYMBOL="${SYMBOL:-ETH}"
else
  DECIMALS="${DECIMALS:-6}"
  SYMBOL="${SYMBOL:-USDC}"
  if [[ -z "$TOKEN" ]]; then
    case "$CHAIN_ID" in
      1) TOKEN="0xA0b86991c6218b36c1d19d4a2e9eb0ce3606eb48" ;;
      8453) TOKEN="0x833589fCD6eDb6E08f4c7C32D4f71b54bDa02913" ;;
      11155111) TOKEN="0x1c7d4b196cb0c7b01d743fbc6116a902379c7238" ;;
      84532) TOKEN="0x036CbD53842c5426634e7929541eC2318f3dCf7e" ;;
      *)
        echo "No default token for chain $CHAIN_ID. Provide --token." >&2
        exit 1
        ;;
    esac
  fi
  if [[ ! "$TOKEN" =~ ^0x[a-fA-F0-9]{40}$ ]]; then
    echo "Invalid token address: $TOKEN" >&2
    exit 1
  fi
fi

# Convert amount to base units
AMOUNT_BASE_UNITS="$(node -e '
const amount = process.argv[1];
const decimals = Number(process.argv[2]);
if (!/^\d+(\.\d+)?$/.test(amount)) process.exit(2);
const [whole, fracRaw = ""] = amount.split(".");
if (fracRaw.length > decimals) { console.error("Too many decimals"); process.exit(3); }
const frac = (fracRaw + "0".repeat(decimals)).slice(0, decimals);
const value = BigInt(whole) * (10n ** BigInt(decimals)) + BigInt(frac || "0");
process.stdout.write(value.toString());
' "$AMOUNT" "$DECIMALS")"

SHORT_TO="${TO:0:8}...${TO: -6}"

# Trust Wallet uses SLIP-44 coin type in asset identifier
# c60 = Ethereum ecosystem. Token format: c60_t<tokenAddress>
# For native ETH: asset=c60
# For ERC20: asset=c60_t<tokenAddress>
# Note: Trust Wallet uses the same c60 prefix for all EVM chains,
# chain switching is handled by the wallet based on the token address.

# Build deeplink per wallet
build_metamask_deeplink() {
  if [[ "$ASSET" == "ETH" ]]; then
    echo "https://link.metamask.io/send/${TO}@${CHAIN_ID}?value=${AMOUNT_BASE_UNITS}"
  else
    echo "https://link.metamask.io/send/${TOKEN}@${CHAIN_ID}/transfer?address=${TO}&uint256=${AMOUNT_BASE_UNITS}"
  fi
}

build_trust_deeplink() {
  if [[ "$ASSET" == "ETH" ]]; then
    echo "https://link.trustwallet.com/send?asset=c60&address=${TO}&amount=${AMOUNT}"
  else
    echo "https://link.trustwallet.com/send?asset=c60_t${TOKEN}&address=${TO}&amount=${AMOUNT}"
  fi
}

case "$WALLET" in
  metamask) DEEPLINK="$(build_metamask_deeplink)" ;;
  trust)    DEEPLINK="$(build_trust_deeplink)" ;;
esac

# Build intent JSON
if [[ "$ASSET" == "ETH" ]]; then
  INTENT_JSON="{
    \"chain\": \"evm\",
    \"chainId\": ${CHAIN_ID},
    \"asset\": \"ETH\",
    \"symbol\": \"${SYMBOL}\",
    \"decimals\": ${DECIMALS},
    \"to\": \"${TO}\",
    \"amountHuman\": \"${AMOUNT}\",
    \"amountBaseUnits\": \"${AMOUNT_BASE_UNITS}\"
  }"
else
  INTENT_JSON="{
    \"chain\": \"evm\",
    \"chainId\": ${CHAIN_ID},
    \"asset\": \"ERC20\",
    \"token\": \"${TOKEN}\",
    \"symbol\": \"${SYMBOL}\",
    \"decimals\": ${DECIMALS},
    \"to\": \"${TO}\",
    \"amountHuman\": \"${AMOUNT}\",
    \"amountBaseUnits\": \"${AMOUNT_BASE_UNITS}\"
  }"
fi

WALLET_DISPLAY="$(echo "$WALLET" | sed 's/metamask/MetaMask/;s/trust/Trust Wallet/')"

cat <<JSON
{
  "intent": ${INTENT_JSON},
  "wallet": "${WALLET}",
  "deeplink": "${DEEPLINK}",
  "messageTemplate": "Payment request: ${AMOUNT} ${SYMBOL} to ${SHORT_TO}. Tap to open ${WALLET_DISPLAY} and approve. Reject if recipient or amount doesn't match."
}
JSON
