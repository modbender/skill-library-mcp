#!/usr/bin/env bash
set -euo pipefail

CLIENT=""
SOURCE="all"
PERIOD="30d"

while [[ $# -gt 0 ]]; do
  case $1 in
    --client) CLIENT="$2"; shift 2 ;;
    --source) SOURCE="$2"; shift 2 ;;
    --period) PERIOD="$2"; shift 2 ;;
    *) shift ;;
  esac
done

[ -z "$CLIENT" ] && { echo "Usage: pull-metrics.sh --client <name> [--source ga4|gsc|social|all] [--period 30d]"; exit 1; }

BASE_DIR="${CLIENT_REPORTS_DIR:-$HOME/.openclaw/workspace/client-reports}"
CLIENT_DIR="$BASE_DIR/clients/$CLIENT"
DATA_DIR="$CLIENT_DIR/data"

[ ! -d "$CLIENT_DIR" ] && { echo "❌ Client not found: $CLIENT"; exit 1; }
mkdir -p "$DATA_DIR"

export METRICS_CLIENT_DIR="$CLIENT_DIR"
export METRICS_DATA_DIR="$DATA_DIR"
export METRICS_SOURCE="$SOURCE"
export METRICS_PERIOD="$PERIOD"
export METRICS_BASE_DIR="$BASE_DIR"

python3 << 'PYEOF'
import json, os, sys
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print("pip3 install requests")
    sys.exit(1)

client_dir = os.environ["METRICS_CLIENT_DIR"]
data_dir = os.environ["METRICS_DATA_DIR"]
source = os.environ["METRICS_SOURCE"]
period = os.environ["METRICS_PERIOD"]
base_dir = os.environ["METRICS_BASE_DIR"]

# Load configs
client_config = {}
client_config_path = os.path.join(client_dir, "config.json")
if os.path.exists(client_config_path):
    with open(client_config_path) as f:
        client_config = json.load(f)

global_config = {}
global_config_path = os.path.join(base_dir, "config.json")
if os.path.exists(global_config_path):
    with open(global_config_path) as f:
        global_config = json.load(f)

# Parse period
days = int(period.replace("d", ""))
end_date = datetime.utcnow()
start_date = end_date - timedelta(days=days)

client_name = client_config.get("display_name", client_config.get("name", "Unknown"))
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

print(f"📊 Pulling metrics for {client_name}")
print(f"   Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

metrics = {
    "client": client_name,
    "period": {"start": start_date.strftime("%Y-%m-%d"), "end": end_date.strftime("%Y-%m-%d"), "days": days},
    "pulled_at": datetime.utcnow().isoformat() + "Z",
    "sources": {},
}

# --- Google Analytics 4 ---
if source in ("all", "ga4"):
    ga4_id = client_config.get("ga4_property_id", "")
    creds_file = global_config.get("ga4_credentials_file", "")
    
    if ga4_id and creds_file:
        print("   → GA4: pulling...")
        # GA4 API call would go here
        # For now, create placeholder structure
        metrics["sources"]["ga4"] = {
            "status": "requires_credentials",
            "message": "Set ga4_property_id and ga4_credentials_file to enable",
            "expected_metrics": ["sessions", "users", "new_users", "pageviews", "bounce_rate", "avg_session_duration", "top_pages", "traffic_sources"],
        }
        print("   → GA4: ⚠️ credentials needed")
    else:
        metrics["sources"]["ga4"] = {"status": "not_configured"}
        if source == "ga4":
            print("   → GA4: not configured. Set ga4_property_id in client config.")

# --- Google Search Console ---
if source in ("all", "gsc"):
    gsc_site = client_config.get("search_console_site", "")
    creds_file = global_config.get("search_console_credentials_file", "")
    domain = client_config.get("domain", "")
    
    if gsc_site and creds_file:
        print("   → GSC: pulling...")
        metrics["sources"]["gsc"] = {
            "status": "requires_credentials",
            "expected_metrics": ["clicks", "impressions", "ctr", "avg_position", "top_queries", "top_pages"],
        }
        print("   → GSC: ⚠️ credentials needed")
    elif domain:
        # Fallback: use our SEO audit tools for basic metrics
        print("   → GSC: not configured, using web audit fallback...")
        try:
            resp = requests.get(f"https://{domain}", headers={"User-Agent": "ReighlanBot/1.0"}, timeout=10)
            metrics["sources"]["gsc"] = {
                "status": "fallback",
                "domain_reachable": resp.status_code == 200,
                "response_time_ms": int(resp.elapsed.total_seconds() * 1000),
            }
            print(f"   → GSC: fallback — site reachable, {resp.elapsed.total_seconds():.1f}s response")
        except:
            metrics["sources"]["gsc"] = {"status": "error", "message": "Could not reach domain"}
    else:
        metrics["sources"]["gsc"] = {"status": "not_configured"}

# --- Social Media ---
if source in ("all", "social"):
    handles = client_config.get("social_handles", {})
    if any(handles.values()):
        print("   → Social: pulling...")
        social_data = {}
        for platform, handle in handles.items():
            if handle:
                social_data[platform] = {"handle": handle, "status": "api_key_required"}
        metrics["sources"]["social"] = social_data
        print("   → Social: ⚠️ API keys needed for detailed metrics")
    else:
        metrics["sources"]["social"] = {"status": "not_configured"}

# Save metrics
output = os.path.join(data_dir, f"metrics-{timestamp}.json")
with open(output, "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\n   Saved: {output}")

# Check what's configured vs not
configured = [s for s, d in metrics["sources"].items() if isinstance(d, dict) and d.get("status") not in ("not_configured",)]
not_configured = [s for s, d in metrics["sources"].items() if isinstance(d, dict) and d.get("status") == "not_configured"]

if not_configured:
    print(f"\n   ⚠️ Not configured: {', '.join(not_configured)}")
    print(f"   Edit {client_config_path} to add API connections")
PYEOF
