#!/bin/bash
###############################################################################
# AI内容收集脚本 - V4 完整版
# 数据源: Hacker News / Reddit / TechCrunch / Twitter (browser抓取)
# 用法: ./collect-v4.sh [--twitter] [日期]
###############################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPELINE_DIR="$(dirname "$SCRIPT_DIR")"
DATE="${2:-$(date +%Y-%m-%d)}"
ENABLE_TWITTER=false

# 解析参数
if [[ "$1" == "--twitter" ]]; then
    ENABLE_TWITTER=true
fi

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
> 📊 数据源: Hacker News | Reddit | TechCrunch ${ENABLE_TWITTER:+'| Twitter (browser)'}

---

EOF

log "========== AI内容收集开始 =========="
log "日期: $DATE"
log "Twitter收集: $([ "$ENABLE_TWITTER" = true ] && echo '已启用' || echo '已跳过')"
TOTAL=0

###############################################################################
# 1. Hacker News
###############################################################################
log "📡 [1/4] Hacker News..."

HN_FILE=$(mktemp)
API_URL="https://hn.algolia.com/api/v1/search?query=AI+OR+GPT+OR+LLM&tags=story&numericFilters=points%3E15&hitsPerPage=12"

if curl -s --max-time 30 "$API_URL" -o "$HN_FILE" 2>/dev/null && jq -e '.hits' "$HN_FILE" > /dev/null 2>&1; then
    ITEMS=$(jq '[.hits[] | select(.points >= 10)] | map({
        title: .title,
        url: (.url // ("https://news.ycombinator.com/item?id=" + .objectID)),
        author: .author,
        points: .points,
        comments: .num_comments,
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
                "- 📊 ⬆️ " + (.points | tostring) + " points | 💬 " + (.comments | tostring) + " | 👤 @" + .author + "\n" +
                "- 🔗 [原文](" + .url + ") | [HN](" + .hn_url + ")\n" +
                "---\n"
            '
        } >> "$MARKDOWN_FILE"
        TOTAL=$((TOTAL + ITEM_COUNT))
        log "   ✅ $ITEM_COUNT 条"
    fi
else
    log "   ❌ 失败"
fi
rm -f "$HN_FILE"

###############################################################################
# 2. TechCrunch
###############################################################################
log "📡 [2/4] TechCrunch..."

TC_FILE=$(mktemp)
if curl -s --max-time 30 \
    "https://api.rss2json.com/v1/api.json?rss_url=https://techcrunch.com/category/artificial-intelligence/feed/" \
    -o "$TC_FILE" 2>/dev/null && jq -e '.items' "$TC_FILE" > /dev/null 2>&1; then
    
    ITEMS=$(jq '.items[:6] | map({
        title: .title,
        url: .link,
        author: .author,
        published: .pubDate,
        description: (.description | gsub("<[^>]+>"; "") | .[:150]),
        source: "TechCrunch AI"
    })' "$TC_FILE")
    
    ITEM_COUNT=$(echo "$ITEMS" | jq 'length')
    if [[ $ITEM_COUNT -gt 0 ]]; then
        SOURCE_JSON=$(jq -n --arg name "📰 TechCrunch" --arg id "techcrunch-ai" --argjson items "$ITEMS" \
            '{name: $name, id: $id, count: ($items | length), items: $items}')
        jq --argjson source "$SOURCE_JSON" '.sources += [$source]' "$RAW_FILE" > "${RAW_FILE}.tmp" && mv "${RAW_FILE}.tmp" "$RAW_FILE"
        
        {
            echo "## 📰 TechCrunch - AI新闻"
            echo ""
            echo "$ITEMS" | jq -r '.[] | 
                "### " + .title + "\n" +
                "- 👤 " + .author + " | 📅 " + .published[:10] + "\n" +
                "- 📝 " + .description + "...\n" +
                "- 🔗 [阅读](" + .url + ")\n" +
                "---\n"
            '
        } >> "$MARKDOWN_FILE"
        TOTAL=$((TOTAL + ITEM_COUNT))
        log "   ✅ $ITEM_COUNT 条"
    fi
else
    log "   ⚠️ 不可用"
fi
rm -f "$TC_FILE"

###############################################################################
# 3. Reddit
###############################################################################
log "📡 [3/4] Reddit..."

