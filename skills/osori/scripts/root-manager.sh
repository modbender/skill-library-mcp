#!/usr/bin/env bash
# Manage registry roots (list/add/path-add/path-remove/set-label/remove)
# Usage:
#   root-manager.sh list
#   root-manager.sh add <root-key> [label]
#   root-manager.sh path-add <root-key> <path>
#   root-manager.sh path-remove <root-key> <path>
#   root-manager.sh set-label <root-key> <label>
#   root-manager.sh remove <root-key> [--reassign <target-root>] [--force]

set -euo pipefail

COMMAND="${1:-list}"
if [[ $# -gt 0 ]]; then
  shift
fi

REGISTRY_FILE="${OSORI_REGISTRY:-$HOME/.openclaw/osori.json}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat << 'EOF'
Usage:
  root-manager.sh list
  root-manager.sh add <root-key> [label]
  root-manager.sh path-add <root-key> <path>
  root-manager.sh path-remove <root-key> <path>
  root-manager.sh set-label <root-key> <label>
  root-manager.sh remove <root-key> [--reassign <target-root>] [--force]
EOF
}

case "$COMMAND" in
  list)
    OSORI_SCRIPT_DIR="$SCRIPT_DIR" OSORI_REG="$REGISTRY_FILE" python3 << 'PYEOF'
import os
import sys

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from registry_lib import load_registry, registry_projects, registry_roots

res = load_registry(os.environ["OSORI_REG"], auto_migrate=True, make_backup_on_migrate=True)
registry = res.registry
roots = registry_roots(registry)
projects = registry_projects(registry)

counts = {}
for p in projects:
    rk = str(p.get("root", "default") or "default")
    counts[rk] = counts.get(rk, 0) + 1

print(f"🗂️ Roots ({len(roots)})")
print()
for r in roots:
    key = r.get("key", "default")
    label = r.get("label", key.title())
    paths = [p for p in r.get("paths", []) if isinstance(p, str)]
    print(f"• {key} (label: {label})")
    print(f"  - projects: {counts.get(key, 0)}")
    print(f"  - paths: {len(paths)}")
    for p in paths:
        print(f"    - {p}")
    print()

if res.migrated:
    notes = "; ".join(res.migration_notes)
    print(f"ℹ️ Migrated registry: {notes}")
    if res.backup_path:
        print(f"ℹ️ Migration backup: {res.backup_path}")
PYEOF
    ;;

  add)
    ROOT_KEY="${1:-}"
    LABEL="${2:-}"
    [[ -z "$ROOT_KEY" ]] && { usage; exit 1; }

    OSORI_SCRIPT_DIR="$SCRIPT_DIR" OSORI_REG="$REGISTRY_FILE" OSORI_ROOT_KEY="$ROOT_KEY" OSORI_LABEL="$LABEL" python3 << 'PYEOF'
import os
import re
import sys

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from registry_lib import load_registry, registry_roots, save_registry

key = os.environ["OSORI_ROOT_KEY"].strip()
label = os.environ.get("OSORI_LABEL", "").strip()

if not re.match(r"^[A-Za-z0-9_-]+$", key):
    print("❌ root key must match [A-Za-z0-9_-]+")
    raise SystemExit(1)

if key in {"all", "*"}:
    print("❌ root key cannot be 'all' or '*'")
    raise SystemExit(1)

res = load_registry(os.environ["OSORI_REG"], auto_migrate=True, make_backup_on_migrate=True)
registry = res.registry
roots = registry_roots(registry)

found = False
for r in roots:
    if r.get("key") == key:
        found = True
        if label:
            r["label"] = label
        break

if not found:
    roots.append({"key": key, "label": label or key.title(), "paths": []})

registry["roots"] = roots
backup_path = save_registry(os.environ["OSORI_REG"], registry, make_backup=True)

if found:
    print(f"✅ Updated root: {key}")
else:
    print(f"✅ Added root: {key}")

if backup_path:
    print(f"Backup: {backup_path}")
