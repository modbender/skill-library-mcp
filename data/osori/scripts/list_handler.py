#!/usr/bin/env python3
"""Osori list command handler."""

import os
import sys

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from registry_lib import filter_projects, load_registry, registry_projects, registry_roots

root_filter = os.environ.get("OSORI_ROOT_FILTER", "").strip()

res = load_registry(os.environ["OSORI_REG"], auto_migrate=True, make_backup_on_migrate=True)
all_projects = registry_projects(res.registry)
projects = filter_projects(all_projects, root_key=root_filter)
roots = registry_roots(res.registry)
root_keys = [r.get('key', 'default') for r in roots]

if not projects:
    if root_filter:
        print(f"📂 No projects in root '{root_filter}'.")
        print(f"Available roots: {', '.join(root_keys)}")
    else:
        print("📂 No projects registered yet.")
    raise SystemExit(0)

header = f"📋 *{len(projects)} Projects*"
meta = f"(schema={res.registry.get('schema')} v{res.registry.get('version')})"
root_meta = f" [root={root_filter}]" if root_filter else ""
print(f"{header}{root_meta} {meta}\n")

for p in projects[:20]:
    name = p.get('name', '-')
    lang = p.get('lang', '-')
    root = p.get('root', 'default')
    tags = ', '.join(p.get('tags', [])) or '-'
    repo = p.get('repo', '')

    repo_str = f" | 🌐 {repo}" if repo else ""
    print(f"• *{name}* | {lang} | {root} | {tags}{repo_str}")

if len(projects) > 20:
    print(f"\n... and {len(projects) - 20} more")

if res.migrated:
    notes = '; '.join(res.migration_notes)
    print(f"\nℹ️ Migrated registry: {notes}")
    if res.backup_path:
        print(f"ℹ️ Migration backup: {res.backup_path}")
