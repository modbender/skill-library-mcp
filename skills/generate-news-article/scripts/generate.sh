#!/bin/bash

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
SERPAPI_SCRIPT="/Users/lihaijian/.openclaw/workspace-wechat-publisher/skills/serpapi/scripts/serp.py"

# Default parameters
KEYWORD="${1:-AI助手}"
NUM_RESULTS="${2:-5}"

# Current date for directory and filename
CURRENT_DATE=$(date +%Y-%m-%d)

# Output directory structure (in agent root directory)
AGENT_ROOT="/Users/lihaijian/.openclaw/workspace-wechat-publisher"
OUTPUT_DIR="$AGENT_ROOT/output/$CURRENT_DATE"
mkdir -p "$OUTPUT_DIR"

# Assets directory for cover images
ASSETS_DIR="$OUTPUT_DIR/assets"
mkdir -p "$ASSETS_DIR"

echo "📰 Generating articles..."
echo "   Keyword: $KEYWORD"
echo "   Results: $NUM_RESULTS"
echo "   Output: $OUTPUT_DIR"

# Call SerpAPI to get search results
echo ""
echo "🔍 Searching..."
if [ ! -f "$SERPAPI_SCRIPT" ]; then
    echo "❌ Error: SerpAPI script not found at $SERPAPI_SCRIPT"
    exit 1
fi

# Execute serp.py search and save to temporary file
TEMP_JSON=$(mktemp)
SERPAPI_API_KEY="9cda299d6f3c24995d727709d33fd8a2ae9b6287be51667802acb4edb7b16796" python3 "$SERPAPI_SCRIPT" google "$KEYWORD" --num "$NUM_RESULTS" > "$TEMP_JSON" 2>&1

# Check if search was successful
if grep -q '"error"' "$TEMP_JSON"; then
    echo "❌ Error in search:"
    grep '"error"' "$TEMP_JSON"
    rm -f "$TEMP_JSON"
    exit 1
fi

# Check if we have results
if ! grep -q '"organic_results"' "$TEMP_JSON"; then
    echo "⚠️  No search results found for: $KEYWORD"
    rm -f "$TEMP_JSON"
    exit 0
fi

# Parse JSON and generate individual articles
echo ""
echo "📝 Generating articles..."

# Process JSON with Python
python3 << PYTHON_SCRIPT
import json
import os
import re
import sys
import urllib.request
from urllib.parse import urlparse

# Read from environment
keyword = "$KEYWORD"
output_dir = "$OUTPUT_DIR"
assets_dir = "$ASSETS_DIR"
num_articles = int("$NUM_RESULTS")

# Read JSON from temporary file
with open("$TEMP_JSON", 'r', encoding='utf-8') as f:
    data = json.load(f)

results = data.get('organic_results', [])

# Limit to NUM_RESULTS articles
articles = results[:num_articles]

if not articles:
    print('未找到相关搜索结果。', file=sys.stderr)
    sys.exit(1)

for item in articles:
    title = item.get('title', 'No Title')
    link = item.get('link', '')
    snippet = item.get('snippet', '')

    # Get thumbnail or favicon if available
    thumbnail = item.get('thumbnail', '')
    favicon = item.get('favicon', '')

    # Clean filename from title
    # Remove special characters and limit length
    safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
    safe_title = re.sub(r'\s+', '_', safe_title)
    safe_title = safe_title[:100]  # Limit to 100 characters

    # Download thumbnail or favicon if available
    cover_image = ''
    image_url = thumbnail if thumbnail else favicon
    if image_url:
        try:
            # Extract filename from URL
            parsed_url = urlparse(image_url)
            filename = os.path.basename(parsed_url.path)
            if not filename or filename == '':
                filename = f'{safe_title[:30]}_cover.png'

            # Download image
            image_path = os.path.join(assets_dir, filename)
            urllib.request.urlretrieve(image_url, image_path)
            cover_image = f'./assets/{filename}'
            print(f'📥 Downloaded image: {filename}', file=sys.stderr)
        except Exception as e:
            print(f'⚠️  Failed to download image: {e}', file=sys.stderr)

    # Create markdown file
    filename = f'{safe_title}.md'
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f'---\n')
        f.write(f'title: {title}\n')
        if cover_image:
            f.write(f'cover: {cover_image}\n')
        f.write(f'---\n')
        f.write(f'\n')
        f.write(f'# {title}\n')
        f.write(f'\n')
        if snippet:
            f.write(f'{snippet}\n')
        f.write(f'\n')
        f.write(f'[原文链接]({link})\n')

    print(f'✅ Generated: {filename}', file=sys.stderr)

print(f'\n📊 Total articles generated: {len(articles)}', file=sys.stderr)
PYTHON_SCRIPT

# Clean up temporary file
rm -f "$TEMP_JSON"

# Check if generation was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All articles generated successfully!"
    echo "📁 Directory: $OUTPUT_DIR"
    echo ""
    echo "📂 Generated files:"
    ls -lh "$OUTPUT_DIR"/*.md 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}'
    echo ""
    echo "🖼️ Downloaded images:"
    ls -lh "$OUTPUT_DIR/assets/" 2>/dev/null | grep -v "^total" | awk '{print "   " $9 " (" $5 ")"}'
else
    echo "❌ Error generating articles"
    exit 1
fi