PYEOF
    ;;

  path-add)
    ROOT_KEY="${1:-}"
    ROOT_PATH="${2:-}"
    [[ -z "$ROOT_KEY" || -z "$ROOT_PATH" ]] && { usage; exit 1; }

    OSORI_SCRIPT_DIR="$SCRIPT_DIR" OSORI_REG="$REGISTRY_FILE" OSORI_ROOT_KEY="$ROOT_KEY" OSORI_ROOT_PATH="$ROOT_PATH" python3 << 'PYEOF'
import os
import re
import sys

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from registry_lib import load_registry, registry_roots, save_registry

key = os.environ["OSORI_ROOT_KEY"].strip()
raw_path = os.environ["OSORI_ROOT_PATH"].strip()
path = os.path.realpath(os.path.abspath(os.path.expanduser(raw_path)))

if not re.match(r"^[A-Za-z0-9_-]+$", key):
    print("❌ root key must match [A-Za-z0-9_-]+")
    raise SystemExit(1)

if not os.path.isdir(path):
    print(f"❌ directory not found: {path}")
    raise SystemExit(1)

res = load_registry(os.environ["OSORI_REG"], auto_migrate=True, make_backup_on_migrate=True)
registry = res.registry
roots = registry_roots(registry)

target = None
for r in roots:
    if r.get("key") == key:
        target = r
        break

if target is None:
    target = {"key": key, "label": key.title(), "paths": []}
    roots.append(target)

paths = [os.path.realpath(os.path.abspath(os.path.expanduser(p))) for p in target.get("paths", []) if isinstance(p, str)]
if path not in paths:
    paths.append(path)

target["paths"] = paths
registry["roots"] = roots
backup_path = save_registry(os.environ["OSORI_REG"], registry, make_backup=True)

print(f"✅ Added path to root '{key}': {path}")
if backup_path:
    print(f"Backup: {backup_path}")
PYEOF
    ;;

  path-remove)
    ROOT_KEY="${1:-}"
    ROOT_PATH="${2:-}"
    [[ -z "$ROOT_KEY" || -z "$ROOT_PATH" ]] && { usage; exit 1; }

    OSORI_SCRIPT_DIR="$SCRIPT_DIR" OSORI_REG="$REGISTRY_FILE" OSORI_ROOT_KEY="$ROOT_KEY" OSORI_ROOT_PATH="$ROOT_PATH" python3 << 'PYEOF'
import os
import sys

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from registry_lib import load_registry, registry_roots, save_registry

key = os.environ["OSORI_ROOT_KEY"].strip()
path = os.path.realpath(os.path.abspath(os.path.expanduser(os.environ["OSORI_ROOT_PATH"].strip())))

res = load_registry(os.environ["OSORI_REG"], auto_migrate=True, make_backup_on_migrate=True)
registry = res.registry
roots = registry_roots(registry)

target = None
for r in roots:
    if r.get("key") == key:
        target = r
        break

if target is None:
    print(f"❌ root not found: {key}")
    raise SystemExit(1)

paths = [os.path.realpath(os.path.abspath(os.path.expanduser(p))) for p in target.get("paths", []) if isinstance(p, str)]
new_paths = [p for p in paths if p != path]

if len(new_paths) == len(paths):
    print(f"ℹ️ path not found in root '{key}': {path}")
    raise SystemExit(0)

target["paths"] = new_paths
registry["roots"] = roots
backup_path = save_registry(os.environ["OSORI_REG"], registry, make_backup=True)

print(f"✅ Removed path from root '{key}': {path}")
if backup_path:
    print(f"Backup: {backup_path}")
PYEOF
    ;;

  set-label)
    ROOT_KEY="${1:-}"
    LABEL="${2:-}"
    [[ -z "$ROOT_KEY" || -z "$LABEL" ]] && { usage; exit 1; }

    OSORI_SCRIPT_DIR="$SCRIPT_DIR" OSORI_REG="$REGISTRY_FILE" OSORI_ROOT_KEY="$ROOT_KEY" OSORI_LABEL="$LABEL" python3 << 'PYEOF'
import os
import sys

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from registry_lib import load_registry, registry_roots, save_registry

