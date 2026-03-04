/**
 * 后台执行管理器
 * 管理研究任务的后台运行、进度推送和完成检测
 */

import { spawn } from 'child_process';
import { createLogger } from './logger.js';
import { createTaskManager } from './taskManager.js';
import { sendProgressNotification, sendResearchCompleteNotification, sendMonitorSuggestionNotification } from '../notifier/index.js';
import { getReportContent, extractReportInsights, generateMonitorSuggestions } from '../api/cuecueClient.js';

const logger = createLogger('BackgroundExecutor');

// 存储正在运行的任务
const runningTasks = new Map();

/**
 * 启动后台研究任务
 * @param {Object} options
 * @param {string} options.taskId - 任务 ID
 * @param {string} options.topic - 研究主题
 * @param {string} options.mode - 研究模式
 * @param {string} options.chatId - 聊天 ID
 * @param {string} options.apiKey - API Key
 * @returns {Promise<Object>}
 */
export async function startBackgroundResearch({
  taskId,
  topic,
  mode,
  chatId,
  apiKey
}) {
  try {
    await logger.info(`Starting background research: ${taskId}`);
    
    const taskManager = createTaskManager(chatId);
    
    // 启动研究进程
    const researchProcess = spawn('node', [
      'src/cron/research-worker.js',
      taskId,
      topic,
      mode,
      chatId,
      apiKey
    ], {
      detached: true,
      stdio: 'ignore'
    });
    
    // 保存进程信息
    runningTasks.set(taskId, {
      pid: researchProcess.pid,
      startTime: Date.now(),
      chatId,
      topic
    });
    
    // 保存 PID 到任务文件
    await taskManager.updateTask(taskId, {
      pid: researchProcess.pid,
      status: 'running'
    });
    
    // 启动进度推送定时器
    startProgressNotifier(taskId, chatId, topic);
    
    // 启动完成检测（传递 apiKey 以便获取报告）
    startCompletionWatcher(taskId, chatId, topic, researchProcess, apiKey);
    
    await logger.info(`Background research started: ${taskId} (PID: ${researchProcess.pid})`);
    
    return {
      taskId,
      pid: researchProcess.pid,
      status: 'started'
    };
  } catch (error) {
    await logger.error(`Failed to start background research: ${taskId}`, error);
    throw error;
  }
}

/**
 * 启动进度推送定时器
 * @param {string} taskId - 任务 ID
 * @param {string} chatId - 聊天 ID
 * @param {string} topic - 研究主题
 */
function startProgressNotifier(taskId, chatId, topic) {
  const startTime = Date.now();
  
  // 每5分钟推送一次进度
  const intervalId = setInterval(async () => {
    try {
      // 检查任务是否还在运行
      if (!runningTasks.has(taskId)) {
        clearInterval(intervalId);
        return;
      }
      
      const elapsedMinutes = Math.round((Date.now() - startTime) / (1000 * 60));
      
      // 超过60分钟自动停止
      if (elapsedMinutes >= 60) {
        clearInterval(intervalId);
        return;
      }
      
      // 发送进度通知
      await sendProgressNotification({
        chatId,
        taskId,
        topic,
        progress: getStageDescription(elapsedMinutes),
        elapsedMinutes
      });
      
      await logger.info(`Progress notification sent: ${taskId} (${elapsedMinutes}min)`);
    } catch (error) {
      await logger.error(`Progress notification failed: ${taskId}`, error);
    }
  }, 5 * 60 * 1000); // 5分钟
}

/**
 * 启动完成检测
 * @param {string} taskId - 任务 ID
 * @param {string} chatId - 聊天 ID
 * @param {string} topic - 研究主题
 * @param {Object} process - 子进程
 * @param {string} apiKey - API Key
 */
function startCompletionWatcher(taskId, chatId, topic, process, apiKey) {
  const startTime = Date.now();
  const timeoutMs = 60 * 60 * 1000; // 60分钟超时
  
  process.on('exit', async (code) => {
    try {
      const elapsedMinutes = Math.round((Date.now() - startTime) / (1000 * 60));
      const taskManager = createTaskManager(chatId);
      
      runningTasks.delete(taskId);
      
      if (code === 0) {
        // 成功完成 - 获取报告内容
        try {
          const apiKey = process.env.CUECUE_API_KEY;
          const report = await getReportContent(conversationId, apiKey);
          const insights = extractReportInsights(report);
          const monitorSuggestions = generateMonitorSuggestions(insights, topic);
          
          // 保存报告内容到任务
          await taskManager.completeTask(taskId, {
            conversation_id: conversationId,
            report_url: `https://cuecue.cn/c/${conversationId}`,
            summary: insights.summary,
            key_points: insights.keyPoints,
            monitor_suggestions: monitorSuggestions
          });
          
          // 发送完成通知（带监控建议）
          await sendResearchCompleteNotification({
            chatId,
            taskId,
            topic,
            reportUrl: `https://cuecue.cn/c/${conversationId}`,
            duration: elapsedMinutes,
            monitorSuggestions: monitorSuggestions.map(s => s.title)
          });
          
          // 发送监控建议通知
          if (monitorSuggestions.length > 0) {
            await sendMonitorSuggestionNotification({
              chatId,
              taskId,
              topic,
              suggestions: monitorSuggestions
            });
          }
          
          await logger.info(`Research completed with report: ${taskId}`);
        } catch (reportError) {
          // 如果获取报告失败，仍然标记完成
          await logger.error(`Failed to get report content: ${taskId}`, reportError);
          await taskManager.completeTask(taskId, {
            conversation_id: conversationId,
            report_url: `https://cuecue.cn/c/${conversationId}`
          });
          await sendResearchCompleteNotification({
            chatId,
            taskId,
            topic,
            reportUrl: `https://cuecue.cn/c/${conversationId}`,
            duration: elapsedMinutes
          });
        }
      } else {
        // 失败
        await taskManager.failTask(taskId, `Process exited with code ${code}`);
        await logger.error(`Research failed: ${taskId} (code: ${code})`);
      }
    } catch (error) {
      await logger.error(`Completion handling failed: ${taskId}`, error);
    }
  });
  
  // 超时检测
  setTimeout(async () => {
    if (runningTasks.has(taskId)) {
      try {
        process.kill();
        runningTasks.delete(taskId);
        
        const taskManager = createTaskManager(chatId);
        await taskManager.timeoutTask(taskId);
        
        await logger.warn(`Research timeout: ${taskId}`);
      } catch (error) {
        await logger.error(`Timeout handling failed: ${taskId}`, error);
      }
    }
  }, timeoutMs);
}

/**
 * 获取阶段描述
 * @param {number} elapsedMinutes - 已耗时（分钟）
 * @returns {string}
 */
function getStageDescription(elapsedMinutes) {
  if (elapsedMinutes < 10) {
    return '全网信息搜集与初步筛选';
  } else if (elapsedMinutes < 30) {
    return '多源交叉验证与事实核查';
  } else if (elapsedMinutes < 50) {
    return '深度分析与逻辑推理';
  } else {
    return '报告生成与质量检查';
  }
}

/**
 * 检查任务是否正在运行
 * @param {string} taskId - 任务 ID
 * @returns {boolean}
 */
export function isTaskRunning(taskId) {
  return runningTasks.has(taskId);
}

/**
 * 获取运行中的任务列表
 * @returns {Array}
 */
export function getRunningTasks() {
  return Array.from(runningTasks.entries()).map(([taskId, info]) => ({
    taskId,
    ...info
  }));
}
