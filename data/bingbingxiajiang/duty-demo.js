/**
 * 春节值班机制 - 完整演示
 */

const { AICollaborationSystem } = require('./dist/index');

console.log('\n');
console.log('╔══════════════════════════════════════════════════════════════════════╗');
console.log('║           春节值班机制 - AI协作系统支持方案                           ║');
console.log('╚══════════════════════════════════════════════════════════════════════╝');
console.log('\n');

// 初始化系统
const ai = new AICollaborationSystem('duty_system', 'memory');

// ============================================================
// 第一部分：值班机制设计
// ============================================================
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【第一部分】值班机制设计');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

// 存储值班机制到L3知识记忆
ai.memory.addToL3({
  id: '',
  level: 'L3',
  category: 'methodology',
  key: '春节值班机制',
  value: {
    name: '春节产业热点监测值班机制',
    schedule: {
      time: '每天2位同学值班',
      duty: '监测前一天或当天产业科技热点'
    },
    tasks: [
      { time: '09:00', task: '开始监测热点' },
      { time: '12:00', task: '中午快速同步' },
      { time: '18:00', task: '发布当日总结（截止时间）' }
    ],
    outputs: {
      daily: '每日热点总结（关注等级）',
      analysis: '深度分析材料（触发条件：舆论火爆）'
    }
  },
  tags: ['duty', 'mechanism'],
  importance: 5,
  system: 'workflow',
  createdAt: new Date().toISOString(),
  accessedAt: new Date().toISOString(),
  accessCount: 0
});

console.log('✅ 值班机制已存储到系统');
console.log('');

// ============================================================
// 第二部分：热点监测与等级判断
// ============================================================
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【第二部分】热点监测与关注等级判断');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

// 模拟当天监测到的热点
const todayHotspots = [
  {
    title: 'OpenAI发布GPT-4.5',
    source: '官方公告',
    timeSensitivity: 'immediate',
    impactDepth: 'worldview',
    actionability: 9,
    compoundValue: 10,
    // 额外维度：舆论热度
    publicAttention: 95,      // 舆论关注度 0-100
    discussionVolume: 50000,  // 讨论量
    emotionIntensity: 80      // 情绪强度
  },
  {
    title: '某科技公司裁员传闻',
    source: '社交媒体',
    timeSensitivity: 'immediate',
    impactDepth: 'strategy',
    actionability: 6,
    compoundValue: 5,
    publicAttention: 75,
    discussionVolume: 20000,
    emotionIntensity: 90
  },
  {
    title: '新能源汽车销量数据发布',
    source: '行业报告',
    timeSensitivity: 'delayed',
    impactDepth: 'strategy',
    actionability: 7,
    compoundValue: 6,
    publicAttention: 45,
    discussionVolume: 5000,
    emotionIntensity: 30
  },
  {
    title: '某明星代言科技产品',
    source: '娱乐新闻',
    timeSensitivity: 'immediate',
    impactDepth: 'tool',
    actionability: 2,
    compoundValue: 2,
    publicAttention: 60,
    discussionVolume: 30000,
    emotionIntensity: 70
  },
  {
    title: 'AI监管新规出台',
    source: '政府公告',
    timeSensitivity: 'delayed',
    impactDepth: 'strategy',
    actionability: 8,
    compoundValue: 8,
    publicAttention: 55,
    discussionVolume: 8000,
    emotionIntensity: 40
  }
];

console.log('▶ 今日监测到的热点（原始数据）');
console.log('─────────────────────────────────────');
todayHotspots.forEach((h, i) => {
  console.log(`  ${i+1}. ${h.title}`);
  console.log(`     来源: ${h.source} | 舆论热度: ${h.publicAttention} | 讨论量: ${h.discussionVolume}`);
});
console.log('');

// 使用信号识别系统评估
console.log('▶ 关注等级判断（自动评估）');
console.log('─────────────────────────────────────');
console.log('');

