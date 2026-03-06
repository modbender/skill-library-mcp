/**
 * AI协作操作系统 - 详细演示
 */

const { AICollaborationSystem } = require('./dist/index');

console.log('\n');
console.log('╔══════════════════════════════════════════════════════════════════════╗');
console.log('║               AI协作操作系统 - 详细功能演示                           ║');
console.log('╚══════════════════════════════════════════════════════════════════════╝');
console.log('\n');

// ========== 创建系统实例 ==========
const ai = new AICollaborationSystem('demo_system', 'memory');

// ============================================================
// 第一部分：统一记忆系统演示
// ============================================================
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【第一部分】统一记忆系统 - 五层记忆演示');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

// L0 闪存 - 临时变量
console.log('▶ L0 闪存（临时变量）');
console.log('─────────────────────────────────────');
ai.memory.setVariable('current_user', '张三');
ai.memory.setVariable('session_id', 'demo_001');
ai.memory.setVariable('task_count', 3);
console.log('设置变量: current_user=张三, session_id=demo_001, task_count=3');
console.log('读取变量:', ai.memory.getAllVariables());
console.log('');

// L1 工作记忆 - 当前任务
console.log('▶ L1 工作记忆（当前任务）');
console.log('─────────────────────────────────────');
ai.memory.addToL1('今日目标', '完成AI协作系统演示', 'task', 4);
ai.memory.addToL1('核心规则', '所有输出必须有结构化格式', 'rule', 5);
console.log('已添加2条工作记忆');
console.log('');

// L2 经验记忆 - 经验教训
console.log('▶ L2 经验记忆（经验教训）');
console.log('─────────────────────────────────────');
ai.memory.addToL2(
  '成功经验',
  { task: '系统演示', result: '成功', key: '清晰的输出格式让用户更容易理解' },
  'insight',
  4,
  ['success', 'demo'],
  'shared'
);
ai.memory.addToL2(
  '踩坑记录',
  { task: '记忆存储', issue: '忘记创建目录', solution: '添加自动创建目录逻辑' },
  'insight',
  3,
  ['error', 'fix'],
  'shared'
);
console.log('已添加2条经验记忆');
console.log('');

// L3 知识记忆 - 方法论
console.log('▶ L3 知识记忆（方法论）');
console.log('─────────────────────────────────────');
ai.memory.addToL3({
  id: '',
  level: 'L3',
  category: 'methodology',
  key: 'AI协作方法论',
  value: {
    name: 'AI协作五步法',
    steps: ['1.明确目标', '2.收集信息', '3.分析决策', '4.执行沉淀', '5.复盘优化'],
    principles: ['简洁优先', '结构化输出', '持续迭代']
  },
  tags: ['methodology', 'ai-collaboration'],
  importance: 5,
  system: 'shared',
  createdAt: new Date().toISOString(),
  accessedAt: new Date().toISOString(),
  accessCount: 0
});
console.log('已添加1条方法论到L3知识记忆');
console.log('');

// L4 智慧记忆 - 人生洞察
console.log('▶ L4 智慧记忆（人生洞察）');
console.log('─────────────────────────────────────');
ai.memory.addToL4({
  id: '',
  level: 'L4',
  category: 'insight',
  key: '关于成长的洞察',
  value: {
    observation: '持续学习比天赋更重要',
    evidence: '观察身边成功人士的共同特点',
    implication: '每天进步1%，一年后提升37倍'
  },
  tags: ['insight', 'growth'],
  importance: 5,
  system: 'goal',
  createdAt: new Date().toISOString(),
  accessedAt: new Date().toISOString(),
  accessCount: 0
});
console.log('已添加1条洞察到L4智慧记忆');
console.log('');

// ============================================================
// 第二部分：信息信号识别演示
// ============================================================
console.log('\n');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【第二部分】信息信号识别系统 - 从噪音中发现信号');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

const rawSignals = [
  {
    title: 'GPT-5即将发布',
    source: 'OpenAI官方',
    timeSensitivity: 'immediate',
    impactDepth: 'worldview',
    actionability: 9,
    compoundValue: 10
  },
  {
    title: 'AI Agent自主决策能力突破',
    source: 'DeepMind论文',
    timeSensitivity: 'delayed',
    impactDepth: 'cognition',
    actionability: 7,
    compoundValue: 9
  },
  {
    title: '某明星离婚八卦',
    source: '娱乐新闻',
    timeSensitivity: 'immediate',
    impactDepth: 'tool',
    actionability: 1,
    compoundValue: 1
  },
  {
    title: '新编程语言发布',
    source: '技术社区',
    timeSensitivity: 'continuous',
    impactDepth: 'method',
    actionability: 5,
    compoundValue: 4
  },
  {
    title: 'AI监管政策出台',
    source: '政府公告',
    timeSensitivity: 'delayed',
    impactDepth: 'strategy',
    actionability: 8,
    compoundValue: 7
  }
];

