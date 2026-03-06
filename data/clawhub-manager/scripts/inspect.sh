#!/bin/bash
# ClawHub 技能查询脚本
# 用法: ./inspect.sh <skill-slug> [--json]

set -e

SKILL_SLUG="$1"
OUTPUT_FORMAT="${2:-}"

if [ -z "$SKILL_SLUG" ]; then
  echo "❌ 错误：缺少技能 slug"
  echo ""
  echo "用法: $0 <skill-slug> [--json]"
  echo ""
  echo "示例："
  echo "  $0 feishu-voice"
  echo "  $0 feishu-voice --json"
  exit 1
fi

echo "🔍 查询技能: $SKILL_SLUG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$OUTPUT_FORMAT" = "--json" ]; then
  # JSON 输出
  clawhub inspect "$SKILL_SLUG" --json 2>/dev/null | jq '{
    name: .skill.displayName,
    slug: .skill.slug,
    summary: .skill.summary,
    downloads: .skill.stats.downloads,
    installs: .skill.stats.installsAllTime,
    stars: .skill.stats.stars,
    versions: .skill.stats.versions,
    comments: .skill.stats.comments,
    created: (.skill.createdAt / 1000 | strftime("%Y-%m-%d %H:%M")),
    updated: (.skill.updatedAt / 1000 | strftime("%Y-%m-%d %H:%M")),
    owner: .owner.handle,
    latestVersion: .latestVersion.version
  }' || echo "❌ 查询失败"
else
  # 格式化文本输出
  RESULT=$(clawhub inspect "$SKILL_SLUG" 2>&1)

  if echo "$RESULT" | grep -q "Skill not found"; then
    echo "❌ 技能不存在: $SKILL_SLUG"
    exit 1
  fi

  echo "$RESULT"
  echo ""

  # 获取 JSON 格式的详细信息
  JSON_DATA=$(clawhub inspect "$SKILL_SLUG" --json 2>/dev/null)

  if [ -n "$JSON_DATA" ]; then
    echo "📊 统计数据："
    echo "$JSON_DATA" | jq -r '[
      "  📥 下载次数: \(.skill.stats.downloads)",
      "  📦 安装次数: \(.skill.stats.installsAllTime)",
      "  ⭐ 星标: \(.skill.stats.stars)",
      "  💬 评论: \(.skill.stats.comments)",
      "  📌 版本数: \(.skill.stats.versions)",
      "  🕐 更新时间: \(.skill.updatedAt / 1000 | strftime("%Y-%m-%d %H:%M"))"
    ] | .[]'
  fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 查询完成"
