#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_PATH="$BASE_DIR/references/kb-config.json"
KB_PATH=""
MODE="safe"   # safe|commit|status
BRANCH=""
MSG="chore(kb): sync"
NO_PUSH=0

usage() {
  cat <<EOF
Usage:
  sync_kb.sh [--config <path>] [--kb <path>] [--mode safe|commit|status] [--branch <name>] [--message <msg>] [--no-push]

Defaults are loaded from config JSON:
  $CONFIG_PATH
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config) CONFIG_PATH="$2"; shift 2 ;;
    --kb) KB_PATH="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --branch) BRANCH="$2"; shift 2 ;;
    --message) MSG="$2"; shift 2 ;;
    --no-push) NO_PUSH=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 1 ;;
  esac
done

if [[ -f "$CONFIG_PATH" ]] && command -v jq >/dev/null 2>&1; then
  [[ -z "$KB_PATH" ]] && KB_PATH="$(jq -r '.local_path // empty' "$CONFIG_PATH")"
  [[ -z "$BRANCH" ]] && BRANCH="$(jq -r '.branch // "main"' "$CONFIG_PATH")"
fi

[[ -z "$BRANCH" ]] && BRANCH="main"

if [[ -z "$KB_PATH" || "$KB_PATH" == *"<"* ]]; then
  echo "ERROR: local_path is not configured. Set in kb-config.json or pass --kb." >&2
  exit 2
fi

if [[ ! -d "$KB_PATH/.git" ]]; then
  echo "ERROR: $KB_PATH is not a git repo" >&2
  exit 2
fi

has_markers() {
  grep -R --exclude-dir=.git -nE '^(<<<<<<<|=======|>>>>>>>)' "$KB_PATH" >/dev/null 2>&1
}

if [[ "$MODE" == "status" ]]; then
  git -C "$KB_PATH" fetch origin "$BRANCH" >/dev/null 2>&1 || true
  echo "--- git status ---"
  git -C "$KB_PATH" status -sb
  exit 0
fi

git -C "$KB_PATH" fetch origin "$BRANCH"
git -C "$KB_PATH" pull --rebase origin "$BRANCH"

if has_markers; then
  echo "ERROR: merge markers detected. resolve before push." >&2
  exit 3
fi

if [[ "$MODE" == "commit" ]]; then
  if [[ -n "$(git -C "$KB_PATH" status --porcelain)" ]]; then
    git -C "$KB_PATH" add -A
    git -C "$KB_PATH" commit -m "$MSG" || true
  fi
fi

if [[ $NO_PUSH -eq 0 ]]; then
  git -C "$KB_PATH" push origin "$BRANCH"
fi

echo "sync complete"
