#!/bin/bash
###############################################################################
# AI内容收集脚本 - V2 多源版
# 数据源: Hacker News / Reddit / TechCrunch
# 用法: ./collect-v2.sh [日期，格式YYYY-MM-DD，默认为今天]
###############################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPELINE_DIR="$(dirname "$SCRIPT_DIR")"
DATE="${1:-$(date +%Y-%m-%d)}"
OUTPUT_DIR="$PIPELINE_DIR/collected/$DATE"
mkdir -p "$OUTPUT_DIR"

LOG_FILE="$OUTPUT_DIR/collection.log"
RAW_FILE="$OUTPUT_DIR/raw-content.json"
MARKDOWN_FILE="$OUTPUT_DIR/raw-content.md"

log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 初始化JSON和Markdown
echo '{"date": "'$DATE'", "sources": []}' > "$RAW_FILE"
cat > "$MARKDOWN_FILE" << EOF
# 🤖 AI内容收集报告 - $DATE

> ⏰ 收集时间: $(date '+%Y-%m-%d %H:%M:%S')  
> 📊 数据源: Hacker News | Reddit | TechCrunch

---

EOF

log "========== 开始收集AI内容 =========="
TOTAL=0

###############################################################################
# 1. Hacker News - 热门AI内容
###############################################################################
log "📡 [1/3] Hacker News..."

HN_FILE=$(mktemp)
# 使用不同的搜索词获取更热门的内容
API_URL="https://hn.algolia.com/api/v1/search?query=AI+OR+GPT+OR+LLM&tags=story&numericFilters=points%3E20&hitsPerPage=20"

if curl -s --max-time 30 "$API_URL" -o "$HN_FILE" 2>/dev/null && jq -e '.hits' "$HN_FILE" > /dev/null 2>&1; then
    COUNT=$(jq '.hits | length' "$HN_FILE")
    log "   ✅ 获取到 $COUNT 条"
    
    ITEMS=$(jq '[.hits[] | select(.points >= 10)] | map({
        title: .title,
        url: (.url // ("https://news.ycombinator.com/item?id=" + .objectID)),
        author: .author,
        points: .points,
        comments: .num_comments,
        time: .created_at,
        source: "Hacker News",
        hn_url: ("https://news.ycombinator.com/item?id=" + .objectID)
    })' "$HN_FILE")
    
    ITEM_COUNT=$(echo "$ITEMS" | jq 'length')
    if [[ $ITEM_COUNT -gt 0 ]]; then
        SOURCE_JSON=$(jq -n --arg name "🔥 Hacker News" --arg id "hn-ai" --argjson items "$ITEMS" \
            '{name: $name, id: $id, count: ($items | length), items: $items}')
        jq --argjson source "$SOURCE_JSON" '.sources += [$source]' "$RAW_FILE" > "${RAW_FILE}.tmp" && mv "${RAW_FILE}.tmp" "$RAW_FILE"
        
        {
            echo "## 🔥 Hacker News - 热门AI内容"
            echo ""
            echo "$ITEMS" | jq -r '.[] | 
                "### " + .title + "\n" +
                "- 📊 **热度**: ⬆️ " + (.points | tostring) + " points | 💬 " + (.comments | tostring) + " comments\n" +
                "- 👤 **作者**: @" + .author + "\n" +
                "- 🔗 **链接**: [原文](" + .url + ") | [HN讨论](" + .hn_url + ")\n" +
                "---\n"
            '
        } >> "$MARKDOWN_FILE"
        TOTAL=$((TOTAL + ITEM_COUNT))
    fi
else
    log "   ❌ 获取失败"
fi
rm -f "$HN_FILE"

###############################################################################
# 2. Reddit - 多个AI相关社区
###############################################################################
log "📡 [2/3] Reddit AI社区..."

# Reddit r/ArtificialIntelligence
REDDIT_FILE=$(mktemp)
if curl -s --max-time 30 \
    -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
    "https://www.reddit.com/r/ArtificialIntelligence/top.json?t=day&limit=15" \
    -o "$REDDIT_FILE" 2>/dev/null; then
    
    if jq -e '.data.children' "$REDDIT_FILE" > /dev/null 2>&1; then
        ITEMS=$(jq '[.data.children[] | select(.data.stickied != true and .data.ups > 5)] | map({
            title: .data.title,
            url: .data.url,
            permalink: "https://reddit.com" + .data.permalink,
            author: .data.author,
            upvotes: .data.ups,
            upvote_ratio: .data.upvote_ratio,
            comments: .data.num_comments,
            domain: .data.domain,
            source: "Reddit r/AI"
        })' "$REDDIT_FILE")
        
        ITEM_COUNT=$(echo "$ITEMS" | jq 'length')
        if [[ $ITEM_COUNT -gt 0 ]]; then
            SOURCE_JSON=$(jq -n --arg name "🤖 Reddit r/AI" --arg id "reddit-ai" --argjson items "$ITEMS" \
                '{name: $name, id: $id, count: ($items | length), items: $items}')
            jq --argjson source "$SOURCE_JSON" '.sources += [$source]' "$RAW_FILE" > "${RAW_FILE}.tmp" && mv "${RAW_FILE}.tmp" "$RAW_FILE"
            
            {
                echo "## 🤖 Reddit r/ArtificialIntelligence"
                echo ""
                echo "$ITEMS" | jq -r '.[] | 
                    "### " + .title + "\n" +
                    "- 📊 **热度**: ⬆️ " + (.upvotes | tostring) + " upvotes | 💬 " + (.comments | tostring) + " comments\n" +
                    "- 👤 **作者**: u/" + .author + " | 📰 " + .domain + "\n" +
                    "- 🔗 **链接**: [原文](" + .url + ") | [Reddit](" + .permalink + ")\n" +
                    "---\n"
                '
            } >> "$MARKDOWN_FILE"
            TOTAL=$((TOTAL + ITEM_COUNT))
            log "   ✅ r/AI: $ITEM_COUNT 条"
        fi
    fi
