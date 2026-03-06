#!/usr/bin/env node

/**
 * 财税自媒体内容生成器 (增强版)
 * 用法: node finance-content-generator.js [选项]
 *
 * 功能:
 *   - 交互式选题
 *   - 热门主题推荐 (财务/税务/审计/政策/技术)
 *   - 多种文章模板
 *   - 公众号专用格式
 *   - 自动保存到 articles 目录
 *
 * 示例:
 *   node finance-content-generator.js
 *   node finance-content-generator.js --topic "增值税新政" --type 政策解读 --save
 *   node finance-content-generator.js --list-topics
 */

import fs from 'fs';
import path from 'path';
import readline from 'readline';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  cyan: '\x1b[36m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  red: '\x1b[31m'
};

function colorize(text, color) {
  return `${colors[color]}${text}${colors.reset}`;
}

// ==================== 数据模块 ====================

// 热门主题库 (按领域分类)
const HOT_TOPICS = {
  // 2026年1月热点
  2026_01: [
    // 审计类
    { topic: '2025年度财务报表审计重点', domain: '审计', category: '年报审计', hot: 5, description: '新一年年报审计的关注要点和风险提示' },
    { topic: 'ESG审计实务指南', domain: '审计', category: '新兴领域', hot: 5, description: 'ESG报告审计的程序和方法' },
    { topic: '数据资产入账审计', domain: '审计', category: '新兴领域', hot: 4, description: '数据资源相关会计处理的审计要点' },

    // 财务会计类
    { topic: '新会计准则执行情况分析', domain: '财务', category: '准则解读', hot: 4, description: '新准则实施后的常见问题及应对' },
    { topic: '收入准则五步法应用', domain: '财务', category: '实务操作', hot: 3, description: '新收入准则实务应用难点解析' },
    { topic: '租赁准则实务应用', domain: '财务', category: '准则解读', hot: 3, description: '新租赁准则的账务处理要点' },
    { topic: '商誉减值测试实务', domain: '财务', category: '实务操作', hot: 3, description: '商誉减值测试的会计处理' },

    // 税务类
    { topic: '2026年税收优惠政策汇总', domain: '税务', category: '政策解读', hot: 5, description: '最新税收优惠政策梳理' },
    { topic: '增值税加计抵减政策', domain: '税务', category: '政策解读', hot: 4, description: '增值税加计抵减的实务操作' },
    { topic: '个人所得税汇算清缴', domain: '税务', category: '实务操作', hot: 5, description: '个税汇算清缴注意事项' },
    { topic: '研发费用加计扣除', domain: '税务', category: '实务操作', hot: 4, description: '研发费加计扣除实务指南' },

    // 政策类
    { topic: '数字货币会计处理指引', domain: '政策', category: '新兴领域', hot: 4, description: '数字货币相关会计处理规定' },
    { topic: '数据资产入表规定', domain: '政策', category: '新兴领域', hot: 5, description: '数据资源入表相关要求' },

    // 技术类
    { topic: 'AI在财务审计中的应用', domain: '技术', category: '财务科技', hot: 5, description: '人工智能技术在财务审计中的实践' },
    { topic: '财务共享中心建设', domain: '技术', category: '财务科技', hot: 4, description: '财务共享中心的搭建与运营' },
    { topic: 'ERP系统实施要点', domain: '技术', category: '信息化', hot: 3, description: 'ERP系统实施的关键环节' },
    { topic: '财务数据分析工具', domain: '技术', category: '数据分析', hot: 4, description: '财务数据分析常用工具介绍' }
  ],

  // 常青主题
  always: [
    // 审计类
    { topic: '货币资金审计', domain: '审计', category: '基础实务', hot: 3, description: '现金、银行存款等的审计程序' },
    { topic: '应收账款函证程序', domain: '审计', category: '基础实务', hot: 3, description: '应收账款函证的设计与执行' },
    { topic: '存货舞弊审计案例', domain: '审计', category: '风险领域', hot: 4, description: '存货舞弊的识别与审计应对' },
    { topic: '关联方交易审计', domain: '审计', category: '风险领域', hot: 4, description: '关联方交易的审计程序和风险应对' },
    { topic: '营业收入审计', domain: '审计', category: '风险领域', hot: 4, description: '营业收入确认的真实性、完整性审计' },
    { topic: '内部控制审计评价', domain: '审计', category: '内控审计', hot: 3, description: '内部控制审计的评价标准和方法' },
    { topic: '持续经营审计评估', domain: '审计', category: '风险领域', hot: 4, description: '持续经营假设的审计评估程序' },
    { topic: '审计工作底稿编制', domain: '审计', category: '职业规范', hot: 3, description: '审计底稿的编制要求和方法' },
    { topic: '审计重要性水平确定', domain: '审计', category: '职业规范', hot: 3, description: '重要性水平的确定和应用' },
    { topic: '审计抽样方法', domain: '审计', category: '职业规范', hot: 3, description: '审计抽样的设计和实施' },

    // 财务会计类
    { topic: '现金流量表编制', domain: '财务', category: '基础实务', hot: 4, description: '现金流量表的编制方法和技巧' },
    { topic: '合并报表编制', domain: '财务', category: '实务操作', hot: 4, description: '合并财务报表的编制要点' },
    { topic: '金融工具分类与计量', domain: '财务', category: '准则解读', hot: 3, description: '金融工具的分类标准与计量方法' },
    { topic: '固定资产核算', domain: '财务', category: '基础实务', hot: 2, description: '固定资产的取得、折旧、处置核算' },
    { topic: '应付账款核算', domain: '财务', category: '基础实务', hot: 2, description: '应付账款的确认、计量与披露' },
    { topic: '成本核算方法', domain: '财务', category: '实务操作', hot: 3, description: '常用成本核算方法介绍' },
    { topic: '财务报表分析', domain: '财务', category: '分析工具', hot: 4, description: '财务报表分析的基本方法' },
    { topic: '预算编制实务', domain: '财务', category: '管理会计', hot: 3, description: '企业预算编制的实务操作' },
    { topic: '内部控制体系建设', domain: '财务', category: '内控', hot: 3, description: '内部控制体系的建立与完善' },
    { topic: '财务人员职业发展', domain: '财务', category: '职业规划', hot: 3, description: '财务人员的职业发展路径' },

    // 税务类
    { topic: '增值税发票开具规范', domain: '税务', category: '实务操作', hot: 4, description: '增值税发票的开具要求和注意事项' },
    { topic: '增值税进项抵扣', domain: '税务', category: '实务操作', hot: 4, description: '增值税进项税额抵扣实务' },
    { topic: '企业所得税汇算清缴', domain: '税务', category: '实务操作', hot: 5, description: '企业所得税汇算清缴操作指南' },
    { topic: '税收筹划方法', domain: '税务', category: '筹划', hot: 4, description: '企业常用税收筹划方法' },
    { topic: '转让定价实务', domain: '税务', category: '国际税收', hot: 3, description: '转让定价的实务操作' },
    { topic: '税务稽查应对', domain: '税务', category: '风险管理', hot: 4, description: '税务稽查的应对策略' },
    { topic: '税收优惠政策解读', domain: '税务', category: '政策解读', hot: 4, description: '常用税收优惠政策介绍' },
    { topic: '跨境税收实务', domain: '税务', category: '国际税收', hot: 3, description: '跨境业务的税收处理' },
    { topic: '发票管理规范', domain: '税务', category: '实务操作', hot: 3, description: '企业发票管理的规范化要求' },
    { topic: '税务风险管控', domain: '税务', category: '风险管理', hot: 4, description: '企业税务风险识别与管控' },

    // 政策类
    { topic: '会计法规体系', domain: '政策', category: '法规基础', hot: 3, description: '中国会计法规体系介绍' },
    { topic: '税收法规解读', domain: '政策', category: '法规基础', hot: 3, description: '常用税收法规解读' },
    { topic: '证券法规解读', domain: '政策', category: '法规基础', hot: 3, description: '证券相关法规对财务的影响' },
    { topic: '财务政策解读', domain: '政策', category: '政策解读', hot: 3, description: '最新财务政策解读' },

    // 技术类
    { topic: 'Excel财务函数应用', domain: '技术', category: '办公技能', hot: 4, description: '财务常用Excel函数介绍' },
    { topic: '财务数据分析', domain: '技术', category: '数据分析', hot: 4, description: '财务数据分析的方法和工具' },
    { topic: '财务软件选型', domain: '技术', category: '信息化', hot: 3, description: '企业财务软件选型指南' },
    { topic: '云财务系统', domain: '技术', category: '信息化', hot: 3, description: '云财务系统的应用与实践' },
    { topic: '电子发票系统', domain: '技术', category: '信息化', hot: 3, description: '电子发票系统的使用' },
    { topic: 'RPA在财务中的应用', domain: '技术', category: '财务科技', hot: 4, description: 'RPA技术在财务流程中的应用' },
    { topic: '大数据财务分析', domain: '技术', category: '数据分析', hot: 4, description: '大数据技术在财务分析中的应用' }
  ]
};

