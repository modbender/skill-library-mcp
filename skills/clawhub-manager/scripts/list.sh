#!/bin/bash
# 列出本地已安装的 ClawHub 技能
# 用法: ./list.sh

set -e

echo "📦 本地已安装的技能"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"

clawhub list

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 列表完成"
echo ""
echo "💡 提示："
echo "  - 使用 inspect.sh 查看技能详情"
echo "  - 使用 search.sh 在 ClawHub 上搜索更多技能"