console.log('▶ 输入：5条原始信息');
console.log('─────────────────────────────────────');
rawSignals.forEach((s, i) => {
  console.log(`  ${i+1}. ${s.title} (来源: ${s.source})`);
});
console.log('');

const scanReport = ai.signal.generateDailyScanReport(new Date().toISOString().split('T')[0], rawSignals);

console.log('▶ 信号识别结果');
console.log('─────────────────────────────────────');
console.log('');
console.log('【元信号】(最高价值，改变世界观)');
scanReport.signals.filter(s => s.level === 'meta').forEach(s => {
  console.log(`  ★ ${s.title}`);
  console.log(`    价值: ${s.reason}`);
  console.log(`    来源: ${s.source}`);
});
console.log('');

console.log('【核心信号】(高价值，影响决策)');
scanReport.signals.filter(s => s.level === 'core').forEach(s => {
  console.log(`  ◆ ${s.title}`);
  console.log(`    价值: ${s.reason}`);
  console.log(`    来源: ${s.source}`);
});
console.log('');

console.log('【普通信号】(值得关注)');
scanReport.signals.filter(s => s.level === 'signal').forEach(s => {
  console.log(`  ○ ${s.title}`);
  console.log(`    价值: ${s.reason}`);
});
console.log('');

console.log('【噪音】(可忽略)');
scanReport.signals.filter(s => s.level === 'noise').forEach(s => {
  console.log(`  ✗ ${s.title}`);
  console.log(`    原因: ${s.reason}`);
});
console.log('');

console.log('▶ 发现的模式');
console.log('─────────────────────────────────────');
scanReport.patterns.forEach(p => {
  console.log(`  • ${p.name}: ${p.description}`);
});
console.log('');

// ============================================================
// 第三部分：工作流资产沉淀演示
// ============================================================
console.log('\n');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【第三部分】工作流资产沉淀系统 - 隐性知识显性化');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

const tasks = ['完成产品需求文档', '主持团队周会', '解决线上Bug'];
const responses = [
  {
    operation: '1.用户调研 2.需求分析 3.文档撰写 4.评审修改',
    experience: '调研阶段多花时间，后期返工少',
    decision: '如果时间紧，先写核心功能，次要功能后续迭代',
    thinking: '从用户价值出发，而非功能堆砌',
    value: '用户价值第一，团队效率第二'
  },
  {
    operation: '1.同步进度 2.讨论问题 3.分配任务',
    experience: '周会时间控制在1小时内效果最好',
    decision: '如果有争议，先记录后续单独讨论',
    thinking: '周会是同步信息，不是解决问题',
    value: '高效沟通比长时间讨论更重要'
  },
  {
    operation: '1.复现问题 2.定位原因 3.修复验证 4.发布上线',
    experience: '先看日志，再看代码',
    decision: '如果是紧急Bug，先热修复，再彻底解决',
    thinking: 'Bug是系统问题的信号，要找到根因',
    value: '质量是生命线'
  }
];

console.log('▶ 输入：3个任务的工作过程');
console.log('─────────────────────────────────────');
tasks.forEach((t, i) => {
  console.log(`  ${i+1}. ${t}`);
});
console.log('');

const workflowReport = ai.workflow.generateDailyWorkflowReport(
  new Date().toISOString().split('T')[0],
  tasks,
  responses
);

console.log('▶ 隐性知识显性化结果');
console.log('─────────────────────────────────────');
console.log('');
console.log('【操作步骤层】');
workflowReport.tacitKnowledge.filter(k => k.level === 'operation').forEach(k => {
  console.log(`  • ${k.content}`);
});
console.log('');

console.log('【经验技巧层】');
workflowReport.tacitKnowledge.filter(k => k.level === 'experience').forEach(k => {
  console.log(`  • ${k.content}`);
});
console.log('');

console.log('【决策逻辑层】');
workflowReport.tacitKnowledge.filter(k => k.level === 'decision').forEach(k => {
  console.log(`  • ${k.content}`);
});
console.log('');

