/**
 * 信息时间衰减机制 - 演示
 * 核心原则：不错过最新信息，一周以上信息自动降级
 */

const { AICollaborationSystem } = require('./dist/index');

console.log('\n');
console.log('╔══════════════════════════════════════════════════════════════════════╗');
console.log('║           信息时间衰减机制 - 最新信息优先                            ║');
console.log('╚══════════════════════════════════════════════════════════════════════╝');
console.log('\n');

// ============================================================
// 时间衰减机制设计
// ============================================================
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【时间衰减机制】');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

// 时间衰减配置
const TIME_CONFIG = {
  // 默认只显示最近7天的信息
  DEFAULT_MAX_AGE_DAYS: 7,
  
  // 时间衰减系数
  DECAY_RATES: {
    '0-1天': 1.0,      // 当天/昨天：不衰减
    '1-3天': 0.9,      // 1-3天：轻微衰减
    '3-7天': 0.7,      // 3-7天：中度衰减
    '7-14天': 0.4,     // 7-14天：重度衰减（默认不显示）
    '14天以上': 0.1    // 14天以上：极低（默认不显示）
  },
  
  // 等级调整规则
  LEVEL_ADJUSTMENT: {
    '7天以上': {
      action: '降级',
      rule: '最高只能为B级，无论原本等级多高'
    },
    '14天以上': {
      action: '归档',
      rule: '默认不显示，仅存档可查'
    }
  }
};

console.log('▶ 时间衰减系数');
console.log('─────────────────────────────────────');
console.log('');
console.log('  信息年龄      衰减系数    说明');
console.log('  ─────────────────────────────────────');
console.log('  0-1天         1.0 (100%)  当天/昨天：不衰减，最高优先级');
console.log('  1-3天         0.9 (90%)   轻微衰减');
console.log('  3-7天         0.7 (70%)   中度衰减');
console.log('  7-14天        0.4 (40%)   重度衰减，默认不显示');
console.log('  14天以上      0.1 (10%)   极低，仅存档可查');
console.log('');

console.log('▶ 等级调整规则');
console.log('─────────────────────────────────────');
console.log('  • 7天以上的信息：最高只能为B级');
console.log('  • 14天以上的信息：默认不显示，需要手动查询');
console.log('  • 当天信息：优先级最高，始终置顶');
console.log('');

// ============================================================
// 时间衰减计算函数
// ============================================================

function calculateTimeDecay(publishDate) {
  const now = new Date();
  const publish = new Date(publishDate);
  const ageInDays = Math.floor((now - publish) / (1000 * 60 * 60 * 24));
  
  let decayRate = 1.0;
  let ageCategory = '0-1天';
  let isDefaultVisible = true;
  let maxLevel = 'S级';
  
  if (ageInDays <= 1) {
    decayRate = 1.0;
    ageCategory = '0-1天';
    isDefaultVisible = true;
    maxLevel = 'S级';
  } else if (ageInDays <= 3) {
    decayRate = 0.9;
    ageCategory = '1-3天';
    isDefaultVisible = true;
    maxLevel = 'S级';
  } else if (ageInDays <= 7) {
    decayRate = 0.7;
    ageCategory = '3-7天';
    isDefaultVisible = true;
    maxLevel = 'A级';
  } else if (ageInDays <= 14) {
    decayRate = 0.4;
    ageCategory = '7-14天';
    isDefaultVisible = false;  // 默认不显示
    maxLevel = 'B级';
  } else {
    decayRate = 0.1;
    ageCategory = '14天以上';
    isDefaultVisible = false;  // 默认不显示
    maxLevel = 'C级';
  }
  
  return {
    ageInDays,
    ageCategory,
    decayRate,
    isDefaultVisible,
    maxLevel
  };
}

// ============================================================
// 演示：不同时间的信息处理
// ============================================================
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【演示】不同时间信息处理');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

// 模拟不同时间的信息
const newsWithTime = [
  {
    title: 'OpenAI刚刚发布GPT-5',
    source: '官方公告',
    publishDate: new Date(),  // 今天
    publicAttention: 95,
    discussionVolume: 50000,
    emotionIntensity: 90,
    impactDepth: 'worldview'
  },
  {
    title: '某科技公司昨天发布财报',
    source: '财经新闻',
    publishDate: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),  // 昨天
    publicAttention: 70,
    discussionVolume: 20000,
    emotionIntensity: 60,
    impactDepth: 'strategy'
  },
  {
    title: '三天前的新能源政策',
    source: '政府公告',
    publishDate: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),  // 3天前
    publicAttention: 65,
    discussionVolume: 15000,
    emotionIntensity: 50,
    impactDepth: 'strategy'
  },
  {
    title: '一周前的AI行业峰会',
    source: '行业新闻',
    publishDate: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000),  // 8天前
    publicAttention: 80,
    discussionVolume: 30000,
    emotionIntensity: 70,
    impactDepth: 'cognition'
  },
  {
    title: '一个月前的科技展会',
    source: '展会报道',
    publishDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),  // 30天前
    publicAttention: 75,
    discussionVolume: 25000,
    emotionIntensity: 65,
    impactDepth: 'method'
  },
  {
    title: '两个月前的产品发布',
    source: '产品新闻',
    publishDate: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000),  // 60天前
    publicAttention: 85,
    discussionVolume: 40000,
    emotionIntensity: 80,
    impactDepth: 'strategy'
  }
];

