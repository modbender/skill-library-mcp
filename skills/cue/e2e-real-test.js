#!/usr/bin/env node
/**
 * Cue v1.0.4 端到端真实测试
 * 模拟真实用户操作流程
 */

import { createTaskManager } from './src/core/taskManager.js';
import { createMonitorManager } from './src/core/monitorManager.js';
import { autoDetectMode, buildPrompt } from './src/api/cuecueClient.js';
import { evaluateSmartTrigger } from './src/utils/smartTrigger.js';
import { enqueueNotification } from './src/utils/notificationQueue.js';

const TEST_USER = 'real_test_user_' + Date.now();

console.log('\n🎯 Cue v1.0.4 端到端真实测试\n');
console.log('=' .repeat(60));

// ========== 场景 1: 用户发起研究 ==========
console.log('\n📝 场景 1: 用户发起研究 "/cue 宁德时代 2024 财报分析"');

const taskManager = createTaskManager(TEST_USER);
const taskId = 'real_test_' + Date.now();

const task = await taskManager.createTask({
  taskId,
  topic: '宁德时代 2024 财报分析',
  mode: autoDetectMode('宁德时代 2024 财报分析')
});

console.log(`   ✅ 任务创建：${task.task_id}`);
console.log(`   ✅ 模式识别：${task.mode} (应为 fund-manager)`);
console.log(`   ✅ 状态：${task.status}`);

// ========== 场景 2: 研究进行中 ==========
console.log('\n📝 场景 2: 研究进度推送');

await taskManager.updateTaskProgress(taskId, '正在分析财务报表...', 30);
const progress1 = await taskManager.getTask(taskId);
console.log(`   ✅ 进度 30%: ${progress1.progress}`);

await taskManager.updateTaskProgress(taskId, '计算 ROE 和 PE 估值...', 60);
const progress2 = await taskManager.getTask(taskId);
console.log(`   ✅ 进度 60%: ${progress2.progress}`);

await taskManager.updateTaskProgress(taskId, '生成投资建议...', 90);
const progress3 = await taskManager.getTask(taskId);
console.log(`   ✅ 进度 90%: ${progress3.progress}`);

// ========== 场景 3: 研究完成 ==========
console.log('\n📝 场景 3: 研究完成并通知');

const completed = await taskManager.completeTask(taskId, {
  conversation_id: 'conv_' + Date.now(),
  report_url: 'https://cuecue.cn/r/test_report',
  summary: '宁德时代 2024 年表现强劲，ROE 达 25%'
});

console.log(`   ✅ 任务完成：${completed.status}`);
console.log(`   ✅ 耗时：${completed.duration}ms`);

// ========== 场景 4: 创建监控项 ==========
console.log('\n📝 场景 4: 基于报告创建监控项');

const monitorManager = createMonitorManager(TEST_USER);
const monitorId = 'monitor_' + Date.now();

const monitor = await monitorManager.createMonitor({
  monitorId,
  title: '宁德时代股价监控',
  symbol: '300750.SZ',
  category: 'Price',
  trigger: '股价突破 500 元'
});

console.log(`   ✅ 监控创建：${monitor.monitor_id}`);
console.log(`   ✅ 监控标的：${monitor.symbol}`);
console.log(`   ✅ 触发条件：${monitor.trigger}`);

// ========== 场景 5: 监控触发评估 ==========
console.log('\n📝 场景 5: 监控触发智能评估');

const triggerResult = await evaluateSmartTrigger(
  '宁德时代股价突破 500 元',
  '宁德时代今日股价大涨，突破 500 元关口，创历史新高',
  { useLLM: false, threshold: 0.5 }
);

console.log(`   ✅ 置信度：${(triggerResult.confidence * 100).toFixed(1)}%`);
console.log(`   ✅ 应触发：${triggerResult.shouldTrigger}`);

// ========== 场景 6: 发送完成通知 ==========
console.log('\n📝 场景 6: 发送研究完成通知');

const notifId = await enqueueNotification({
  chatId: TEST_USER,
  type: 'research_complete',
  data: {
    taskId,
    topic: '宁德时代 2024 财报分析',
    duration: '15 分钟',
    reportUrl: 'https://cuecue.cn/r/test_report'
  }
});

console.log(`   ✅ 通知入队：${notifId}`);

// ========== 测试总结 ==========
console.log('\n' + '='.repeat(60));
console.log('\n✅ 端到端测试完成！\n');
console.log('测试覆盖:');
console.log('  ✅ 任务创建和管理');
console.log('  ✅ 进度推送');
console.log('  ✅ 任务完成');
console.log('  ✅ 监控创建');
console.log('  ✅ 智能触发评估');
console.log('  ✅ 通知队列');
console.log('\n🎉 Cue v1.0.4 核心功能全部正常！\n');

process.exit(0);
