#!/usr/bin/env bash
# Initialize construction PM data directory and job database
set -euo pipefail

DATA_DIR="${DATA_DIR:-${OPENCLAW_WORKSPACE:-.}/construction-pm-data}"

mkdir -p "$DATA_DIR"

if [ ! -f "$DATA_DIR/jobs.json" ]; then
    cat > "$DATA_DIR/jobs.json" << 'EOF'
{
  "jobs": [],
  "metadata": {
    "created": "",
    "version": "1.0.0"
  }
}
EOF
    # Set creation date
    if command -v python3 &>/dev/null; then
        python3 -c "
import json, datetime
with open('$DATA_DIR/jobs.json', 'r+') as f:
    d = json.load(f)
    d['metadata']['created'] = datetime.date.today().isoformat()
    f.seek(0); json.dump(d, f, indent=2); f.truncate()
"
    fi
    echo "Initialized construction PM database at $DATA_DIR/jobs.json"
else
    echo "Database already exists at $DATA_DIR/jobs.json"
    python3 -c "
import json
with open('$DATA_DIR/jobs.json') as f:
    d = json.load(f)
    jobs = d.get('jobs', [])
    print(f'  {len(jobs)} jobs tracked')
"
fi
