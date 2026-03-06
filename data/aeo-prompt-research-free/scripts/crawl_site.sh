#!/usr/bin/env bash
# Crawl key pages of a website and output combined text for analysis.
# Usage: ./crawl_site.sh <domain> [output_file]
# Requires: curl
# Outputs markdown-formatted content from homepage, about, pricing, and blog pages.

set -euo pipefail

DOMAIN="${1:?Usage: crawl_site.sh <domain> [output_file]}"
OUTPUT="${2:-/dev/stdout}"

# Normalize domain — strip protocol and trailing slash
DOMAIN="${DOMAIN#https://}"
DOMAIN="${DOMAIN#http://}"
DOMAIN="${DOMAIN%/}"

BASE="https://${DOMAIN}"

# Common pages to crawl
PAGES=(
  "/"
  "/about"
  "/about-us"
  "/pricing"
  "/products"
  "/services"
  "/features"
  "/blog"
  "/resources"
)

echo "# Site Crawl: ${DOMAIN}" > "$OUTPUT"
echo "" >> "$OUTPUT"
echo "Crawled at: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$OUTPUT"
echo "" >> "$OUTPUT"

for path in "${PAGES[@]}"; do
  url="${BASE}${path}"
  status=$(curl -s -o /dev/null -w "%{http_code}" -L --max-time 10 "$url" 2>/dev/null || echo "000")
  
  if [ "$status" = "200" ]; then
    echo "## ${url}" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    # Extract text content, strip HTML tags, collapse whitespace
    curl -sL --max-time 15 "$url" 2>/dev/null \
      | sed 's/<script[^>]*>.*<\/script>//g' \
      | sed 's/<style[^>]*>.*<\/style>//g' \
      | sed 's/<[^>]*>//g' \
      | sed 's/&nbsp;/ /g; s/&amp;/\&/g; s/&lt;/</g; s/&gt;/>/g' \
      | tr -s '[:space:]' '\n' \
      | head -200 \
      >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    echo "---" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
  fi
done

echo "Crawl complete." >> "$OUTPUT"
