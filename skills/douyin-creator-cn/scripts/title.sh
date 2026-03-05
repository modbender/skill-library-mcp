#!/bin/bash
# 抖音标题优化建议
# 用法: ./title.sh "原标题"

TITLE="${1:-}"

if [ -z "$TITLE" ]; then
  echo "用法: ./title.sh \"你的标题\""
  exit 1
fi

echo "================================"
echo "✍️ 标题优化分析"
echo "================================"
echo ""
echo "原标题: $TITLE"
echo ""

# 分析标题长度
LENGTH=${#TITLE}
echo "📏 长度分析:"
if [ $LENGTH -lt 10 ]; then
  echo "  ⚠️ 标题太短（${LENGTH}字），建议 15-30 字"
elif [ $LENGTH -gt 50 ]; then
  echo "  ⚠️ 标题太长（${LENGTH}字），建议控制在 30 字以内"
else
  echo "  ✅ 长度适中（${LENGTH}字）"
fi
echo ""

# 检查是否包含吸引元素
echo "🎯 吸引力分析:"
if echo "$TITLE" | grep -qE "[0-9]+"; then
  echo "  ✅ 包含数字（增加可信度）"
else
  echo "  💡 建议加入数字（如：3个、5种、10分钟）"
fi

if echo "$TITLE" | grep -qE "[？?!！]"; then
  echo "  ✅ 包含疑问/感叹（吸引注意）"
else
  echo "  💡 建议加入疑问句或感叹句"
fi

if echo "$TITLE" | grep -qE "(你|我|他|她)"; then
  echo "  ✅ 包含人称代词（增加代入感）"
else
  echo "  💡 建议加入'你'、'我'等代词"
fi

if echo "$TITLE" | grep -qE "(最后|终于|竟然|居然|没想到)"; then
  echo "  ✅ 包含悬念词（制造好奇）"
else
  echo "  💡 建议加入悬念词"
fi
echo ""

# 提供优化建议
echo "🔥 优化建议:"
echo ""

# 生成优化版本
OPT1="${TITLE} | 最后一个太绝了"
OPT2="不敢相信！${TITLE}"
OPT3="${TITLE}，看完你会感谢我"
OPT4="【必看】${TITLE}，99%的人不知道"

echo "版本1（悬念型）: $OPT1"
echo "版本2（惊叹型）: $OPT2"
echo "版本3（价值型）: $OPT3"
echo "版本4（揭秘型）: $OPT4"
echo ""

echo "💡 标题技巧:"
echo "- 开头用数字：'3个技巧...'、'5分钟学会...'"
echo "- 制造悬念：'最后一个是惊喜'、'没想到...'"
echo "- 提供价值：'看完你会...'、'建议收藏'"
echo "- 引发共鸣：'你是不是也...'、'终于找到了...'"
echo "- 结合热点：蹭当前热门话题"
echo ""