// 文章类型模板库
const ARTICLE_TYPES = {
  '案例分析': {
    description: '以具体案例为核心，分析过程和经验教训',
    structure: [
      { section: '案例背景', content: '描述基本情况、发现的问题' },
      { section: '分析过程', content: '详细描述分析程序、方法、证据收集' },
      { section: '问题分析', content: '深入分析问题成因、影响、涉及法规' },
      { section: '处理结果', content: '处理意见、解决方案' },
      { section: '经验启示', content: '可推广的经验、警示要点' }
    ],
    titleTemplates: [
      '【案例】{topic}实战：从发现到解决',
      '案例拆解：{topic}全流程解析',
      '从一起{topic}案例看风险应对',
      '{topic}：一个真实案例的启示',
      '深度复盘：{topic}案例解析'
    ]
  },
  '政策解读': {
    description: '解读最新政策、准则、法规，分析影响和应对',
    structure: [
      { section: '政策背景', content: '出台背景、目的、适用范围' },
      { section: '核心内容', content: '关键条款、变化要点、重点解读' },
      { section: '影响分析', content: '对企业、工作的影响' },
      { section: '实务应对', content: '如何落实、注意事项、操作建议' },
      { section: '常见问题', content: '执行中的疑问与解答' }
    ],
    titleTemplates: [
      '【解读】{topic}：核心要点与实务应对',
      '深度解读：{topic}对企业的影响',
      '{topic}政策全文解读（附操作指南）',
      '一图读懂{topic}核心要点',
      '{topic}：财务人员需要知道的那些变化'
    ]
  },
  '实务指南': {
    description: '提供可操作的实务方法、程序、技巧',
    structure: [
      { section: '实务概述', content: '定义、适用场景、重要性' },
      { section: '操作流程', content: '分步骤详细操作指南' },
      { section: '工具方法', content: '常用工具、表格、检查清单' },
      { section: '注意事项', content: '常见误区、风险点' },
      { section: '质量控制', content: '质量把控要点、复核要求' }
    ],
    titleTemplates: [
      '【实务】{topic}：操作指南',
      '{topic}：从入门到精通',
      '实务：{topic}完全手册',
      '{topic}：5大步骤+3个工具',
      '手把手教你做{topic}'
    ]
  },
  '风险提示': {
    description: '聚焦风险识别、评估、应对',
    structure: [
      { section: '风险概述', content: '定义、表现形式、危害' },
      { section: '风险识别', content: '如何发现、识别方法、预警信号' },
      { section: '风险评估', content: '风险评估方法、等级划分' },
      { section: '应对措施', content: '针对性的应对程序、控制建议' },
      { section: '案例警示', content: '真实案例教训' }
    ],
    titleTemplates: [
      '【风险】{topic}：必须警惕的风险点',
      '{topic}风险识别与应对',
      '警惕：{topic}领域的5大风险',
      '{topic}高风险领域指南',
      '从失败案例看{topic}风险'
    ]
  },
  '经验分享': {
    description: '分享个人经验、心得、技巧',
    structure: [
      { section: '经验背景', content: '工作场景、遇到的问题' },
      { section: '核心经验', content: '关键做法、创新点' },
      { section: '实施步骤', content: '具体操作方法' },
      { section: '效果对比', content: '优化前后的变化' },
      { section: '适用场景', content: '什么情况下可用、注意事项' }
    ],
    titleTemplates: [
      '【分享】{topic}：我的经验总结',
      '做了10年财务，我总结了{topic}的3个要点',
      '{topic}：资深从业者的实战心得',
      '分享：{topic}的5个高效技巧',
      '从实践中来：{topic}经验谈'
    ]
  },
  '技术教程': {
    description: '技术工具、软件、方法的教程',
    structure: [
      { section: '技术概述', content: '技术/工具简介、应用场景' },
      { section: '环境准备', content: '安装配置、准备工作' },
      { section: '操作教程', content: '分步操作演示、关键功能' },
      { section: '进阶技巧', content: '高级功能、技巧方法' },
      { section: '常见问题', content: '故障排除、FAQ' }
    ],
    titleTemplates: [
      '【教程】{topic}入门与精通',
      '{topic}实战教程：从0到1',
      '10分钟学会{topic}',
      '{topic}：一看就懂的教程',
      '{topic}使用指南：图文并茂'
    ]
  },
  '行业洞察': {
    description: '行业趋势、前沿话题、深度思考',
    structure: [
      { section: '行业现状', content: '当前行业发展概况' },
      { section: '趋势分析', content: '未来发展趋势判断' },
      { section: '热点话题', content: '行业热点、前沿动态' },
      { section: '深度思考', content: '问题分析、观点阐述' },
      { section: '行动建议', content: '对企业和个人的建议' }
    ],
    titleTemplates: [
      '【洞察】{topic}：趋势与机遇',
      '深度思考：{topic}的未来',
      '{topic}行业发展趋势解读',
      '从{topic}看行业变革',
      '{topic}：下一个风口？'
    ]
  }
};

