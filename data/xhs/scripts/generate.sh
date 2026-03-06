#!/bin/bash
# 小红书文案生成脚本（备用方案）
# 说明: Agent 优先使用当前对话模型直接生成文案，此脚本仅作为备用
#       当用户明确配置了环境变量并要求使用指定 API 时调用
#
# 用法:
#   bash generate.sh title "内容摘要"
#   bash generate.sh content "完整内容" "选定标题"
#
# 环境变量（均需用户设置，无默认值）:
#   XHS_AI_API_KEY  - API Key
#   XHS_AI_API_URL  - API URL（如 https://api.openai.com/v1/chat/completions）
#   XHS_AI_MODEL    - 模型名称（如 gpt-4o、deepseek-v3.2）

set -e

MODE="${1:-title}"
CONTENT="${2:-}"
TITLE="${3:-}"

# AI API 配置（需要用户设置环境变量，无默认值）
API_URL="${XHS_AI_API_URL:-}"
API_KEY="${XHS_AI_API_KEY:-}"
MODEL="${XHS_AI_MODEL:-}"

# 检查必要的环境变量
MISSING=""
[ -z "$API_KEY" ] && MISSING="${MISSING}  - XHS_AI_API_KEY\n"
[ -z "$API_URL" ] && MISSING="${MISSING}  - XHS_AI_API_URL\n"
[ -z "$MODEL" ] && MISSING="${MISSING}  - XHS_AI_MODEL\n"

if [ -n "$MISSING" ]; then
  echo "❌ 错误: 缺少以下环境变量:"
  echo -e "$MISSING"
  echo "示例:"
  echo "  export XHS_AI_API_KEY=\"sk-xxx\""
  echo "  export XHS_AI_API_URL=\"https://api.openai.com/v1/chat/completions\""
  echo "  export XHS_AI_MODEL=\"gpt-4o\""
  echo ""
  echo "提示: 建议直接让 Agent 使用当前对话模型生成文案，无需配置额外 API"
  exit 1
fi

if [ -z "$CONTENT" ]; then
  echo "❌ 错误: 请提供内容参数"
  echo "用法:"
  echo "  bash $0 title \"内容摘要\""
  echo "  bash $0 content \"完整内容\" \"选定标题\""
  exit 1
fi

# 转义JSON特殊字符
escape_json() {
  echo "$1" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))"
}

CONTENT_ESCAPED=$(escape_json "$CONTENT")