REDDIT_COUNT=0
for SUBREDDIT in "ArtificialIntelligence" "singularity"; do
    RD_FILE=$(mktemp)
    if curl -s --max-time 25 \
        -H "User-Agent: Mozilla/5.0" \
        "https://www.reddit.com/r/${SUBREDDIT}/top.json?t=day&limit=6" \
        -o "$RD_FILE" 2>/dev/null && jq -e '.data.children' "$RD_FILE" > /dev/null 2>&1; then
        
        ITEMS=$(jq '[.data.children[] | select(.data.stickied != true and .data.ups > 5)] | map({
            title: .data.title,
            url: .data.url,
            permalink: "https://reddit.com" + .data.permalink,
            author: .data.author,
            upvotes: .data.ups,
            comments: .data.num_comments,
            source: "Reddit r/'$SUBREDDIT'"
        })' "$RD_FILE")
        
        ITEM_COUNT=$(echo "$ITEMS" | jq 'length')
        if [[ $ITEM_COUNT -gt 0 ]]; then
            SOURCE_JSON=$(jq -n --arg name "🤖 Reddit r/$SUBREDDIT" --arg id "reddit-$SUBREDDIT" --argjson items "$ITEMS" \
                '{name: $name, id: $id, count: ($items | length), items: $items}')
            jq --argjson source "$SOURCE_JSON" '.sources += [$source]' "$RAW_FILE" > "${RAW_FILE}.tmp" && mv "${RAW_FILE}.tmp" "$RAW_FILE"
            
            if [[ $REDDIT_COUNT -eq 0 ]]; then
                echo "## 🤖 Reddit - AI社区" >> "$MARKDOWN_FILE"
                echo "" >> "$MARKDOWN_FILE"
            fi
            
            echo "**r/$SUBREDDIT**" >> "$MARKDOWN_FILE"
            echo "" >> "$MARKDOWN_FILE"
            echo "$ITEMS" | jq -r '.[] | 
                "- **" + .title + "**\n" +
                "  ⬆️ " + (.upvotes | tostring) + " | 💬 " + (.comments | tostring) + " | [链接](" + .url + ")\n"
            ' >> "$MARKDOWN_FILE"
            
            TOTAL=$((TOTAL + ITEM_COUNT))
            REDDIT_COUNT=$((REDDIT_COUNT + ITEM_COUNT))
        fi
    fi
    rm -f "$RD_FILE"
done

if [[ $REDDIT_COUNT -gt 0 ]]; then
    log "   ✅ $REDDIT_COUNT 条"
    echo "" >> "$MARKDOWN_FILE"
    echo "---" >> "$MARKDOWN_FILE"
    echo "" >> "$MARKDOWN_FILE"
fi

###############################################################################
# 4. Twitter (可选，需要browser工具)
###############################################################################
log "📡 [4/4] Twitter..."

if [[ "$ENABLE_TWITTER" == true ]]; then
    log "   🌐 创建Twitter收集指南..."
    
    # 创建Twitter收集任务文件
    cat > "$OUTPUT_DIR/twitter-tasks.md" << EOF
# 🐦 Twitter收集任务 - $DATE

## 待收集的Twitter账号

在OpenClaw中执行以下命令:

### 1. OpenAI团队
\`\`\`
browser open "https://nitter.net/sama"
browser snapshot
browser open "https://nitter.net/gdb"
browser snapshot
\`\`\`

### 2. AI研究人员
\`\`\`
browser open "https://nitter.net/karpathy"
browser snapshot
browser open "https://nitter.net/DrJimFan"
browser snapshot
\`\`\`

### 3. AI话题搜索
\`\`\`
browser open "https://nitter.net/search?f=tweets&q=GPT+Claude+AI&since=$DATE"
browser snapshot
\`\`\`

## 收集内容格式

将截图/内容保存到: \`$OUTPUT_DIR/twitter-content.md\`

格式:
\`\`\`markdown
## Twitter @sama - $DATE

### 推文1
**热度**: X likes, Y retweets
> 推文内容...
**适合公众号**: [是/否] - 原因
\`\`\`
EOF

    {
        echo "## 🐦 Twitter (待收集)"
        echo ""
        echo "⚠️ **需要手动/browser工具收集**"
        echo ""
        echo "📋 **收集指南**: \`$OUTPUT_DIR/twitter-tasks.md\`"
        echo ""
        echo "**推荐账号**:\n- @sama (OpenAI)\n- @karpathy (AI研究员)\n- @DrJimFan (NVIDIA)"
        echo ""
        echo "**快速命令**:\n\`\`\`\nbrowser open \"https://nitter.net/sama\"\nbrowser snapshot\n\`\`\`"
        echo ""
        echo "---"
        echo ""
    } >> "$MARKDOWN_FILE"
    
    log "   ✅ 任务文件已创建"
else
    log "   ⏭️ 已跳过 (使用 --twitter 启用)"
    {
        echo "## 🐦 Twitter"
        echo ""
        echo "⏭️ **已跳过** - 使用 \`--twitter\` 参数启用browser收集"
        echo ""
        echo "**启用方式**:\n\`\`\`\n./collect-v4.sh --twitter\n\`\`\`"
        echo ""
        echo "---"
        echo ""
    } >> "$MARKDOWN_FILE"
fi

###############################################################################
# 完成
###############################################################################
log "========== 收集完成 =========="
log "📊 总计: $TOTAL 条"

echo "" >> "$MARKDOWN_FILE"
echo "---" >> "$MARKDOWN_FILE"
echo "" >> "$MARKDOWN_FILE"
echo "📊 **汇总**: 共 $TOTAL 条AI相关内容" >> "$MARKDOWN_FILE"

echo ""
echo "✅ 收集完成! 共 $TOTAL 条"
echo "📄 $MARKDOWN_FILE"

if [[ "$ENABLE_TWITTER" == true ]]; then
    echo "🐦 Twitter任务: $OUTPUT_DIR/twitter-tasks.md"
fi