// 公众号格式模板
const WECHAT_FORMAT = {
  separator: '────────────────────────────────────',
  divider: '────────────────────────',
  boxTop: '╔════════════════════════════════════╗',
  boxSide: '║',
  boxBottom: '╚════════════════════════════════════╝',
  tip: '💡',
  warning: '⚠️',
  example: '📌',
  keyPoint: '🔑',
  checklist: '✅',
  arrow: '▶'
};

// ==================== 工具函数 ====================

function getCurrentMonth() {
  const now = new Date();
  return `${now.getFullYear()}_${String(now.getMonth() + 1).padStart(2, '0')}`;
}

function getHotTopics(domain = null) {
  const month = getCurrentMonth();
  const monthly = HOT_TOPICS[`2026_${String(new Date().getMonth() + 1).padStart(2, '0')}`] || HOT_TOPICS[month] || [];
  let allTopics = [...monthly, ...HOT_TOPICS.always];

  if (domain) {
    allTopics = allTopics.filter(t => t.domain === domain);
  }

  return allTopics;
}

function getDomains() {
  const domains = new Set();
  Object.values(HOT_TOPICS).forEach(topics => {
    topics.forEach(t => domains.add(t.domain));
  });
  return Array.from(domains);
}

function ensureArticlesDir() {
  const articlesDir = path.join(process.cwd(), 'articles');
  if (!fs.existsSync(articlesDir)) {
    fs.mkdirSync(articlesDir, { recursive: true });
  }
  return articlesDir;
}

