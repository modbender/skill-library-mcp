#!/usr/bin/env bash
set -euo pipefail

CLIENT="${2:-}"
[ "$1" = "--client" ] && shift 2 || { CLIENT="$1"; shift || true; }

[ -z "$CLIENT" ] && { echo "Usage: dashboard.sh --client <name>"; exit 1; }

BASE_DIR="${CLIENT_REPORTS_DIR:-$HOME/.openclaw/workspace/client-reports}"
CLIENT_DIR="$BASE_DIR/clients/$CLIENT"

[ ! -d "$CLIENT_DIR" ] && { echo "❌ Client not found: $CLIENT"; exit 1; }

export DASH_CLIENT_DIR="$CLIENT_DIR"

python3 << 'PYEOF'
import json, os, glob

client_dir = os.environ["DASH_CLIENT_DIR"]

config = {}
with open(os.path.join(client_dir, "config.json")) as f:
    config = json.load(f)

name = config.get("display_name", config.get("name", "Unknown"))

# Find latest metrics
data_dir = os.path.join(client_dir, "data")
files = sorted(glob.glob(os.path.join(data_dir, "metrics-*.json")), reverse=True)

print(f"┌──────────────────────────────────────┐")
print(f"│  📊 {name:^32s}  │")
print(f"├──────────────────────────────────────┤")

if not files:
    print(f"│  No metrics data yet.                │")
    print(f"│  Run: pull-metrics.sh --client {config.get('name', '?'):5s}  │")
    print(f"└──────────────────────────────────────┘")
    exit(0)

with open(files[0]) as f:
    metrics = json.load(f)

period = metrics.get("period", {})
print(f"│  Period: {period.get('start', '?')} to {period.get('end', '?')}  │")
print(f"├──────────────────────────────────────┤")

sources = metrics.get("sources", {})

for source_name, data in sources.items():
    if not isinstance(data, dict):
        continue
    status = data.get("status", "unknown")
    if status == "not_configured":
        print(f"│  {source_name.upper():6s}  ⚪ Not configured           │")
    elif status in ("requires_credentials", "api_key_required"):
        print(f"│  {source_name.upper():6s}  🟡 Needs API credentials    │")
    elif status == "fallback":
        rt = data.get("response_time_ms", "?")
        print(f"│  {source_name.upper():6s}  🟢 Reachable ({rt}ms)         │")
    else:
        print(f"│  {source_name.upper():6s}  🟢 Connected                 │")

print(f"├──────────────────────────────────────┤")

# Report count
reports_dir = os.path.join(client_dir, "reports")
report_count = len(glob.glob(os.path.join(reports_dir, "*"))) if os.path.isdir(reports_dir) else 0
print(f"│  Reports generated: {report_count:<16d}  │")
print(f"│  Latest metrics: {os.path.basename(files[0]):18s}  │")
print(f"└──────────────────────────────────────┘")
PYEOF
