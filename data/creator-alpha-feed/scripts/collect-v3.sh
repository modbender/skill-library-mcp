#!/bin/bash
###############################################################################
# AI内容收集脚本 - V3 浏览器版 (支持Twitter)
# 数据源: Hacker News / Reddit / TechCrunch / Twitter (browser抓取)
# 用法: ./collect-v3.sh [日期，格式YYYY-MM-DD，默认为今天]
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
TWITTER_FILE="$OUTPUT_DIR/twitter-snapshot.html"

log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 初始化JSON和Markdown
echo '{"date": "'$DATE'", "sources": []}' > "$RAW_FILE"
cat > "$MARKDOWN_FILE" << EOF
# 🤖 AI内容收集报告 - $DATE

> ⏰ 收集时间: $(date '+%Y-%m-%d %H:%M:%S')  
> 📊 数据源: Hacker News | Reddit | TechCrunch | Twitter

---

EOF

log "========== 开始收集AI内容 =========="
TOTAL=0

###############################################################################
# 1. Hacker News - 热门AI内容
###############################################################################
log "📡 [1/4] Hacker News..."

HN_FILE=$(mktemp)
API_URL="https://hn.algolia.com/api/v1/search?query=AI+OR+GPT+OR+LLM&tags=story&numericFilters=points%3E20&hitsPerPage=15"

if curl -s --max-time 30 "$API_URL" -o "$HN_FILE" 2>/dev/null && jq -e '.hits' "$HN_FILE" > /dev/null 2>&1; then
    COUNT=$(jq '.hits | length' "$HN_FILE")
    log "   ✅ 获取到 $COUNT 条"
    
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
# 2. TechCrunch - AI板块 (RSS)
###############################################################################
log "📡 [2/4] TechCrunch..."

TECHCRUNCH_FILE=$(mktemp)
if curl -s --max-time 30 \
    "https://api.rss2json.com/v1/api.json?rss_url=https://techcrunch.com/category/artificial-intelligence/feed/" \
    -o "$TECHCRUNCH_FILE" 2>/dev/null && jq -e '.items' "$TECHCRUNCH_FILE" > /dev/null 2>&1; then
    
    ITEMS=$(jq '.items[:8] | map({
        title: .title,
        url: .link,
        author: .author,
        published: .pubDate,
        description: (.description | gsub("<[^>]+>"; "") | .[:180]),
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
                "- 👤 **作者**: " + .author + " | 📅 " + .published[:10] + "\n" +
                "- 📝 **摘要**: " + .description + "...\n" +
                "- 🔗 **链接**: [阅读原文](" + .url + ")\n" +
                "---\n"
            '
        } >> "$MARKDOWN_FILE"
        TOTAL=$((TOTAL + ITEM_COUNT))
        log "   ✅ TechCrunch: $ITEM_COUNT 条"
    fi
else
    log "   ⚠️ TechCrunch暂时不可用"
fi
rm -f "$TECHCRUNCH_FILE"

###############################################################################
# 3. Reddit - AI社区
###############################################################################
log "📡 [3/4] Reddit AI社区..."

REDDIT_TOTAL=0

# r/ArtificialIntelligence
for SUBREDDIT in "ArtificialIntelligence" "singularity" "LocalLLaMA"; do
    REDDIT_FILE=$(mktemp)
    if curl -s --max-time 25 \
        -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
        "https://www.reddit.com/r/${SUBREDDIT}/top.json?t=day&limit=8" \
        -o "$REDDIT_FILE" 2>/dev/null && jq -e '.data.children' "$REDDIT_FILE" > /dev/null 2>&1; then
        
        ITEMS=$(jq '[.data.children[] | select(.data.stickied != true and .data.ups > 3)] | map({
            title: .data.title,
            url: .data.url,
            permalink: "https://reddit.com" + .data.permalink,
            author: .data.author,
            upvotes: .data.ups,
            comments: .data.num_comments,
            domain: .data.domain,
            source: "Reddit r/'$SUBREDDIT'"
        })' "$REDDIT_FILE")
        
        ITEM_COUNT=$(echo "$ITEMS" | jq 'length')
        if [[ $ITEM_COUNT -gt 0 ]]; then
            SOURCE_JSON=$(jq -n --arg name "🤖 Reddit r/$SUBREDDIT" --arg id "reddit-$SUBREDDIT" --argjson items "$ITEMS" \
                '{name: $name, id: $id, count: ($items | length), items: $items}')
            jq --argjson source "$SOURCE_JSON" '.sources += [$source]' "$RAW_FILE" > "${RAW_FILE}.tmp" && mv "${RAW_FILE}.tmp" "$RAW_FILE"
            
            if [[ $REDDIT_TOTAL -eq 0 ]]; then
                echo "## 🤖 Reddit - AI社区" >> "$MARKDOWN_FILE"
                echo "" >> "$MARKDOWN_FILE"
            fi
            
            echo "### r/$SUBREDDIT" >> "$MARKDOWN_FILE"
            echo "" >> "$MARKDOWN_FILE"
            
            echo "$ITEMS" | jq -r '.[] | 
                "#### " + .title + "\n" +
                "- 📊 ⬆️ " + (.upvotes | tostring) + " | 💬 " + (.comments | tostring) + " | 👤 u/" + .author + "\n" +
                "- 🔗 [" + .domain + "](" + .url + ") | [Reddit](" + .permalink + ")\n"
            ' >> "$MARKDOWN_FILE"
            
            TOTAL=$((TOTAL + ITEM_COUNT))
            REDDIT_TOTAL=$((REDDIT_TOTAL + ITEM_COUNT))
        fi
    fi
    rm -f "$REDDIT_FILE"
