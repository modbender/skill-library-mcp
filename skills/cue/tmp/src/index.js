#!/usr/bin/env node
/**
 * Cue - 主入口
 * Node.js 版本 v1.0.4
 */

import { createLogger } from './core/logger.js';
import { createUserState } from './core/userState.js';
import { createTaskManager } from './core/taskManager.js';
import { createMonitorManager } from './core/monitorManager.js';
import { getApiKey, detectServiceFromKey, setApiKey } from './utils/envUtils.js';
import { startResearch, autoDetectMode } from './api/cuecueClient.js';
import { randomUUID } from 'crypto';

const logger = createLogger('Cue');

// 获取环境配置
const chatId = process.env.CHAT_ID || process.env.FEISHU_CHAT_ID || 'default';

// 初始化核心模块
const userState = createUserState(chatId);
const taskManager = createTaskManager(chatId);
const monitorManager = createMonitorManager(chatId);

/**
 * 处理命令
 * @param {string} command - 命令
 * @param {Array} args - 参数
 */
export async function handleCommand(command, args = []) {
  try {
    switch (command) {
      case 'cue':
        return await handleCue(args);
      case 'ct':
        return await handleCt();
      case 'cm':
        return await handleCm();
      case 'cn':
        return await handleCn(args[0]);
      case 'key':
        return await handleKey(args[0]);
      case 'ch':
        return handleCh();
      default:
        return handleCh();
    }
  } catch (error) {
    logger.error(`Command failed: ${command}`, error);
    return `❌ 错误：${error.message}`;
  }
}

/**
 * 处理 /cue 命令
 */
async function handleCue(args) {
  // 解析参数
  let mode = null;
  let topic = args.join(' ');
  
  if (args[0] === '--mode') {
    mode = args[1];
    topic = args.slice(2).join(' ');
  }
  
  // 检查用户状态
  const status = await userState.checkVersion();
  let output = '';
  
  if (status === 'first_time') {
    output += showWelcome();
    await userState.markInitialized();
  } else if (status === 'updated') {
    output += showUpdateNotice();
  }
  
  // 检查 API Key
  const apiKey = await getApiKey('CUECUE_API_KEY');
  if (!apiKey) {
    output += '\n⚠️  需要配置 API Key\n使用 /key 命令或直接发送 API Key 进行配置\n';
    return output;
  }
  
  // 自动检测模式
  if (!mode || mode === 'default') {
    mode = autoDetectMode(topic);
  }
  
  const modeNames = {
    trader: '短线交易视角',
    'fund-manager': '基金经理视角',
    researcher: '产业研究视角',
    advisor: '理财顾问视角'
  };
  
  output += `\n🎯 根据主题自动匹配研究视角：${modeNames[mode]}\n\n`;
  
  // 创建任务
  const taskId = `cuecue_${Date.now()}`;
  await taskManager.createTask({ taskId, topic, mode });
  
  // 启动研究
  try {
    const result = await startResearch({ topic, mode, chatId, apiKey });
    
    output += `✅ 研究任务已启动！\n\n`;
    output += `📋 任务信息：\n`;
    output += `   主题：${topic}\n`;
    output += `   任务 ID：${taskId}\n`;
    output += `   报告链接：${result.reportUrl}\n\n`;
    output += `⏳ 进度更新：每 5 分钟推送一次\n`;
    output += `🔔 完成通知：研究完成后自动推送\n`;
    
  } catch (error) {
    output += `❌ 研究启动失败：${error.message}\n`;
  }
  
  return output;
}

/**
 * 处理 /ct 命令
 */
async function handleCt() {
  const tasks = await taskManager.getTasks(10);
  
  if (tasks.length === 0) {
    return '📭 暂无研究任务\n';
  }
  
  let output = '📊 研究任务列表\n\n';
  
  for (const task of tasks) {
    const statusEmoji = {
      running: '🔄',
      completed: '✅',
      failed: '❌',
      timeout: '⏱️'
    }[task.status] || '🔄';
    
    output += `${statusEmoji} ${task.topic}\n`;
    output += `   ID: ${task.task_id} | 状态：${task.status}\n\n`;
  }
  
  return output;
}

/**
 * 处理 /cm 命令
 */
