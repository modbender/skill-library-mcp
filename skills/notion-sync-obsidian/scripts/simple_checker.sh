#!/bin/bash
# 简化版Notion检查器 - 快速测试API连接和基本功能

echo "🧪 Notion同步系统 - 简化检查器"
echo "========================================"

SCRIPT_DIR="$(dirname "$0")"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$SKILL_DIR/config.json"

# 加载配置
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 配置文件不存在: $CONFIG_FILE"
    echo "请先复制 config.json.example 为 config.json 并配置"
    exit 1
fi

# 从配置读取参数
API_KEY=$(grep -o '"api_key": "[^"]*' "$CONFIG_FILE" 2>/dev/null | cut -d'"' -f4)
OBSIDIAN_ROOT=$(grep -o '"root_dir": "[^"]*' "$CONFIG_FILE" 2>/dev/null | cut -d'"' -f4)
TIMEZONE=$(grep -o '"timezone": "[^"]*' "$CONFIG_FILE" 2>/dev/null | cut -d'"' -f4)

# 设置默认值
[ -z "$TIMEZONE" ] && TIMEZONE="Asia/Shanghai"
[ -z "$OBSIDIAN_ROOT" ] && OBSIDIAN_ROOT="/path/to/your/obsidian"

# 获取当前时间
CURRENT_DATETIME=$(TZ="$TIMEZONE" date '+%Y-%m-%d %H:%M:%S')
YEAR_MONTH=$(TZ="$TIMEZONE" date '+%Y-%m')

# 创建目录
NOTION_DIR="$OBSIDIAN_ROOT/notion"
mkdir -p "$NOTION_DIR/$YEAR_MONTH"

echo "✅ 时区: $TIMEZONE"
echo "✅ 当前时间: $CURRENT_DATETIME"
echo "✅ 导出目录: $NOTION_DIR/$YEAR_MONTH"
echo "========================================"

# 检查API密钥
if [ -z "$API_KEY" ] || [ "$API_KEY" = "ntn_your_api_key_here" ]; then
    echo "❌ 请先在config.json中配置正确的Notion API密钥"
    echo "   获取地址: https://notion.so/my-integrations"
    exit 1
fi

echo "✅ API密钥: ${API_KEY:0:10}..."

# 测试API连接
echo ""
echo "🔍 测试Notion API连接..."
TEST_RESPONSE=$(curl -s -X GET "https://api.notion.com/v1/users/me" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" 2>/dev/null)

if echo "$TEST_RESPONSE" | grep -q '"object":"user"'; then
    USER_NAME=$(echo "$TEST_RESPONSE" | grep -o '"name":"[^"]*' | cut -d'"' -f4)
    WORKSPACE=$(echo "$TEST_RESPONSE" | grep -o '"workspace_name":"[^"]*' | cut -d'"' -f4)
    echo "✅ API连接成功"
    echo "   用户: ${USER_NAME:-未知}"
    echo "   工作空间: ${WORKSPACE:-未知}"
    
    # 创建测试文件
    echo ""
    echo "📝 创建测试文件..."
    
    TEST_TITLE="Notion同步测试_$(date +%Y%m%d_%H%M%S)"
    SAFE_TITLE=$(echo "$TEST_TITLE" | tr -cd '[:alnum:]_-')
    FILENAME="$NOTION_DIR/$YEAR_MONTH/${SAFE_TITLE}.md"
    
    cat > "$FILENAME" << EOF
---
title: $TEST_TITLE
notion_id: test_$(date +%s)
created_time: $CURRENT_DATETIME
last_edited_time: $CURRENT_DATETIME
export_time: $CURRENT_DATETIME
export_version: notion-sync-obsidian-v1.0
---

# $TEST_TITLE

这是Notion同步系统的测试文章。

## 系统信息

- **测试时间**: $CURRENT_DATETIME
- **时区**: $TIMEZONE
- **API用户**: ${USER_NAME:-未知}
- **工作空间**: ${WORKSPACE:-未知}
- **系统版本**: notion-sync-obsidian v1.0

## 功能特性

### ✅ 核心功能
1. **自动同步** - 定时检查Notion更新
2. **完整导出** - 导出文章标题和内容
3. **智能标题** - 正确提取文章原始标题
4. **移动通知** - 移动端优化格式

### ⚙️ 配置选项
- 检查频率: 可配置 (默认15分钟)
- 安静时段: 可配置 (默认00:00-08:30)
- 导出目录: 可自定义
- 通知格式: 移动端优化

## 使用说明

### 启动定时同步
\`\`\`bash
cd $SKILL_DIR
./scripts/start_timer.sh
\`\`\`

### 手动检查 (忽略安静时段)
\`\`\`bash
FORCE_CHECK=1 ./scripts/simple_checker.sh
\`\`\`

### 查看状态
\`\`\`bash
./scripts/status_timer.sh
\`\`\`

## 技术支持

技能名称: notion-sync-obsidian
版本: 1.0.0
维护者: OpenClaw社区

---
*测试完成时间: $CURRENT_DATETIME*
*系统状态: 正常 ✅*
EOF
    
    echo "✅ 创建测试文件: $(basename "$FILENAME")"
    echo "📁 文件路径: $FILENAME"
    
    echo ""
    echo "📱 移动端通知示例:"
    echo ""
    echo "📱 Notion同步系统测试成功"
    echo ""
    echo "📄 测试标题: $TEST_TITLE"
    echo "👤 API用户: ${USER_NAME:-未知}"
    echo "🏢 工作空间: ${WORKSPACE:-未知}"
    echo "📁 保存位置: $YEAR_MONTH/$(basename "$FILENAME")"
    echo "🕒 测试时间: $CURRENT_DATETIME"
    echo ""
    echo "✅ 系统连接正常"
    echo "🚀 可以开始使用定时同步功能"
    
else
    echo "❌ API连接失败"
    echo "请检查:"
    echo "1. API密钥是否正确"
    echo "2. 集成是否已分享到Notion工作空间"
    echo "3. 网络连接是否正常"
    echo ""
    echo "响应详情:"
    echo "$TEST_RESPONSE" | head -5
fi

echo ""
echo "========================================"
echo "🎉 简化检查器完成"
echo "📊 下一步: 配置定时同步"
echo "   ./scripts/start_timer.sh"
echo "========================================"