#!/usr/bin/env bash
set -euo pipefail

WALLET_JSON_FILE="${HOME}/.apiosk/wallet.json"
WALLET_TXT_FILE="${HOME}/.apiosk/wallet.txt"

trim() {
  local v="$1"
  # shellcheck disable=SC2001
  echo "$(echo "$v" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
}

lowercase_wallet() {
  echo "$1" | tr '[:upper:]' '[:lower:]'
}

validate_wallet_format() {
  local wallet="$1"
  [[ "$wallet" =~ ^0x[a-fA-F0-9]{40}$ ]]
}

load_wallet_address() {
  local explicit_wallet="${1:-}"

  if [[ -n "$explicit_wallet" ]]; then
    echo "$explicit_wallet"
    return 0
  fi

  if [[ -f "$WALLET_JSON_FILE" ]]; then
    local from_json
    from_json="$(jq -r '.address // empty' "$WALLET_JSON_FILE")"
    from_json="$(trim "$from_json")"
    if [[ -n "$from_json" ]]; then
      echo "$from_json"
      return 0
    fi
  fi

  if [[ -f "$WALLET_TXT_FILE" ]]; then
    local from_txt
    from_txt="$(cat "$WALLET_TXT_FILE")"
    from_txt="$(trim "$from_txt")"
    if [[ -n "$from_txt" ]]; then
      echo "$from_txt"
      return 0
    fi
  fi

  return 1
}

load_private_key() {
  local explicit_private_key="${1:-}"

  if [[ -n "$explicit_private_key" ]]; then
    echo "$explicit_private_key"
    return 0
  fi

  if [[ -n "${APIOSK_PRIVATE_KEY:-}" ]]; then
    echo "$APIOSK_PRIVATE_KEY"
    return 0
  fi

  if [[ -f "$WALLET_JSON_FILE" ]]; then
    local from_json
    from_json="$(jq -r '.private_key // empty' "$WALLET_JSON_FILE")"
    from_json="$(trim "$from_json")"
    if [[ -n "$from_json" ]]; then
      echo "$from_json"
      return 0
    fi
  fi

  return 1
}

require_signing_bin() {
  if ! command -v cast >/dev/null 2>&1; then
    echo "Error: 'cast' is required for signed wallet auth."
    echo "Install Foundry: https://book.getfoundry.sh/getting-started/installation"
    exit 1
  fi
}

generate_nonce() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex 16
    return 0
  fi

  if command -v uuidgen >/dev/null 2>&1; then
    uuidgen | tr '[:upper:]' '[:lower:]' | tr -d '-'
    return 0
  fi

  date +%s%N
}

sign_wallet_auth() {
  local action="$1"
  local resource="$2"
  local wallet="$3"
  local private_key="$4"

  AUTH_TIMESTAMP="$(date +%s)"
  AUTH_NONCE="$(generate_nonce)"

  local lower_wallet
  lower_wallet="$(lowercase_wallet "$wallet")"

  local message
  message="$(printf 'Apiosk auth\naction:%s\nwallet:%s\nresource:%s\ntimestamp:%s\nnonce:%s' \
    "$action" "$lower_wallet" "$resource" "$AUTH_TIMESTAMP" "$AUTH_NONCE")"

  AUTH_SIGNATURE="$(cast wallet sign --private-key "$private_key" "$message" | tr -d '\r\n')"
}
