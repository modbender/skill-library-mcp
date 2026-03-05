#!/usr/bin/env node
/**
 * Cue v1.0.4 真实集成测试
 * 实际执行功能测试，不是模拟
 */

import { createTaskManager } from './src/core/taskManager.js';
import { createMonitorManager } from './src/core/monitorManager.js';
import { startBackgroundResearch } from './src/core/backgroundExecutor.js';
import { getReportContent, extractReportInsights, generateMonitorSuggestions } from './src/api/cuecueClient.js';
import { evaluateSmartTrigger } from './src/utils/smartTrigger.js';
import { enqueueNotification, getPendingNotifications, getNotificationsForRetry } from './src/utils/notificationQueue.js';
import { autoDetectMode, buildPrompt } from './src/api/cuecueClient.js';

const TEST_CHAT_ID = 'integration_test_' + Date.now();

// 测试结果
const results = {
  scenarios: [],
  passed: 0,
  failed: 0,
  startTime: Date.now()
};

async function testScenario(name, fn) {
  console.log(`\n🧪 测试场景：${name}`);
  console.log('='.repeat(50));
  
  const scenarioResult = {
    name,
    tests: [],
    startTime: Date.now()
  };
  
  try {
    await fn(scenarioResult);
    results.passed++;
    scenarioResult.status = '✅ PASS';
    console.log(`\n✅ 场景通过：${name}`);
  } catch (error) {
    results.failed++;
    scenarioResult.status = '❌ FAIL';
    scenarioResult.error = error.message;
    console.log(`\n❌ 场景失败：${name} - ${error.message}`);
  }
  
  scenarioResult.duration = Date.now() - scenarioResult.startTime;
  results.scenarios.push(scenarioResult);
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message || 'Assertion failed');
  }
}

// ========== 场景 1: 完整研究流程 ==========
async function testResearchFlow(scenarioResult) {
  console.log('\n📋 步骤 1: 创建任务');
  const taskManager = createTaskManager(TEST_CHAT_ID);
  const taskId = `test_research_${Date.now()}`;
  
  const task = await taskManager.createTask({
    taskId,
    topic: '集成测试主题',
    mode: 'researcher'
  });
  
  assert(task.task_id === taskId, '任务 ID 不匹配');
  assert(task.status === 'running', '任务状态应为 running');
  scenarioResult.tests.push({ name: '创建任务', status: '✅' });
  console.log('   ✅ 任务创建成功');
  
  console.log('\n📋 步骤 2: 更新任务进度');
  await taskManager.updateTaskProgress(taskId, '测试中...', 50);
  const updatedTask = await taskManager.getTask(taskId);
  assert(updatedTask.progress === '测试中...', '进度未更新');
  assert(updatedTask.percent === 50, '百分比未更新');
  scenarioResult.tests.push({ name: '更新进度', status: '✅' });
  console.log('   ✅ 进度更新成功');
  
  console.log('\n📋 步骤 3: 完成任务');
  const completed = await taskManager.completeTask(taskId, {
    conversation_id: 'test_conv_001',
    report_url: 'https://cuecue.cn/c/test'
  });
  assert(completed.status === 'completed', '状态应为 completed');
  assert(completed.duration >= 0, '持续时间应有效');
  scenarioResult.tests.push({ name: '完成任务', status: '✅' });
  console.log('   ✅ 任务完成成功');
  
  console.log('\n📋 步骤 4: 获取任务列表');
  const tasks = await taskManager.getTasks(10);
  assert(Array.isArray(tasks), '应返回数组');
  assert(tasks.length > 0, '应有任务');
  scenarioResult.tests.push({ name: '获取任务列表', status: '✅' });
  console.log('   ✅ 任务列表获取成功');
}

