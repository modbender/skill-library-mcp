#!/usr/bin/env bash
# Manage aliases and favorites in osori registry
# Usage:
#   alias-favorite-manager.sh alias-add <alias> <project>
#   alias-favorite-manager.sh alias-remove <alias>
#   alias-favorite-manager.sh aliases
#   alias-favorite-manager.sh favorite-add <project-or-alias>
#   alias-favorite-manager.sh favorite-remove <project-or-alias>
#   alias-favorite-manager.sh favorites

set -euo pipefail

COMMAND="${1:-}"
if [[ $# -gt 0 ]]; then
  shift
fi

REGISTRY_FILE="${OSORI_REGISTRY:-$HOME/.openclaw/osori.json}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat << 'EOF'
Usage:
  alias-favorite-manager.sh alias-add <alias> <project>
  alias-favorite-manager.sh alias-remove <alias>
  alias-favorite-manager.sh aliases
  alias-favorite-manager.sh favorite-add <project-or-alias>
  alias-favorite-manager.sh favorite-remove <project-or-alias>
  alias-favorite-manager.sh favorites
EOF
}

case "$COMMAND" in
  alias-add)
    ALIAS_KEY="${1:-}"
    PROJECT_QUERY="${2:-}"
    [[ -z "$ALIAS_KEY" || -z "$PROJECT_QUERY" ]] && { usage; exit 1; }

    OSORI_SCRIPT_DIR="$SCRIPT_DIR" OSORI_REG="$REGISTRY_FILE" OSORI_ALIAS="$ALIAS_KEY" OSORI_QUERY="$PROJECT_QUERY" python3 << 'PYEOF'
import os
import re
import sys

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from registry_lib import (
    load_registry,
    registry_aliases,
    registry_projects,
    save_registry,
    set_registry_aliases,
)

alias_key = os.environ["OSORI_ALIAS"].strip().lower()
query = os.environ["OSORI_QUERY"].strip().lower()

if not re.match(r"^[A-Za-z0-9_-]+$", alias_key):
    print("❌ alias must match [A-Za-z0-9_-]+")
    raise SystemExit(1)

res = load_registry(os.environ["OSORI_REG"], auto_migrate=True, make_backup_on_migrate=True)
registry = res.registry
projects = registry_projects(registry)

matches = [p for p in projects if query == str(p.get("name", "")).lower()]
if not matches:
    matches = [p for p in projects if query in str(p.get("name", "")).lower()]

if not matches:
    print(f"❌ project not found: {os.environ['OSORI_QUERY']}")
    raise SystemExit(1)
if len(matches) > 1:
    names = ", ".join(str(p.get("name", "")) for p in matches[:5])
    print(f"❌ ambiguous project query: {os.environ['OSORI_QUERY']} ({names})")
    raise SystemExit(1)

target_name = str(matches[0].get("name", "")).strip()
if not target_name:
    print("❌ selected project has invalid name")
    raise SystemExit(1)

aliases = registry_aliases(registry)
aliases[alias_key] = target_name
set_registry_aliases(registry, aliases)
backup_path = save_registry(os.environ["OSORI_REG"], registry, make_backup=True)

print(f"✅ alias added: {alias_key} -> {target_name}")
if backup_path:
    print(f"Backup: {backup_path}")
PYEOF
    ;;

  alias-remove)
    ALIAS_KEY="${1:-}"
    [[ -z "$ALIAS_KEY" ]] && { usage; exit 1; }

    OSORI_SCRIPT_DIR="$SCRIPT_DIR" OSORI_REG="$REGISTRY_FILE" OSORI_ALIAS="$ALIAS_KEY" python3 << 'PYEOF'
import os
import sys

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from registry_lib import load_registry, registry_aliases, save_registry, set_registry_aliases

alias_key = os.environ["OSORI_ALIAS"].strip().lower()
res = load_registry(os.environ["OSORI_REG"], auto_migrate=True, make_backup_on_migrate=True)
registry = res.registry
aliases = registry_aliases(registry)

if alias_key not in aliases:
    print(f"❌ alias not found: {alias_key}")
    raise SystemExit(1)