function saveToFile(content, filename) {
  const articlesDir = ensureArticlesDir();
  const filepath = path.join(articlesDir, filename);
  fs.writeFileSync(filepath, content, 'utf-8');
  return filepath;
}

function getSafeFilename(topic) {
  const now = new Date();
  const dateStr = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}`;
  const safeTopic = topic.replace(/[<>:"/\\|?*\x00-\x1f]/g, '_').substring(0, 30);
  return `${dateStr}_${safeTopic}.md`;
}

// ==================== 生成器函数 ====================

function generateTitles(topic, articleType) {
  const typeConfig = ARTICLE_TYPES[articleType] || ARTICLE_TYPES['实务指南'];
  return typeConfig.titleTemplates.map((t, i) => {
    return `${i + 1}. ${t.replace('{topic}', topic)}`;
  });
}

function generateOutline(topic, articleType) {
  const typeConfig = ARTICLE_TYPES[articleType] || ARTICLE_TYPES['实务指南'];

  let outline = `# ${topic}：${articleType}\n\n`;

  typeConfig.structure.forEach((section, index) => {
    const sectionNum = index + 1;
    outline += `## ${sectionNum}、${section.section}\n\n`;
    outline += `- ${section.content}\n\n`;
  });

  return outline;
}

function generateFullArticle(topic, articleType) {
  const typeConfig = ARTICLE_TYPES[articleType] || ARTICLE_TYPES['实务指南'];
  const titles = generateTitles(topic, articleType);

  let article = `# ${titles[0].substring(3)}\n\n`;
  article += `> 📖 建议阅读时间：8-10分钟\n\n`;
  article += `---\n\n`;
  article += `## 引言\n\n`;
  article += `在当前的财税实务工作中，${topic}是一个备受关注的话题。本文将结合${articleType}的视角，为你系统梳理相关要点。\n\n`;
  article += `---\n\n`;

  typeConfig.structure.forEach((section, index) => {
    const sectionNum = ['一', '二', '三', '四', '五'][index] || `${index + 1}`;
    const subNum = index + 1;

    article += `## ${sectionNum}、${section.section}\n\n`;
    article += `### ${subNum}.${section.section.split('：')[0] || section.section}概述\n\n`;
    article += `${section.content}\n\n`;
    article += `### ${subNum}.${sectionNum} ${section.section.split('：')[0] || section.section}要点\n\n`;
    article += `- 要点1：[具体内容]\n`;
    article += `- 要点2：[具体内容]\n`;
    article += `- 要点3：[具体内容]\n\n`;
    article += `> 💡 **提示**：[此处可填写操作建议或注意事项]\n\n`;
    article += `---\n\n`;
  });

  article += `## 结语\n\n`;
  article += `${topic}涉及的内容较为复杂，需要结合具体情况进行分析和判断。希望本文能为您的实务工作提供参考。\n\n`;
  article += `---\n\n`;
  article += `**相关阅读**\n\n`;
  article += `- [推荐阅读1](#)\n`;
  article += `- [推荐阅读2](#)\n\n`;
  article += `---\n\n`;
  article += `*本文内容仅供学习交流，不构成专业建议。实际工作中请遵循相关准则和法规要求。*\n\n`;
  article += `*如需更多专业支持，欢迎关注我们获取更多内容。*\n`;

  return article;
}

