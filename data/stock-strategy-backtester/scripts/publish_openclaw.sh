#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

SLUG="${OPENCLAW_SKILL_SLUG:-stock-strategy-backtester}"
VERSION="${1:-1.0.0}"
CHANGELOG="${2:-Initial release: stock strategy backtesting with win-rate and return analytics.}"

if ! command -v clawhub >/dev/null 2>&1; then
  echo "clawhub CLI not found."
  echo "Install: npm install -g clawhub"
  exit 1
fi

echo "Publishing ${SLUG}@${VERSION} from ${SKILL_DIR}"
if ! clawhub whoami >/dev/null 2>&1; then
  clawhub login
fi
clawhub publish "${SKILL_DIR}" \
  --slug "${SLUG}" \
  --version "${VERSION}" \
  --tags "latest,stocks,quant,backtest" \
  --changelog "${CHANGELOG}"