// ========== 场景 2: 监控功能 ==========
async function testMonitorFlow(scenarioResult) {
  console.log('\n📋 步骤 1: 创建监控项');
  const monitorManager = createMonitorManager(TEST_CHAT_ID);
  const monitorId = `test_monitor_${Date.now()}`;
  
  const monitor = await monitorManager.createMonitor({
    monitorId,
    title: '集成测试监控',
    symbol: '000001.SZ',
    category: 'Price',
    trigger: '股价突破 10 元'
  });
  
  assert(monitor.monitor_id === monitorId, '监控 ID 不匹配');
  assert(monitor.is_active === true, '监控应激活');
  scenarioResult.tests.push({ name: '创建监控', status: '✅' });
  console.log('   ✅ 监控创建成功');
  
  console.log('\n📋 步骤 2: 获取活跃监控');
  const activeMonitors = await monitorManager.getActiveMonitors();
  assert(Array.isArray(activeMonitors), '应返回数组');
  assert(activeMonitors.length > 0, '应有活跃监控');
  scenarioResult.tests.push({ name: '获取活跃监控', status: '✅' });
  console.log('   ✅ 活跃监控获取成功');
  
  console.log('\n📋 步骤 3: 更新监控');
  await monitorManager.updateMonitor(monitorId, {
    trigger_count: 1,
    last_triggered_at: new Date().toISOString()
  });
  const updatedMonitor = await monitorManager.getMonitor(monitorId);
  assert(updatedMonitor.trigger_count === 1, '触发次数未更新');
  scenarioResult.tests.push({ name: '更新监控', status: '✅' });
  console.log('   ✅ 监控更新成功');
}

// ========== 场景 3: 智能触发评估 ==========
async function testSmartTrigger(scenarioResult) {
  console.log('\n📋 步骤 1: 高相关度测试');
  const result1 = await evaluateSmartTrigger(
    '宁德时代股价上涨',
    '宁德时代今日股价大幅上扬，创近期新高，成交量放大',
    { useLLM: false, threshold: 0.5 }
  );
  assert(result1.confidence > 0.5, '置信度应大于 0.5');
  scenarioResult.tests.push({ name: '高相关度测试', status: '✅' });
  console.log(`   ✅ 置信度：${(result1.confidence * 100).toFixed(1)}%`);
  
  console.log('\n📋 步骤 2: 低相关度测试');
  const result2 = await evaluateSmartTrigger(
    '宁德时代股价上涨',
    '今天天气很好，适合出游',
    { useLLM: false, threshold: 0.6 }
  );
  assert(result2.shouldTrigger === false, '不应触发');
  scenarioResult.tests.push({ name: '低相关度测试', status: '✅' });
  console.log(`   ✅ 置信度：${(result2.confidence * 100).toFixed(1)}% (不触发)`);
  
  console.log('\n📋 步骤 3: 实体提取测试');
  const entities = await evaluateSmartTrigger(
    '比亚迪 002594.SZ 突破 300 元',
    '比亚迪股份有限公司股价今日突破 300 元大关',
    { useLLM: false, threshold: 0.5 }
  );
  assert(entities.confidence > 0.3, '应有一定置信度');
  scenarioResult.tests.push({ name: '实体提取测试', status: '✅' });
  console.log(`   ✅ 实体识别成功`);
}

// ========== 场景 4: 通知队列 ==========
async function testNotificationQueue(scenarioResult) {
  console.log('\n📋 步骤 1: 添加通知到队列');
  const notifId = await enqueueNotification({
    chatId: TEST_CHAT_ID,
    type: 'test',
    data: { message: '集成测试通知' }
  });
  assert(typeof notifId === 'string', '应返回字符串 ID');
  assert(notifId.startsWith('notif_'), 'ID 格式应正确');
  scenarioResult.tests.push({ name: '添加通知', status: '✅' });
  console.log('   ✅ 通知入队成功');
  
  console.log('\n📋 步骤 2: 获取待发送通知');
  const pending = await getPendingNotifications(TEST_CHAT_ID);
  assert(Array.isArray(pending), '应返回数组');
  assert(pending.length > 0, '应有待发送通知');
  scenarioResult.tests.push({ name: '获取待发送', status: '✅' });
  console.log(`   ✅ 待发送通知：${pending.length} 条`);
  
  console.log('\n📋 步骤 3: 获取需要重试的通知');
  const forRetry = await getNotificationsForRetry(TEST_CHAT_ID);
  assert(Array.isArray(forRetry), '应返回数组');
  scenarioResult.tests.push({ name: '获取重试通知', status: '✅' });
  console.log(`   ✅ 需要重试：${forRetry.length} 条`);
}

