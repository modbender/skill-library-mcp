#!/usr/bin/env python3
"""Osori find command handler."""

import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from registry_lib import (
    filter_projects,
    load_registry,
    normalize_root_key,
    registry_projects,
    registry_roots,
    resolve_alias,
    search_paths_for_discovery,
)


def within_any(path, roots):
    rp = os.path.realpath(path)
    for root in roots:
        rr = os.path.realpath(root)
        try:
            if os.path.commonpath([rp, rr]) == rr:
                return True
        except Exception:
            continue
    return False


name = os.environ["OSORI_NAME"].strip()
root_filter = os.environ.get("OSORI_ROOT_FILTER", "").strip()

res = load_registry(os.environ["OSORI_REG"], auto_migrate=True, make_backup_on_migrate=True)
resolved_name = resolve_alias(name, res.registry)
query = resolved_name.lower()
projects = filter_projects(registry_projects(res.registry), root_key=root_filter)
root_key = normalize_root_key(root_filter)
roots_meta = registry_roots(res.registry)
root_keys = [r.get("key", "default") for r in roots_meta]

if resolved_name != name:
    print(f"ℹ️ alias resolved: {name} -> {resolved_name}")

# 1) Registry lookup (root-prioritized when root_filter is set)
for p in projects:
    pname = p.get('name', '')
    if query in pname.lower():
        print(f"📁 *{pname}*")
        print(f"📍 {p.get('path', '-')}")
        if p.get('repo'):
            print(f"🌐 {p.get('repo')}")
        if p.get('lang') and p.get('lang') != 'unknown':
            print(f"🔤 {p.get('lang')}")
        print(f"🧭 root: {p.get('root', 'default')}")
        if res.migrated:
            notes = '; '.join(res.migration_notes)
            print(f"\nℹ️ Migrated registry: {notes}")
            if res.backup_path:
                print(f"ℹ️ Migration backup: {res.backup_path}")
        raise SystemExit(0)

# Build prioritized search paths from roots[].paths + OSORI_SEARCH_PATHS
search_paths = search_paths_for_discovery(
    res.registry,
    root_key=root_filter,
    env_paths=os.environ.get('OSORI_SEARCH_PATHS', ''),
)

# 2) Spotlight (macOS)
if shutil.which('mdfind'):
    r = subprocess.run(['mdfind', f'kMDItemFSName == "{resolved_name}"'], capture_output=True, text=True)
    lines = [line for line in r.stdout.strip().split('\n') if line.strip()]
    if lines:
        if root_key:
            root_only_paths = search_paths_for_discovery(res.registry, root_key=root_filter, env_paths='')
            if root_only_paths:
                lines = [line for line in lines if within_any(line, root_only_paths)]
        if lines:
            print("🔍 *Found via Spotlight:*")
            for p in lines[:3]:
                print(f"📍 {p}")
            raise SystemExit(0)

# 3) find fallback (root paths first)
for sp in search_paths:
    if not os.path.exists(sp):
        continue
    r = subprocess.run(
        ['find', sp, '-maxdepth', '4', '-type', 'd', '-name', f'*{name}*'],
        capture_output=True, text=True, timeout=10,
    )
    lines = [line for line in r.stdout.strip().split('\n') if line.strip()]
    if lines:
        print("🔍 *Found via search:*")
        for p in lines[:3]:
            print(f"📍 {p}")
        raise SystemExit(0)

if root_key and root_key not in root_keys:
    print(f"ℹ️ Unknown root '{root_key}'. Available roots: {', '.join(root_keys)}")

if not search_paths:
    print("ℹ️ Tip: set roots[].paths in registry or OSORI_SEARCH_PATHS for fallback discovery")

print(f"❌ Project '{name}' not found.")
