#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PUBLISH_SCRIPT="${SCRIPT_DIR}/publish_openclaw.sh"

VERSION="${1:-1.0.1}"
CHANGELOG="${2:-Add A/B marketplace copy variants and Chinese listing text for conversion optimization.}"
MAX_RETRIES="${3:-8}"
SLEEP_SECONDS="${4:-45}"

for ((i=1; i<=MAX_RETRIES; i++)); do
  echo "[${i}/${MAX_RETRIES}] Publishing version ${VERSION}..."
  OUTPUT="$(bash "${PUBLISH_SCRIPT}" "${VERSION}" "${CHANGELOG}" 2>&1 || true)"
  echo "${OUTPUT}"

  if [[ "${OUTPUT}" == *"Published stock-strategy-backtester@${VERSION}"* ]]; then
    echo "Publish succeeded."
    exit 0
  fi

  if [[ "${OUTPUT}" == *"Rate limit exceeded"* ]]; then
    if [[ "${i}" -lt "${MAX_RETRIES}" ]]; then
      echo "Rate limited, waiting ${SLEEP_SECONDS}s before retry..."
      sleep "${SLEEP_SECONDS}"
      continue
    fi
  fi

  echo "Publish failed with non-retryable output."
  exit 1
done

echo "Publish retries exhausted."
exit 1

