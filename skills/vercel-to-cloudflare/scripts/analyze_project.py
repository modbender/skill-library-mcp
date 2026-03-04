#!/usr/bin/env python3
"""Analyze a Next.js project for Vercel-to-Cloudflare migration readiness."""

import os
import sys
import re
import json
from pathlib import Path

def find_files(root, extensions=('.ts', '.tsx', '.js', '.jsx')):
    """Find all source files."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ('node_modules', '.next', '.git', 'dist', '.open-next')]
        for f in filenames:
            if any(f.endswith(ext) for ext in extensions):
                yield os.path.join(dirpath, f)

def analyze(project_path):
    root = Path(project_path).resolve()
    if not root.exists():
        print(f"❌ Path not found: {root}")
        sys.exit(1)

    issues = []
    stats = {
        'process_env_db': [],
        'global_db_singleton': [],
        'import_db': [],
        'supabase_client': [],
        'drizzle_usage': [],
        'prisma_usage': [],
    }

    for filepath in find_files(root):
        rel = os.path.relpath(filepath, root)
        try:
            content = open(filepath, 'r', encoding='utf-8', errors='ignore').read()
        except:
            continue

        # Check for process.env.DATABASE_URL
        if re.search(r'process\.env\.(DATABASE_URL|SUPABASE_URL|DB_URL|POSTGRES_URL)', content):
            stats['process_env_db'].append(rel)

        # Check for global db singleton pattern
        if re.search(r'^export\s+(const|let)\s+db\s*=', content, re.MULTILINE):
            stats['global_db_singleton'].append(rel)

        # Check for db imports
        if re.search(r"import\s+\{[^}]*\bdb\b[^}]*\}\s+from", content):
            stats['import_db'].append(rel)

        # Check for Supabase client
        if 'createClient' in content and 'supabase' in content.lower():
            stats['supabase_client'].append(rel)

        # Check for Drizzle
        if 'drizzle(' in content or 'from \'drizzle-orm' in content or 'from "drizzle-orm' in content:
            stats['drizzle_usage'].append(rel)

        # Check for Prisma
        if 'PrismaClient' in content or 'from \'@prisma' in content or 'from "@prisma' in content:
            stats['prisma_usage'].append(rel)

    # Check for existing config files
    has_wrangler = (root / 'wrangler.toml').exists() or (root / 'wrangler.json').exists()
    has_vercel = (root / 'vercel.json').exists()
    has_next_config = (root / 'next.config.ts').exists() or (root / 'next.config.js').exists() or (root / 'next.config.mjs').exists()

    # Package.json analysis
    pkg_path = root / 'package.json'
    orm = 'unknown'
    if pkg_path.exists():
        pkg = json.loads(pkg_path.read_text())
        deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
        if 'drizzle-orm' in deps:
            orm = 'drizzle'
        elif '@prisma/client' in deps:
            orm = 'prisma'
        elif '@supabase/supabase-js' in deps:
            orm = 'supabase-js'

    # Report
    print("=" * 60)
    print("📋 Vercel → Cloudflare Migration Analysis")
    print("=" * 60)
    print(f"\n📁 Project: {root}")
    print(f"🔧 ORM: {orm}")
    print(f"📦 Has wrangler.toml: {'✅' if has_wrangler else '❌ (needs creation)'}")
    print(f"📦 Has vercel.json: {'✅' if has_vercel else '—'}")
    print(f"📦 Has next.config: {'✅' if has_next_config else '❌'}")

    print(f"\n🔍 Findings:")
    print(f"  process.env DB references: {len(stats['process_env_db'])} files")
    for f in stats['process_env_db'][:10]:
        print(f"    → {f}")

    print(f"  Global db singletons: {len(stats['global_db_singleton'])} files")
    for f in stats['global_db_singleton'][:10]:
        print(f"    → {f}")

    print(f"  Files importing db: {len(stats['import_db'])} files")
    print(f"  Supabase client usage: {len(stats['supabase_client'])} files")

    total_changes = len(stats['process_env_db']) + len(stats['global_db_singleton']) + len(stats['import_db'])
    print(f"\n📊 Estimated migration effort:")
    if total_changes < 5:
        print(f"  🟢 Small ({total_changes} files to modify)")
    elif total_changes < 20:
        print(f"  🟡 Medium ({total_changes} files to modify)")
    else:
        print(f"  🔴 Large ({total_changes} files to modify)")

    print(f"\n📝 Next steps:")
    print(f"  1. Install @opennextjs/cloudflare")
    print(f"  2. Create wrangler.toml with Hyperdrive binding")
    print(f"  3. Rewrite {len(stats['global_db_singleton'])} global DB singletons → getDb() pattern")
    print(f"  4. Update {len(stats['import_db'])} files importing db")
    print(f"  5. Replace {len(stats['process_env_db'])} process.env references")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_project.py <project-path>")
        sys.exit(1)
    analyze(sys.argv[1])
