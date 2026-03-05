#!/usr/bin/env bash
set -euo pipefail

SLUG="${1:-stock-strategy-backtester}"
ATTEMPTS="${2:-12}"
SLEEP_SECONDS="${3:-30}"

for ((i=1; i<=ATTEMPTS; i++)); do
  echo "[${i}/${ATTEMPTS}] Checking ${SLUG}..."
  OUTPUT="$(clawhub inspect "${SLUG}" 2>&1 || true)"
  echo "${OUTPUT}"
  if [[ "${OUTPUT}" != *"hidden while security scan is pending"* ]] && [[ "${OUTPUT}" != *"Error:"* ]]; then
    echo "Status looks ready."
    exit 0
  fi
  if [[ "${i}" -lt "${ATTEMPTS}" ]]; then
    sleep "${SLEEP_SECONDS}"
  fi
done

echo "Still pending or inaccessible after ${ATTEMPTS} checks."
exit 1

