/**
 * AI协作操作系统 - 使用示例
 */

import { AICollaborationSystem } from './index';

console.log('╔════════════════════════════════════════════════════════════╗');
console.log('║          AI协作操作系统 - 完整示例                          ║');
console.log('╚════════════════════════════════════════════════════════════╝\n');

// ========== 1. 初始化系统 ==========
console.log('【1. 初始化系统】');
const ai = new AICollaborationSystem('my_ai_system', '../memory');
console.log('✅ 系统初始化完成\n');

// ========== 2. 信息信号识别 ==========
console.log('【2. 信息信号识别】');
const signals = [
  { title: 'GPT-5发布预告', source: 'OpenAI', timeSensitivity: 'immediate', impactDepth: 'worldview', actionability: 8, compoundValue: 9 },
  { title: 'AI Agent技术突破', source: 'Tech', timeSensitivity: 'delayed', impactDepth: 'cognition', actionability: 7, compoundValue: 8 },
  { title: '某明星八卦', source: '微博', timeSensitivity: 'immediate', impactDepth: 'tool', actionability: 1, compoundValue: 1 }
];

const scanReport = ai.dailyScan(signals);
console.log('核心信号:');
scanReport.signals.filter((s: any) => s.level === 'core' || s.level === 'meta').forEach((s: any) => {
  console.log(`  • ${s.title}: ${s.reason}`);
});
console.log('');

// ========== 3. 工作流资产沉淀 ==========
console.log('【3. 工作流资产沉淀】');
const tasks = ['完成产品需求文档', '参加团队周会'];
const responses = [
  { operation: '1.调研 2.分析 3.撰写', experience: '调研要充分', decision: '先核心后细节', thinking: '用户价值优先', value: '质量第一' },
  { operation: '1.同步 2.讨论', experience: '控制在1小时', decision: '争议单独讨论', thinking: '同步为主', value: '高效沟通' }
];

const workflowReport = ai.dailyWorkflow(tasks, responses);
console.log('隐性知识:');
workflowReport.tacitKnowledge.forEach((k: any) => {
  console.log(`  • [${k.level}] ${k.content}`);
});
console.log('');

// ========== 4. 个人目标追踪 ==========
console.log('【4. 个人目标追踪】');
const goals = [
  { name: '学习AI技术', priority: 8, progress: 30, deadline: new Date('2026-12-31'), motivations: [] },
  { name: '保持健康', priority: 9, progress: 60, deadline: new Date('2026-12-31'), motivations: [] }
];
const timeLog = { career: 50, family: 20, health: 5, learning: 10, social: 5, leisure: 10 };
const ideal = { career: 35, family: 25, health: 15, learning: 15, social: 5, leisure: 5 };

const energy = ai.dailyGoalTracking(goals, timeLog, ideal);
console.log('精力分配:');
energy.forEach((e: any) => {
  const status = e.gap > 5 ? '⚠️ 过度' : e.gap < -5 ? '⚠️ 不足' : '✅ 正常';
  console.log(`  • ${e.dimension}: ${e.actualPercentage.toFixed(0)}% (理想: ${e.idealPercentage}%) ${status}`);
});
console.log('');

// ========== 5. AI镜像洞察 ==========
console.log('【5. AI镜像洞察】');
const insight = ai.generateInsight();
console.log(`观察: ${insight.observation}`);
console.log(`模式: ${insight.pattern}`);
console.log(`盲点: ${insight.blindSpot}`);
console.log(`建议: ${insight.suggestion}`);
console.log(`预测: ${insight.prediction}`);
console.log('');

// ========== 6. 系统健康检查 ==========
console.log('【6. 系统健康检查】');
const health = ai.healthCheck();
console.log('各层状态:');
Object.entries(health.levels).forEach(([level, status]: [string, any]) => {
  console.log(`  • ${level}: ${status.usage} [${status.status}]`);
});
console.log('');

// ========== 7. 系统摘要 ==========
console.log('【7. 系统摘要】');
console.log(ai.getSummary());

console.log('\n✅ 示例运行完成！');
