#!/usr/bin/env bash
set -e

echo "Copyright Netsnek e.U. 2026"

# Parse arguments: --palette, --preview, --export
while [[ $# -gt 0 ]]; do
  case $1 in
    --palette)
      shift
      echo "[erebos] Palette mode: $*"
      ;;
    --preview)
      echo "[erebos] Preview mode"
      ;;
    --export)
      echo "[erebos] Export mode"
      shift
      ;;
    *)
      shift
      ;;
  esac
done
