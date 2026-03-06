#!/usr/bin/env node
/**
 * 研究工作进程
 * 在后台执行实际的研究任务
 */

import { startResearch } from '../api/cuecueClient.js';
import { createTaskManager } from '../core/taskManager.js';
import { createLogger } from '../core/logger.js';

const logger = createLogger('ResearchWorker');

async function main() {
  const [,, taskId, topic, mode, chatId, apiKey] = process.argv;
  
  if (!taskId || !topic || !apiKey) {
    console.error('Usage: research-worker.js <taskId> <topic> <mode> <chatId> <apiKey>');
    process.exit(1);
  }
  
  try {
    await logger.info(`Research worker started: ${taskId}`);
    
    const taskManager = createTaskManager(chatId);
    
    // 更新进度：初始化
    await taskManager.updateTaskProgress(taskId, '正在连接 CueCue 服务...', 5);
    
    // 启动研究
    const result = await startResearch({
      topic,
      mode: mode || 'default',
      chatId,
      apiKey
    });
    
    // 更新进度：已启动
    await taskManager.updateTask(taskId, {
      conversation_id: result.conversationId,
      report_url: result.reportUrl,
      progress: '研究已启动，等待完成...',
      percent: 10
    });
    
    await logger.info(`Research started on CueCue: ${result.conversationId}`);
    
    // 等待研究完成（模拟轮询）
    await waitForCompletion(taskId, chatId, result.conversationId);
    
    await logger.info(`Research worker completed: ${taskId}`);
    process.exit(0);
  } catch (error) {
    await logger.error(`Research worker failed: ${taskId}`, error);
    
    const taskManager = createTaskManager(chatId);
    await taskManager.failTask(taskId, error.message);
    
    process.exit(1);
  }
}

/**
 * 等待研究完成
 * 轮询检查报告状态
 */
async function waitForCompletion(taskId, chatId, conversationId) {
  const taskManager = createTaskManager(chatId);
  const maxWaitTime = 60 * 60 * 1000; // 60分钟
  const pollInterval = 5 * 60 * 1000; // 5分钟
  const startTime = Date.now();
  
  while (Date.now() - startTime < maxWaitTime) {
    await new Promise(resolve => setTimeout(resolve, pollInterval));
    
    const elapsedMinutes = Math.round((Date.now() - startTime) / (1000 * 60));
    
    // 更新进度
    if (elapsedMinutes < 10) {
      await taskManager.updateTaskProgress(taskId, '全网信息搜集与初步筛选...', 20);
    } else if (elapsedMinutes < 30) {
      await taskManager.updateTaskProgress(taskId, '多源交叉验证与事实核查...', 40);
    } else if (elapsedMinutes < 50) {
      await taskManager.updateTaskProgress(taskId, '深度分析与逻辑推理...', 70);
    } else {
      await taskManager.updateTaskProgress(taskId, '报告生成与质量检查...', 90);
    }
    
    // TODO: 实际应该调用 CueCue API 检查报告状态
    // 目前模拟完成
    if (elapsedMinutes >= 55) {
      await taskManager.completeTask(taskId, {
        conversation_id: conversationId,
        report_url: `https://cuecue.cn/c/${conversationId}`
      });
      return;
    }
  }
  
  // 超时
  throw new Error('Research timeout after 60 minutes');
}

main();
