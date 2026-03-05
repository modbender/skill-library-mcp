#!/usr/bin/env bash
# Scan a directory for git repos and add them to the registry
# Usage: scan-projects.sh <root-dir> [--depth N]

set -euo pipefail

ROOT="${1:-.}"
DEPTH=3

shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --depth) DEPTH="${2:-3}"; shift 2 ;;
    *) shift ;;
  esac
done

if [[ ! -d "$ROOT" ]]; then
  echo "Directory not found: $ROOT"
  exit 1
fi

REGISTRY_FILE="${OSORI_REGISTRY:-$HOME/.openclaw/osori.json}"
ROOT_KEY="${OSORI_ROOT_KEY:-default}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TMPFILE="$(mktemp)"
echo "[]" > "$TMPFILE"
trap 'rm -f "$TMPFILE"' EXIT

# Load existing names (with auto-migration)
EXISTING_NAMES=$(OSORI_SCRIPT_DIR="$SCRIPT_DIR" OSORI_REG="$REGISTRY_FILE" python3 << 'PYEOF'
import os
import sys

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from registry_lib import load_registry, registry_projects

res = load_registry(os.environ["OSORI_REG"], auto_migrate=True, make_backup_on_migrate=True)
projects = registry_projects(res.registry)
for p in projects:
    name = p.get("name", "")
    if name:
        print(name)

if res.migrated:
    notes = "; ".join(res.migration_notes)
    print(f"Migrated registry on load: {notes}")
    if res.backup_path:
        print(f"Migration backup: {res.backup_path}")
PYEOF
)

while IFS= read -r gitdir; do
  dir="$(dirname "$gitdir")"
  name="$(basename "$dir")"

  # Skip if already registered
  if echo "$EXISTING_NAMES" | grep -qx "$name"; then
    continue
  fi

  # Detect remote/repo
  remote=$(git -C "$dir" remote get-url origin 2>/dev/null || true)
  repo=""
  if [[ -n "$remote" ]]; then
    repo=$(OSORI_REMOTE="$remote" PYTHONPATH="$SCRIPT_DIR" python3 - << 'PYEOF'
import os
from registry_lib import parse_repo_from_remote
print(parse_repo_from_remote(os.environ.get("OSORI_REMOTE", "")))
PYEOF
)
  fi

  # Detect language
  lang="unknown"
  if [[ -f "$dir/Package.swift" ]]; then lang="swift"
  elif [[ -f "$dir/package.json" ]]; then lang="typescript"
  elif [[ -f "$dir/Cargo.toml" ]]; then lang="rust"
  elif [[ -f "$dir/go.mod" ]]; then lang="go"
  elif [[ -f "$dir/pyproject.toml" ]] || [[ -f "$dir/setup.py" ]]; then lang="python"
  elif [[ -f "$dir/Gemfile" ]]; then lang="ruby"
  fi

  # Detect description safely
  desc=""
  if [[ -f "$dir/package.json" ]]; then
    desc=$(python3 -c "import json,sys; print(json.load(sys.stdin).get('description',''))" < "$dir/package.json" 2>/dev/null || true)
  fi

  parent="$(basename "$(dirname "$dir")")"
  today=$(date +%Y-%m-%d)

  OSORI_TMPFILE="$TMPFILE" \
  OSORI_NAME="$name" \
  OSORI_PATH="$dir" \
  OSORI_REPO="$repo" \
  OSORI_LANG="$lang" \
  OSORI_TAG="$parent" \
  OSORI_DESC="$desc" \
  OSORI_TODAY="$today" \
  OSORI_ROOT_KEY="$ROOT_KEY" \
  python3 << 'PYEOF'
import json
import os

path = os.environ["OSORI_TMPFILE"]
with open(path, encoding="utf-8") as f:
    entries = json.load(f)

entries.append({
    "name": os.environ["OSORI_NAME"],
    "path": os.environ["OSORI_PATH"],
    "repo": os.environ["OSORI_REPO"],
    "lang": os.environ["OSORI_LANG"],
    "tags": [os.environ["OSORI_TAG"]] if os.environ.get("OSORI_TAG") else [],
    "description": os.environ["OSORI_DESC"],
    "addedAt": os.environ["OSORI_TODAY"],
    "root": os.environ.get("OSORI_ROOT_KEY", "default") or "default",
})

with open(path, "w", encoding="utf-8") as f:
    json.dump(entries, f, ensure_ascii=False)
PYEOF

done < <(find "$ROOT" -maxdepth "$DEPTH" -name '.git' -type d 2>/dev/null)

# Merge with existing registry
OSORI_SCRIPT_DIR="$SCRIPT_DIR" \
OSORI_REG="$REGISTRY_FILE" \
OSORI_TMPFILE="$TMPFILE" \
python3 << 'PYEOF'
import json
import os
import sys

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from registry_lib import ensure_root_exists, load_registry, registry_projects, save_registry, set_registry_projects

reg_file = os.environ["OSORI_REG"]
with open(os.environ["OSORI_TMPFILE"], encoding="utf-8") as f:
    new_entries = json.load(f)

loaded = load_registry(reg_file, auto_migrate=True, make_backup_on_migrate=True)
registry = loaded.registry
projects = registry_projects(registry)
existing_names = {p.get("name") for p in projects}

added = 0
for e in new_entries:
    if e.get("name") in existing_names:
        continue
    e["root"] = ensure_root_exists(registry, e.get("root", "default"))
    projects.append(e)
    existing_names.add(e.get("name"))
    added += 1

set_registry_projects(registry, projects)
backup_path = save_registry(reg_file, registry, make_backup=True)

if loaded.migrated:
    notes = "; ".join(loaded.migration_notes)
    print(f"Migrated registry on load: {notes}")
    if loaded.backup_path:
        print(f"Migration backup: {loaded.backup_path}")

if backup_path:
    print(f"Backup: {backup_path}")

print(f"Added {added} projects. Total: {len(projects)}")
PYEOF