#!/bin/bash
# github-trending - 获取 GitHub 热门项目
# 用法：github-trending [daily|weekly|monthly]

set -e

TIMEFRAME="${1:-daily}"

YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

get_period_display() {
    case "$1" in
        daily) echo "今日" ;;
        weekly) echo "本周" ;;
        monthly) echo "本月" ;;
        *) echo "热门" ;;
    esac
}

case "$TIMEFRAME" in
    daily|today) PERIOD="daily" ;;
    weekly|week) PERIOD="weekly" ;;
    monthly|month) PERIOD="monthly" ;;
    *) echo "用法：github-trending [daily|weekly|monthly]"; exit 1 ;;
esac

PERIOD_DISPLAY=$(get_period_display "$PERIOD")

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🔥 GitHub Trending ${PERIOD_DISPLAY}${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 获取并解析数据
curl -s "https://github.com/trending?since=$PERIOD" | python3 -c "
import sys, re

html = sys.stdin.read()

# 查找所有 trending 项目块
blocks = re.findall(r'(<h2[^>]*>.*?</article>)', html, re.DOTALL)

for i, block in enumerate(blocks[:10]):
    # 项目名称
    name_match = re.search(r'href=\"(/[^/\"]+/[^/\"]+)\"', block)
    if not name_match: continue
    name = name_match.group(1).lstrip('/')
    
    # 描述
    desc_match = re.search(r'<p[^>]*>(.*?)</p>', block, re.DOTALL)
    desc = re.sub(r'<[^>]+>', '', desc_match.group(1)).strip()[:80] if desc_match else ''
    if desc: desc += '...' if len(desc) < 80 else ''
    
    # 语言
    lang_match = re.search(r'<span[^>]*>([A-Za-z+#]+)</span>', block)
    lang = lang_match.group(1) if lang_match else 'Unknown'
    
    # Stars
    stars_match = re.search(r'stargazers\"[^>]*>[\\s\\n]*([\\d,\\.]+[kKmM]?)', block, re.IGNORECASE)
    stars = stars_match.group(1) if stars_match else '0'
    
    # Today
    today_match = re.search(r'>([\\d,\\.]+[kKmM]?) stars? today<', block, re.IGNORECASE)
    today = today_match.group(1) if today_match else '0'
    
    emoji = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟'][i]
    print(f\"{emoji} **{name}** ({lang}) +{today}⭐\")
    if desc: print(f'   {desc}')
    print(f'   ⭐ {stars} total | https://github.com/{name}')
    print()
"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}数据来源：https://github.com/trending${NC}"