removed = aliases.pop(alias_key)
set_registry_aliases(registry, aliases)
backup_path = save_registry(os.environ["OSORI_REG"], registry, make_backup=True)

print(f"✅ alias removed: {alias_key} (was -> {removed})")
if backup_path:
    print(f"Backup: {backup_path}")
PYEOF
    ;;

  aliases)
    OSORI_SCRIPT_DIR="$SCRIPT_DIR" OSORI_REG="$REGISTRY_FILE" python3 << 'PYEOF'
import os
import sys

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from registry_lib import load_registry, registry_aliases

res = load_registry(os.environ["OSORI_REG"], auto_migrate=True, make_backup_on_migrate=True)
aliases = registry_aliases(res.registry)

if not aliases:
    print("📎 No aliases configured.")
    raise SystemExit(0)

print(f"📎 Aliases ({len(aliases)})")
for k in sorted(aliases.keys()):
    print(f"- {k} -> {aliases[k]}")
PYEOF
    ;;

  favorite-add|favorite-remove)
    PROJECT_QUERY="${1:-}"
    [[ -z "$PROJECT_QUERY" ]] && { usage; exit 1; }

    OSORI_SCRIPT_DIR="$SCRIPT_DIR" OSORI_REG="$REGISTRY_FILE" OSORI_QUERY="$PROJECT_QUERY" OSORI_COMMAND="$COMMAND" python3 << 'PYEOF'
import os
import sys

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from registry_lib import load_registry, registry_projects, resolve_alias, save_registry, set_registry_projects

query_raw = os.environ["OSORI_QUERY"].strip()
cmd = os.environ["OSORI_COMMAND"]
mark_value = cmd == "favorite-add"

res = load_registry(os.environ["OSORI_REG"], auto_migrate=True, make_backup_on_migrate=True)
registry = res.registry
projects = registry_projects(registry)
query = resolve_alias(query_raw, registry).lower()

matches = [p for p in projects if query == str(p.get("name", "")).lower()]
if not matches:
    matches = [p for p in projects if query in str(p.get("name", "")).lower()]

if not matches:
    print(f"❌ project not found: {query_raw}")
    raise SystemExit(1)
if len(matches) > 1:
    names = ", ".join(str(p.get("name", "")) for p in matches[:5])
    print(f"❌ ambiguous project query: {query_raw} ({names})")
    raise SystemExit(1)

target_name = str(matches[0].get("name", ""))
changed = False
for p in projects:
    if str(p.get("name", "")) == target_name:
        if bool(p.get("favorite", False)) != mark_value:
            p["favorite"] = mark_value
            changed = True
        break

if not changed:
    state = "already favorite" if mark_value else "already not favorite"
    print(f"ℹ️ {target_name}: {state}")
    raise SystemExit(0)

set_registry_projects(registry, projects)
backup_path = save_registry(os.environ["OSORI_REG"], registry, make_backup=True)

if mark_value:
    print(f"⭐ favorite added: {target_name}")
else:
    print(f"✅ favorite removed: {target_name}")
if backup_path:
    print(f"Backup: {backup_path}")
PYEOF
    ;;

  favorites)
    OSORI_SCRIPT_DIR="$SCRIPT_DIR" OSORI_REG="$REGISTRY_FILE" python3 << 'PYEOF'
import os
import sys

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from registry_lib import load_registry, registry_projects

res = load_registry(os.environ["OSORI_REG"], auto_migrate=True, make_backup_on_migrate=True)
projects = registry_projects(res.registry)
favs = [p for p in projects if bool(p.get("favorite", False))]

if not favs:
    print("⭐ No favorite projects.")
    raise SystemExit(0)

favs.sort(key=lambda p: str(p.get("name", "")).lower())
print(f"⭐ Favorites ({len(favs)})")
for p in favs:
    name = p.get("name", "-")
    root = p.get("root", "default")
    path = p.get("path", "-")
    print(f"- {name} [{root}] | {path}")
PYEOF
    ;;

  -h|--help|help)
    usage
    ;;

  *)
    usage
    exit 1
    ;;
esac