function generateWeChatFormat(topic, articleType) {
  const titles = generateTitles(topic, articleType);
  const outline = generateOutline(topic, articleType);

  let output = '';
  output += `${WECHAT_FORMAT.boxTop}\n`;
  output += `${WECHAT_FORMAT.boxSide}${' '.repeat(16)}财税自媒体内容生成器${' '.repeat(16)}${WECHAT_FORMAT.boxSide}\n`;
  output += `${WECHAT_FORMAT.boxBottom}\n\n`;
  output += `${WECHAT_FORMAT.tip} 主题：${topic}\n`;
  output += `${WECHAT_FORMAT.tip} 类型：${articleType}\n`;
  output += `${WECHAT_FORMAT.tip} 日期：${new Date().toLocaleDateString('zh-CN')}\n\n`;
  output += `${WECHAT_FORMAT.separator}\n\n`;
  output += `【推荐标题】\n\n${WECHAT_FORMAT.separator}\n\n`;
  titles.forEach(t => output += `${t}\n`);
  output += `\n${WECHAT_FORMAT.separator}\n\n`;
  output += `【文章大纲】\n\n${WECHAT_FORMAT.separator}\n\n`;
  output += `${outline}`;
  output += `${WECHAT_FORMAT.separator}\n\n`;
  output += `【公众号排版建议】\n\n${WECHAT_FORMAT.separator}\n\n`;
  output += `${WECHAT_FORMAT.checklist} 标题：使用数字+关键词，如「5个要点」「3个方法」\n`;
  output += `${WECHAT_FORMAT.checklist} 导语：1-2句话概括文章价值，引发兴趣\n`;
  output += `${WECHAT_FORMAT.checklist} 正文：小标题分割，每段不超过3行\n`;
  output += `${WECHAT_FORMAT.checklist} 重点：使用引用框标注关键信息\n`;
  output += `${WECHAT_FORMAT.checklist} 配图：建议2-3张图表或信息图\n`;
  output += `${WECHAT_FORMAT.checklist} 金句：每部分提炼1-2句金句，便于传播\n`;
  output += `${WECHAT_FORMAT.checklist} 结尾：引导关注、点赞、转发\n\n`;
  output += `${WECHAT_FORMAT.separator}\n\n`;

  return output;
}

