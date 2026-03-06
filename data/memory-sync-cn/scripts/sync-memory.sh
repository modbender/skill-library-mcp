#!/bin/bash
# sync-memory.sh - 同步 MEMORY.md 到 CortexGraph
# 用法: ./sync-memory.sh [--dry-run]

set -e

DRY_RUN="${1:-}"
MEMORY_FILE="$HOME/.openclaw/workspace/MEMORY.md"
TAGS='["long-term","memory-md"]'

echo "🧠 同步 MEMORY.md → CortexGraph"
echo "   源文件: $MEMORY_FILE"

if [[ ! -f "$MEMORY_FILE" ]]; then
    echo "❌ MEMORY.md 不存在"
    exit 1
fi

# 解析 MEMORY.md 的主要部分
declare -A SECTIONS
CURRENT_SECTION=""
CURRENT_CONTENT=""

while IFS= read -r line; do
    # 检测标题
    if [[ "$line" =~ ^##\ (.+)$ ]]; then
        # 保存上一个 section
        if [[ -n "$CURRENT_SECTION" && -n "$CURRENT_CONTENT" ]]; then
            SECTIONS["$CURRENT_SECTION"]="$CURRENT_CONTENT"
        fi
        CURRENT_SECTION="${BASH_REMATCH[1]}"
        CURRENT_CONTENT=""
    else
        CURRENT_CONTENT+="$line"$'\n'
    fi
done < "$MEMORY_FILE"

# 保存最后一个 section
if [[ -n "$CURRENT_SECTION" && -n "$CURRENT_CONTENT" ]]; then
    SECTIONS["$CURRENT_SECTION"]="$CURRENT_CONTENT"
fi

echo "📋 发现 ${#SECTIONS[@]} 个 section"

# 导入到 CortexGraph
for section in "${!SECTIONS[@]}"; do
    content="${SECTIONS[$section]}"
    
    # 跳过空内容
    if [[ -z "${content// /}" ]]; then
        continue
    fi
    
    # 清理内容（转义引号）
    content_escaped=$(echo "$content" | sed 's/"/\\"/g' | tr '\n' ' ' | sed 's/  */ /g')
    section_escaped=$(echo "$section" | sed 's/"/\\"/g')
    
    # 确定标签（只允许英文）
    # 映射中文 section 到英文标签
    declare -A SECTION_TAGS
    SECTION_TAGS["关于宏斌"]="about-hongbin"
    SECTION_TAGS["宏斌的硬件"]="hardware"
    SECTION_TAGS["宏斌的 API Keys"]="api-keys"
    SECTION_TAGS["我的身份"]="identity"
    SECTION_TAGS["工作原则"]="principles"
    SECTION_TAGS["搜索优先"]="search-first"
    SECTION_TAGS["发布规范"]="publish-rules"
    SECTION_TAGS["术语定义 💡"]="glossary"
    SECTION_TAGS["已发布 Skills"]="published-skills"
    SECTION_TAGS["已安装的能力增强 Skills"]="installed-skills"
    SECTION_TAGS["待发布 Skills（Rate Limit 后）"]="pending-skills"
    SECTION_TAGS["重要教训"]="lessons"
    SECTION_TAGS["撤回方法"]="withdraw-method"
    SECTION_TAGS["Moltbook 账号"]="moltbook"
    SECTION_TAGS["工作文件位置"]="files"
    SECTION_TAGS["数据驱动策略"]="data-strategy"
    
    # 获取标签，默认用 generic
    section_tag="${SECTION_TAGS[$section]:-section}"

    
    # 确定强度（重要信息更高）
    strength=1.5
    if [[ "$section" =~ "教训" || "$section" =~ "原则" || "$section" =~ "规范" ]]; then
        strength=2.0
    fi
    
    echo "  📌 导入: $section (strength=$strength)"
    
    if [[ "$DRY_RUN" != "--dry-run" ]]; then
        mcporter call cortexgraph.save_memory \
            --config ~/.openclaw/workspace/config/mcporter.json \
            content="$section_escaped: $content_escaped" \
            tags='["memory-md","'"$section_tag"'"]' \
            strength=$strength \
            source="MEMORY.md"
    else
        echo "     [DRY RUN] 跳过保存"
    fi
done

echo "✅ 同步完成"