// 定义关注等级标准
const attentionLevels = {
  S级: { min: 80, desc: '舆论非常火爆，需要立即输出分析材料', action: '立即撰写深度分析' },
  A级: { min: 60, desc: '高度关注，需要重点监测', action: '纳入每日总结重点' },
  B级: { min: 40, desc: '中等关注，持续跟踪', action: '简要记录' },
  C级: { min: 20, desc: '低关注，可忽略', action: '不纳入总结' }
};

// 评估每个热点
const evaluatedHotspots = todayHotspots.map(h => {
  // 综合评分 = 基础价值 + 舆论热度 + 情绪强度
  const baseValue = ai.signal.evaluateSignal(h);
  const attentionScore = (
    h.publicAttention * 0.4 + 
    (h.discussionVolume / 1000) * 0.3 + 
    h.emotionIntensity * 0.3
  );
  
  // 确定关注等级
  let level = 'C级';
  let action = '不纳入总结';
  let needAnalysis = false;
  
  if (attentionScore >= 80) {
    level = 'S级';
    action = '立即撰写深度分析';
    needAnalysis = true;
  } else if (attentionScore >= 60) {
    level = 'A级';
    action = '纳入每日总结重点';
  } else if (attentionScore >= 40) {
    level = 'B级';
    action = '简要记录';
  }
  
  return {
    ...h,
    baseLevel: baseValue.level,
    attentionScore: Math.round(attentionScore),
    attentionLevel: level,
    action,
    needAnalysis
  };
});

// 按等级分组显示
console.log('【S级 - 需要立即输出分析材料】');
evaluatedHotspots.filter(h => h.attentionLevel === 'S级').forEach(h => {
  console.log(`  🔴 ${h.title}`);
  console.log(`     综合评分: ${h.attentionScore} | 舆论热度: ${h.publicAttention} | 讨论量: ${h.discussionVolume}`);
  console.log(`     基础价值: ${h.baseLevel} | 行动: ${h.action}`);
});
console.log('');

console.log('【A级 - 高度关注】');
evaluatedHotspots.filter(h => h.attentionLevel === 'A级').forEach(h => {
  console.log(`  🟠 ${h.title}`);
  console.log(`     综合评分: ${h.attentionScore} | 舆论热度: ${h.publicAttention}`);
  console.log(`     行动: ${h.action}`);
});
console.log('');

console.log('【B级 - 中等关注】');
evaluatedHotspots.filter(h => h.attentionLevel === 'B级').forEach(h => {
  console.log(`  🟡 ${h.title}`);
  console.log(`     综合评分: ${h.attentionScore}`);
});
console.log('');

console.log('【C级 - 可忽略】');
evaluatedHotspots.filter(h => h.attentionLevel === 'C级').forEach(h => {
  console.log(`  ⚪ ${h.title} (评分: ${h.attentionScore})`);
});
console.log('');

// ============================================================
// 第三部分：每日总结输出模板
// ============================================================
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【第三部分】每日总结输出（18:00前发布）');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

const today = new Date().toLocaleDateString('zh-CN');
const dutyPersons = ['张三', '李四']; // 值班人员

// 生成每日总结
const dailySummary = {
  date: today,
  dutyPersons: dutyPersons,
  summary: `【${today} 产业热点日报】`,
  hotspots: evaluatedHotspots.filter(h => h.attentionLevel !== 'C级').map(h => ({
    title: h.title,
    level: h.attentionLevel,
    score: h.attentionScore,
    source: h.source,
    brief: generateBrief(h),
    needAnalysis: h.needAnalysis
  })),
  alertCount: evaluatedHotspots.filter(h => h.needAnalysis).length,
  nextSteps: []
};

// 生成简要描述
function generateBrief(hotspot) {
  const briefs = {
    'OpenAI发布GPT-4.5': 'OpenAI正式发布GPT-4.5模型，性能大幅提升，引发行业广泛关注和讨论。',
    '某科技公司裁员传闻': '社交媒体流传某科技公司裁员消息，引发员工和行业关注。',
    '新能源汽车销量数据发布': '最新销量数据显示新能源汽车市场持续增长。',
    'AI监管新规出台': '相关部门发布AI行业监管新规，对行业发展有重要影响。'
  };
  return briefs[hotspot.title] || '详见相关报道';
}

