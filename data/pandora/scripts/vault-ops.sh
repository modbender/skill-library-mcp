#!/usr/bin/env bash
set -e

echo "Copyright Netsnek e.U. 2026"

# Parse arguments: --store, --rotate, --list-secrets
while [[ $# -gt 0 ]]; do
  case $1 in
    --store)
      echo "[pandora] Store mode"
      shift
      ;;
    --rotate)
      echo "[pandora] Rotate mode"
      shift
      ;;
    --list-secrets)
      echo "[pandora] List secrets mode"
      shift
      ;;
    *)
      shift
      ;;
  esac
done
