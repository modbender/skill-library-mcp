#!/usr/bin/env bash
set -euo pipefail

NAME=""
DOMAIN=""
EMAIL=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --name) NAME="$2"; shift 2 ;;
    --domain) DOMAIN="$2"; shift 2 ;;
    --email) EMAIL="$2"; shift 2 ;;
    *) shift ;;
  esac
done

[ -z "$NAME" ] && { echo "Usage: add-client.sh --name <slug> --domain <domain> --email <email>"; exit 1; }

BASE_DIR="${CLIENT_REPORTS_DIR:-$HOME/.openclaw/workspace/client-reports}"
CLIENT_DIR="$BASE_DIR/clients/$NAME"

mkdir -p "$CLIENT_DIR"/{reports,data,templates}

if [ ! -f "$CLIENT_DIR/config.json" ]; then
  cat > "$CLIENT_DIR/config.json" << EOF
{
  "name": "$NAME",
  "display_name": "$(echo "$NAME" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2));}1')",
  "domain": "${DOMAIN:-}",
  "contact_email": "${EMAIL:-}",
  "ga4_property_id": "",
  "search_console_site": "https://${DOMAIN:-example.com}/",
  "social_handles": {
    "x": "",
    "linkedin": "",
    "instagram": ""
  },
  "branding": {
    "logo_url": "",
    "primary_color": "#f97316",
    "accent_color": "#7c3aed"
  },
  "report_preferences": {
    "frequency": "monthly",
    "include_traffic": true,
    "include_search": true,
    "include_social": false,
    "include_recommendations": true
  }
}
EOF
fi

echo "✅ Client added: $NAME"
echo "   Directory: $CLIENT_DIR"
echo "   Edit $CLIENT_DIR/config.json to configure API connections and branding"
