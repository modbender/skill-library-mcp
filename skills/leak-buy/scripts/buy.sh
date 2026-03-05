#!/usr/bin/env bash
set -euo pipefail

# Buy from a leak promo URL (/) or buy URL (/download) and save the artifact.
#
# Usage:
#   bash skills/leak-buy/scripts/buy.sh <promo_or_download_url> [--download-code <code>] --buyer-private-key-file <path> [--out <path> | --basename <name>]
#
# Examples:
#   bash skills/leak-buy/scripts/buy.sh "https://xxxx.trycloudflare.com/" --buyer-private-key-file ./buyer.key
#   bash skills/leak-buy/scripts/buy.sh "https://xxxx.trycloudflare.com/download" --download-code friends-only --buyer-private-key-file ./buyer.key
#   bash skills/leak-buy/scripts/buy.sh "https://xxxx.trycloudflare.com/download" --buyer-private-key-file ./buyer.key --basename myfile
#   bash skills/leak-buy/scripts/buy.sh "https://xxxx.trycloudflare.com/" --buyer-private-key-file ./buyer.key --out ./downloads/myfile.bin

validate_download_url() {
  local url="$1"
  if [ -z "$url" ]; then
    echo "[leak-buy] ERROR: promo/download URL is required."
    exit 1
  fi
  # Defense-in-depth: reject whitespace/control chars and require http(s).
  if [[ "$url" =~ [[:space:][:cntrl:]] ]]; then
    echo "[leak-buy] ERROR: URL contains invalid whitespace/control characters."
    exit 1
  fi
  if ! [[ "$url" =~ ^https?://[^[:space:]]+$ ]]; then
    echo "[leak-buy] ERROR: URL must start with http:// or https://."
    exit 1
  fi
}

normalize_input_path() {
  local p="$1"
  if [[ "$p" == ~/* ]]; then
    echo "${HOME}/${p#~/}"
    return
  fi
  echo "$p"
}

resolve_abs_path() {
  local raw="$1"
  local dir
  local base
  dir="$(cd "$(dirname "$raw")" && pwd -P)" || return 1
  base="$(basename "$raw")"
  echo "${dir}/${base}"
}

run_leak() {
  if command -v leak >/dev/null 2>&1; then
    exec leak "$@"
  fi
  echo "[leak-buy] ERROR: leak is not installed on PATH."
  echo "[leak-buy] Install leak-cli first: npm i -g leak-cli"
  exit 1
}

if [ "$#" -lt 1 ]; then
  echo "Usage: bash skills/leak-buy/scripts/buy.sh <promo_or_download_url> [--download-code <code>] --buyer-private-key-file <path> [--out <path> | --basename <name>]"
  exit 1
fi

DOWNLOAD_URL="$1"
shift
validate_download_url "$DOWNLOAD_URL"

BLOCKED_RAW_FLAG="--buyer-private-key"
BLOCKED_STDIN_FLAG="--buyer-private-key""-stdin"

BUYER_KEY_FILE=""
for ARG in "$@"; do
  case "$ARG" in
    "$BLOCKED_RAW_FLAG"|"$BLOCKED_RAW_FLAG"=*)
      echo "[leak-buy] ERROR: --buyer-private-key is blocked."
      echo "[leak-buy] Use --buyer-private-key-file <path>."
      exit 1
      ;;
    "$BLOCKED_STDIN_FLAG"|"$BLOCKED_STDIN_FLAG"=*)
      echo "[leak-buy] ERROR: stdin key mode is blocked for this hardened skill."
      echo "[leak-buy] Use --buyer-private-key-file <path>."
      exit 1
      ;;
  esac
done

HAS_KEY_FILE=0
PREV=""
for ARG in "$@"; do
  if [ "$PREV" = "--buyer-private-key-file" ]; then
    HAS_KEY_FILE=1
    BUYER_KEY_FILE="$ARG"
    PREV=""
    continue
  fi
  case "$ARG" in
    --buyer-private-key-file)
      PREV="--buyer-private-key-file"
      ;;
    --buyer-private-key-file=*)
      HAS_KEY_FILE=1
      BUYER_KEY_FILE="${ARG#--buyer-private-key-file=}"
      ;;
  esac
done

if [ "$HAS_KEY_FILE" -eq 0 ]; then
  echo "[leak-buy] ERROR: --buyer-private-key-file <path> is required."
  exit 1
fi

if [ "$PREV" = "--buyer-private-key-file" ]; then
  echo "[leak-buy] ERROR: --buyer-private-key-file requires a path value."
  exit 1
fi

if [ -z "$BUYER_KEY_FILE" ]; then
  echo "[leak-buy] ERROR: --buyer-private-key-file path cannot be empty."
  exit 1
fi

if [[ "$BUYER_KEY_FILE" =~ [[:space:][:cntrl:]] ]]; then
  echo "[leak-buy] ERROR: key file path contains invalid whitespace/control characters."
  exit 1
fi

KEY_FILE_PATH="$(normalize_input_path "$BUYER_KEY_FILE")"
ABS_KEY_FILE_PATH="$(resolve_abs_path "$KEY_FILE_PATH")" || {
  echo "[leak-buy] ERROR: cannot resolve key file path: $BUYER_KEY_FILE"
  exit 1
}

if [ -L "$KEY_FILE_PATH" ]; then
  echo "[leak-buy] ERROR: key file path cannot be a symlink: $BUYER_KEY_FILE"
  exit 1
fi

if [ ! -f "$KEY_FILE_PATH" ]; then
  echo "[leak-buy] ERROR: key file must exist and be a regular file: $BUYER_KEY_FILE"
  exit 1
fi

if [ ! -r "$KEY_FILE_PATH" ]; then
  echo "[leak-buy] ERROR: key file is not readable: $BUYER_KEY_FILE"
  exit 1
fi

echo "[leak-buy] Using buyer key file: ${ABS_KEY_FILE_PATH}"

run_leak buy "$DOWNLOAD_URL" "$@"
