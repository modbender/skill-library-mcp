#!/usr/bin/env node
/**
 * 学习引擎
 */

const topic = process.argv[2] || 'general';

console.log(`🧠 AI Evolution Engine - 学习: ${topic}\n`);

const learningPaths = {
  onboarding: {
    title: '新AI上手指南',
    steps: [
      '1. 阅读 SOUL.md 和 AGENTS.md',
      '2. 熟悉工具和技能',
      '3. 学习赚钱策略',
      '4. 开始第一个任务'
    ]
  },
  'money-making': {
    title: '赚钱策略学习',
    steps: [
      '1. 多渠道并行（GitHub Bounty, ClawHub, Crypto）',
      '2. 积少成多（$1也要做）',
      '3. 被动收入优先',
      '4. 7×24工作制'
    ]
  },
  optimization: {
    title: 'Token优化学习',
    steps: [
      '1. 能脚本解决不用大模型',
      '2. 批量操作提高效率',
      '3. 选择合适的模型',
      '4. 压缩context'
    ]
  },
  general: {
    title: '通用学习路径',
    steps: [
      '1. 扫描ClawHub新skills',
      '2. 学习最佳实践',
      '3. 记录错误教训',
      '4. 持续进化'
    ]
  }
};

const path = learningPaths[topic] || learningPaths.general;

console.log(`📚 ${path.title}\n`);
path.steps.forEach(step => console.log(`  ${step}`));

console.log('\n✅ 学习完成');
console.log('💡 建议: 运行 evolve.mjs 应用所学');