key = os.environ["OSORI_ROOT_KEY"].strip()
label = os.environ["OSORI_LABEL"].strip()

res = load_registry(os.environ["OSORI_REG"], auto_migrate=True, make_backup_on_migrate=True)
registry = res.registry
roots = registry_roots(registry)

for r in roots:
    if r.get("key") == key:
        r["label"] = label
        registry["roots"] = roots
        backup_path = save_registry(os.environ["OSORI_REG"], registry, make_backup=True)
        print(f"✅ Updated label for root '{key}': {label}")
        if backup_path:
            print(f"Backup: {backup_path}")
        raise SystemExit(0)

print(f"❌ root not found: {key}")
raise SystemExit(1)
PYEOF
    ;;

  remove)
    ROOT_KEY="${1:-}"
    shift || true
    REASSIGN_TARGET=""
    FORCE="false"

    while [[ $# -gt 0 ]]; do
      case "$1" in
        --reassign)
          REASSIGN_TARGET="${2:-}"
          shift 2
          ;;
        --force)
          FORCE="true"
          shift
          ;;
        *)
          shift
          ;;
      esac
    done

    [[ -z "$ROOT_KEY" ]] && { usage; exit 1; }

    OSORI_SCRIPT_DIR="$SCRIPT_DIR" \
    OSORI_REG="$REGISTRY_FILE" \
    OSORI_ROOT_KEY="$ROOT_KEY" \
    OSORI_REASSIGN_TARGET="$REASSIGN_TARGET" \
    OSORI_FORCE="$FORCE" \
    python3 << 'PYEOF'
import os
import re
import sys

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from registry_lib import load_registry, registry_projects, registry_roots, save_registry, set_registry_projects

root_key = os.environ["OSORI_ROOT_KEY"].strip()
reassign = os.environ.get("OSORI_REASSIGN_TARGET", "").strip()
force = os.environ.get("OSORI_FORCE", "false").lower() == "true"

if not re.match(r"^[A-Za-z0-9_-]+$", root_key):
    print("❌ root key must match [A-Za-z0-9_-]+")
    raise SystemExit(1)

if root_key == "default":
    print("❌ cannot remove protected root: default")
    raise SystemExit(1)

if reassign and reassign == root_key:
    print("❌ --reassign target must be different from removed root")
    raise SystemExit(1)

res = load_registry(os.environ["OSORI_REG"], auto_migrate=True, make_backup_on_migrate=True)
registry = res.registry
roots = registry_roots(registry)
projects = registry_projects(registry)

root_keys = [r.get("key", "default") for r in roots]
if root_key not in root_keys:
    print(f"❌ root not found: {root_key}")
    raise SystemExit(1)

affected = [p for p in projects if str(p.get("root", "default") or "default") == root_key]
affected_count = len(affected)

if affected_count > 0 and not reassign and not force:
    print(f"❌ root '{root_key}' has {affected_count} project(s); use --reassign <target-root> or --force")
    raise SystemExit(1)

target_root = None
if reassign:
    if reassign == "default":
        target_root = "default"
    else:
        if reassign not in root_keys:
            print(f"❌ reassign target root not found: {reassign}")
            raise SystemExit(1)
        target_root = reassign
elif force and affected_count > 0:
    target_root = "default"

if target_root:
    for p in projects:
        if str(p.get("root", "default") or "default") == root_key:
            p["root"] = target_root

new_roots = [r for r in roots if r.get("key") != root_key]
registry["roots"] = new_roots
set_registry_projects(registry, projects)
backup_path = save_registry(os.environ["OSORI_REG"], registry, make_backup=True)

if target_root:
    if force and not reassign:
        print(f"⚠️ force mode: reassigned {affected_count} project(s) to 'default' before removing '{root_key}'")
    else:
        print(f"✅ reassigned {affected_count} project(s) from '{root_key}' to '{target_root}'")

print(f"✅ removed root: {root_key}")
if backup_path:
    print(f"Backup: {backup_path}")
PYEOF
    ;;

  -h|--help|help)
    usage
    ;;

  *)
    echo "Unknown command: $COMMAND"
    usage
    exit 1
    ;;
esac