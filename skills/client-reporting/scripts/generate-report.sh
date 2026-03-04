#!/usr/bin/env bash
set -euo pipefail

CLIENT=""
TYPE="monthly"
FORMAT="html"

while [[ $# -gt 0 ]]; do
  case $1 in
    --client) CLIENT="$2"; shift 2 ;;
    --type) TYPE="$2"; shift 2 ;;
    --format) FORMAT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

[ -z "$CLIENT" ] && { echo "Usage: generate-report.sh --client <name> [--type weekly|monthly|quarterly] [--format html|md]"; exit 1; }

BASE_DIR="${CLIENT_REPORTS_DIR:-$HOME/.openclaw/workspace/client-reports}"
CLIENT_DIR="$BASE_DIR/clients/$CLIENT"

[ ! -d "$CLIENT_DIR" ] && { echo "❌ Client not found: $CLIENT"; exit 1; }

export RPT_CLIENT_DIR="$CLIENT_DIR"
export RPT_BASE_DIR="$BASE_DIR"
export RPT_TYPE="$TYPE"
export RPT_FORMAT="$FORMAT"

python3 << 'PYEOF'
import json, os, glob
from datetime import datetime

client_dir = os.environ["RPT_CLIENT_DIR"]
base_dir = os.environ["RPT_BASE_DIR"]
report_type = os.environ["RPT_TYPE"]
report_format = os.environ["RPT_FORMAT"]

# Load client config
client_config = {}
config_path = os.path.join(client_dir, "config.json")
if os.path.exists(config_path):
    with open(config_path) as f:
        client_config = json.load(f)

client_name = client_config.get("display_name", client_config.get("name", "Unknown"))
reports_dir = os.path.join(client_dir, "reports")
os.makedirs(reports_dir, exist_ok=True)

# Find latest metrics
data_dir = os.path.join(client_dir, "data")
metric_files = sorted(glob.glob(os.path.join(data_dir, "metrics-*.json")), reverse=True)

metrics = {}
if metric_files:
    with open(metric_files[0]) as f:
        metrics = json.load(f)

timestamp = datetime.now().strftime("%Y%m%d")
period = metrics.get("period", {"start": "N/A", "end": "N/A"})

if report_format == "html":
    # Try Jinja2 template
    template_path = os.path.join(client_dir, "templates", f"{report_type}.html")
    if not os.path.exists(template_path):
        template_path = os.path.join(base_dir, "templates", f"{report_type}.html")
    
    if os.path.exists(template_path):
        try:
            from jinja2 import Template
            with open(template_path) as f:
                tmpl = Template(f.read())
            
            # Build template context with safe defaults
            context = {
                "client_name": client_name,
                "period_start": period["start"],
                "period_end": period["end"],
                "generated_at": datetime.now().strftime("%B %d, %Y"),
                "sessions": "—", "users": "—", "pageviews": "—", "bounce_rate": "—",
                "sessions_change": 0, "users_change": 0, "pageviews_change": 0, "bounce_change": 0,
                "clicks": "—", "impressions": "—", "ctr": "—", "avg_position": "—",
                "top_queries": [], "top_pages": [],
            }
            
            # Merge actual metrics if available
            ga4 = metrics.get("sources", {}).get("ga4", {})
            if isinstance(ga4, dict) and ga4.get("status") not in ("not_configured", "requires_credentials"):
                for key in ["sessions", "users", "pageviews", "bounce_rate"]:
                    if key in ga4:
                        context[key] = ga4[key]
            
            html = tmpl.render(**context)
            output = os.path.join(reports_dir, f"{report_type}-{timestamp}.html")
            with open(output, "w") as f:
                f.write(html)
            print(f"✅ HTML report generated: {output}")
        except ImportError:
            print("⚠️ jinja2 not installed. Falling back to markdown.")
            report_format = "md"
    else:
        print(f"⚠️ Template not found: {template_path}. Falling back to markdown.")
        report_format = "md"

if report_format == "md":
    report = f"# {client_name} — {report_type.title()} Report\n\n"
    report += f"**Period:** {period['start']} to {period['end']}\n"
    report += f"**Generated:** {datetime.now().strftime('%B %d, %Y')}\n\n"
    
    sources = metrics.get("sources", {})
    
    if "ga4" in sources:
        ga4 = sources["ga4"]
        report += "## Traffic Overview\n\n"
        if ga4.get("status") == "not_configured":
            report += "Google Analytics not configured. Add `ga4_property_id` to client config.\n\n"
        elif ga4.get("status") == "requires_credentials":
            report += "Google Analytics credentials needed. Add service account key.\n\n"
        else:
            report += f"- Sessions: {ga4.get('sessions', 'N/A')}\n"
            report += f"- Users: {ga4.get('users', 'N/A')}\n\n"
    
    if "gsc" in sources:
        gsc = sources["gsc"]
        report += "## Search Performance\n\n"
        if gsc.get("status") in ("not_configured", "requires_credentials"):
            report += "Search Console not configured.\n\n"
        elif gsc.get("status") == "fallback":
            report += f"- Domain reachable: {'✅' if gsc.get('domain_reachable') else '❌'}\n"
            report += f"- Response time: {gsc.get('response_time_ms', 'N/A')}ms\n\n"
    
    report += "---\n*Generated by Reighlan Skills*\n"
    
    output = os.path.join(reports_dir, f"{report_type}-{timestamp}.md")
    with open(output, "w") as f:
        f.write(report)
    print(f"✅ Markdown report generated: {output}")

print(f"\n   Client: {client_name}")
print(f"   Type: {report_type}")
print(f"   Next: Run deliver-report.sh --client {client_config.get('name', '')} --latest")
PYEOF
