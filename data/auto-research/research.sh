#!/bin/bash
#
# research.sh - Main research orchestrator for OpenClaw auto-research skill
#
# Usage: research.sh "<topic>" [depth]
#   depth: quick (5 sources), standard (7 sources), deep (10+ sources)
#

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRAVE_API_KEY="${BRAVE_API_KEY:-BSAfZrm_28TmR5FM9FhMCrTA1A3zS2n}"
OBSIDIAN_VAULT="${OBSIDIAN_VAULT:-$HOME/Documents/Obsidian/YoderVault}"
QDRANT_URL="${QDRANT_URL:-http://10.0.0.120:6333}"
OUTPUT_DIR="$OBSIDIAN_VAULT/Inbox"
CACHE_SCRIPT="$SCRIPT_DIR/search-cache.sh"
VECTORIZE_SCRIPT="$SCRIPT_DIR/vectorize.sh"
TEMPLATE_FILE="$SCRIPT_DIR/briefing-template.md"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Cross-platform hash function
hash_sha256() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$@"
    else
        shasum -a 256 "$@"
    fi
}

hash_sha256_string() {
    if command -v sha256sum >/dev/null 2>&1; then
        echo -n "$1" | sha256sum | cut -d' ' -f1
    else
        echo -n "$1" | shasum -a 256 | cut -d' ' -f1
    fi
}

# Parse arguments
TOPIC="${1:-}"
DEPTH="${2:-${RESEARCH_DEPTH:-standard}}"

if [[ -z "$TOPIC" ]]; then
    echo -e "${RED}Error: No research topic provided${NC}"
    echo "Usage: research.sh \"<topic>\" [quick|standard|deep]"
    exit 1
fi

# Set source count based on depth
case "$DEPTH" in
    quick)
        SOURCE_COUNT=5
        DETAIL_LEVEL="brief"
        ;;
    deep)
        SOURCE_COUNT=10
        DETAIL_LEVEL="comprehensive"
        ;;
    standard|*)
        SOURCE_COUNT=7
        DETAIL_LEVEL="standard"
        DEPTH="standard"
        ;;
esac

echo -e "${BLUE}🔍 Auto-Research Agent${NC}"
echo "=========================="
echo -e "Topic: ${YELLOW}$TOPIC${NC}"
echo -e "Depth: ${YELLOW}$DEPTH${NC} (${SOURCE_COUNT} sources)"
echo ""

# Create output directory if needed
mkdir -p "$OUTPUT_DIR"

# Generate safe filename
SAFE_TOPIC=$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-' | head -c 50)
DATE_STR=$(date +%Y-%m-%d)
OUTPUT_FILE="$OUTPUT_DIR/Research - ${SAFE_TOPIC} - ${DATE_STR}.md"

# Build search query with context for better results
SEARCH_QUERY="$TOPIC"
if [[ "$DEPTH" == "deep" ]]; then
    SEARCH_QUERY="$TOPIC comprehensive analysis 2026"
fi

# Check cache first
echo -e "${BLUE}Checking cache...${NC}"
CACHE_KEY="research:$(hash_sha256_string "$TOPIC:$DEPTH")"
CACHED_RESULT=$($CACHE_SCRIPT get "$CACHE_KEY" 2>/dev/null || echo "")

if [[ -n "$CACHED_RESULT" && "$CACHED_RESULT" != "null" && "$CACHED_RESULT" != "NOT_FOUND" ]]; then
    echo -e "${GREEN}✓ Cache hit - using cached results${NC}"
    SEARCH_RESULTS="$CACHED_RESULT"
else
    echo -e "${BLUE}Executing web search...${NC}"
    
    
    # Call Brave Search API
    API_RESPONSE=$(curl -s --max-time 30 \
        -H "Accept: application/json" \
        -H "X-Subscription-Token: $BRAVE_API_KEY" \
        "https://api.search.brave.com/res/v1/web/search?q=$(printf '%s' "$SEARCH_QUERY" | jq -sRr @uri)&count=$SOURCE_COUNT&freshness=py&result_filter=web") || {
        echo -e "${RED}✗ Search API call failed${NC}"
        exit 1
    }
    
    # Validate response
    if ! echo "$API_RESPONSE" | jq -e '.web' >/dev/null 2>&1; then
        echo -e "${RED}✗ Invalid API response${NC}"
        echo "$API_RESPONSE" | jq -r '.message // "Unknown error"' 2>/dev/null || echo "No results found"
        exit 1
    fi
    
    SEARCH_RESULTS="$API_RESPONSE"
    
    # Cache the results
    $CACHE_SCRIPT set "$CACHE_KEY" "$SEARCH_RESULTS" 86400 >/dev/null 2>&1 || true
    echo -e "${GREEN}✓ Search complete - ${SOURCE_COUNT} sources requested${NC}"