// ==================== 交互式功能 ====================

function createInterface() {
  return readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
}

function question(rl, prompt) {
  return new Promise(resolve => {
    rl.question(prompt, answer => resolve(answer));
  });
}

async function interactiveMode() {
  const rl = createInterface();

  console.log('');
  console.log(colorize('════════════════════════════════════', 'cyan'));
  console.log(colorize('   财税自媒体内容生成器 - 交互模式', 'cyan'));
  console.log(colorize('════════════════════════════════════', 'cyan'));
  console.log('');

  // 选择功能
  console.log(colorize('请选择功能：', 'yellow'));
  console.log('  1. 从热门主题中选择');
  console.log('  2. 输入自定义主题');
  console.log('  3. 查看所有热门主题');
  console.log('');

  const choice = await question(rl, colorize('请输入选项 (1-3): ', 'cyan'));

  let topic, articleType = '实务指南';

  if (choice === '1' || choice === '3') {
    // 选择领域
    if (choice === '1') {
      console.log('');
      console.log(colorize('【选择领域】', 'yellow'));
      console.log('');
      const domains = getDomains();
      domains.forEach((d, i) => {
        console.log(`  ${i + 1}. ${d}`);
      });
      console.log(`  ${domains.length + 1}. 全部领域`);
      console.log('');

      const domainChoice = await question(rl, colorize('请选择领域 (默认全部): ', 'cyan'));
      const domainIndex = parseInt(domainChoice) - 1;

      let selectedDomain = null;
      if (domainIndex >= 0 && domainIndex < domains.length) {
        selectedDomain = domains[domainIndex];
      }
    }

    const hotTopics = getHotTopics();

    if (choice === '3') {
      console.log('');
      console.log(colorize('【热门主题列表】', 'yellow'));
      console.log('');
      hotTopics.forEach((t, i) => {
        const hotStars = '⭐'.repeat(t.hot);
        const domainTag = colorize(`[${t.domain}]`, 'cyan');
        console.log(`  ${i + 1}. ${domainTag} ${t.topic}`);
        console.log(`     ${colorize(t.category, 'dim')} ${hotStars}`);
        console.log(`     ${t.description}`);
        console.log('');
      });
      rl.close();
      return;
    }

    // 显示热门主题
    console.log('');
    console.log(colorize('【热门主题推荐】', 'yellow'));
    console.log('');
    hotTopics.slice(0, 20).forEach((t, i) => {
      const hotStars = '⭐'.repeat(t.hot);
      const domainTag = colorize(`[${t.domain}]`, 'cyan');
      console.log(`  ${colorize(String(i + 1), 'cyan')}. ${domainTag} ${t.topic} ${colorize(hotStars, 'yellow')}`);
      console.log(`     ${colorize(t.category, 'dim')} - ${t.description}`);
    });
    console.log('');

    const topicChoice = await question(rl, colorize('请选择主题编号: ', 'cyan'));
    const topicIndex = parseInt(topicChoice) - 1;
    if (topicIndex >= 0 && topicIndex < hotTopics.length) {
      topic = hotTopics[topicIndex].topic;
    } else {
      console.log(colorize('无效的选择', 'red'));
      rl.close();
      return;
    }
  } else if (choice === '2') {
    topic = await question(rl, colorize('请输入主题: ', 'cyan'));
    if (!topic) {
      console.log(colorize('主题不能为空', 'red'));
      rl.close();
      return;
    }
  } else {
    console.log(colorize('无效的选择', 'red'));
    rl.close();
    return;
  }

  // 选择文章类型
  console.log('');
  console.log(colorize('【文章类型】', 'yellow'));
  console.log('');
  const types = Object.keys(ARTICLE_TYPES);
  types.forEach((t, i) => {
    console.log(`  ${i + 1}. ${t}`);
    console.log(`     ${ARTICLE_TYPES[t].description}`);
    console.log('');
  });

  const typeChoice = await question(rl, colorize('请选择文章类型 (默认1): ', 'cyan'));
  const typeIndex = parseInt(typeChoice) - 1;
  if (typeIndex >= 0 && typeIndex < types.length) {
    articleType = types[typeIndex];
  }

  // 选择输出格式
  console.log('');
  console.log(colorize('【输出格式】', 'yellow'));
  console.log('  1. 仅标题');
  console.log('  2. 仅大纲');
  console.log('  3. 完整文章');
  console.log('  4. 公众号格式');

  const formatChoice = await question(rl, colorize('请选择格式 (默认4): ', 'cyan'));
  const formats = ['titles', 'outline', 'full', 'wechat'];
  const format = formats[parseInt(formatChoice) - 1] || 'wechat';

  // 是否保存
  const saveChoice = await question(rl, colorize('是否保存到文件? (y/n, 默认y): ', 'cyan'));
  const shouldSave = !saveChoice || saveChoice.toLowerCase() === 'y';

  rl.close();

  // 生成内容
  console.log('');
  console.log(colorize('════════════════════════════════════', 'cyan'));
  console.log(colorize('   生成内容', 'cyan'));
  console.log(colorize('════════════════════════════════════', 'cyan'));
  console.log('');

  let content = '';
  let filename = '';

  switch (format) {
    case 'titles':
      content = generateTitles(topic, articleType).join('\n');
      console.log(content);
      filename = `标题_${getSafeFilename(topic)}`;
      break;
    case 'outline':
      content = generateOutline(topic, articleType);
      console.log(content);
      filename = `大纲_${getSafeFilename(topic)}`;
      break;
    case 'full':
      content = generateFullArticle(topic, articleType);
      console.log(content);
      filename = getSafeFilename(topic);
      break;
    case 'wechat':
      content = generateWeChatFormat(topic, articleType);
      console.log(content);
      filename = `公众号_${getSafeFilename(topic)}`;
      break;
  }

  if (shouldSave) {
    const filepath = saveToFile(content, filename);
    console.log('');
    console.log(colorize('════════════════════════════════════', 'cyan'));
    console.log(colorize(`✓ 已保存到: ${filepath}`, 'green'));
    console.log(colorize('════════════════════════════════════', 'cyan'));
  }
  console.log('');
}

