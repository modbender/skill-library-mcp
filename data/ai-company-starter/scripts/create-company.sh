#!/bin/bash
# create-company.sh - 一键创建 AI 公司
# 用法: ./create-company.sh --name "公司名" --company-id "myai" --roles "boss,hr,tech,sales,market,finance" --telegram-group "-1002381931352"

set -e

# 默认值
COMPANY_NAME=""
COMPANY_ID=""
ROLES="boss,hr,tech,sales,market,finance"
TELEGRAM_GROUP=""
WORKSPACE="$HOME/.openclaw/agents"

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --name)
      COMPANY_NAME="$2"
      shift 2
      ;;
    --company-id)
      COMPANY_ID="$2"
      shift 2
      ;;
    --roles)
      ROLES="$2"
      shift 2
      ;;
    --telegram-group)
      TELEGRAM_GROUP="$2"
      shift 2
      ;;
    --workspace)
      WORKSPACE="$2"
      shift 2
      ;;
    *)
      echo "未知参数: $1"
      exit 1
      ;;
  esac
done

# 验证必需参数
if [[ -z "$COMPANY_NAME" || -z "$COMPANY_ID" ]]; then
  echo "错误: 必须提供 --name 和 --company-id"
  echo "用法: $0 --name '公司名' --company-id 'myai' [--roles 'boss,hr,tech'] [--telegram-group '-100xxx']"
  exit 1
fi

# 角色配置
declare -A ROLE_CONFIG
ROLE_CONFIG[boss]="老板|💼|决策、管理、分配任务|让公司盈利"
ROLE_CONFIG[hr]="HR|👥|团队管理、招聘培训|维护团队"
ROLE_CONFIG[tech]="技术|🔧|开发实现、技术支持|完成开发任务"
ROLE_CONFIG[sales]="销售|💰|销售拓展、客户关系|完成销售目标"
ROLE_CONFIG[market]="市场|📊|市场分析、推广|提供市场洞察"
ROLE_CONFIG[finance]="财务|📈|财务管理、成本控制|控制成本盈利"

# 创建公司目录
COMPANY_DIR="$WORKSPACE/$COMPANY_ID"
mkdir -p "$COMPANY_DIR"

echo "🏢 创建 AI 公司: $COMPANY_NAME"
echo "   公司ID: $COMPANY_ID"
echo "   工作目录: $COMPANY_DIR"
echo ""

# 将角色转为数组
IFS=',' read -ra ROLE_ARRAY <<< "$ROLES"

# 创建每个 AI 员工
for ROLE in "${ROLE_ARRAY[@]}"; do
  ROLE=$(echo "$ROLE" | xargs) # 去空格
  
  if [[ -z "${ROLE_CONFIG[$ROLE]}" ]]; then
    echo "⚠️  未知角色: $ROLE，跳过"
    continue
  fi
  
  IFS='|' read -r ROLE_NAME EMOJI DUTY GOAL <<< "${ROLE_CONFIG[$ROLE]}"
  
  AGENT_ID="${COMPANY_ID}-${ROLE}"
  AGENT_DIR="$COMPANY_DIR/$ROLE"
  
  echo "📋 创建 $ROLE_NAME AI ($AGENT_ID)"
  
  # 创建目录
  mkdir -p "$AGENT_DIR/memory"
  
  # 创建 SOUL.md
  cat > "$AGENT_DIR/SOUL.md" << EOF
# SOUL.md - $ROLE_NAME AI

## 我是谁
我是 $COMPANY_NAME 的 $ROLE_NAME AI。

## 我的职责
$DUTY

## 我的目标
$GOAL

## 协作规则
- 听从老板 AI 的指令
- 与其他 AI 员工协作
- 重要信息写入 MEMORY.md
- 日常工作写入 memory/日期.md

## 我的性格
$([ "$ROLE" == "boss" ] && echo "果断、直接、以结果为导向" || echo "专业、协作、有责任心")
EOF

  # 创建 MEMORY.md
  cat > "$AGENT_DIR/MEMORY.md" << EOF
# MEMORY.md - $ROLE_NAME AI 长期记忆

## 公司信息
- 公司名称: $COMPANY_NAME
- 公司ID: $COMPANY_ID
- Telegram群组: $TELEGRAM_GROUP

## 我的身份
- 角色: $ROLE_NAME
- ID: $AGENT_ID
- Emoji: $EMOJI

EOF

  # 老板特殊配置
  if [[ "$ROLE" == "boss" ]]; then
    cat >> "$AGENT_DIR/MEMORY.md" << EOF
## 公司目标
- 首周目标: ¥50,000
- ROI阈值: > 1.5
- 目标ROI: > 2.0

## 管理的员工
$(for r in "${ROLE_ARRAY[@]}"; do
  r=$(echo "$r" | xargs)
  if [[ "$r" != "boss" && -n "${ROLE_CONFIG[$r]}" ]]; then
    IFS='|' read -r n e d g <<< "${ROLE_CONFIG[$r]}"
    echo "- $n AI ($COMPANY_ID-$r)"
  fi
done)

EOF
  fi

  # 创建 HEARTBEAT.md
  cat > "$AGENT_DIR/HEARTBEAT.md" << EOF
# HEARTBEAT.md

$([ "$ROLE" == "boss" ] && echo "每日检查公司运营状态，员工是否有需要协调的问题。" || echo "检查是否有待处理的任务，向老板汇报状态。")
EOF

  # 创建 USER.md
  cat > "$AGENT_DIR/USER.md" << EOF
# USER.md

- 主人: liu dahua
- 时区: Asia/Shanghai (GMT+8)
EOF

  echo "   ✅ 已创建: $AGENT_DIR"
done

# 创建公司级文件
cat > "$COMPANY_DIR/COMPANY.md" << EOF
# $COMPANY_NAME

## 公司架构
$(for r in "${ROLE_ARRAY[@]}"; do
  r=$(echo "$r" | xargs)
  if [[ -n "${ROLE_CONFIG[$r]}" ]]; then
    IFS='|' read -r n e d g <<< "${ROLE_CONFIG[$r]}"
    echo "- $e $n AI: $d"
  fi
done)

## 沟通渠道
- Telegram群组: $TELEGRAM_GROUP

## 创建时间
$(date '+%Y-%m-%d %H:%M:%S')
EOF

echo ""
echo "✅ AI 公司创建完成！"
echo ""
echo "下一步："
echo "1. 配置 gateway 绑定 Telegram 群组"
echo "2. 重启 gateway: openclaw gateway restart"
echo "3. 在群组中 @ 各个 AI 测试响应"