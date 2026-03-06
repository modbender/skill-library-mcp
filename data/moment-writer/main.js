/**
 * 朋友圈写作助手 Lite
 * 精简版，适配OpenClaw 8192 tokens限制
 */

// 文案类型定义
const CONTENT_TYPES = {
  professional: {
    name: '专业型',
    formula: '故事案例 + 细节 + 美好结果',
    purpose: '建立权威，展示专业能力'
  },
  reliable: {
    name: '靠谱型',
    formula: '失败故事 + 不服输过程 + 成功结果',
    purpose: '建立信任，展示靠谱特质'
  },
  warm: {
    name: '温暖型',
    formula: '生活场景 + 真实互动 + 情感连接',
    purpose: '建立亲密度，展示真实生活'
  },
  altruistic: {
    name: '利他型',
    formula: '事件 + 细节 + 解释 + 价值观/金句',
    purpose: '降低防御，提供价值观点'
  },
  counter: {
    name: '反认知破圈',
    formula: '打破错误认知 + 植入你的理念',
    purpose: '清除错误认知，建立新理念'
  },
  target: {
    name: '圈用户',
    formula: '筛选目标人群 + 制造稀缺感',
    purpose: '精准圈人，建立边界'
  },
  intro_100: {
    name: '100字自我介绍',
    formula: '深耕[领域][时间] + 踩坑经验 + 价值钩子',
    purpose: '快速展示核心价值'
  }
};

// 核心提示词模板（精简）
function buildPrompt(type, topic) {
  const contentType = CONTENT_TYPES[type];
  if (!contentType) {
    return null;
  }

  let prompt = `请生成一条${contentType.name}朋友圈文案。

【类型公式】${contentType.formula}
【目的】${contentType.purpose}`;

  if (topic) {
    prompt += `\n【主题】${topic}`;
  }

  prompt += `

【排版要求】
1. 第一段20-25字以内，场景化切入
2. 每段不超过3行，段间空一行
3. 结尾用金句引导互动（认同类/好奇类/行动类）

【语言风格】
- 口语化表达，有场景感
- 避免粗俗词汇
- 收尾要利落

请直接输出文案，不要解释。`;

  return prompt;
}

// 主函数
async function momentsWriter(args) {
  const type = args.type || '';
  const topic = args.topic || '';

  if (!type || !CONTENT_TYPES[type]) {
    const typeList = Object.keys(CONTENT_TYPES).map(t => `- ${t}: ${CONTENT_TYPES[t].name}`).join('\n');
    return `❌ 未知类型: ${type}

【支持的类型】
${typeList}

【用法示例】
/moments professional 户外咨询场景
/moments warm 亲子时光
/moments counter 补课谎言`;
  }

  const prompt = buildPrompt(type, topic);
  return prompt;
}

// 导出
module.exports = { momentsWriter, CONTENT_TYPES };
