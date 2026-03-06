#!/usr/bin/env bash
# Load Home Assistant env vars from an external file (optional).
# Behavior:
# - Loads only when HA_ENV_FILE is explicitly set.
# - Parses KEY=VALUE lines safely (no source/eval execution).
# - Imports only allowlisted keys: HA_TOKEN, HA_URL_PUBLIC, HA_URL_LOCAL, HA_URL.

set -euo pipefail

ENV_FILE="${HA_ENV_FILE:-}"

if [[ -z "$ENV_FILE" ]]; then
  exit 0
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: HA_ENV_FILE is set but file does not exist: $ENV_FILE" >&2
  exit 1
fi

if [[ ! -r "$ENV_FILE" ]]; then
  echo "Error: HA_ENV_FILE is not readable: $ENV_FILE" >&2
  exit 1
fi

allowed_key() {
  case "$1" in
    HA_TOKEN|HA_URL_PUBLIC|HA_URL_LOCAL|HA_URL) return 0 ;;
    *) return 1 ;;
  esac
}

strip_wrapping_quotes() {
  local v="$1"
  if [[ "$v" =~ ^\"(.*)\"$ ]]; then
    printf '%s' "${BASH_REMATCH[1]}"
    return
  fi
  if [[ "$v" =~ ^\'(.*)\'$ ]]; then
    printf '%s' "${BASH_REMATCH[1]}"
    return
  fi
  printf '%s' "$v"
}

while IFS= read -r raw_line || [[ -n "$raw_line" ]]; do
  line="${raw_line%$'\r'}"

  # Skip blank/comment lines
  [[ -z "${line//[[:space:]]/}" ]] && continue
  [[ "$line" =~ ^[[:space:]]*# ]] && continue

  if [[ ! "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
    echo "Warning: Skipping invalid env line in HA_ENV_FILE: $line" >&2
    continue
  fi

  key="${BASH_REMATCH[1]}"
  value="${BASH_REMATCH[2]}"

  # Trim leading spaces in value
  value="${value#${value%%[![:space:]]*}}"
  value="$(strip_wrapping_quotes "$value")"

  if ! allowed_key "$key"; then
    echo "Warning: Ignoring unsupported key in HA_ENV_FILE: $key" >&2
    continue
  fi

  export "$key=$value"
done < "$ENV_FILE"
