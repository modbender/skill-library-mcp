#!/usr/bin/env bash
# Job Hunter — Multi-source job search aggregator
# Usage: search_jobs.sh "role keywords" [--location "city"] [--remote] [--days 7] [--limit 20]
#
# Searches multiple job boards via web scraping and returns structured results.
# Sources: LinkedIn, Indeed, Glassdoor (via Google site: search)
#
# Output: JSON array of job objects to stdout
# Requires: curl, python3

set -euo pipefail

QUERY="${1:?Usage: search_jobs.sh \"role keywords\" [--location city] [--remote] [--days 7] [--limit 20]}"
LOCATION=""
REMOTE=false
DAYS=7
LIMIT=20

shift
while [[ $# -gt 0 ]]; do
    case "$1" in
        --location) LOCATION="$2"; shift 2 ;;
        --remote) REMOTE=true; shift ;;
        --days) DAYS="$2"; shift 2 ;;
        --limit) LIMIT="$2"; shift 2 ;;
        *) shift ;;
    esac
done

# Build search queries for multiple sources
ENCODED_QUERY=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$QUERY'))")
ENCODED_LOCATION=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${LOCATION:-}'))")

LOCATION_PART=""
if [[ -n "$LOCATION" ]]; then
    LOCATION_PART="+${ENCODED_LOCATION}"
fi

REMOTE_PART=""
if [[ "$REMOTE" == "true" ]]; then
    REMOTE_PART="+remote"
fi

FRESHNESS="pw"
if [[ "$DAYS" -le 1 ]]; then
    FRESHNESS="pd"
elif [[ "$DAYS" -le 7 ]]; then
    FRESHNESS="pw"
elif [[ "$DAYS" -le 30 ]]; then
    FRESHNESS="pm"
else
    FRESHNESS="py"
fi

# Search via Brave API if available, otherwise output search URLs for manual use
if [[ -n "${BRAVE_API_KEY:-}" ]]; then
    SEARCH_QUERIES=(
        "site:linkedin.com/jobs ${QUERY} ${LOCATION:-} ${REMOTE:+remote}"
        "site:indeed.com ${QUERY} ${LOCATION:-} ${REMOTE:+remote}"
        "site:glassdoor.com/job ${QUERY} ${LOCATION:-} ${REMOTE:+remote}"
        "${QUERY} jobs ${LOCATION:-} ${REMOTE:+remote} hiring"
    )
    
    ALL_RESULTS="[]"
    
    for sq in "${SEARCH_QUERIES[@]}"; do
        ENCODED_SQ=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$sq'))")
        RESPONSE=$(curl -s "https://api.search.brave.com/res/v1/web/search?q=${ENCODED_SQ}&count=10&freshness=${FRESHNESS}" \
            -H "Accept: application/json" \
            -H "X-Subscription-Token: ${BRAVE_API_KEY}" 2>/dev/null || echo '{}')
        
        PARSED=$(echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    results = data.get('web', {}).get('results', [])
    jobs = []
    for r in results[:5]:
        jobs.append({
            'title': r.get('title', ''),
            'url': r.get('url', ''),
            'description': r.get('description', ''),
            'source': r.get('url', '').split('/')[2] if '/' in r.get('url', '') else 'unknown',
            'date': r.get('page_age', r.get('published', ''))
        })
    print(json.dumps(jobs))
except:
    print('[]')
" 2>/dev/null || echo '[]')
        
        ALL_RESULTS=$(python3 -c "
import json, sys
a = json.loads('$ALL_RESULTS')
b = json.loads(sys.stdin.read())
seen = set(x['url'] for x in a)
for item in b:
    if item['url'] not in seen:
        a.append(item)
        seen.add(item['url'])
print(json.dumps(a))
" <<< "$PARSED" 2>/dev/null || echo "$ALL_RESULTS")
    done
    
    # Trim to limit
    echo "$ALL_RESULTS" | python3 -c "
import json, sys
results = json.load(sys.stdin)[:${LIMIT}]
print(json.dumps(results, indent=2))
"
else
    # No API key — output search URLs for the agent to use with web_search tool
    cat << URLS
{
  "mode": "manual",
  "message": "No BRAVE_API_KEY found. Use these search queries with the web_search tool:",
  "queries": [
    "site:linkedin.com/jobs ${QUERY} ${LOCATION:-} ${REMOTE:+remote}",
    "site:indeed.com ${QUERY} ${LOCATION:-} ${REMOTE:+remote}",
    "site:glassdoor.com/job ${QUERY} ${LOCATION:-} ${REMOTE:+remote}",
    "${QUERY} jobs ${LOCATION:-} ${REMOTE:+remote} hiring 2024 2025 2026"
  ],
  "freshness": "${FRESHNESS}"
}
URLS
fi