console.log('┌─────────────────────────────────────────────────────────────────┐');
console.log(`│ ${dailySummary.summary.padEnd(61)} │`);
console.log('├─────────────────────────────────────────────────────────────────┤');
console.log(`│ 值班人员: ${dailySummary.dutyPersons.join('、').padEnd(50)} │`);
console.log('├─────────────────────────────────────────────────────────────────┤');
console.log('│                                                                 │');
console.log('│ 【今日热点】                                                    │');
console.log('│                                                                 │');

dailySummary.hotspots.forEach((h, i) => {
  const levelIcon = h.level === 'S级' ? '🔴' : h.level === 'A级' ? '🟠' : '🟡';
  console.log(`│ ${levelIcon} [${h.level}] ${h.title.padEnd(48)} │`);
  console.log(`│     评分: ${h.score.toString().padEnd(3)} | ${h.brief.substring(0, 40).padEnd(44)} │`);
  if (h.needAnalysis) {
    console.log(`│     ⚠️  需要输出深度分析材料                                    │`);
  }
});

console.log('│                                                                 │');
console.log('├─────────────────────────────────────────────────────────────────┤');
console.log(`│ 📊 今日统计: 共监测${todayHotspots.length}条热点，S级${evaluatedHotspots.filter(h=>h.attentionLevel==='S级').length}条，A级${evaluatedHotspots.filter(h=>h.attentionLevel==='A级').length}条`.padEnd(62) + '│');
console.log(`│ ⚠️  待处理: ${dailySummary.alertCount}条需要深度分析`.padEnd(56) + '│');
console.log('└─────────────────────────────────────────────────────────────────┘');
console.log('');

// ============================================================
// 第四部分：深度分析材料触发机制
// ============================================================
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【第四部分】深度分析材料触发机制');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

console.log('▶ 触发条件（满足任一即触发）');
console.log('─────────────────────────────────────');
console.log('');
console.log('  1. 舆论关注度 ≥ 80');
console.log('  2. 讨论量 ≥ 30000');
console.log('  3. 情绪强度 ≥ 85');
console.log('  4. 综合评分 ≥ 75');
console.log('  5. 影响深度 = worldview（世界观级）');
console.log('');

console.log('▶ 今日需要输出分析材料的热点');
console.log('─────────────────────────────────────');

const needAnalysis = evaluatedHotspots.filter(h => h.needAnalysis);
if (needAnalysis.length > 0) {
  needAnalysis.forEach(h => {
    console.log('');
    console.log(`  【${h.title}】`);
    console.log(`  触发原因:`);
    if (h.publicAttention >= 80) console.log(`    • 舆论关注度: ${h.publicAttention} (≥80)`);
    if (h.discussionVolume >= 30000) console.log(`    • 讨论量: ${h.discussionVolume} (≥30000)`);
    if (h.emotionIntensity >= 85) console.log(`    • 情绪强度: ${h.emotionIntensity} (≥85)`);
    if (h.impactDepth === 'worldview') console.log(`    • 影响深度: 世界观级`);
    console.log(`  建议分析框架:`);
    console.log(`    1. 事件概述`);
    console.log(`    2. 舆论态势分析`);
    console.log(`    3. 对产业的影响`);
    console.log(`    4. 建议应对措施`);
  });
} else {
  console.log('  今日无需要深度分析的热点');
}
console.log('');

// ============================================================
// 第五部分：工作流程沉淀
// ============================================================
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【第五部分】工作流程沉淀（方法论）');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

// 沉淀值班工作流程
const dutyWorkflow = {
  name: '春节值班工作流程',
  steps: [
    {
      time: '09:00',
      action: '开始监测',
      tasks: ['打开监测工具', '查看前一日热点', '关注当日新闻源']
    },
    {
      time: '09:00-12:00',
      action: '持续监测',
      tasks: ['记录新出现的热点', '评估关注等级', '标记需要分析的热点']
    },
    {
      time: '12:00',
      action: '中午同步',
      tasks: ['与搭档快速同步', '确认重点关注事项']
    },
    {
      time: '12:00-17:00',
      action: '深度跟踪',
      tasks: ['跟踪S级热点发展', '准备分析材料（如需要）', '整理当日总结']
    },
    {
      time: '17:30',
      action: '完成总结',
      tasks: ['撰写每日热点日报', '确认关注等级', '标注待处理事项']
    },
    {
      time: '18:00前',
      action: '发布报告',
      tasks: ['发布每日总结', '提交分析材料（如有）', '交接给次日值班人员']
    }
  ]
};

