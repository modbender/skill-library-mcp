#!/usr/bin/env node
/**
 * Cue v1.0.4 全面测试套件
 * 验证所有功能不比 v1.0.3 差
 */

import { createTaskManager } from './src/core/taskManager.js';
import { createMonitorManager } from './src/core/monitorManager.js';
import { evaluateSmartTrigger, extractEntities } from './src/utils/smartTrigger.js';
import { enqueueNotification, getPendingNotifications } from './src/utils/notificationQueue.js';
import { autoDetectMode, buildPrompt } from './src/api/cuecueClient.js';

const TEST_CHAT_ID = 'test_chat_001';

// 测试结果统计
const results = {
  passed: 0,
  failed: 0,
  tests: []
};

function test(name, fn) {
  return new Promise(async (resolve) => {
    try {
      await fn();
      results.passed++;
      results.tests.push({ name, status: '✅ PASS' });
      console.log(`✅ ${name}`);
      resolve();
    } catch (error) {
      results.failed++;
      results.tests.push({ name, status: '❌ FAIL', error: error.message });
      console.log(`❌ ${name}: ${error.message}`);
      resolve();
    }
  });
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message || 'Assertion failed');
  }
}

async function runTests() {
  console.log('\n🧪 Cue v1.0.4 全面测试套件\n');
  console.log('=====================================');
  
  // ========== 任务管理测试 ==========
  console.log('\n📋 任务管理测试');
  
  await test('创建任务', async () => {
    const manager = createTaskManager(TEST_CHAT_ID);
    const task = await manager.createTask({
      taskId: 'test_task_001',
      topic: '测试主题',
      mode: 'trader'
    });
    assert(task.task_id === 'test_task_001', '任务ID不匹配');
    assert(task.status === 'running', '任务状态应为running');
  });
  
  await test('更新任务进度', async () => {
    const manager = createTaskManager(TEST_CHAT_ID);
    const updated = await manager.updateTaskProgress('test_task_001', '测试中...', 50);
    assert(updated.progress === '测试中...', '进度未更新');
    assert(updated.percent === 50, '百分比未更新');
  });
  
  await test('完成任务', async () => {
    const manager = createTaskManager(TEST_CHAT_ID);
    const completed = await manager.completeTask('test_task_001', { summary: '测试完成' });
    assert(completed.status === 'completed', '任务状态应为completed');
    assert(completed.duration >= 0, '持续时间应为非负数');
  });
  
  await test('获取任务列表', async () => {
    const manager = createTaskManager(TEST_CHAT_ID);
    const tasks = await manager.getTasks(10);
    assert(Array.isArray(tasks), '应返回数组');
    assert(tasks.length > 0, '应有至少一个任务');
  });
  
  // ========== 监控管理测试 ==========
  console.log('\n🔔 监控管理测试');
  
  await test('创建监控项', async () => {
    const manager = createMonitorManager(TEST_CHAT_ID);
    const monitor = await manager.createMonitor({
      monitorId: 'test_monitor_001',
      title: '测试监控',
      symbol: '000001.SZ',
      category: 'Price',
      trigger: '股价突破10元'
    });
    assert(monitor.monitor_id === 'test_monitor_001', '监控ID不匹配');
    assert(monitor.is_active === true, '监控应为激活状态');
  });
  
  await test('获取活跃监控', async () => {
    const manager = createMonitorManager(TEST_CHAT_ID);
    const active = await manager.getActiveMonitors();
    assert(Array.isArray(active), '应返回数组');
    assert(active.length > 0, '应有至少一个活跃监控');
  });
  
  // ========== 智能触发评估测试 ==========
  console.log('\n🧠 智能触发评估测试');
  
  await test('语义相似度计算', async () => {
    const sim1 = await evaluateSmartTrigger(
      '宁德时代股价上涨',
      '宁德时代今日股价大幅上扬，创近期新高',
      { useLLM: false, threshold: 0.5 }
    );
    assert(sim1.confidence > 0.5, '相似度应大于0.5');
    assert(sim1.shouldTrigger === true, '应触发');
  });
  
  await test('实体提取', async () => {
    const entities = extractEntities('宁德时代300750.SZ股价上涨5%，突破500元');
    assert(entities.tickers.includes('300750.SZ'), '应提取股票代码');
    assert(entities.numbers.length > 0, '应提取数字');
  });
  
  await test('不相关内容应不触发', async () => {
    const result = await evaluateSmartTrigger(
      '宁德时代股价上涨',
      '今天天气很好，适合出游',
      { useLLM: false, threshold: 0.6 }
    );
    assert(result.shouldTrigger === false, '不应触发');
    assert(result.confidence < 0.6, '置信度应低于阈值');
  });
  
  // ========== 通知队列测试 ==========
  console.log('\n📨 通知队列测试');
  
  await test('添加通知到队列', async () => {
    const id = await enqueueNotification({
      chatId: TEST_CHAT_ID,
      type: 'test',
      data: { message: '测试通知' }
    });
    assert(typeof id === 'string', '应返回字符串ID');
    assert(id.startsWith('notif_'), 'ID格式应为notif_开头');
  });
  
  await test('获取待发送通知', async () => {
    const notifications = await getPendingNotifications(TEST_CHAT_ID);
    assert(Array.isArray(notifications), '应返回数组');
  });
  
  // ========== 自动角色匹配测试 ==========
  console.log('\n🎯 自动角色匹配测试');
  
  await test('短线交易模式识别', async () => {
    const mode = autoDetectMode('今日龙虎榜分析，主力资金流向');
    assert(mode === 'trader', '应识别为trader模式');
  });
  
  await test('基金经理模式识别', async () => {
    const mode = autoDetectMode('宁德时代2024年报财务分析，ROE和PE估值');
    assert(mode === 'fund-manager', '应识别为fund-manager模式');
  });
  
  await test('研究员模式识别', async () => {
    const mode = autoDetectMode('锂电池产业链竞争格局分析');
    assert(mode === 'researcher', '应识别为researcher模式');
  });
  
  await test('提示词构建', async () => {
    const prompt = buildPrompt('测试主题', 'trader');
    assert(prompt.includes('【调研目标】'), '应包含调研目标');
    assert(prompt.includes('【信息搜集与整合框架】'), '应包含框架');
    assert(prompt.includes('短线交易'), '应包含角色信息');
  });
  
  // ========== 测试总结 ==========
  console.log('\n=====================================');
  console.log('\n📊 测试总结');
  console.log(`✅ 通过: ${results.passed}`);
  console.log(`❌ 失败: ${results.failed}`);
  console.log(`📈 成功率: ${((results.passed / (results.passed + results.failed)) * 100).toFixed(1)}%`);
  
  if (results.failed === 0) {
    console.log('\n🎉 所有测试通过！v1.0.4 功能完备。');
    process.exit(0);
  } else {
    console.log('\n⚠️  部分测试失败，请检查实现。');
    results.tests.filter(t => t.status === '❌ FAIL').forEach(t => {
      console.log(`  - ${t.name}: ${t.error}`);
    });
    process.exit(1);
  }
}

runTests().catch(error => {
  console.error('测试运行失败:', error);
  process.exit(1);
});