console.log('▶ 原始信息列表（包含不同时间）');
console.log('─────────────────────────────────────');
newsWithTime.forEach((n, i) => {
  const dateStr = new Date(n.publishDate).toLocaleDateString('zh-CN');
  console.log(`  ${i+1}. ${n.title}`);
  console.log(`     发布时间: ${dateStr} | 舆论热度: ${n.publicAttention}`);
});
console.log('');

// 应用时间衰减
const processedNews = newsWithTime.map(n => {
  const timeDecay = calculateTimeDecay(n.publishDate);
  
  // 计算原始分数
  const rawScore = (
    n.publicAttention * 0.4 + 
    (n.discussionVolume / 1000) * 0.3 + 
    n.emotionIntensity * 0.3
  );
  
  // 应用时间衰减
  const adjustedScore = rawScore * timeDecay.decayRate;
  
  // 确定最终等级（考虑时间限制）
  let finalLevel;
  if (adjustedScore >= 75 && timeDecay.maxLevel === 'S级') {
    finalLevel = 'S级';
  } else if (adjustedScore >= 60 && ['S级', 'A级'].includes(timeDecay.maxLevel)) {
    finalLevel = 'A级';
  } else if (adjustedScore >= 40) {
    finalLevel = Math.min(timeDecay.maxLevel, 'B级');
  } else {
    finalLevel = 'C级';
  }
  
  // 7天以上强制降级
  if (timeDecay.ageInDays > 7 && finalLevel !== 'C级') {
    finalLevel = 'B级';
  }
  if (timeDecay.ageInDays > 14) {
    finalLevel = 'C级';
  }
  
  return {
    ...n,
    timeDecay,
    rawScore: Math.round(rawScore),
    adjustedScore: Math.round(adjustedScore),
    finalLevel
  };
});

console.log('▶ 时间衰减处理结果');
console.log('─────────────────────────────────────');
console.log('');
console.log('  标题                        原始分  衰减后  最终等级  默认显示');
console.log('  ─────────────────────────────────────────────────────────────');
processedNews.forEach(n => {
  const title = n.title.substring(0, 16).padEnd(16);
  console.log(`  ${title}  ${n.rawScore.toString().padStart(3)}    ${n.adjustedScore.toString().padStart(3)}     ${String(n.finalLevel).padEnd(4)}    ${n.timeDecay.isDefaultVisible ? '✅' : '❌'}`);
});
console.log('');

// ============================================================
// 默认显示 vs 手动查询
// ============================================================
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【默认显示】最近7天的信息');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

const defaultVisible = processedNews.filter(n => n.timeDecay.isDefaultVisible);

console.log('▶ 今日热点（默认显示）');
console.log('─────────────────────────────────────');
defaultVisible.forEach(n => {
  const dateStr = new Date(n.publishDate).toLocaleDateString('zh-CN');
  const levelIcon = n.finalLevel === 'S级' ? '🔴' : n.finalLevel === 'A级' ? '🟠' : '🟡';
  console.log(`  ${levelIcon} [${n.finalLevel}] ${n.title}`);
  console.log(`     发布: ${dateStr} | 评分: ${n.adjustedScore} | 年龄: ${n.timeDecay.ageInDays}天`);
});
console.log('');

console.log('▶ 已过滤（7天以上，默认不显示）');
console.log('─────────────────────────────────────');
const filtered = processedNews.filter(n => !n.timeDecay.isDefaultVisible);
if (filtered.length > 0) {
  filtered.forEach(n => {
    const dateStr = new Date(n.publishDate).toLocaleDateString('zh-CN');
    console.log(`  ⚪ ${n.title}`);
    console.log(`     发布: ${dateStr} | 已过期 ${n.timeDecay.ageInDays} 天`);
  });
  console.log('');
  console.log('  💡 如需查看历史信息，请使用手动查询：');
  console.log('     ai.queryHistory({ maxAge: 30 })  // 查看最近30天');
  console.log('     ai.queryHistory({ date: "2026-01-01" })  // 查看特定日期');
} else {
  console.log('  无过期信息');
}
console.log('');

