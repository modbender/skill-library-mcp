#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEV_BOARD_DIR="${SCRIPT_DIR}/dev-board"

if [[ ! -f "${DEV_BOARD_DIR}/apps/api/src/server.js" ]]; then
  echo "Error: embedded dev-board not found at ${DEV_BOARD_DIR}" >&2
  exit 1
fi

export TEAM_DEV_SKILL_DIR="${TEAM_DEV_SKILL_DIR:-${SKILL_DIR}}"
export PORT="${PORT:-4310}"

if [[ ! -d "${TEAM_DEV_SKILL_DIR}" ]]; then
  echo "[dev-team] TEAM_DEV_SKILL_DIR not found: ${TEAM_DEV_SKILL_DIR}" >&2
  echo "[dev-team] fallback to bundled skill dir: ${SKILL_DIR}"
  export TEAM_DEV_SKILL_DIR="${SKILL_DIR}"
fi

echo "[dev-team] starting dev-board"
echo "[dev-team] skill dir: ${TEAM_DEV_SKILL_DIR}"
echo "[dev-team] url: http://localhost:${PORT}"
echo "[dev-team] local actions: ${ENABLE_LOCAL_ACTIONS:-0} (set ENABLE_LOCAL_ACTIONS=1 to enable)"

cd "${DEV_BOARD_DIR}"
npm run dev
