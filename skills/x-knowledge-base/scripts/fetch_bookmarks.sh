#!/bin/bash
# fetch_bookmarks.sh - 從 Twitter/X 抓書籤
# 依賴：bird CLI

set -euo pipefail

BOOKMARKS_DIR="${BOOKMARKS_DIR:-/home/ubuntu/clawd/memory/bookmarks}"
BOOKMARKS_TMP_FILE="${BOOKMARKS_TMP_FILE:-/tmp/new_bookmarks.txt}"

# 安全：必須由環境變數提供，不允許硬編碼預設值
BIRD_AUTH_TOKEN="${BIRD_AUTH_TOKEN:-}"
BIRD_CT0="${BIRD_CT0:-}"

if [[ -z "$BIRD_AUTH_TOKEN" || -z "$BIRD_CT0" ]]; then
  echo "❌ 缺少 BIRD_AUTH_TOKEN / BIRD_CT0 環境變數"
  echo "   請先 export 後再執行"
  exit 1
fi

mkdir -p "$BOOKMARKS_DIR"
: > "$BOOKMARKS_TMP_FILE"

echo "📥 開始抓取書籤..."

if ! command -v bird >/dev/null 2>&1; then
  echo "❌ 找不到 bird CLI，請先安裝"
  exit 1
fi

OUTPUT=$(bird --auth-token "$BIRD_AUTH_TOKEN" --ct0 "$BIRD_CT0" bookmarks 2>&1 || true)

if [[ -z "$OUTPUT" ]]; then
  echo "⚠️ bird 無輸出，請檢查 token 或 API 狀態"
  exit 0
fi

echo "$OUTPUT" | grep -E "🔗 https://x.com/" | while read -r line; do
  URL=$(echo "$line" | grep -oE "https://x.com/[a-zA-Z0-9_]+/status/[0-9]+" || true)
  if [[ -n "$URL" ]]; then
    echo "📌 發現書籤: $URL"
    echo "$URL" >> "$BOOKMARKS_TMP_FILE"
  fi
done

echo "✅ 書籤列表已擷取: $BOOKMARKS_TMP_FILE"
