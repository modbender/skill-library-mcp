#!/bin/bash
# B站标题优化建议
# 用法: ./title.sh "原标题"

TITLE="${1:-}"

if [ -z "$TITLE" ]; then
  echo "用法: ./title.sh \"你的标题\""
  exit 1
fi

echo "================================"
echo "✍️ B站标题优化分析"
echo "================================"
echo ""
echo "原标题: $TITLE"
echo ""

# 分析标题长度
LENGTH=${#TITLE}
echo "📏 长度分析:"
if [ $LENGTH -lt 15 ]; then
  echo "  ⚠️ 标题太短（${LENGTH}字），建议 20-40 字"
elif [ $LENGTH -gt 50 ]; then
  echo "  ⚠️ 标题太长（${LENGTH}字），建议控制在 40 字以内"
elif [ $LENGTH -lt 20 ]; then
  echo "  💡 偏短（${LENGTH}字），可以加更多吸引元素"
else
  echo "  ✅ 长度适中（${LENGTH}字）"
fi
echo ""

# B站特有元素检查
echo "🎯 B站元素分析:"

if echo "$TITLE" | grep -qE "(【|】)"; then
  echo "  ✅ 包含【标签】（B站特色）"
else
  echo "  💡 建议加入【标签】，如【游戏】、【测评】"
fi

if echo "$TITLE" | grep -qE "[0-9]+(分钟|秒|期|集|万|亿)"; then
  echo "  ✅ 包含数字（增加可信度）"
else
  echo "  💡 建议加入数字（如：3分钟、第5期）"
fi

if echo "$TITLE" | grep -qE "(？|!|！)"; then
  echo "  ✅ 包含疑问/感叹（吸引注意）"
else
  echo "  💡 建议加入疑问句"
fi

if echo "$TITLE" | grep -qE "(笑死|破防|泪目|燃爆|震惊|万万没想到)"; then
  echo "  ✅ 包含情绪词（B站特色）"
else
  echo "  💡 可加入B站热门情绪词"
fi

if echo "$TITLE" | grep -qE "(硬核|干货|保姆级|手把手|终极)"; then
  echo "  ✅ 包含强调词（知识区）"
fi
echo ""

# 提供优化版本
echo "🔥 B站风格优化:"
echo ""

OPT1="【${TITLE}】没想到最后居然..."
OPT2="${TITLE} | 看完这期我悟了"
OPT3="【硬核】${TITLE}，建议收藏"
OPT4="${TITLE}！笑死我了哈哈哈哈"

echo "版本1（悬念型）: $OPT1"
echo "版本2（共鸣型）: $OPT2"
echo "版本3（知识型）: $OPT3"
echo "版本4（情绪型）: $OPT4"
echo ""

echo "💡 B站标题技巧:"
echo ""
echo "【标签】开头："
echo "  - 【游戏】、【测评】、【科普】"
echo "  - 帮助系统推荐"
echo ""
echo "数字吸引："
echo "  - 3分钟学会..."
echo "  - 第100期特别篇"
echo "  - 播放量破100万"
echo ""
echo "情绪词："
echo "  - 笑死、破防、泪目、燃爆"
echo "  - 万万没想到、震惊"
echo ""
echo "悬念制造："
echo "  - 没想到最后..."
echo "  - 结局万万没想到"
echo "  - 看到最后有惊喜"
echo ""
echo "互动引导："
echo "  - 你遇到过吗？"
echo "  - 你会选择哪个？"
echo ""
