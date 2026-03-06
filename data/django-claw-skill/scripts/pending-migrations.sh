#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/load-config.sh"

TMPFILE=$(mktemp /tmp/django_query_XXXXXX.py)
trap 'rm -f "$TMPFILE"' EXIT

cat > "$TMPFILE" << PYEOF
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '${SETTINGS}')
sys.path.insert(0, '${PROJECT_PATH}')
django.setup()

from django.db.migrations.executor import MigrationExecutor
from django.db import connection

executor = MigrationExecutor(connection)
targets = executor.loader.graph.leaf_nodes()
pending = executor.migration_plan(targets)

if pending:
    print(f"⚠️  {len(pending)} pending migration(s):")
    for migration, _ in pending:
        print(f"  [ ] {migration.app_label}.{migration.name}")
else:
    print("✅ No pending migrations — database is up to date")
PYEOF

cd "$PROJECT_PATH"
"$PYTHON" "$TMPFILE"
