#!/usr/bin/env python3
"""Osori status command handler."""

import os
import subprocess
import sys

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from registry_lib import filter_projects, load_registry, registry_projects

root_filter = os.environ.get("OSORI_ROOT_FILTER", "").strip()

res = load_registry(os.environ["OSORI_REG"], auto_migrate=True, make_backup_on_migrate=True)
projects = filter_projects(registry_projects(res.registry), root_key=root_filter)

clean = modified = missing = 0

for p in projects:
    path = p.get('path', '')
    if not path or not os.path.exists(path):
        missing += 1
        continue

    try:
        result = subprocess.run(
            ['git', '-C', path, 'status', '--short'],
            capture_output=True, text=True, timeout=3,
        )
        if result.stdout.strip():
            modified += 1
        else:
            clean += 1
    except Exception:
        missing += 1

root_meta = f" [root={root_filter}]" if root_filter else ""
print(f"📊 *Project Status*{root_meta}\n")
print(f"✅ Clean: {clean}")
print(f"📝 Modified: {modified}")
print(f"⚠️ Missing: {missing}")
print(f"📁 Total: {len(projects)}")
print(f"🧾 Registry: schema={res.registry.get('schema')} v{res.registry.get('version')}")

if res.migrated:
    notes = '; '.join(res.migration_notes)
    print(f"\nℹ️ Migrated registry: {notes}")
    if res.backup_path:
        print(f"ℹ️ Migration backup: {res.backup_path}")
