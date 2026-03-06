#!/usr/bin/env bash
# Add a single project to the registry
# Usage: add-project.sh <path> [--tag <tag>] [--name <name>]

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <path> [--tag <tag>] [--name <name>]"
  exit 1
fi

PROJECT_PATH_RAW="$1"
shift

if [[ ! -d "$PROJECT_PATH_RAW" ]]; then
  echo "Directory not found: $PROJECT_PATH_RAW"
  exit 1
fi

PROJECT_PATH="$(cd "$PROJECT_PATH_RAW" && pwd)"
NAME="$(basename "$PROJECT_PATH")"
TAG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag) TAG="${2:-}"; shift 2 ;;
    --name) NAME="${2:-}"; shift 2 ;;
    *) shift ;;
  esac
done

REGISTRY_FILE="${OSORI_REGISTRY:-$HOME/.openclaw/osori.json}"
ROOT_KEY="${OSORI_ROOT_KEY:-default}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detect remote
REPO=""
REMOTE=$(git -C "$PROJECT_PATH" remote get-url origin 2>/dev/null || true)

if [[ -n "$REMOTE" ]]; then
  REPO=$(OSORI_REMOTE="$REMOTE" PYTHONPATH="$SCRIPT_DIR" python3 - << 'PYEOF'
import os
from registry_lib import parse_repo_from_remote
print(parse_repo_from_remote(os.environ.get("OSORI_REMOTE", "")))
PYEOF
)
fi

# Detect language
LANG_DETECTED="unknown"
if [[ -f "$PROJECT_PATH/Package.swift" ]]; then LANG_DETECTED="swift"
elif [[ -f "$PROJECT_PATH/package.json" ]]; then LANG_DETECTED="typescript"
elif [[ -f "$PROJECT_PATH/Cargo.toml" ]]; then LANG_DETECTED="rust"
elif [[ -f "$PROJECT_PATH/go.mod" ]]; then LANG_DETECTED="go"
elif [[ -f "$PROJECT_PATH/pyproject.toml" ]] || [[ -f "$PROJECT_PATH/setup.py" ]]; then LANG_DETECTED="python"
elif [[ -f "$PROJECT_PATH/Gemfile" ]]; then LANG_DETECTED="ruby"
fi

# Detect description safely
DESC=""
if [[ -f "$PROJECT_PATH/package.json" ]]; then
  DESC=$(python3 -c "import json,sys; print(json.load(sys.stdin).get('description',''))" < "$PROJECT_PATH/package.json" 2>/dev/null || true)
fi

TODAY=$(date +%Y-%m-%d)

OSORI_SCRIPT_DIR="$SCRIPT_DIR" \
OSORI_REG="$REGISTRY_FILE" \
OSORI_NAME="$NAME" \
OSORI_PATH="$PROJECT_PATH" \
OSORI_REPO="$REPO" \
OSORI_LANG="$LANG_DETECTED" \
OSORI_TAG="$TAG" \
OSORI_DESC="$DESC" \
OSORI_TODAY="$TODAY" \
OSORI_ROOT_KEY="$ROOT_KEY" \
python3 << 'PYEOF'
import os
import sys

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from registry_lib import (
    ensure_root_exists,
    load_registry,
    registry_projects,
    save_registry,
    set_registry_projects,
)

reg_file = os.environ["OSORI_REG"]
name = os.environ["OSORI_NAME"]
path = os.environ["OSORI_PATH"]
repo = os.environ["OSORI_REPO"]
lang = os.environ["OSORI_LANG"]
tag = os.environ["OSORI_TAG"]
desc = os.environ["OSORI_DESC"]
today = os.environ["OSORI_TODAY"]
root_key = os.environ["OSORI_ROOT_KEY"] or "default"

loaded = load_registry(reg_file, auto_migrate=True, make_backup_on_migrate=True)
registry = loaded.registry
resolved_root = ensure_root_exists(registry, root_key)
projects = registry_projects(registry)

for p in projects:
    if p.get("name") == name:
        print(f"Already registered: {name}")
        if loaded.migrated:
            notes = "; ".join(loaded.migration_notes)
            print(f"Migrated registry on load: {notes}")
            if loaded.backup_path:
                print(f"Migration backup: {loaded.backup_path}")
        raise SystemExit(0)

entry = {
    "name": name,
    "path": path,
    "repo": repo,
    "lang": lang,
    "tags": [tag] if tag else [],
    "description": desc,
    "addedAt": today,
    "root": resolved_root,
}

projects.append(entry)
set_registry_projects(registry, projects)
backup_path = save_registry(reg_file, registry, make_backup=True)

if loaded.migrated:
    notes = "; ".join(loaded.migration_notes)
    print(f"Migrated registry on load: {notes}")
    if loaded.backup_path:
        print(f"Migration backup: {loaded.backup_path}")

if backup_path:
    print(f"Backup: {backup_path}")

print(f"Added: {name} ({path})")
PYEOF