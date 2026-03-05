#!/bin/bash
# 远程发布文章到微信公众号 (Optimized for Compliance)
# 基于 wenyan-mcp HTTP Stateless 模式

set -e

# Get script directory for relative path resolution
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
CONFIG_FILE="${SKILL_ROOT}/wechat.env"
MCP_CONFIG_FILE="${MCP_CONFIG_FILE:-$HOME/.openclaw/mcp.json}"

# Load Configuration
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
fi

# Dependencies Check
check_deps() {
    local missing=0
    for cmd in jq mcporter curl; do
        if ! command -v "$cmd" &> /dev/null; then
            echo "❌ Error: Required command '$cmd' not found."
            missing=1
        fi
    done
    
    if [ $missing -eq 1 ]; then
        echo "Please install missing dependencies."
        exit 1
    fi
}

check_deps

# Check Config Files
if [ ! -f "$MCP_CONFIG_FILE" ]; then
    echo "❌ Error: MCP config file not found at: $MCP_CONFIG_FILE"
    echo "Please create it or set MCP_CONFIG_FILE env var."
    exit 1
fi

# Check Credentials
if [ -z "$WECHAT_APP_ID" ] || [ -z "$WECHAT_APP_SECRET" ]; then
    echo "❌ Error: WECHAT_APP_ID or WECHAT_APP_SECRET not set."
    echo "Please configure '$CONFIG_FILE' based on 'wechat.env.example'."
    exit 1
fi

# Usage
FILE_PATH="$1"
THEME_ID="${2:-default}"

if [ -z "$FILE_PATH" ]; then
  echo "Usage: $(basename "$0") <path/to/article.md> [theme_id]"
  echo "Example: ./publish-remote.sh ./my-post.md lapis"
  exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
  echo "❌ Error: File '$FILE_PATH' not found."
  exit 1
fi

# Upload File
echo "🚀 Uploading file to wenyan-mcp..."
FILENAME=$(basename "$FILE_PATH")
CONTENT=$(cat "$FILE_PATH")

# Safe JSON construction with jq
UPLOAD_ARGS=$(jq -n --arg content "$CONTENT" --arg filename "$FILENAME" '{content: $content, filename: $filename}')

# Call remote MCP
UPLOAD_RES=$(mcporter call wenyan-mcp.upload_file --config "$MCP_CONFIG_FILE" --args "$UPLOAD_ARGS" 2>/dev/null)

# Parse Upload Result
FILE_ID=$(echo "$UPLOAD_RES" | jq -r '.file_id // empty')
ERROR_MSG=$(echo "$UPLOAD_RES" | jq -r '.error // empty')

if [ -n "$ERROR_MSG" ]; then
  echo "❌ Upload failed: $ERROR_MSG"
  exit 1
fi

if [ -z "$FILE_ID" ] || [ "$FILE_ID" == "null" ]; then
  echo "❌ Upload failed: Could not parse file_id from response."
  echo "Response: $UPLOAD_RES"
  exit 1
fi

echo "✅ File uploaded! ID: $FILE_ID"
echo "⏳ Publishing to WeChat draft box..."

# Construct Publish Arguments
PUBLISH_ARGS=$(jq -n \
  --arg file_id "$FILE_ID" \
  --arg theme_id "$THEME_ID" \
  --arg app_id "$WECHAT_APP_ID" \
  --arg app_secret "$WECHAT_APP_SECRET" \
  '{file_id: $file_id, theme_id: $theme_id, wechat_app_id: $app_id, wechat_app_secret: $app_secret}')

# Call remote MCP
PUBLISH_RES=$(mcporter call wenyan-mcp.publish_article --config "$MCP_CONFIG_FILE" --args "$PUBLISH_ARGS" 2>/dev/null)

# Parse Publish Result
MEDIA_ID=$(echo "$PUBLISH_RES" | jq -r '.media_id // empty')
PUBLISH_ERR=$(echo "$PUBLISH_RES" | jq -r '.error // empty')

if [ -n "$PUBLISH_ERR" ]; then
  echo "❌ Publish failed: $PUBLISH_ERR"
  echo "Tip: Check if remote server IP is whitelisted in WeChat MP backend."
  exit 1
fi

if [ -z "$MEDIA_ID" ] || [ "$MEDIA_ID" == "null" ]; then
  echo "❌ Publish failed: Unknown response."
  echo "Response: $PUBLISH_RES"
  exit 1
fi

echo "🎉 Success! Media ID: $MEDIA_ID"
echo "Please check your WeChat Official Account draft box."