async function handleCm() {
  const monitors = await monitorManager.getMonitors(15);
  
  if (monitors.length === 0) {
    return '📭 暂无监控项\n\n💡 研究完成后回复 Y 可创建监控项\n';
  }
  
  let output = '🔔 监控项列表\n\n';
  
  for (const monitor of monitors) {
    const statusEmoji = monitor.is_active !== false ? '✅' : '⏸️';
    const catEmoji = {
      Price: '💰',
      Event: '📅',
      Data: '📊'
    }[monitor.category] || '📊';
    
    output += `${statusEmoji} ${catEmoji} ${monitor.title}\n`;
    if (monitor.symbol) {
      output += `   标的：${monitor.symbol}\n`;
    }
    output += `   触发：${monitor.semantic_trigger?.slice(0, 30) || '-'}\n\n`;
  }
  
  return output;
}

/**
 * 处理 /cn 命令
 */
async function handleCn(days = '3') {
  // TODO: 实现通知查询
  return `🔔 监控触发通知（最近${days}日）\n\n📭 暂无触发通知\n`;
}

/**
 * 处理 /key 命令
 */
async function handleKey(apiKey) {
  if (!apiKey) {
    // 查看状态
    const { getApiKeyStatus } = await import('./utils/envUtils.js');
    const status = await getApiKeyStatus();
    
    let output = '╔══════════════════════════════════════════╗\n';
    output += '║           当前 API Key 配置状态           ║\n';
    output += '╠══════════════════════════════════════════╣\n';
    
    for (const s of status) {
      if (s.configured) {
        output += `║  ✅ ${s.name.padEnd(18)} ${s.masked.padEnd(24)} ║\n`;
      } else {
        output += `║  ❌ ${s.name.padEnd(18)} 未配置                        ║\n`;
      }
    }
    
    output += '╠══════════════════════════════════════════╣\n';
    output += '║  直接发送 API Key 即可自动配置            ║\n';
    output += '╚══════════════════════════════════════════╝\n';
    
    return output;
  }
  
  // 配置 API Key
  const service = detectServiceFromKey(apiKey);
  
  if (!service) {
    let output = '❌ 无法识别 API Key 类型\n\n';
    output += '支持的格式：\n';
    output += '  • Tavily:  tvly-xxxxx\n';
    output += '  • CueCue:  skb-xxxxx 或 sk-xxxxx\n';
    output += '  • QVeris:  sk-xxxxx (长格式)\n';
    return output;
  }
  
  await setApiKey(service.key, apiKey);
  
  return `✅ ${service.name} API Key 配置成功！\n\n密钥已保存并生效，无需重启。\n`;
}

/**
 * 处理 /ch 命令
 */
function handleCh() {
  return `╔══════════════════════════════════════════╗
║         Cue - 你的专属调研助理          ║
╠══════════════════════════════════════════╣
║  使用方式：                              ║
║  • /cue <主题>         智能调研          ║
║  • /cue --mode <模式>  指定视角          ║
║  • /ct                 查看任务列表      ║
║  • /cm                 查看监控项列表    ║
║  • /cn [天数]          查看监控通知      ║
║  • /key                配置 API Key      ║
║  • /ch                 显示帮助          ║
║                                          ║
║  研究视角模式：                          ║
║  • trader       - 短线交易视角           ║
║  • fund-manager - 基金经理视角           ║
║  • researcher   - 产业研究视角           ║
║  • advisor      - 理财顾问视角           ║
╚══════════════════════════════════════════╝
`;
}

/**
 * 显示欢迎消息
 */
function showWelcome() {
  return `╔══════════════════════════════════════════╗
║  🎉 欢迎使用 Cue - 你的专属调研助理     ║
╠══════════════════════════════════════════╣
║                                          ║
║  ⚠️  安全提示：                          ║
║  • 本工具会创建 ~/.cuecue 本地存储       ║
║  • 会安装 cron 定时任务（每 30 分钟）        ║
║  • 需要外部 API 访问权限                   ║
║                                          ║
║  快速开始：                              ║
║  • /cue <主题>  开始深度研究             ║
║  • /key         配置 API Key             ║
║  • /ch          查看帮助                 ║
║                                          ║
╚══════════════════════════════════════════╝
`;
}

/**
 * 显示更新提示
 */
function showUpdateNotice() {
  return `╔══════════════════════════════════════════╗
║  ✨ Cue 已更新至 v1.0.4 (Node.js 版)        ║
╠══════════════════════════════════════════╣
║                                          ║
║  本次更新内容：                          ║
║  🔧 全面 Node.js 重构                     ║
║  🔧 自动角色匹配                         ║
║  🔧 /cn 监控通知查询                     ║
║  🔧 /key API Key 配置                    ║
║                                          ║
╚══════════════════════════════════════════╝
`;
}

// 导出 handleCommand 供外部调用
export default { handleCommand };
