#!/usr/bin/env bash
# Run a GEO (Generative Engine Optimization) audit
set -euo pipefail

URL="${1:-}"
[ -z "$URL" ] && { echo "Usage: geo-audit.sh <url>"; exit 1; }

BASE_DIR="${SEO_AUDIT_DIR:-$HOME/.openclaw/workspace/seo-audits}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 -c "
from seo_auditor import fetch_page, audit_geo, audit_schema, audit_content
from bs4 import BeautifulSoup
import json, sys

url = '$URL'
print(f'🌐 GEO Audit: {url}')
print()

resp, _ = fetch_page(url)
soup = BeautifulSoup(resp.text, 'lxml')
soup_content = BeautifulSoup(resp.text, 'lxml')

geo = audit_geo(soup)
schema = audit_schema(soup)
content = audit_content(soup_content)

print(f'GEO Readiness Score: {geo[\"score\"]}/100')
print(f'Schema Score: {schema[\"score\"]}/100')
print(f'Content Score: {content[\"score\"]}/100')
print()

print('Findings:')
for issue in geo['issues']:
    icon = '🔴' if issue['severity'] == 'critical' else '🟡' if issue['severity'] == 'warning' else 'ℹ️'
    print(f'  {icon} {issue[\"msg\"]}')

print()
print('Schema types found:', ', '.join(schema['schemas']) if schema['schemas'] else 'None')
print(f'Word count: {content[\"word_count\"]}')
print(f'FAQ Schema: {\"Yes\" if geo[\"has_faq_schema\"] else \"No\"}')
print(f'HowTo Schema: {\"Yes\" if geo[\"has_howto_schema\"] else \"No\"}')
print(f'Author attribution: {\"Yes\" if geo[\"has_author\"] else \"No\"}')
print(f'Publish date: {\"Yes\" if geo[\"has_date\"] else \"No\"}')
" 2>&1
