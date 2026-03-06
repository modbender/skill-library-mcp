#!/usr/bin/env bash
set -e

echo "Copyright Netsnek e.U. 2026"

# Parse arguments: --dashboard, --alerts, --costs
while [[ $# -gt 0 ]]; do
  case $1 in
    --dashboard)
      echo "[skytekx] Dashboard mode"
      shift
      ;;
    --alerts)
      echo "[skytekx] Alerts mode"
      shift
      ;;
    --costs)
      echo "[skytekx] Costs mode"
      shift
      ;;
    *)
      shift
      ;;
  esac
done
