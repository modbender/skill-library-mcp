#!/usr/bin/env python3
"""Osori remove command handler."""

import os
import sys

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from registry_lib import load_registry, registry_projects, save_registry, set_registry_projects

name = os.environ["OSORI_NAME"]
res = load_registry(os.environ["OSORI_REG"], auto_migrate=True, make_backup_on_migrate=True)
registry = res.registry
projects = registry_projects(registry)

original_len = len(projects)
projects = [p for p in projects if p.get('name', '').lower() != name.lower()]

if len(projects) == original_len:
    print(f"❌ Project '{name}' not found.")
    raise SystemExit(1)

set_registry_projects(registry, projects)
backup_path = save_registry(os.environ["OSORI_REG"], registry, make_backup=True)

print(f"✅ Removed: {name}")
if backup_path:
    print(f"Backup: {backup_path}")
