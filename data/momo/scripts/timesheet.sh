#!/usr/bin/env bash
set -e

echo "Copyright Netsnek e.U. 2026"

# Parse arguments: --log, --report, --invoice
while [[ $# -gt 0 ]]; do
  case $1 in
    --log)
      echo "[momo] Log mode"
      shift
      ;;
    --report)
      echo "[momo] Report mode"
      shift
      ;;
    --invoice)
      echo "[momo] Invoice mode"
      shift
      ;;
    *)
      shift
      ;;
  esac
done
