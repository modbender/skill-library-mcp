#!/usr/bin/env bash
# Manage Entire CLI per registered project
# Usage:
#   entire-manager.sh status <project> [root|--root <root>]
#   entire-manager.sh enable <project> [root|--root <root>] [entire enable flags...]
#   entire-manager.sh rewind-list <project> [root|--root <root>]

set -euo pipefail

COMMAND="${1:-}"
if [[ $# -gt 0 ]]; then
  shift
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY_FILE="${OSORI_REGISTRY:-$HOME/.openclaw/osori.json}"

PROJECT_QUERY=""
ROOT_FILTER=""
EXTRA_ARGS=()
PROJECT_NAME=""
PROJECT_PATH=""
PROJECT_ROOT=""

usage() {
  cat << 'EOF'
Usage:
  entire-manager.sh status <project> [root|--root <root>]
  entire-manager.sh enable <project> [root|--root <root>] [entire enable flags...]
  entire-manager.sh rewind-list <project> [root|--root <root>]

Examples:
  entire-manager.sh status osori
  entire-manager.sh enable osori --agent claude-code --strategy manual-commit
  entire-manager.sh rewind-list osori --root work
EOF
}

ensure_entire() {
  if ! command -v entire >/dev/null 2>&1; then
    echo "❌ 'entire' CLI not found. Install first: brew tap entireio/tap && brew install entireio/tap/entire"
    exit 1
  fi
}

parse_target_and_extra() {
  PROJECT_QUERY=""
  ROOT_FILTER=""
  EXTRA_ARGS=()

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --root)
        ROOT_FILTER="${2:-}"
        if [[ -z "$ROOT_FILTER" ]]; then
          echo "❌ --root requires a value"
          exit 1
        fi
        shift 2
        ;;
      --agent|--strategy|--telemetry|--to)
        if [[ $# -lt 2 ]]; then
          echo "❌ $1 requires a value"
          exit 1
        fi
        EXTRA_ARGS+=("$1" "$2")
        shift 2
        ;;
      --agent=*|--strategy=*|--telemetry=*|--to=*)
        EXTRA_ARGS+=("$1")
        shift
        ;;
      --local|--project|--skip-push-sessions|--force|--logs-only|--reset)
        EXTRA_ARGS+=("$1")
        shift
        ;;
      *)
        if [[ -z "$PROJECT_QUERY" ]]; then
          PROJECT_QUERY="$1"
        elif [[ -z "$ROOT_FILTER" ]]; then
          ROOT_FILTER="$1"
        else
          EXTRA_ARGS+=("$1")
        fi
        shift
        ;;
    esac
  done

  if [[ -z "$PROJECT_QUERY" ]]; then
    echo "❌ project query is required"
    exit 1
  fi
}

resolve_project() {
  local resolved
  resolved=$(OSORI_SCRIPT_DIR="$SCRIPT_DIR" OSORI_REG="$REGISTRY_FILE" OSORI_QUERY="$PROJECT_QUERY" OSORI_ROOT_FILTER="$ROOT_FILTER" python3 << 'PYEOF'
import os
import sys

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from registry_lib import filter_projects, load_registry, registry_projects

query = os.environ["OSORI_QUERY"].strip().lower()
root_filter = os.environ.get("OSORI_ROOT_FILTER", "").strip()

res = load_registry(os.environ["OSORI_REG"], auto_migrate=True, make_backup_on_migrate=True)
projects = filter_projects(registry_projects(res.registry), root_key=root_filter)

if not projects:
    if root_filter:
        print(f"❌ no projects found in root '{root_filter}'")
    else:
        print("❌ no projects registered")
    raise SystemExit(1)

exact = [p for p in projects if str(p.get("name", "")).lower() == query]
candidates = exact if exact else [p for p in projects if query in str(p.get("name", "")).lower()]

if not candidates:
    suffix = f" in root '{root_filter}'" if root_filter else ""
    print(f"❌ project '{os.environ['OSORI_QUERY']}' not found{suffix}")
    raise SystemExit(1)

if len(candidates) > 1:
    print(f"❌ ambiguous project query '{os.environ['OSORI_QUERY']}'. matches:")
    for i, p in enumerate(candidates[:10], start=1):
        print(f"  {i}. {p.get('name', '-')} [{p.get('root', 'default')}] | {p.get('path', '-')}")
    raise SystemExit(1)

target = candidates[0]
name = str(target.get("name", "")).strip()
path = str(target.get("path", "")).strip()
root = str(target.get("root", "default") or "default")

if not name or not path:
    print("❌ invalid project entry (missing name/path)")
    raise SystemExit(1)

print(f"{name}\t{path}\t{root}")
PYEOF
)

  IFS=$'\t' read -r PROJECT_NAME PROJECT_PATH PROJECT_ROOT <<< "$resolved"

  if [[ -z "$PROJECT_PATH" || ! -d "$PROJECT_PATH" ]]; then
    echo "❌ project path does not exist: $PROJECT_PATH"
    exit 1
  fi
}

run_for_project() {
  echo "📁 *$PROJECT_NAME*"
  echo "📍 $PROJECT_PATH"
  echo "🧭 root: $PROJECT_ROOT"
  echo

  local cwd
  cwd="$(pwd)"
  cd "$PROJECT_PATH"

  case "$COMMAND" in
    status)
      entire status --detailed
      ;;
    enable)
      local has_agent="false"
      local has_strategy="false"
      local -a enable_args=()

      for arg in "${EXTRA_ARGS[@]-}"; do
        [[ -z "$arg" ]] && continue
        enable_args+=("$arg")
      done

      for arg in "${enable_args[@]-}"; do
        case "$arg" in
          --agent|--agent=*) has_agent="true" ;;
          --strategy|--strategy=*) has_strategy="true" ;;
        esac
      done
      if [[ "$has_agent" != "true" ]]; then
        enable_args+=("--agent" "claude-code")
      fi
      if [[ "$has_strategy" != "true" ]]; then
        enable_args+=("--strategy" "manual-commit")
      fi

      if [[ ${#enable_args[@]} -gt 0 ]]; then
        entire enable "${enable_args[@]}"
      else
        entire enable
      fi
      ;;
    rewind-list)
      entire rewind --list
      ;;
    *)
      cd "$cwd"
      echo "❌ unsupported command: $COMMAND"
      exit 1
      ;;
  esac

  cd "$cwd"
}

case "$COMMAND" in
  status|enable|rewind-list)
    ensure_entire
    parse_target_and_extra "$@"
    resolve_project
    run_for_project
    ;;
  -h|--help|help|"")
    usage
    ;;
  *)
    usage
    exit 1
    ;;
esac