// ============================================================
// 优先级排序：最新信息置顶
// ============================================================
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【优先级排序】最新信息置顶');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

// 排序规则：先按时间新鲜度，再按等级
const sorted = [...defaultVisible].sort((a, b) => {
  // 首先按时间排序（越新越靠前）
  if (a.timeDecay.ageInDays !== b.timeDecay.ageInDays) {
    return a.timeDecay.ageInDays - b.timeDecay.ageInDays;
  }
  // 时间相同，按等级排序
  const levelOrder = { 'S级': 0, 'A级': 1, 'B级': 2, 'C级': 3 };
  return levelOrder[a.finalLevel] - levelOrder[b.finalLevel];
});

console.log('▶ 排序后的热点列表');
console.log('─────────────────────────────────────');
sorted.forEach((n, i) => {
  const levelIcon = n.finalLevel === 'S级' ? '🔴' : n.finalLevel === 'A级' ? '🟠' : '🟡';
  const freshTag = n.timeDecay.ageInDays === 0 ? '【最新】' : n.timeDecay.ageInDays === 1 ? '【昨天】' : '';
  console.log(`  ${i+1}. ${levelIcon} [${n.finalLevel}] ${n.title} ${freshTag}`);
});
console.log('');

// ============================================================
// 配置更新
// ============================================================
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【配置更新】时间衰减参数');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

// 更新系统配置
const ai = new AICollaborationSystem('duty_system', 'memory');

// 存储时间衰减配置到L3
ai.memory.addToL3({
  id: '',
  level: 'L3',
  category: 'methodology',
  key: '信息时间衰减配置',
  value: {
    config: TIME_CONFIG,
    rules: [
      '默认只显示最近7天的信息',
      '当天信息优先级最高，始终置顶',
      '7天以上信息自动降级为B级或更低',
      '14天以上信息默认不显示，仅存档',
      '如需历史信息，需手动查询'
    ],
    principle: '不错过最新信息'
  },
  tags: ['config', 'time-decay'],
  importance: 5,
  system: 'signal',
  createdAt: new Date().toISOString(),
  accessedAt: new Date().toISOString(),
  accessCount: 0
});

console.log('✅ 时间衰减配置已更新');
console.log('');
console.log('▶ 当前配置');
console.log('─────────────────────────────────────');
console.log(`  默认显示范围: 最近 ${TIME_CONFIG.DEFAULT_MAX_AGE_DAYS} 天`);
console.log(`  当天信息系数: ${TIME_CONFIG.DECAY_RATES['0-1天']} (不衰减)`);
console.log(`  7天以上处理: ${TIME_CONFIG.LEVEL_ADJUSTMENT['7天以上'].action}`);
console.log(`  14天以上处理: ${TIME_CONFIG.LEVEL_ADJUSTMENT['14天以上'].action}`);
console.log('');

// ============================================================
// 总结
// ============================================================
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【总结】时间衰减机制要点');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

console.log('┌─────────────────────────────────────────────────────────────────┐');
console.log('│                     时间衰减机制                                │');
console.log('├─────────────────────────────────────────────────────────────────┤');
console.log('│                                                                 │');
console.log('│  ✅ 核心原则：不错过最新信息                                    │');
console.log('│                                                                 │');
console.log('│  ✅ 默认行为：                                                  │');
console.log('│     • 只显示最近7天的信息                                       │');
console.log('│     • 当天信息优先级最高，始终置顶                              │');
console.log('│     • 7天以上自动降级，不再作为热点                             │');
console.log('│                                                                 │');
console.log('│  ✅ 等级限制：                                                  │');
console.log('│     • 0-7天：可评为S/A/B级                                      │');
console.log('│     • 7-14天：最高B级                                           │');
console.log('│     • 14天以上：C级，默认不显示                                 │');
console.log('│                                                                 │');
console.log('│  ✅ 手动查询历史：                                              │');
console.log('│     • ai.queryHistory({ maxAge: 30 })                           │');
console.log('│     • ai.queryHistory({ date: "2026-01-01" })                   │');
console.log('│                                                                 │');
console.log('│  ✅ 不改变现有设定：                                            │');
console.log('│     • 信号评估逻辑不变                                          │');
console.log('│     • 等级判断标准不变                                          │');
console.log('│     • 只是增加了时间维度过滤                                    │');
console.log('│                                                                 │');
console.log('└─────────────────────────────────────────────────────────────────┘');
console.log('');

console.log('✅ 时间衰减机制已生效！最新信息优先，过期信息自动降级。');
console.log('');
