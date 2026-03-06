#!/usr/bin/env node

/**
 * Safety Logic - 安全分级逻辑
 * 
 * 提供安全级别判断、图标获取、确认提示等功能
 * 
 * @version 1.0.0
 * @author Neo（宇宙神经系统）
 */

const { SAFETY } = require('./commands.js');

/**
 * 安全级别配置
 */
const SAFETY_CONFIG = {
  [SAFETY.SAFE]: {
    emoji: '🟢',
    color: 'green',
    text: '安全',
    description: '无风险，可直接使用'
  },
  [SAFETY.WARNING]: {
    emoji: '🟡',
    color: 'yellow',
    text: '危险（需确认）',
    description: '需要二次确认'
  },
  [SAFETY.HIDDEN]: {
    emoji: '🔴',
    color: 'red',
    text: '隐藏（高风险）',
    description: '默认不显示，高风险'
  }
};

/**
 * 获取安全级别图标和文本
 */
function getSafetyIcon(safety) {
  const config = SAFETY_CONFIG[safety];
  if (!config) {
    return { emoji: '⚪', color: 'gray', text: '未知', description: '' };
  }
  return config;
}

/**
 * 获取来源标识
 */
function getSourceIcon(source) {
  const icons = {
    native: { emoji: '🏷️', text: 'OpenClaw 原生' },
    ours: { emoji: '🛠️', text: '我们开发的' },
    'third-party': { emoji: '🧩', text: '第三方' }
  };
  
  return icons[source] || { emoji: '❓', text: '未知' };
}

/**
 * 检查是否需要二次确认
 */
function needsConfirm(command) {
  return command?.confirm || false;
}

/**
 * 生成确认提示
 */
function generateConfirmMessage(command, params) {
  if (!command.confirm) {
    return null;
  }
  
  if (typeof command.confirmMessage === 'function') {
    return command.confirmMessage(params);
  }
  
  return command.confirmMessage || '确定要执行吗？';
}

/**
 * 检查命令是否可见（隐藏命令默认不显示）
 */
function isVisible(command, showHidden = false) {
  if (command.safety === SAFETY.HIDDEN) {
    return showHidden;
  }
  return true;
}

/**
 * 格式化命令显示
 */
function formatCommandDisplay(command) {
  const safetyIcon = getSafetyIcon(command.safety);
  const sourceIcon = getSourceIcon(command.source);
  
  return {
    command: command.command,
    description: command.description,
    safety: `${safetyIcon.emoji} ${safetyIcon.text}`,
    source: `${sourceIcon.emoji} ${sourceIcon.text}`,
    category: command.category,
    executeHint: command.executeHint,
    needsConfirm: needsConfirm(command),
    warning: command.warning
  };
}

/**
 * 生成命令列表显示
 */
function generateCommandsDisplay(commands, showHidden = false) {
  const display = {
    native: [],
    ours: [],
    thirdParty: [],
    hidden: []
  };
  
  commands.forEach(cmd => {
    if (!isVisible(cmd, showHidden)) {
      return;
    }
    
    const formatted = formatCommandDisplay(cmd);
    
    if (cmd.source === 'native') {
      display.native.push(formatted);
    } else if (cmd.source === 'ours') {
      display.ours.push(formatted);
    } else if (cmd.source === 'third-party') {
      display.thirdParty.push(formatted);
    }
    
    if (cmd.safety === SAFETY.HIDDEN) {
      display.hidden.push(formatted);
    }
  });
  
  return display;
}

/**
 * 生成分页询问文本
 */
function generateAskText() {
  return `
说明：🟢 安全  🟡 危险（需确认） 🔴 隐藏（默认不显示）

[查看隐藏命令] [导出列表] [搜索命令]`;
}

module.exports = {
  SAFETY_CONFIG,
  getSafetyIcon,
  getSourceIcon,
  needsConfirm,
  generateConfirmMessage,
  isVisible,
  formatCommandDisplay,
  generateCommandsDisplay,
  generateAskText
};

// 测试
if (require.main === module) {
  console.log('测试安全分级逻辑：');
  console.log('================');
  
  console.log('\n安全级别图标：');
  console.log('SAFE:', getSafetyIcon(SAFETY.SAFE));
  console.log('WARNING:', getSafetyIcon(SAFETY.WARNING));
  console.log('HIDDEN:', getSafetyIcon(SAFETY.HIDDEN));
  
  console.log('\n来源标识：');
  console.log('native:', getSourceIcon('native'));
  console.log('ours:', getSourceIcon('ours'));
  console.log('third-party:', getSourceIcon('third-party'));
}
