#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_PATH="$BASE_DIR/references/kb-config.json"
KB_PATH=""
REPO_URL=""
BRANCH=""

usage() {
  cat <<EOF
Usage:
  init_kb_repo.sh [--config <path>] [--kb <path>] [--repo <url>] [--branch <name>]

Defaults are loaded from config JSON:
  $CONFIG_PATH
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config) CONFIG_PATH="$2"; shift 2 ;;
    --kb) KB_PATH="$2"; shift 2 ;;
    --repo) REPO_URL="$2"; shift 2 ;;
    --branch) BRANCH="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 1 ;;
  esac
done

if [[ -f "$CONFIG_PATH" ]] && command -v jq >/dev/null 2>&1; then
  [[ -z "$REPO_URL" ]] && REPO_URL="$(jq -r '.repo_url // empty' "$CONFIG_PATH")"
  [[ -z "$KB_PATH" ]] && KB_PATH="$(jq -r '.local_path // empty' "$CONFIG_PATH")"
  [[ -z "$BRANCH" ]] && BRANCH="$(jq -r '.branch // "main"' "$CONFIG_PATH")"
fi

[[ -z "$BRANCH" ]] && BRANCH="main"

if [[ -z "$REPO_URL" || "$REPO_URL" == *"<owner>"* || "$REPO_URL" == *"<repo>"* ]]; then
  echo "ERROR: repo_url is not configured. Set in kb-config.json or pass --repo." >&2
  exit 2
fi

if [[ -z "$KB_PATH" || "$KB_PATH" == *"<"* ]]; then
  echo "ERROR: local_path is not configured. Set in kb-config.json or pass --kb." >&2
  exit 2
fi

mkdir -p "$KB_PATH"
if [[ ! -d "$KB_PATH/.git" ]]; then
  git -C "$KB_PATH" init
fi

git -C "$KB_PATH" remote remove origin >/dev/null 2>&1 || true
git -C "$KB_PATH" remote add origin "$REPO_URL"
git -C "$KB_PATH" checkout -B "$BRANCH"

echo "Initialized KB repo"
echo "kb=$KB_PATH"
echo "origin=$REPO_URL"
echo "branch=$BRANCH"
