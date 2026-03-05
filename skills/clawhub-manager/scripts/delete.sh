#!/bin/bash
# ClawHub 技能删除脚本
# 用法: ./delete.sh <skill-slug>

set -e

SKILL_SLUG="$1"

if [ -z "$SKILL_SLUG" ]; then
  echo "❌ 错误：缺少技能 slug"
  echo ""
  echo "用法: $0 <skill-slug>"
  echo ""
  echo "示例："
  echo "  $0 my-skill"
  echo ""
  echo "⚠️  警告：删除操作不可逆！"
  exit 1
fi

echo "🗑️  删除 ClawHub 技能"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔖 Slug: $SKILL_SLUG"
echo ""
echo "⚠️  警告：此操作将软删除技能，需要管理员/审核员权限"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 确认删除
read -p "确认删除? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "❌ 已取消删除"
  exit 0
fi

# 执行删除
echo "正在删除..."
clawhub delete "$SKILL_SLUG"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 删除成功"
echo ""
echo "💡 提示："
echo "  - 软删除的技能可能不会立即从搜索中消失"
echo "  - 如果是误删，请联系 ClawHub 管理员"