// ==================== 命令行模式 ====================

function commandLineMode(args) {
  const options = {
    topic: '',
    type: '实务指南',
    format: 'wechat',
    save: false,
    domain: null
  };

  // 先处理不需要其他参数的选项
  if (args.includes('--help') || args.includes('-h')) {
    showHelp();
    return;
  }
  if (args.includes('--interactive') || args.includes('-i')) {
    interactiveMode();
    return;
  }

  // 解析参数
  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--topic':
      case '-t':
        options.topic = args[++i];
        break;
      case '--type':
        options.type = args[++i];
        break;
      case '--format':
      case '-f':
        options.format = args[++i];
        break;
      case '--domain':
      case '-d':
        options.domain = args[++i];
        break;
      case '--save':
      case '-s':
        options.save = true;
        break;
    }
  }

  // 处理 list-topics（在 domain 解析之后）
  if (args.includes('--list-topics') || args.includes('-l')) {
    listTopics(options.domain);
    return;
  }

  if (!options.topic) {
    console.log(colorize('错误: 请指定主题或使用 --interactive 进入交互模式', 'red'));
    console.log('使用 --help 查看帮助');
    process.exit(1);
  }

  // 验证文章类型
  if (!ARTICLE_TYPES[options.type]) {
    console.log(colorize(`错误: 无效的文章类型 "${options.type}"`, 'red'));
    console.log(`可用类型: ${Object.keys(ARTICLE_TYPES).join(', ')}`);
    process.exit(1);
  }

  // 生成内容
  console.log('');
  console.log(colorize('════════════════════════════════════', 'cyan'));
  console.log(colorize('   财税自媒体内容生成器', 'cyan'));
  console.log(colorize('════════════════════════════════════', 'cyan'));
  console.log('');
  console.log(colorize(`📋 主题: ${options.topic}`, 'bright'));
  console.log(colorize(`📝 类型: ${options.type}`, 'bright'));
  console.log('');

  let content = '';
  let filename = '';

  switch (options.format) {
    case 'titles':
      content = generateTitles(options.topic, options.type).join('\n');
      console.log(colorize('【推荐标题】', 'yellow'));
      console.log('');
      console.log(content);
      filename = `标题_${getSafeFilename(options.topic)}`;
      break;
    case 'outline':
      content = generateOutline(options.topic, options.type);
      console.log(colorize('【文章大纲】', 'yellow'));
      console.log('');
      console.log(content);
      filename = `大纲_${getSafeFilename(options.topic)}`;
      break;
    case 'full':
      content = generateFullArticle(options.topic, options.type);
      console.log(colorize('【完整文章】', 'yellow'));
      console.log('');
      console.log(content);
      filename = getSafeFilename(options.topic);
      break;
    case 'wechat':
    default:
      content = generateWeChatFormat(options.topic, options.type);
      console.log(content);
      filename = `公众号_${getSafeFilename(options.topic)}`;
      break;
  }

  if (options.save) {
    const filepath = saveToFile(content, filename);
    console.log('');
    console.log(colorize('────────────────────────────────────', 'cyan'));
    console.log(colorize(`✓ 已保存到: ${filepath}`, 'green'));
    console.log(colorize('────────────────────────────────────', 'cyan'));
  }
  console.log('');
}

