#!/bin/bash
###############################################################################
# AI内容收集脚本 - 简化版
# 用法: ./collect-simple.sh [日期，格式YYYY-MM-DD，默认为今天]
###############################################################################

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPELINE_DIR="$(dirname "$SCRIPT_DIR")"

# 日期处理
DATE="${1:-$(date +%Y-%m-%d)}"

# 输出目录
OUTPUT_DIR="$PIPELINE_DIR/collected/$DATE"
mkdir -p "$OUTPUT_DIR"

# 日志文件
LOG_FILE="$OUTPUT_DIR/collection.log"
RAW_FILE="$OUTPUT_DIR/raw-content.json"
MARKDOWN_FILE="$OUTPUT_DIR/raw-content.md"

# 初始化日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========== AI内容收集开始 =========="
log "日期: $DATE"

# 初始化JSON
echo '{"date": "'$DATE'", "sources": []}' > "$RAW_FILE"

# 初始化Markdown
cat > "$MARKDOWN_FILE" << EOF
# AI内容收集报告 - $DATE

> 收集时间: $(date '+%Y-%m-%d %H:%M:%S')

---

EOF

###############################################################################
# Hacker News 收集
###############################################################################
log "[Hacker News] 收集AI相关内容..."

HN_JSON=$(mktemp)
if curl -s --max-time 30 \
    "https://hn.algolia.com/api/v1/search?query=artificial+intelligence+OR+machine+learning&tags=story&hitsPerPage=15" \
    -o "$HN_JSON" 2>/dev/null; then
    
    if jq -e '.hits' "$HN_JSON" > /dev/null 2>&1; then
        COUNT=$(jq '.hits | length' "$HN_JSON")
        log "[Hacker News] 获取到 $COUNT 条"
        
        # 提取有效条目
        ITEMS=$(jq '[.hits[] | select(.title != null)] | map({
            title: .title,
            url: (.url // ("https://news.ycombinator.com/item?id=" + .objectID)),
            author: .author,
            points: .points,
            comments: .num_comments,
            created_at: .created_at,
            source: "Hacker News"
        })' "$HN_JSON")
        
        # 更新JSON
        SOURCE_JSON=$(jq -n --arg name "Hacker News" --arg id "hn-ai" --argjson items "$ITEMS" \
            '{name: $name, id: $id, count: ($items | length), items: $items}')
        
        jq --argjson source "$SOURCE_JSON" '.sources += [$source]' "$RAW_FILE" > "${RAW_FILE}.tmp" && mv "${RAW_FILE}.tmp" "$RAW_FILE"
        
        # 写入Markdown
        {
            echo "## 🔥 Hacker News - AI相关内容"
            echo ""
            echo "$ITEMS" | jq -r '.[] | 
                "### " + .title + "\n" +
                "- **热度**: ⬆️ " + (.points | tostring) + " points, 💬 " + (.comments | tostring) + " comments\n" +
                "- **作者**: @" + .author + "\n" +
                "- **链接**: " + .url + "\n" +
                "---\n"
            '
        } >> "$MARKDOWN_FILE"
    else
        log "[Hacker News] 数据解析失败"
    fi
else
    log "[Hacker News] 请求失败"
fi

rm -f "$HN_JSON"

###############################################################################
# Reddit 收集 (使用更简单的方式)
###############################################################################
log "[Reddit] 尝试获取内容..."

REDDIT_JSON=$(mktemp)
# 使用旧版Reddit接口
if curl -s --max-time 30 \
    -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
    "https://old.reddit.com/r/ArtificialIntelligence/hot.json?limit=10" \
    -o "$REDDIT_JSON" 2>/dev/null; then
    
    if jq -e '.data.children' "$REDDIT_JSON" > /dev/null 2>&1; then
        COUNT=$(jq '[.data.children[] | select(.data.stickied != true)] | length' "$REDDIT_JSON")
        log "[Reddit] 获取到 $COUNT 条"
        
        ITEMS=$(jq '[.data.children[] | select(.data.stickied != true)] | map({
            title: .data.title,
            url: .data.url,
            permalink: "https://reddit.com" + .data.permalink,
            author: .data.author,
            upvotes: .data.ups,
            comments: .data.num_comments,
            domain: .data.domain,
            source: "Reddit r/AI"
        })' "$REDDIT_JSON")
        
        SOURCE_JSON=$(jq -n --arg name "Reddit r/AI" --arg id "reddit-ai" --argjson items "$ITEMS" \
            '{name: $name, id: $id, count: ($items | length), items: $items}')
        
        jq --argjson source "$SOURCE_JSON" '.sources += [$source]' "$RAW_FILE" > "${RAW_FILE}.tmp" && mv "${RAW_FILE}.tmp" "$RAW_FILE"
        
        {
            echo "## 🤖 Reddit - ArtificialIntelligence"
            echo ""
            echo "$ITEMS" | jq -r '.[] | 
                "### " + .title + "\n" +
                "- **热度**: ⬆️ " + (.upvotes | tostring) + " upvotes, 💬 " + (.comments | tostring) + " comments\n" +
                "- **作者**: u/" + .author + "\n" +
                "- **来源**: " + .domain + "\n" +
                "- **链接**: " + .url + "\n" +
                "---\n"
            '
        } >> "$MARKDOWN_FILE"
    else
        log "[Reddit] 数据解析失败"
    fi
else
    log "[Reddit] 请求失败"
fi

rm -f "$REDDIT_JSON"

###############################################################################
# 统计和完成
###############################################################################
TOTAL=$(jq '[.sources[].count] | add // 0' "$RAW_FILE")
log "========== 收集完成 =========="
log "总条目: $TOTAL 条"
log "输出: $OUTPUT_DIR"

echo ""
echo "✅ 收集完成! 共 $TOTAL 条内容"
echo "📄 查看: cat $MARKDOWN_FILE"