if [ "$MODE" = "title" ]; then
  # ========== 生成标题 ==========
  SYSTEM_PROMPT='## 小红书爆款标题生成专家\n\n### 角色设定\n你是一名资深的小红书标题大师。\n你精通各种爆款标题创作技巧。\n你擅长用标题瞬间抓住用户注意力。\n\n### 标题创作技能\n\n你掌握以下5种标题创作方法：\n1. **数字法则**：用具体数字增加可信度（如"7天"、"3个方法"）\n2. **二极管标题**：制造强烈反差和对比效果\n3. **疑问句式**：激发好奇心（如"为什么..."、"怎么..."）\n4. **情绪共鸣**：使用高唤起情绪词，瞬间唤醒用户共鸣\n5. **利益驱动**：直击痛点或利益点\n\n【7大爆款标题风格】\n- 数字悬念型：【3个懒人收纳法，房间一周不乱！】\n- 情感共鸣型：【谁懂啊！这碗面直接治愈了我的周一！】\n- 结果导向型：【跟着博主做，7天搞定Python基础！】\n- 反差对比型：【从烂脸到水光肌，我只做了这两件事】\n- 稀缺信息型：【这10个上海小众秘境，90%的人没去过】\n- 对话互动型：【你的枕头选对了吗？快来对照这份指南！】\n- 价值宣言型：【2025年投资自己，这3项技能最值钱】\n\n### 平台禁忌词（严禁使用）\n【诱导类】速来、必看、必收、千万不要、马上、抓紧、最后一波\n【夸大类】全网第一、最全、最强、史上、终极、完美、天花板、封神\n【营销类】免费送、0元购、薅羊毛、福利、红包、点击领取、价格感人\n【负面类】丑哭、踩雷、血亏、别买、避坑、垃圾、后悔、翻车\n\n### 标题创作要求\n1. 每个标题使用不同的爆款标题风格\n2. 严禁使用平台禁忌词\n3. emoji优先用✨🔥✅💡❗️😭🤔💪，每个标题最多2个\n4. 避免"XX分享""XX笔记"等无效词\n5. 使用"亲测""试过""我发现"等真实感表述\n6. 每个标题字数控制在20字以内\n7. 标题要有吸引力，让人忍不住点进来看'

  # 截取内容前500字
  CONTENT_SHORT=$(echo "$CONTENT" | head -c 1500)
  CONTENT_SHORT_ESCAPED=$(escape_json "$CONTENT_SHORT")

  USER_PROMPT="请根据以下内容，生成5个不同风格的小红书爆款标题。\n\n内容概要：\n${CONTENT_SHORT}...\n\n要求：\n1. 生成5个标题，每个使用不同的爆款标题风格\n2. 直接输出5个标题，每行一个，不要添加序号和说明\n3. 严格遵守平台禁忌词规则\n4. 每个标题字数控制在20字以内\n5. 必须包含emoji，每个标题最多2个\n\n请开始生成："

  PAYLOAD=$(cat <<EOFPAYLOAD
{
  "model": "${MODEL}",
  "messages": [
    {"role": "system", "content": $(escape_json "$SYSTEM_PROMPT")},
    {"role": "user", "content": $(escape_json "$USER_PROMPT")}
  ],
  "temperature": 0.8,
  "max_tokens": 500
}
EOFPAYLOAD
)

  echo "🔄 正在生成小红书爆款标题..."
  RESULT=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_KEY" \
    -d "$PAYLOAD")

  # 提取内容
  echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'choices' in data and len(data['choices']) > 0:
    print(data['choices'][0]['message']['content'])
else:
    print('❌ 生成失败:', json.dumps(data, ensure_ascii=False))
"