fi
rm -f "$REDDIT_FILE"

# Reddit r/singularity
REDDIT_FILE=$(mktemp)
if curl -s --max-time 30 \
    -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
    "https://www.reddit.com/r/singularity/top.json?t=day&limit=10" \
    -o "$REDDIT_FILE" 2>/dev/null; then
    
    if jq -e '.data.children' "$REDDIT_FILE" > /dev/null 2>&1; then
        ITEMS=$(jq '[.data.children[] | select(.data.stickied != true and .data.ups > 5)] | map({
            title: .data.title,
            url: .data.url,
            permalink: "https://reddit.com" + .data.permalink,
            author: .data.author,
            upvotes: .data.ups,
            comments: .data.num_comments,
            domain: .data.domain,
            source: "Reddit r/singularity"
        })' "$REDDIT_FILE")
        
        ITEM_COUNT=$(echo "$ITEMS" | jq 'length')
        if [[ $ITEM_COUNT -gt 0 ]]; then
            SOURCE_JSON=$(jq -n --arg name "🚀 Reddit r/singularity" --arg id "reddit-singularity" --argjson items "$ITEMS" \
                '{name: $name, id: $id, count: ($items | length), items: $items}')
            jq --argjson source "$SOURCE_JSON" '.sources += [$source]' "$RAW_FILE" > "${RAW_FILE}.tmp" && mv "${RAW_FILE}.tmp" "$RAW_FILE"
            
            {
                echo "## 🚀 Reddit r/singularity"
                echo ""
                echo "$ITEMS" | jq -r '.[] | 
                    "### " + .title + "\n" +
                    "- 📊 **热度**: ⬆️ " + (.upvotes | tostring) + " upvotes | 💬 " + (.comments | tostring) + " comments\n" +
                    "- 👤 **作者**: u/" + .author + " | 📰 " + .domain + "\n" +
                    "- 🔗 **链接**: [原文](" + .url + ") | [Reddit](" + .permalink + ")\n" +
                    "---\n"
                '
            } >> "$MARKDOWN_FILE"
            TOTAL=$((TOTAL + ITEM_COUNT))
            log "   ✅ r/singularity: $ITEM_COUNT 条"
        fi
    fi
fi
rm -f "$REDDIT_FILE"

###############################################################################
# 3. TechCrunch - AI分类 (使用 RSS 转 JSON 服务)
###############################################################################
log "📡 [3/3] TechCrunch..."

# 使用rss2json服务获取TechCrunch AI内容
TECHCRUNCH_FILE=$(mktemp)
if curl -s --max-time 30 \
    "https://api.rss2json.com/v1/api.json?rss_url=https://techcrunch.com/category/artificial-intelligence/feed/" \
    -o "$TECHCRUNCH_FILE" 2>/dev/null; then
    
    if jq -e '.items' "$TECHCRUNCH_FILE" > /dev/null 2>&1; then
        ITEMS=$(jq '.items[:10] | map({
            title: .title,
            url: .link,
            author: .author,
            published: .pubDate,
            description: (.description | gsub("<[^>]+>"; "") | .[:200]),
            source: "TechCrunch AI"
        })' "$TECHCRUNCH_FILE")
        
        ITEM_COUNT=$(echo "$ITEMS" | jq 'length')
        if [[ $ITEM_COUNT -gt 0 ]]; then
            SOURCE_JSON=$(jq -n --arg name "📰 TechCrunch AI" --arg id "techcrunch-ai" --argjson items "$ITEMS" \
                '{name: $name, id: $id, count: ($items | length), items: $items}')
            jq --argjson source "$SOURCE_JSON" '.sources += [$source]' "$RAW_FILE" > "${RAW_FILE}.tmp" && mv "${RAW_FILE}.tmp" "$RAW_FILE"
            
            {
                echo "## 📰 TechCrunch - AI板块"
                echo ""
                echo "$ITEMS" | jq -r '.[] | 
                    "### " + .title + "\n" +
                    "- 👤 **作者**: " + .author + "\n" +
                    "- 📅 **发布**: " + .published + "\n" +
                    "- 📝 **摘要**: " + .description + "...\n" +
                    "- 🔗 **链接**: [阅读原文](" + .url + ")\n" +
                    "---\n"
                '
            } >> "$MARKDOWN_FILE"
            TOTAL=$((TOTAL + ITEM_COUNT))
            log "   ✅ TechCrunch: $ITEM_COUNT 条"
        fi
    fi
else
    log "   ⚠️ TechCrunch RSS暂时不可用"
fi
rm -f "$TECHCRUNCH_FILE"

###############################################################################
# 完成统计
###############################################################################
log "========== 收集完成 =========="
log "📊 总计: $TOTAL 条内容"

echo "" >> "$MARKDOWN_FILE"
echo "---" >> "$MARKDOWN_FILE"
echo "" >> "$MARKDOWN_FILE"
echo "📊 **汇总**: 共收集 $TOTAL 条AI相关内容" >> "$MARKDOWN_FILE"

echo ""
echo "✅ 收集完成! 共 $TOTAL 条"
echo "📄 $MARKDOWN_FILE"
