#!/usr/bin/env bash
# Crawl and audit multiple pages on a site
set -euo pipefail

DOMAIN="${1:-}"
[ -z "$DOMAIN" ] && { echo "Usage: audit-site.sh <domain-url> [--max-pages N]"; exit 1; }

MAX_PAGES=50
while [[ $# -gt 1 ]]; do
  case $2 in
    --max-pages) MAX_PAGES="$3"; shift 2 ;;
    *) shift ;;
  esac
done

BASE_DIR="${SEO_AUDIT_DIR:-$HOME/.openclaw/workspace/seo-audits}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 "$SCRIPT_DIR/site_crawler.py" --url "$DOMAIN" --max-pages "$MAX_PAGES" --output-dir "$BASE_DIR/audits"