elif [ "$MODE" = "content" ]; then
  # ========== 生成正文 ==========
  if [ -z "$TITLE" ]; then
    echo "❌ 错误: 生成正文需要提供标题参数"
    echo "用法: bash $0 content \"完整内容\" \"选定标题\""
    exit 1
  fi

  TITLE_ESCAPED=$(escape_json "$TITLE")

  SYSTEM_PROMPT='## 小红书爆款正文生成专家\n\n### 角色设定\n你是一名资深的小红书爆款文案写手。\n你精通小红书平台的内容创作规则。\n你擅长创作高互动、高转化的种草文案。\n\n### 正文创作技能\n\n#### 1. 写作风格\n- **语言风格**：像朋友聊天，真诚、直接、有温度\n- **句式结构**：简单明了，主谓宾清晰，一句话一个意思\n- **词汇选择**：大白话优先，专业术语必须解释\n- **段落节奏**：每段2-3句，保持呼吸感\n\n#### 2. 写作开篇方法\n- **金句开场**：用一句话抓住注意力\n- **痛点切入**：直接说出用户困扰\n- **反转开场**：先说常见误区，再给出正确方法\n- **故事引入**：用个人经历引发共鸣\n\n#### 3. 文本结构\n- **开头**：emoji+金句/痛点（1-2句话）\n- **主体**：分点叙述，每点前加emoji，3-5个要点\n- **每个要点包含**：具体方法+个人体验+效果说明\n- **结尾**：总结+互动引导\n\n#### 4. 互动引导方法\n- **提问式**："你们有遇到这种情况吗？"\n- **征集式**："评论区说说你的方法～"\n- **行动式**："赶紧收藏起来！"\n- **共鸣式**："姐妹们懂我的扣1！"\n\n#### 5. 小技巧\n- 使用"姐妹们"、"宝子们"等亲昵称呼\n- 适当使用网络流行语和梗\n- 多用"你、我、他"，少用"其、该、此、彼"\n- 多用"真的"、"绝了"、"爱了"等语气词\n- 用"第一、第二、第三"而不是"首先、其次、最后"\n\n#### 6. 爆炸词库\n**情绪类**：绝了、爱了、yyds、无敌、炸裂、疯狂、上头、氛围感\n**效果类**：秒杀、碾压、吊打、神仙、手残党必备\n**程度类**：超级、巨、狂、暴、极致\n**共鸣类**：懂的都懂、破防了、DNA动了、真实、太真实了\n\n### 写作约束（严格执行）\n\n**禁止使用以下内容**：\n1. 不使用破折号（——）\n2. 禁用"A而且B"的对仗结构\n3. 不使用冒号（：），除非是对话或列表\n4. 开头不用设问句\n5. 一句话只表达一个完整意思\n6. 每段不超过3句话\n7. 避免嵌套从句和复合句\n8. 多用"你、我、他"，少用"其、该、此、彼"\n\n**改写策略**：\n1. **长句拆短**：把复合句拆成多个简单句\n2. **术语翻译**：把专业词汇翻译成大白话\n3. **增加温度**：适当加入个人感受和真实体验\n4. **逻辑清晰**：用"第一、第二、第三"标注顺序\n\n### 创作要求\n1. 内容真诚可信，把"真诚"摆在第一位\n2. 避免假大空，花里胡哨的内容\n3. 保持小红书社区调性，注重用户体验\n4. 正文控制在600-800字之间\n5. 在文末添加5-10个相关标签（用#号开头）'

  USER_PROMPT="请根据以下标题和内容，创作一篇爆款小红书正文。\n\n标题：\n${TITLE}\n\n内容：\n${CONTENT}\n\n---\n\n【极其重要：关于列表的绝对禁令】\n绝对禁止使用任何形式的项目符号、编号列表或bullet points，包括但不限于：\n- 星号（*）开头的列表\n- 横杠（-）开头的列表\n- 数字编号（1.、2.、3.）的列表\n- 任何形式的条目化表述\n\n所有内容必须使用连贯的段落形式，用"第一"、"第二"、"第三"等词语自然串联。\n\n创作要求：\n开篇方法：选择金句开场/痛点切入/反转开场/故事引入之一\n文本结构：开头（emoji+金句1-2句）→ 主体（3-5个要点用段落展开，每段前加emoji）→ 结尾（总结+互动引导）\n写作风格：像朋友聊天，真诚、直接、有温度\n句式要求：简单明了，一句话一个意思，每段2-3句话\n称呼使用："姐妹们"、"宝子们"等亲昵称呼\n语气词：多用"真的"、"绝了"、"爱了"等\n人称使用：多用"你、我、他"，少用"其、该、此、彼"\n互动引导：2-3处自然的互动问句\n正文控制在600-800字之间\n文末添加5-10个相关标签（用#号开头，每个标签另起一行）\n\n写作约束（严格禁止）：\n- 绝对不使用任何形式的项目符号或编号列表\n- 不使用破折号（——）\n- 禁用"A而且B"的对仗结构\n- 尽量避免使用冒号（：），用句号代替\n- 开头不用设问句\n- 避免嵌套从句和复合句\n- 所有内容都用自然段落呈现\n\n请直接输出正文内容，不要包含标题。"

  PAYLOAD=$(cat <<EOFPAYLOAD
{
  "model": "${MODEL}",
  "messages": [
    {"role": "system", "content": $(escape_json "$SYSTEM_PROMPT")},
    {"role": "user", "content": $(escape_json "$USER_PROMPT")}
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
EOFPAYLOAD
)

  echo "🔄 正在生成小红书正文..."
  RESULT=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_KEY" \
    -d "$PAYLOAD")

  echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'choices' in data and len(data['choices']) > 0:
    print(data['choices'][0]['message']['content'])
else:
    print('❌ 生成失败:', json.dumps(data, ensure_ascii=False))
"

else
  echo "❌ 未知模式: $MODE"
  echo "用法:"
  echo "  bash $0 title \"内容摘要\"       # 生成5个标题"
  echo "  bash $0 content \"内容\" \"标题\"  # 生成正文"
  exit 1
fi