// ========== 场景 5: 自动角色匹配 ==========
async function testAutoMode(scenarioResult) {
  console.log('\n📋 步骤 1: 短线交易模式');
  const mode1 = autoDetectMode('今日龙虎榜分析，主力资金流向');
  assert(mode1 === 'trader', `应识别为 trader，实际：${mode1}`);
  scenarioResult.tests.push({ name: '短线交易识别', status: '✅' });
  console.log('   ✅ 识别为：trader');
  
  console.log('\n📋 步骤 2: 基金经理模式');
  const mode2 = autoDetectMode('宁德时代 2024 年报财务分析，ROE 和 PE 估值');
  assert(mode2 === 'fund-manager', `应识别为 fund-manager，实际：${mode2}`);
  scenarioResult.tests.push({ name: '基金经理识别', status: '✅' });
  console.log('   ✅ 识别为：fund-manager');
  
  console.log('\n📋 步骤 3: 研究员模式');
  const mode3 = autoDetectMode('锂电池产业链竞争格局分析');
  assert(mode3 === 'researcher', `应识别为 researcher，实际：${mode3}`);
  scenarioResult.tests.push({ name: '研究员识别', status: '✅' });
  console.log('   ✅ 识别为：researcher');
  
  console.log('\n📋 步骤 4: 提示词构建');
  const prompt = buildPrompt('测试主题', 'trader');
  assert(prompt.includes('【调研目标】'), '应包含调研目标');
  assert(prompt.includes('【信息搜集与整合框架】'), '应包含框架');
  scenarioResult.tests.push({ name: '提示词构建', status: '✅' });
  console.log('   ✅ 提示词构建成功');
}

// ========== 执行所有测试 ==========
async function runAllTests() {
  console.log('\n');
  console.log('╔═══════════════════════════════════════════╗');
  console.log('║   Cue v1.0.4 真实集成测试                 ║');
  console.log('║   自主执行 · 极致细节验证                 ║');
  console.log('╚═══════════════════════════════════════════╝');
  console.log(`\n测试用户：${TEST_CHAT_ID}`);
  console.log(`开始时间：${new Date().toLocaleString('zh-CN')}`);
  
  // 执行所有场景
  await testScenario('完整研究流程', testResearchFlow);
  await testScenario('监控功能', testMonitorFlow);
  await testScenario('智能触发评估', testSmartTrigger);
  await testScenario('通知队列', testNotificationQueue);
  await testScenario('自动角色匹配', testAutoMode);
  
  // 生成报告
  const totalDuration = Date.now() - results.startTime;
  const successRate = results.scenarios.length > 0 
    ? ((results.passed / (results.passed + results.failed)) * 100).toFixed(1)
    : 0;
  
  console.log('\n');
  console.log('╔═══════════════════════════════════════════╗');
  console.log('║           测试总结报告                    ║');
  console.log('╚═══════════════════════════════════════════╝');
  console.log(`\n📊 场景统计:`);
  console.log(`   ✅ 通过：${results.passed}`);
  console.log(`   ❌ 失败：${results.failed}`);
  console.log(`   📈 成功率：${successRate}%`);
  console.log(`   ⏱️  总耗时：${(totalDuration / 1000).toFixed(1)}秒`);
  
  console.log(`\n📋 详细结果:`);
  results.scenarios.forEach((s, i) => {
    console.log(`   ${i + 1}. ${s.name}: ${s.status} (${s.duration}ms)`);
    if (s.error) {
      console.log(`      错误：${s.error}`);
    }
  });
  
  // 保存测试报告
  const report = {
    timestamp: new Date().toISOString(),
    testChatId: TEST_CHAT_ID,
    totalDuration,
    successRate,
    scenarios: results.scenarios
  };
  
  console.log(`\n✅ 集成测试完成！`);
  
  if (results.failed === 0) {
    console.log('\n🎉 所有测试通过！v1.0.4 功能完备，可以发布！');
    process.exit(0);
  } else {
    console.log('\n⚠️  部分测试失败，请检查实现。');
    process.exit(1);
  }
}

runAllTests().catch(error => {
  console.error('\n❌ 测试运行失败:', error);
  process.exit(1);
});
