#!/usr/bin/env bash
# Search Florida Sunbiz for corporations/LLCs by officer name
# Usage: sunbiz-officer.sh "First Last"
# Example: sunbiz-officer.sh "John Smith"

set -euo pipefail

NAME="${1:?Usage: sunbiz-officer.sh \"First Last\"}"

# Sunbiz search URL (returns HTML, needs parsing)
# Note: This URL pattern works for officer/RA name search
FIRST=$(echo "$NAME" | awk '{print $1}')
LAST=$(echo "$NAME" | awk '{print $NF}')

echo "Searching Florida Sunbiz for officer: $NAME"
echo "---"

# Try the direct search URL
URL="https://search.sunbiz.org/Inquiry/CorporationSearch/SearchByOfficerRA?SearchTerm=${LAST}+${FIRST}&SearchType=Officer"
echo "URL: $URL"
echo ""
echo "Note: Sunbiz is JS-rendered. If web_fetch returns empty results,"
echo "use the browser tool (profile=openclaw) to navigate to:"
echo "  https://search.sunbiz.org/Inquiry/CorporationSearch/SearchByOfficerRA"
echo "Then search for: $LAST $FIRST"
echo ""

# Attempt fetch (may not render JS)
curl -sL "$URL" | grep -oP '(?<=<a href="/Inquiry/CorporationSearch/SearchResultDetail\?)[^"]+' | head -20 || echo "No results via curl (site may require JS rendering)"
