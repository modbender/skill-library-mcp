/**
 * 监控守护进程
 * 复用 OpenClaw 的 cron 机制或内部调度
 */

import cron from 'node-cron';
import { createLogger } from '../core/logger.js';
import { createMonitorManager } from '../core/monitorManager.js';
import { sendMonitorTriggerNotification } from '../notifier/index.js';
import { evaluateSmartTrigger } from '../utils/smartTrigger.js';
import { execSync } from 'child_process';

const logger = createLogger('MonitorDaemon');

/**
 * 检查单个监控项
 * @param {Object} monitor - 监控项
 * @param {string} chatId - 聊天 ID
 */
async function checkMonitor(monitor, chatId) {
  try {
    await logger.info(`Checking monitor: ${monitor.monitor_id}`);
    
    // 获取触发条件
    const trigger = monitor.semantic_trigger || monitor.trigger;
    if (!trigger) {
      await logger.warn(`Monitor ${monitor.monitor_id} has no trigger condition`);
      return;
    }
    
    // 执行搜索检查（使用 Tavily 或 QVeris）
    const searchResult = await searchForTrigger(trigger, monitor);
    
    // 使用智能触发评估
    const evaluation = await evaluateSmartTrigger(
      trigger,
      searchResult.content || JSON.stringify(searchResult),
      { useLLM: true, threshold: 0.6 }
    );
    
    if (evaluation.shouldTrigger) {
      await logger.info(`Monitor triggered: ${monitor.monitor_id} (confidence: ${evaluation.confidence})`);
      
      // 发送通知
      await sendMonitorTriggerNotification({
        chatId,
        monitorId: monitor.monitor_id,
        monitorTitle: monitor.title,
        message: `${evaluation.reason}\n\n相关内容：${searchResult.content?.slice(0, 200) || '详见报告'}...`,
        category: monitor.category || 'Data'
      });
      
      // 更新监控触发记录
      const monitorManager = createMonitorManager(chatId);
      await monitorManager.updateMonitor(monitor.monitor_id, {
        last_triggered_at: new Date().toISOString(),
        trigger_count: (monitor.trigger_count || 0) + 1
      });
    }
  } catch (error) {
    await logger.error(`Failed to check monitor ${monitor.monitor_id}`, error);
  }
}

/**
 * 搜索触发相关内容
 * @param {string} trigger - 触发条件描述
 * @param {Object} monitor - 监控项
 * @returns {Promise<Object>}
 */
async function searchForTrigger(trigger, monitor) {
  try {
    let searchResult;
    
    // 方法1: 使用 Tavily 搜索
    if (process.env.TAVILY_API_KEY) {
      searchResult = await searchWithTavily(trigger);
    }
    // 方法2: 使用 QVeris
    else if (process.env.QVERIS_API_KEY) {
      searchResult = await searchWithQVeris(trigger);
    }
    // 方法3: 降级到空结果
    else {
      return { content: '', results: [] };
    }
    
    // 合并搜索结果为文本
    const content = searchResult.results
      ?.map(r => `${r.title} ${r.content}`)
      .join(' ') || '';
    
    return {
      content,
      results: searchResult.results || []
    };
  } catch (error) {
    await logger.error('Trigger search failed', error);
    return { content: '', results: [] };
  }
}

/**
 * 使用 Tavily 搜索
 * @param {string} query - 查询
 * @returns {Promise<Object>}
 */
async function searchWithTavily(query) {
  const response = await fetch('https://api.tavily.com/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.TAVILY_API_KEY}`
    },
    body: JSON.stringify({
      query,
      search_depth: 'basic',
      max_results: 5
    })
  });
  
  return await response.json();
}

/**
 * 使用 QVeris 搜索
 * @param {string} query - 查询
 * @returns {Promise<Object>}
 */
async function searchWithQVeris(query) {
  const response = await fetch('https://api.qveris.ai/v1/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.QVERIS_API_KEY}`
    },
    body: JSON.stringify({
      query,
      max_results: 5
    })
  });
  
  return await response.json();
}

/**
 * 分析搜索结果
 * @param {Object} result - 搜索结果
 * @param {string} trigger - 触发条件
 * @returns {boolean}
 */
function analyzeSearchResult(result, trigger) {
  // 简化实现：检查结果中是否包含关键词
  const results = result.results || [];
  const triggerKeywords = trigger.toLowerCase().split(/\s+/);
  
  for (const item of results) {
    const content = (item.content || item.title || '').toLowerCase();
    const matchCount = triggerKeywords.filter(kw => content.includes(kw)).length;
    
    // 如果匹配超过一半关键词，认为触发
    if (matchCount >= triggerKeywords.length / 2) {
      return true;
    }
  }
  
  return false;
}

/**
 * 运行监控检查（单次）
 * @param {string} chatId - 聊天 ID
 */
export async function runMonitorCheck(chatId) {
  await logger.info(`Running monitor check for ${chatId}`);
  
  const monitorManager = createMonitorManager(chatId);
  const monitors = await monitorManager.getActiveMonitors();
  
  if (monitors.length === 0) {
    await logger.info('No active monitors found');
    return;
  }
  
  await logger.info(`Found ${monitors.length} active monitors`);
  
  for (const monitor of monitors) {
    await checkMonitor(monitor, chatId);
  }
  
  await logger.info('Monitor check completed');
}

/**
 * 启动监控守护进程（使用 node-cron）
 * @param {string} chatId - 聊天 ID
 * @returns {Object} cron job
 */
export function startMonitorDaemon(chatId) {
  await logger.info(`Starting monitor daemon for ${chatId}`);
  
  // 每30分钟执行一次
  const job = cron.schedule('*/30 * * * *', async () => {
    await runMonitorCheck(chatId);
  });
  
  return job;
}

/**
 * 使用 OpenClaw 外部 cron（备用方案）
 * @param {string} chatId - 聊天 ID
 */
export async function setupOpenClawCron(chatId) {
  try {
    // 检查 OpenClaw 是否支持 cron
    const cronCheck = execSync('openclaw cron list 2>/dev/null || echo "not supported"', { 
      encoding: 'utf-8' 
    });
    
    if (cronCheck.includes('not supported')) {
      await logger.info('OpenClaw cron not supported, using internal node-cron');
      return startMonitorDaemon(chatId);
    }
    
    // 注册 OpenClaw cron job
    const cronCommand = `cd ${process.cwd()} && node src/cron/run-check.js ${chatId}`;
    execSync(`openclaw cron add --name "cue-monitor-${chatId}" --schedule "*/30 * * * *" --command "${cronCommand}"`);
    
    await logger.info(`OpenClaw cron job registered for ${chatId}`);
    return null;
  } catch (error) {
    await logger.error('Failed to setup OpenClaw cron', error);
    return startMonitorDaemon(chatId);
  }
}