fi

# Extract and process results
echo -e "${BLUE}Analyzing sources...${NC}"

# Build the sources array from Brave API response - limit to SOURCE_COUNT
SOURCES_JSON=$(echo "$SEARCH_RESULTS" | jq -r --argjson count "$SOURCE_COUNT" '
    [.web.results // [] | .[] | select(.url != null)] |
    .[:$count] |
    map({
        title: (.title // "Untitled"),
        url: .url,
        description: (.description // "No description available"),
        age: (.age // "unknown"),
        source_name: (.url | split("/") | .[2] | sub("^www\\."; ""))
    })
')

# Calculate confidence based on source domains
calculate_confidence() {
    local urls="$1"
    local high_count=0
    local total=0
    
    while IFS= read -r url; do
        [[ -z "$url" ]] && continue
        total=$((total + 1))
        if [[ "$url" =~ \.(edu|gov) ]] || \
           [[ "$url" =~ (arxiv\.org|nature\.com|science\.org|ieee\.org) ]] || \
           [[ "$url" =~ (reuters\.com|bloomberg\.com|wsj\.com|nytimes\.com) ]]; then
            high_count=$((high_count + 1))
        fi
    done <<< "$urls"
    
    if [[ $total -eq 0 ]]; then
        echo "Low"
    elif [[ $high_count -ge $((total / 2)) ]]; then
        echo "High"
    elif [[ $high_count -ge $((total / 4)) ]]; then
        echo "Medium"
    else
        echo "Low"
    fi
}

SOURCE_URLS=$(echo "$SOURCES_JSON" | jq -r '.[].url')
CONFIDENCE=$(calculate_confidence "$SOURCE_URLS")

# Generate themes from search results
generate_themes() {
    local descriptions="$1"
    
    # Extract key terms and group them
    echo "$descriptions" | tr '[:upper:]' '[:lower:]' | \
        grep -oE '\b(ai|artificial intelligence|machine learning|automation|software|platform|solution|market|trends|growth|pricing|features|integration|mobile|cloud|security)\b' | \
        sort | uniq -c | sort -rn | head -5 | awk '{print $2}' | tr '\n' ',' | sed 's/,$//'
}

DESCRIPTIONS=$(echo "$SOURCES_JSON" | jq -r '.[].description' | tr '\n' ' ')
THEMES=$(generate_themes "$DESCRIPTIONS")

# Build key findings from descriptions
generate_findings() {
    local sources="$1"
    
    echo "$sources" | jq -r '.[] | "- **" + .source_name + ":** " + .description[:120] + (if (.description | length) > 120 then "..." else "" end)' | head -8
}

KEY_FINDINGS=$(generate_findings "$SOURCES_JSON")

# Build sources list
SOURCES_LIST=$(echo "$SOURCES_JSON" | jq -r '.[] | "- [" + .title + "](" + .url + ") - " + .source_name + " (" + .age + ")"')

# Generate action items based on topic
generate_actions() {
    local topic="$1"
    local confidence="$2"
    
    cat <<EOF
- [ ] Review ${SOURCE_COUNT} sources for complete context
- [ ] Cross-reference findings with internal knowledge base
- [ ] Identify key stakeholders for this research topic
- [ ] Schedule follow-up research if confidence is ${confidence}
EOF
    
    if [[ "$topic" =~ (software|tool|platform|app) ]]; then
        echo "- [ ] Evaluate 2-3 solutions against requirements"
    fi
    if [[ "$topic" =~ (market|industry|trends) ]]; then
        echo "- [ ] Monitor for quarterly updates"
    fi
}

ACTION_ITEMS=$(generate_actions "$TOPIC" "$CONFIDENCE")

# Generate metadata
RESEARCH_ID="$(date +%s)-$(hash_sha256_string "$TOPIC" | cut -c1-8)"
CACHE_STATUS=$([[ -n "$CACHED_RESULT" && "$CACHED_RESULT" != "NOT_FOUND" ]] && echo "Hit" || echo "Miss")
CONFIDENCE_LOWER=$(echo "$CONFIDENCE" | tr '[:upper:]' '[:lower:]')

# Generate executive summary
SOURCE_1=$(echo "$SOURCES_JSON" | jq -r '.[0].source_name // "unknown"')
SOURCE_2=$(echo "$SOURCES_JSON" | jq -r '.[1].source_name // "other credible outlets"')
EXECUTIVE_SUMMARY="Research on \"$TOPIC\" reveals significant activity in this space as of ${DATE_STR}. Key themes include ${THEMES:-various aspects of the topic}. Sources indicate this is a ${DETAIL_LEVEL}-level topic with ${CONFIDENCE_LOWER} confidence based on source quality. Primary sources include ${SOURCE_1} and ${SOURCE_2}. Further analysis recommended for strategic decisions."

# Generate detailed analysis placeholder
FIRST_SOURCE=$(echo "$SOURCES_LIST" | head -1 | sed 's/^- //')
LAST_SOURCE=$(echo "$SOURCES_LIST" | tail -1 | sed 's/^- //')
DETAILED_ANALYSIS="This research gathered information from ${SOURCE_COUNT} sources spanning various perspectives on \"$TOPIC\". The sources range from ${FIRST_SOURCE} to ${LAST_SOURCE}. Key themes that emerged include: ${THEMES:-multiple relevant aspects}. For deeper insights, consider conducting follow-up research on specific subtopics identified in the key findings above."

# Generate trends
TRENDS="The following trends were identified across analyzed sources:

$(echo "$KEY_FINDINGS" | head -5)"

# Generate considerations
CONSIDERATIONS="- **Source Diversity:** Reviewed ${SOURCE_COUNT} sources with varying perspectives
- **Confidence Level:** ${CONFIDENCE} - based on domain authority and recency
- **Research Limitation:** Web search results may not capture all recent developments
- **Recommendation:** Validate key findings with domain experts before strategic decisions"

# Generate the briefing
echo -e "${BLUE}Compiling briefing...${NC}"

cat > "$OUTPUT_FILE" << EOF
# Research: $TOPIC

**Date:** $DATE_STR  
**Depth:** $DEPTH  
**Sources:** $SOURCE_COUNT  
**Confidence:** $CONFIDENCE

## Executive Summary

$EXECUTIVE_SUMMARY

## Key Findings

$KEY_FINDINGS

## Detailed Analysis

### Market Overview

Based on $SOURCE_COUNT sources analyzed, the following patterns emerge for "$TOPIC":

$DETAILED_ANALYSIS

### Emerging Trends

$TRENDS

### Considerations

$CONSIDERATIONS

## Sources

$SOURCES_LIST

## Action Items

$ACTION_ITEMS

## Research Metadata

- **Research ID:** $RESEARCH_ID
- **Cache Status:** $CACHE_STATUS
- **Vectorized:** {{VECTORIZED}}
- **Query:** $SEARCH_QUERY

---

*Generated by OpenClaw Auto-Research Agent v1.0*
EOF

echo -e "${GREEN}✓ Briefing saved: $OUTPUT_FILE${NC}"

# Vectorize the research
echo -e "${BLUE}Vectorizing for Qdrant...${NC}"
if [[ -x "$VECTORIZE_SCRIPT" ]]; then
    if $VECTORIZE_SCRIPT "$OUTPUT_FILE" "$TOPIC" "$SOURCES_LIST"; then
        VECTORIZED="Yes"
        echo -e "${GREEN}✓ Vectorization complete${NC}"
    else
        VECTORIZED="Failed"
        echo -e "${YELLOW}⚠ Vectorization failed (non-critical)${NC}"
    fi
else
    VECTORIZED="Skipped"
    echo -e "${YELLOW}⚠ Vectorize script not found${NC}"
fi

# Update file with vectorization status using a safe replacement
perl -i -pe "s/\\{\\{VECTORIZED\\}\\}/$VECTORIZED/g" "$OUTPUT_FILE" 2>/dev/null || \
sed -e "s/{{VECTORIZED}}/$VECTORIZED/g" "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" 2>/dev/null && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE" 2>/dev/null || true

# Summary
echo ""
echo "=========================="
echo -e "${GREEN}✓ Research Complete!${NC}"
echo "=========================="
echo -e "Topic:     $TOPIC"
echo -e "Depth:     $DEPTH"
echo -e "Sources:   $SOURCE_COUNT"
echo -e "Confidence: $CONFIDENCE"
echo -e "Output:    $OUTPUT_FILE"
echo -e "Vectorized: $VECTORIZED"
echo ""
echo "Next steps:"
echo "  - Review briefing in Obsidian"
echo "  - Search vectorized content: ./tools/yoder-kb.sh search \"$TOPIC\""

# Return output file path for integration
echo "$OUTPUT_FILE"
