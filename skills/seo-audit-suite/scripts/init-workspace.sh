#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="${SEO_AUDIT_DIR:-$HOME/.openclaw/workspace/seo-audit}"

echo "Initializing SEO audit workspace at: $BASE_DIR"

mkdir -p "$BASE_DIR"/{sites,reports,templates}

if [ ! -f "$BASE_DIR/config.json" ]; then
  cat > "$BASE_DIR/config.json" << 'EOF'
{
  "pagespeed_api_key": "",
  "search_console_key_file": "",
  "default_user_agent": "ReighlanSEOBot/1.0 (+https://reighlan.dev)",
  "max_crawl_depth": 3,
  "max_pages": 50,
  "request_delay_ms": 1000,
  "scoring_weights": {
    "on_page": 0.25,
    "technical": 0.25,
    "geo": 0.20,
    "content_quality": 0.15,
    "user_experience": 0.15
  }
}
EOF
  echo "Created config.json"
fi

echo "✅ SEO audit workspace initialized"
