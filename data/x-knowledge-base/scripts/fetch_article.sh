#!/bin/bash
# fetch_article.sh - 用 Jina AI 擷取文章全文
# 依賴：curl, Jina AI (免費)

set -e

# 設定
JINA_API="https://r.jina.ai/https"
BOOKMARKS_FILE="${BOOKMARKS_FILE:-/tmp/new_bookmarks.txt}"
OUTPUT_DIR="${OUTPUT_DIR:-/home/ubuntu/clawd/memory/bookmarks}"

# 確保輸出目錄存在
mkdir -p "$OUTPUT_DIR"

echo "🔍 開始擷取文章內容..."

if [ ! -f "$BOOKMARKS_FILE" ]; then
    echo "❌ 沒有書籤檔案: $BOOKMARKS_FILE"
    exit 1
fi

# 讀取每個書籤連結
while read -r URL; do
    if [ -z "$URL" ]; then
        continue
    fi
    
    echo "📄 擷取: $URL"
    
    # 用 Jina AI 擷取內容
    # Jina 格式：https://r.jina.ai/http://目標網址
    CONTENT=$(curl -s "${JINA_API}/${URL}" 2>/dev/null || echo "")
    
    if [ -n "$CONTENT" ]; then
        # 從 URL 產生檔名
        FILENAME=$(echo "$URL" | sed 's|https://x.com/||' | sed 's|/status/.*||' | sed 's|/|_|g')
        TIMESTAMP=$(date +%Y-%m-%d)
        FULL_PATH="${OUTPUT_DIR}/${TIMESTAMP}_${FILENAME}.md"
        
        # 存檔（不覆蓋已有的）
        if [ ! -f "$FULL_PATH" ]; then
            echo "$CONTENT" > "$FULL_PATH"
            echo "✅ 已存檔: $FULL_PATH"
        else
            echo "⏭️ 略過（已存在）: $FULL_PATH"
        fi
    else
        echo "❌ 擷取失敗: $URL"
    fi
    
done < "$BOOKMARKS_FILE"

echo "✅ 文章擷取完成"