done

if [[ $REDDIT_TOTAL -gt 0 ]]; then
    log "   ✅ Reddit: $REDDIT_TOTAL 条"
    echo "---" >> "$MARKDOWN_FILE"
    echo "" >> "$MARKDOWN_FILE"
fi

###############################################################################
# 4. Twitter - 通过浏览器抓取
###############################################################################
log "📡 [4/4] Twitter (浏览器抓取)..."
log "   ⚠️ Twitter需要使用OpenClaw browser工具手动抓取"
log "   请运行: openclaw agent --message '收集Twitter热门AI推文'"

# 创建Twitter抓取指南
cat > "$OUTPUT_DIR/twitter-guide.md" << 'EOF'
# Twitter AI内容抓取指南

由于Twitter的反爬机制和登录要求，需要通过OpenClaw browser工具手动/半自动抓取。

## 方法1: 使用 Nitter (推荐)

Nitter是Twitter的开源镜像，无需登录即可访问：

```bash
# 访问AI相关账号或搜索
openclaw browser open "https://nitter.net/search?f=tweets&q=AI+OR+GPT+OR+Claude&since=2026-02-09"
```

## 方法2: 使用浏览器抓取Twitter趋势

1. 打开Twitter搜索页
2. 搜索热门AI话题
3. 使用 snapshot 抓取内容

推荐关注的Twitter账号：
- @sama (Sam Altman)
- @gdb (Greg Brockman)
- @ylecun (Yann LeCun)
- @DrJimFan
- @karpathy
- @AndrewYNg
- @ bindu reddy
- @hardmaru

## 方法3: 使用 Twitter List

创建一个包含AI领域KOL的Twitter List，定期通过browser访问：

```
https://twitter.com/i/lists/YOUR_LIST_ID
```

## 自动化方案

未来可考虑：
- 使用 RSSHub 生成Twitter RSS
- 使用 nitter.net 的RSS功能
- 使用付费Twitter API ($100/月起)
EOF

# 添加提示到Markdown报告
{
    echo "## 🐦 Twitter - AI热门推文"
    echo ""
    echo "⚠️ **注意**: Twitter内容需要通过browser工具手动抓取"
    echo ""
    echo "查看抓取指南: \`$OUTPUT_DIR/twitter-guide.md\`"
    echo ""
    echo "**建议操作**（在OpenClaw中执行）:"
    echo '```'
    echo '# 方法1: 访问Nitter搜索AI内容'
    echo 'browser open "https://nitter.net/search?f=tweets&q=artificial+intelligence&since=2026-02-09"'
    echo ''
    echo '# 方法2: 访问特定账号时间线'
    echo 'browser open "https://nitter.net/sama"'
    echo ''
    echo '# 方法3: 抓取后使用web_fetch获取页面内容'
    echo 'web_fetch "https://nitter.net/search?f=tweets&q=GPT"'
    echo '```'
    echo ""
    echo "---"
    echo ""
} >> "$MARKDOWN_FILE"

###############################################################################
# 完成
###############################################################################
log "========== 收集完成 =========="
log "📊 总计: $TOTAL 条内容 (不含Twitter)"

echo "" >> "$MARKDOWN_FILE"
echo "---" >> "$MARKDOWN_FILE"
echo "" >> "$MARKDOWN_FILE"
echo "📊 **汇总**: 共收集 $TOTAL 条AI相关内容" >> "$MARKDOWN_FILE"
echo "- Hacker News: 热门AI项目" >> "$MARKDOWN_FILE"
echo "- TechCrunch: AI新闻" >> "$MARKDOWN_FILE"
echo "- Reddit: 社区讨论" >> "$MARKDOWN_FILE"
echo "- Twitter: 需手动抓取 (见twitter-guide.md)" >> "$MARKDOWN_FILE"

echo ""
echo "✅ 收集完成! 共 $TOTAL 条 (不含Twitter)"
echo ""
echo "📄 主报告: $MARKDOWN_FILE"
echo "📖 Twitter指南: $OUTPUT_DIR/twitter-guide.md"
echo ""
echo "💡 要抓取Twitter内容，请在OpenClaw中运行:"
echo "   browser open 'https://nitter.net/search?f=tweets&q=AI'"