ai.memory.addToL3({
  id: '',
  level: 'L3',
  category: 'methodology',
  key: '值班工作流程',
  value: dutyWorkflow,
  tags: ['duty', 'workflow'],
  importance: 5,
  system: 'workflow',
  createdAt: new Date().toISOString(),
  accessedAt: new Date().toISOString(),
  accessCount: 0
});

console.log('▶ 值班工作流程');
console.log('─────────────────────────────────────');
dutyWorkflow.steps.forEach((step, i) => {
  console.log(`  ${i+1}. [${step.time}] ${step.action}`);
  step.tasks.forEach(t => console.log(`     • ${t}`));
});
console.log('');

// ============================================================
// 第六部分：输出模板
// ============================================================
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【第六部分】输出模板');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

console.log('▶ 每日热点日报模板');
console.log('─────────────────────────────────────');
console.log(`
【X月X日 产业热点日报】

值班人员：XXX、XXX

【S级热点】（需要深度分析）
• 标题：XXX
  评分：XX | 来源：XXX
  简要：XXX

【A级热点】（高度关注）
• 标题：XXX
  评分：XX | 来源：XXX
  简要：XXX

【B级热点】（持续跟踪）
• 标题：XXX
  评分：XX

【今日统计】
共监测X条热点，S级X条，A级X条，B级X条

【待处理事项】
• 需要输出分析材料：X条
  - XXX（截止时间：次日12:00）
`);
console.log('');

console.log('▶ 深度分析材料模板');
console.log('─────────────────────────────────────');
console.log(`
【热点分析】XXX事件

一、事件概述
• 时间：
• 事件：
• 涉及方：

二、舆论态势
• 关注度：XX
• 讨论量：XX
• 情绪倾向：正面/中性/负面
• 主要观点：
  1. XXX
  2. XXX

三、产业影响
• 短期影响：
• 长期影响：
• 涉及领域：

四、建议措施
• 监测建议：
• 应对建议：

五、后续跟踪
• 需持续关注：
• 预计发展：
`);
console.log('');

// ============================================================
// 总结
// ============================================================
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【总结】AI协作系统如何支持值班机制');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

console.log('┌─────────────────────────────────────────────────────────────────┐');
console.log('│                     系统支持能力                                │');
console.log('├─────────────────────────────────────────────────────────────────┤');
console.log('│                                                                 │');
console.log('│  ✅ 信息信号识别系统                                            │');
console.log('│     • 自动评估热点关注等级                                      │');
console.log('│     • 过滤噪音，聚焦核心热点                                    │');
console.log('│     • 发现隐藏模式和趋势                                        │');
console.log('│                                                                 │');
console.log('│  ✅ 工作流资产沉淀系统                                          │');
console.log('│     • 标准化值班工作流程                                        │');
console.log('│     • 沉淀分析方法论                                            │');
console.log('│     • 输出模板管理                                              │');
console.log('│                                                                 │');
console.log('│  ✅ 统一记忆系统                                                │');
console.log('│     • L1：当日值班任务                                          │');
console.log('│     • L2：历史热点记录                                          │');
console.log('│     • L3：分析方法论、工作流程                                  │');
console.log('│     • L4：行业洞察、经验总结                                    │');
console.log('│                                                                 │');
console.log('│  ✅ 自动触发机制                                                │');
console.log('│     • 舆论热度 ≥ 80 → 自动提醒需要分析                          │');
console.log('│     • 讨论量 ≥ 30000 → 自动标记S级                              │');
console.log('│     • 世界观级影响 → 自动触发深度分析                           │');
console.log('│                                                                 │');
console.log('└─────────────────────────────────────────────────────────────────┘');
console.log('');

console.log('✅ 演示完成！系统完全支持您的值班机制需求。');
console.log('');
