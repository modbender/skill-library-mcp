#!/usr/bin/env bash
set -e

# Wrapper to call labradoc-cli with forwarded arguments
BIN="labradoc-cli"

if ! command -v "$BIN" >/dev/null 2>&1; then
  echo "Error: $BIN binary not found on PATH" >&2
  exit 1
fi

exec "$BIN" "$@"
