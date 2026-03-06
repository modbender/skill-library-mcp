#!/usr/bin/env bash
# Run a technical SEO audit
set -euo pipefail

URL="${1:-}"
[ -z "$URL" ] && { echo "Usage: technical-audit.sh <url> [--deep]"; exit 1; }

BASE_DIR="${SEO_AUDIT_DIR:-$HOME/.openclaw/workspace/seo-audits}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

DEEP=""
[ "${2:-}" = "--deep" ] && DEEP="true"

python3 -c "
import requests, json, sys, time
from urllib.parse import urlparse
from bs4 import BeautifulSoup

url = '$URL'
deep = '$DEEP'
parsed = urlparse(url)
base = f'{parsed.scheme}://{parsed.netloc}'

print(f'🔧 Technical SEO Audit: {url}')
print()

# Basic page check
headers = {'User-Agent': 'ReighlanSEOBot/1.0'}
start = time.time()
resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
load_time = time.time() - start

print(f'  Status: {resp.status_code}')
print(f'  Load time: {load_time:.2f}s')
print(f'  HTTPS: {\"✅\" if resp.url.startswith(\"https\") else \"❌\"}')
print(f'  Redirects: {len(resp.history)}')
print()

# robots.txt
try:
    robots = requests.get(f'{base}/robots.txt', headers=headers, timeout=5)
    if robots.status_code == 200:
        print('📄 robots.txt: Found')
        lines = robots.text.strip().split('\n')
        # Check for AI crawler blocks
        ai_bots = ['GPTBot', 'PerplexityBot', 'ClaudeBot', 'Google-Extended']
        for bot in ai_bots:
            blocked = any(bot.lower() in line.lower() and 'disallow' in line.lower() for line in lines)
            print(f'  {bot}: {\"🚫 Blocked\" if blocked else \"✅ Allowed\"}')
    else:
        print('📄 robots.txt: Not found (⚠️)')
except:
    print('📄 robots.txt: Error fetching')

print()

# Sitemap
try:
    sitemap = requests.get(f'{base}/sitemap.xml', headers=headers, timeout=5)
    if sitemap.status_code == 200:
        soup = BeautifulSoup(sitemap.text, 'lxml')
        urls = soup.find_all('url')
        print(f'🗺️  sitemap.xml: Found ({len(urls)} URLs)')
    else:
        print('🗺️  sitemap.xml: Not found (⚠️)')
except:
    print('🗺️  sitemap.xml: Error fetching')

print()

# PageSpeed Insights (if API key available)
import os
psi_key = os.environ.get('PAGESPEED_API_KEY')
if psi_key:
    print('⚡ PageSpeed Insights:')
    for strategy in ['mobile', 'desktop']:
        try:
            psi = requests.get(f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy={strategy}&key={psi_key}', timeout=30)
            data = psi.json()
            score = int(data.get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score', 0) * 100)
            print(f'  {strategy.title()}: {score}/100')
        except:
            print(f'  {strategy.title()}: Error')
else:
    print('⚡ PageSpeed: Set PAGESPEED_API_KEY for Core Web Vitals data')

print()
print('✅ Technical audit complete')
" 2>&1