function listTopics(domain = null) {
  const hotTopics = getHotTopics(domain);

  console.log('');
  console.log(colorize('════════════════════════════════════', 'cyan'));
  console.log(colorize(domain ? `   ${domain}领域热门主题` : '   全部热门主题', 'cyan'));
  console.log(colorize('════════════════════════════════════', 'cyan'));
  console.log('');

  // 按领域和分类显示
  const categories = {};
  hotTopics.forEach(t => {
    const key = `${t.domain}-${t.category}`;
    if (!categories[key]) {
      categories[key] = { domain: t.domain, category: t.category, topics: [] };
    }
    categories[key].topics.push(t);
  });

  Object.keys(categories).forEach(key => {
    const cat = categories[key];
    console.log(colorize(`【${cat.domain} - ${cat.category}】`, 'yellow'));
    console.log('');
    cat.topics.forEach(t => {
      const hotStars = '⭐'.repeat(t.hot);
      console.log(`  • ${t.topic} ${colorize(hotStars, 'yellow')}`);
      console.log(`    ${colorize(t.description, 'dim')}`);
    });
    console.log('');
  });

  console.log(colorize('────────────────────────────────────', 'cyan'));
  console.log(colorize(`共 ${hotTopics.length} 个热门主题`, 'bright'));
  console.log(colorize('────────────────────────────────────', 'cyan'));
  console.log('');
}

function showHelp() {
  console.log('');
  console.log(colorize('财税自媒体内容生成器', 'cyan'));
  console.log('');
  console.log('用法:');
  console.log('  node finance-content-generator.js [选项]');
  console.log('');
  console.log('选项:');
  console.log('  -t, --topic <主题>       指定文章主题');
  console.log('  --type <类型>           文章类型 (默认: 实务指南)');
  console.log(`                         可选: ${Object.keys(ARTICLE_TYPES).join(', ')}`);
  console.log('  -f, --format <格式>      输出格式 (默认: wechat)');
  console.log('                         可选: titles, outline, full, wechat');
  console.log('  -d, --domain <领域>     筛选主题领域 (审计/财务/税务/政策/技术)');
  console.log('  -s, --save              保存到 articles 目录');
  console.log('  -l, --list-topics       列出热门主题');
  console.log('  -i, --interactive       交互式模式');
  console.log('  -h, --help              显示帮助信息');
  console.log('');
  console.log('示例:');
  console.log('  node finance-content-generator.js -i');
  console.log('  node finance-content-generator.js --topic "增值税新政" --save');
  console.log('  node finance-content-generator.js -t "AI审计" --type 技术教程 -f full -s');
  console.log('  node finance-content-generator.js --list-topics --domain 税务');
  console.log('');
}

// ==================== 主函数 ====================

function main() {
  const args = process.argv.slice(2);

  // 无参数时进入交互模式
  if (args.length === 0) {
    interactiveMode();
    return;
  }

  commandLineMode(args);
}

main();