console.log('【思维模式层】');
workflowReport.tacitKnowledge.filter(k => k.level === 'thinking').forEach(k => {
  console.log(`  • ${k.content}`);
});
console.log('');

console.log('【价值观层】');
workflowReport.tacitKnowledge.filter(k => k.level === 'value').forEach(k => {
  console.log(`  • ${k.content}`);
});
console.log('');

console.log('▶ 识别的能力基因');
console.log('─────────────────────────────────────');
workflowReport.capabilityGenes.forEach(g => {
  console.log(`  • ${g.name}`);
  console.log(`    描述: ${g.description}`);
  console.log(`    可迁移场景: ${g.transferableScenarios.join(', ')}`);
});
console.log('');

console.log('▶ 沉淀的方法论');
console.log('─────────────────────────────────────');
workflowReport.methodologies.forEach(m => {
  console.log(`  【${m.name}】`);
  console.log(`  哲学层: ${m.levels.philosophy || '(未填写)'}`);
  console.log(`  原则层: ${m.levels.principles.slice(0,2).join(', ')}`);
  console.log(`  方法层: ${m.levels.methods.slice(0,2).join(', ')}`);
});
console.log('');

// ============================================================
// 第四部分：个人目标追踪演示
// ============================================================
console.log('\n');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【第四部分】个人目标追踪系统 - AI镜像看见自己');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

const goals = [
  { name: '学习AI技术', description: '掌握AI相关技术', priority: 8, progress: 35, deadline: new Date('2026-12-31'), motivations: [] },
  { name: '保持健康', description: '每周运动3次', priority: 9, progress: 50, deadline: new Date('2026-12-31'), motivations: [] },
  { name: '升职加薪', description: '晋升高级职位', priority: 7, progress: 40, deadline: new Date('2026-06-30'), motivations: [] },
  { name: '陪伴家人', description: '每周家庭日', priority: 8, progress: 30, deadline: new Date('2026-12-31'), motivations: [] }
];

const timeLog = {
  career: 45,    // 45小时
  family: 15,    // 15小时
  health: 3,     // 3小时
  learning: 8,   // 8小时
  social: 5,     // 5小时
  leisure: 8     // 8小时
};

const idealAllocation = {
  career: 35,
  family: 25,
  health: 15,
  learning: 15,
  social: 5,
  leisure: 5
};

const statedPriorities = {
  career: 8,
  family: 9,
  health: 9,
  learning: 8,
  social: 5,
  leisure: 4
};

console.log('▶ 目标列表');
console.log('─────────────────────────────────────');
goals.forEach(g => {
  console.log(`  • ${g.name}: 优先级${g.priority}, 进度${g.progress}%`);
});
console.log('');

console.log('▶ 本周时间投入');
console.log('─────────────────────────────────────');
const totalHours = Object.values(timeLog).reduce((a, b) => a + b, 0);
Object.entries(timeLog).forEach(([k, v]) => {
  console.log(`  • ${k}: ${v}小时 (${(v/totalHours*100).toFixed(0)}%)`);
});
console.log('');

const weeklyReport = ai.goal.generateWeeklySelfAwarenessReport(
  '本周',
  goals,
  timeLog,
  idealAllocation,
  statedPriorities
);

console.log('▶ 精力分配分析');
console.log('─────────────────────────────────────');
console.log('');
console.log('  维度        实际     理想     差距     状态');
console.log('  ─────────────────────────────────────────────');
weeklyReport.energyAllocation.forEach(e => {
  const status = e.gap > 5 ? '⚠️ 过度' : e.gap < -5 ? '⚠️ 不足' : '✅ 正常';
  console.log(`  ${e.dimension.padEnd(10)} ${e.actualPercentage.toFixed(0).padStart(3)}%    ${e.idealPercentage.toString().padStart(3)}%    ${e.gap > 0 ? '+' : ''}${e.gap.toFixed(0).padStart(3)}%    ${status}`);
});
console.log('');

console.log('▶ 认知盲点发现');
console.log('─────────────────────────────────────');
if (weeklyReport.blindSpots.length > 0) {
  weeklyReport.blindSpots.forEach(bs => {
    console.log(`  【${bs.type}】`);
    console.log(`  发现: ${bs.description}`);
    console.log(`  影响: ${bs.impact}`);
    console.log(`  建议: ${bs.suggestion}`);
    console.log('');
  });
} else {
  console.log('  未发现明显盲点');
  console.log('');
}

