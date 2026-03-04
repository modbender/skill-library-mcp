#!/bin/bash
###############################################################################
# Twitter AI内容收集 - Browser工具版
# 用法: 在OpenClaw中运行此脚本
###############################################################################

# 配置
OUTPUT_DIR="${1:-$HOME/.openclaw/workspace/ai-content-pipeline/collected/$(date +%Y-%m-%d)}"
mkdir -p "$OUTPUT_DIR"

echo "========== Twitter AI内容收集 =========="
echo "输出目录: $OUTPUT_DIR"
echo ""

# 方法1: 使用 Nitter (Twitter镜像)
echo "📡 方法1: 尝试Nitter镜像..."

# 备选Nitter实例列表
NITTER_INSTANCES=(
    "nitter.net"
    "nitter.privacydev.net"
    "nitter.it"
    "nitter.cz"
)

TWITTER_CONTENT=""

for instance in "${NITTER_INSTANCES[@]}"; do
    echo "   尝试: $instance"
    URL="https://${instance}/search?f=tweets&q=AI+GPT+Claude+LLM&f=tweets"
    
    # 使用web_fetch尝试获取
    if curl -s --max-time 15 -L "$URL" -o "/tmp/twitter-${instance}.html" 2>/dev/null; then
        # 检查是否有效页面
        if grep -q "timeline-item" "/tmp/twitter-${instance}.html" 2>/dev/null; then
            echo "   ✅ 成功获取内容"
            
            # 提取推文内容 (简化提取)
            TWITTER_CONTENT=$(grep -oP '(?<=class="tweet-content"[^>]*>).*?(?=</div>)' "/tmp/twitter-${instance}.html" | head -10)
            
            if [[ -n "$TWITTER_CONTENT" ]]; then
                break
            fi
        fi
    fi
done

# 方法2: 使用特定的Twitter列表RSS (通过RSSHub)
echo ""
echo "📡 方法2: 使用RSSHub获取Twitter列表..."

RSS_URLS=(
    # AI领域KOL的推文 (通过RSSHub)
    "https://rsshub.app/twitter/user/sama"
    "https://rsshub.app/twitter/user/gdb"
    "https://rsshub.app/twitter/user/ylecun"
)

RSS_CONTENT=""
for rss_url in "${RSS_URLS[@]}"; do
    RSS_FILE=$(mktemp)
    if curl -s --max-time 20 "$rss_url" -o "$RSS_FILE" 2>/dev/null; then
        # 检查是否是有效RSS
        if grep -q "<item>" "$RSS_FILE" 2>/dev/null; then
            echo "   ✅ 获取到RSS: ${rss_url##*/}"
            ITEMS=$(grep -oP '(?<=<title>).*?(?=</title>)' "$RSS_FILE" | tail -n +2 | head -5)
            RSS_CONTENT="${RSS_CONTENT}${ITEMS}"
        fi
    fi
    rm -f "$RSS_FILE"
done

# 保存结果
OUTPUT_FILE="$OUTPUT_DIR/twitter-content.md"

cat > "$OUTPUT_FILE" << EOF
# 🐦 Twitter AI热门推文 - $(date +%Y-%m-%d)

> 收集时间: $(date '+%Y-%m-%d %H:%M:%S')

---

## 通过Nitter获取的内容

EOF

if [[ -n "$TWITTER_CONTENT" ]]; then
    echo "$TWITTER_CONTENT" >> "$OUTPUT_FILE"
else
    echo "⚠️ Nitter暂时无法访问" >> "$OUTPUT_FILE"
fi

cat >> "$OUTPUT_FILE" << EOF

---

## 通过RSSHub获取的KOL推文

EOF

if [[ -n "$RSS_CONTENT" ]]; then
    echo "${RSS_CONTENT}" | while read -r line; do
        echo "- $line" >> "$OUTPUT_FILE"
    done
else
    echo "⚠️ RSSHub暂时不可用" >> "$OUTPUT_FILE"
fi

cat >> "$OUTPUT_FILE" << EOF

---

## 💡 备选方案: 手动Browser收集

由于Twitter的反爬机制，推荐以下方式:

### 方法A: 使用OpenClaw browser工具

在OpenClaw中执行:

\`\`\`bash
# 访问Nitter搜索
openclaw browser open "https://nitter.net/sama"
openclaw browser open "https://nitter.net/gdb"

# 或使用web_fetch获取页面
openclaw web_fetch "https://nitter.net/search?f=tweets&q=GPT-5"
\`\`\`

### 方法B: 关注Twitter Lists

推荐列表:
- [AI/ML Community](https://twitter.com/i/lists/AI_ML)
- [OpenAI Team](https://twitter.com/i/lists/OpenAI)

### 方法C: 付费方案

Twitter API Basic: $100/月
- 5000 tweets/月
- 适合自动化收集

EOF

echo ""
echo "✅ Twitter内容收集完成"
echo "📄 输出文件: $OUTPUT_FILE"
echo ""
echo "⚠️ 注意: 由于Twitter限制，自动收集可能不稳定"
echo "   建议使用browser工具手动收集高质量内容"
