#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  sync_skills.sh [options]

Options:
  --root <dir>           Skills root directory (default: $HOME/.openclaw/workspace/skills)
  --bump <type>          patch|minor|major (default: patch)
  --changelog <text>     Changelog for updated skills
  --tags <tags>          Comma-separated tags (default: latest)
  --registry <url>       Registry URL override
  --env-file <file>      Env file path (default: $HOME/.openclaw/.env)
  --dry-run              Preview only
  -h, --help             Show help
EOF
}

load_token_from_env_file() {
  local env_file="$1"
  if [[ ! -f "$env_file" ]]; then
    return 1
  fi
  local value
  value="$(sed -n 's/^CLAWHUB_TOKEN=//p' "$env_file" | sed -n '1p')"
  value="${value%\"}"
  value="${value#\"}"
  value="${value%\'}"
  value="${value#\'}"
  if [[ -n "$value" ]]; then
    export CLAWHUB_TOKEN="$value"
    return 0
  fi
  return 1
}

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Error: missing command '$cmd'" >&2
    exit 1
  fi
}

ensure_authenticated() {
  if clawhub whoami >/dev/null 2>&1; then
    echo "Using existing ClawHub login session."
    return 0
  fi

  if [[ -z "${CLAWHUB_TOKEN:-}" ]]; then
    load_token_from_env_file "$ENV_FILE" || {
      echo "Error: CLAWHUB_TOKEN not found in env or $ENV_FILE" >&2
      exit 1
    }
  fi

  echo "Logging into ClawHub with token (hidden)..."
  clawhub login --token "$CLAWHUB_TOKEN" --no-browser >/dev/null
  clawhub whoami >/dev/null
}

ROOT="${HOME}/.openclaw/workspace/skills"
BUMP="patch"
CHANGELOG=""
TAGS="latest"
REGISTRY=""
ENV_FILE="${HOME}/.openclaw/.env"
DRY_RUN="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      ROOT="${2:-}"; shift 2 ;;
    --bump)
      BUMP="${2:-}"; shift 2 ;;
    --changelog)
      CHANGELOG="${2:-}"; shift 2 ;;
    --tags)
      TAGS="${2:-}"; shift 2 ;;
    --registry)
      REGISTRY="${2:-}"; shift 2 ;;
    --env-file)
      ENV_FILE="${2:-}"; shift 2 ;;
    --dry-run)
      DRY_RUN="true"; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Error: unknown option '$1'" >&2
      usage
      exit 1 ;;
  esac
done

require_cmd clawhub

if [[ ! -d "$ROOT" ]]; then
  echo "Error: skills root not found: $ROOT" >&2
  exit 1
fi

if [[ -n "$REGISTRY" ]]; then
  export CLAWHUB_REGISTRY="$REGISTRY"
fi

ensure_authenticated

cmd=(clawhub sync --root "$ROOT" --all --bump "$BUMP" --tags "$TAGS")
if [[ -n "$CHANGELOG" ]]; then
  cmd+=(--changelog "$CHANGELOG")
fi
if [[ "$DRY_RUN" == "true" ]]; then
  cmd+=(--dry-run)
fi

"${cmd[@]}"
echo "Sync finished for root: $ROOT"
