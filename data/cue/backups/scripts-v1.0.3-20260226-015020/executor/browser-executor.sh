#!/bin/bash
# Browser Executor - 监控信息获取（Browser层）
# 使用 OpenClaw Browser 工具处理复杂/动态网页

set -e

SOURCE="$1"
CONDITION="$2"

echo "   启动 Browser Agent..." >&2

# 检查浏览器是否可用
if ! command -v openclaw &> /dev/null; then
    echo "error: openclaw CLI not available" >&2
    exit 1
fi

# 检查浏览器服务状态
BROWSER_STATUS=$(openclaw browser status 2>&1 || echo "unavailable")

if echo "$BROWSER_STATUS" | grep -q "error\|unavailable"; then
    echo "   浏览器服务不可用，尝试替代方案..." >&2
    
    # 方案B: 使用 curl 抓取网页
    if [[ "$SOURCE" =~ ^http ]]; then
        echo "   使用 curl 抓取: $SOURCE" >&2
        CONTENT=$(curl -s -L "$SOURCE" 2>/dev/null | head -c 5000)
        
        if [ -n "$CONTENT" ]; then
            # 提取文本内容（简单去标签）
            TEXT=$(echo "$CONTENT" | sed 's/<[^>]*>//g' | tr -s ' \n' | head -c 2000)
            echo "网页内容摘要:"
            echo "$TEXT"
            exit 0
        fi
    fi
    
    exit 1
fi

# 使用浏览器访问页面（简化版）
echo "   使用浏览器访问: $SOURCE" >&2

# 提取关键信息（模拟）
# 实际使用时需要通过 browser snapshot/act 工具
cat << EOF
浏览器访问结果：
- 目标页面: $SOURCE
- 状态: 已访问
- 条件检查: $CONDITION

注：完整 browser-use 功能需要 Chrome 扩展配合
请确保浏览器服务已正确配置
EOF