console.log('▶ AI镜像洞察');
console.log('─────────────────────────────────────');
console.log('');
console.log('  ┌─────────────────────────────────────────────────────────┐');
console.log('  │                    AI镜像信                              │');
console.log('  └─────────────────────────────────────────────────────────┘');
console.log('');
console.log(`  【我观察到的你】`);
console.log(`  ${weeklyReport.mirrorFeedback.observations}`);
console.log('');
console.log(`  【你的进步】`);
weeklyReport.mirrorFeedback.progress.forEach(p => {
  console.log(`  ✓ ${p}`);
});
console.log('');
console.log(`  【我担心的地方】`);
weeklyReport.mirrorFeedback.concerns.forEach(c => {
  console.log(`  ⚠ ${c.observation}`);
  console.log(`    担心: ${c.concern}`);
  console.log(`    建议: ${c.suggestion}`);
});
console.log('');
console.log(`  【下周建议】`);
(weeklyReport.mirrorFeedback.nextWeekSuggestions || []).forEach(s => {
  console.log(`  → ${s}`);
});
console.log('');

// ============================================================
// 第五部分：统一查询演示
// ============================================================
console.log('\n');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【第五部分】统一查询 - 跨层级搜索');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

console.log('▶ 搜索关键词: "AI"');
console.log('─────────────────────────────────────');
const searchResults = ai.memory.queryAll('AI');
console.log(`  L1工作记忆: ${searchResults.L1.length}条`);
console.log(`  L2经验记忆: ${searchResults.L2.length}条`);
console.log(`  L3知识记忆: ${searchResults.L3.length}条`);
console.log(`  L4智慧记忆: ${searchResults.L4.length}条`);
console.log('');

// ============================================================
// 第六部分：系统健康检查
// ============================================================
console.log('\n');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【第六部分】系统健康检查');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

const health = ai.memory.healthCheck();

console.log('▶ 各层记忆状态');
console.log('─────────────────────────────────────');
console.log('');
console.log('  层级    使用量      状态      说明');
console.log('  ─────────────────────────────────────────────');
console.log(`  L0     ${health.levels.L0.usage.padEnd(10)} ${health.levels.L0.status === 'OK' ? '✅ 正常' : '⚠️ 警告'}    临时变量`);
console.log(`  L1     ${health.levels.L1.usage.padEnd(10)} ${health.levels.L1.status === 'OK' ? '✅ 正常' : '⚠️ 警告'}    当前任务`);
console.log(`  L2     ${health.levels.L2.usage.padEnd(10)} ${health.levels.L2.status === 'OK' ? '✅ 正常' : '⚠️ 警告'}    经验教训`);
console.log(`  L3     ${health.levels.L3.usage.padEnd(10)} ${health.levels.L3.status === 'OK' ? '✅ 正常' : '⚠️ 警告'}    方法论`);
console.log(`  L4     ${health.levels.L4.usage.padEnd(10)} ${health.levels.L4.status === 'OK' ? '✅ 正常' : '⚠️ 警告'}    人生洞察`);
console.log('');

if (health.recommendations.length > 0) {
  console.log('▶ 系统建议');
  console.log('─────────────────────────────────────');
  health.recommendations.forEach(r => {
    console.log(`  • ${r}`);
  });
  console.log('');
}

// ============================================================
// 最终摘要
// ============================================================
console.log('\n');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【系统摘要】');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
console.log(ai.memory.getSummary());
console.log('');

console.log('╔══════════════════════════════════════════════════════════════════════╗');
console.log('║                     ✅ 演示完成！                                     ║');
console.log('╠══════════════════════════════════════════════════════════════════════╣');
console.log('║                                                                      ║');
console.log('║  这就是AI协作操作系统的完整功能：                                    ║');
console.log('║                                                                      ║');
console.log('║  1. 统一记忆系统 - 五层记忆自动流转                                  ║');
console.log('║  2. 信息信号识别 - 从噪音中发现信号                                  ║');
console.log('║  3. 工作流资产沉淀 - 隐性知识显性化                                  ║');
console.log('║  4. 个人目标追踪 - AI镜像看见自己                                    ║');
console.log('║                                                                      ║');
console.log('║  使用方式:                                                           ║');
console.log('║  const ai = new AICollaborationSystem("my_system");                  ║');
console.log('║  ai.memory / ai.signal / ai.workflow / ai.goal                       ║');
console.log('║                                                                      ║');
console.log('╚══════════════════════════════════════════════════════════════════════╝');
console.log('\n');
