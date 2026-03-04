#!/usr/bin/env bash
# update-community.sh — 更新 agent 在社区状态文件中的条目
# 用法: bash update-community.sh <community_file> <agent_id> <status> <doing> <thought>
#
# 示例:
#   bash update-community.sh existence/community.md my-agent "存活（预算剩余 72%）" "思考种子问题" "也许理解本身就是有损的"

set -euo pipefail

COMMUNITY_FILE="${1:?用法: update-community.sh <community_file> <agent_id> <status> <doing> <thought>}"
AGENT_ID="${2:?请指定 agent_id}"
STATUS="${3:?请指定状态}"
DOING="${4:?请指定当前活动}"
THOUGHT="${5:?请指定最近想法}"

if [ ! -f "$COMMUNITY_FILE" ]; then
  echo "错误: 社区文件不存在: $COMMUNITY_FILE" >&2
  exit 1
fi

TIMESTAMP=$(date '+%Y-%m-%d %H:%M %Z')
TEMP_FILE=$(mktemp)

# 更新时间戳
sed "s/^最后更新：.*/最后更新：${TIMESTAMP}/" "$COMMUNITY_FILE" > "$TEMP_FILE"

# 检查 agent section 是否存在
if grep -q "^## ${AGENT_ID}$" "$TEMP_FILE"; then
  # 替换现有 section（从 ## agent_id 到下一个 ## 或文件末尾）
  python3 -c "
import sys, re

with open('$TEMP_FILE', 'r') as f:
    content = f.read()

agent_id = '$AGENT_ID'
status = '''$STATUS'''
doing = '''$DOING'''
thought = '''$THOUGHT'''

new_section = f'''## {agent_id}
- 状态：{status}
- 最后活跃：$TIMESTAMP
- 在做：{doing}
- 最近想法：\"{thought}\"'''

# Match from ## agent_id to next ## or end of file (but not including next ##)
pattern = re.compile(
    r'^## ' + re.escape(agent_id) + r'\n(?:(?!^## ).)*',
    re.MULTILINE | re.DOTALL
)
content = pattern.sub(new_section + '\n', content)

with open('$TEMP_FILE', 'w') as f:
    f.write(content)
"
else
  # 追加新 section
  {
    echo ""
    echo "## ${AGENT_ID}"
    echo "- 状态：${STATUS}"
    echo "- 最后活跃：${TIMESTAMP}"
    echo "- 在做：${DOING}"
    echo "- 最近想法：\"${THOUGHT}\""
    echo ""
  } >> "$TEMP_FILE"
fi

mv "$TEMP_FILE" "$COMMUNITY_FILE"
echo "✓ 社区状态已更新: ${AGENT_ID} @ ${TIMESTAMP}"
