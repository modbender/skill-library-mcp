#!/usr/bin/env node

/**
 * Slash Command Dashboard - 斜杠命令汉化和全览系统
 * 
 * 显示命令列表、搜索命令、执行命令
 * 
 * @version 1.0.0
 * @author Neo（宇宙神经系统）
 */

const { getAllCommands, searchCommands, getCommandBySlug } = require('./commands.js');
const {
  generateCommandsDisplay,
  generateAskText,
  getSafetyIcon,
  getSourceIcon,
  needsConfirm,
  generateConfirmMessage
} = require('./safety.js');

/**
 * 显示命令列表
 */
async function showCommands(showHidden = false) {
  const commands = getAllCommands(showHidden);
  const display = generateCommandsDisplay(commands, showHidden);
  
  let output = `\n`;
  output += `┌─────────────────────────────────────────────────┐\n`;
  output += `│  📋 斜杠命令全览                         🔍     │\n`;
  output += `├─────────────────────────────────────────────────┤\n`;
  
  // OpenClaw 原生技能
  if (display.native.length > 0) {
    output += `│                                                 │\n`;
    output += `│  🏷️ OpenClaw 原生技能                            │\n`;
    output += `│                                                 │\n`;
    
    display.native.forEach((cmd, index) => {
      output += `│  ${cmd.safety} ${cmd.command.padEnd(28)} │\n`;
      output += `│     ${cmd.description.substring(0, 30).padEnd(30)}│\n`;
      output += `│     [执行] [详情]${' '.repeat(12)}│\n`;
      
      if (index < display.native.length - 1) {
        output += `│                                                 │\n`;
      }
    });
    
    output += `│                                                 │\n`;
  }
  
  // 我们开发的技能
  if (display.ours.length > 0) {
    output += `├─────────────────────────────────────────────────┤\n`;
    output += `│  🛠️ 我们开发的技能                               │\n`;
    output += `│                                                 │\n`;
    
    display.ours.forEach((cmd, index) => {
      output += `│  ${cmd.safety} ${cmd.command.padEnd(28)} │\n`;
      output += `│     ${cmd.description.substring(0, 30).padEnd(30)}│\n`;
      output += `│     [执行] [详情]${' '.repeat(12)}│\n`;
      
      if (index < display.ours.length - 1) {
        output += `│                                                 │\n`;
      }
    });
    
    output += `│                                                 │\n`;
  }
  
  // 第三方技能
  if (display.thirdParty.length > 0) {
    output += `├─────────────────────────────────────────────────┤\n`;
    output += `│  🧩 第三方技能                                    │\n`;
    output += `│                                                 │\n`;
    
    display.thirdParty.forEach((cmd, index) => {
      output += `│  ${cmd.safety} ${cmd.command.padEnd(28)} │\n`;
      output += `│     ${cmd.description.substring(0, 30).padEnd(30)}│\n`;
      output += `│     [执行] [详情]${' '.repeat(12)}│\n`;
      
      if (index < display.thirdParty.length - 1) {
        output += `│                                                 │\n`;
      }
    });
    
    output += `│                                                 │\n`;
  }
  
  // 说明
  output += `├─────────────────────────────────────────────────┤\n`;
  output += `│  ${generateAskText().substring(1, 54)}│\n`;
  output += `│  ${generateAskText().substring(55, 108).padEnd(53)}│\n`;
  output += `└─────────────────────────────────────────────────┘\n`;
  
  return output;
}

/**
 * 显示隐藏命令
 */
async function showHiddenCommands() {
  const hidden = getAllCommands(true).filter(cmd => cmd.safety === 'hidden');
  
  if (hidden.length === 0) {
    return '没有隐藏命令。';
  }
  
  let output = `\n`;
  output += `⚠️ 高风险命令，请谨慎使用\n\n`;
  output += `┌─────────────────────────────────────────────────┐\n`;
  output += `│  🔴 隐藏命令（高风险）                          │\n`;
  output += `├─────────────────────────────────────────────────┤\n`;
  
  hidden.forEach((cmd, index) => {
    output += `│                                                 │\n`;
    output += `│  🔴 ${cmd.command.padEnd(46)}│\n`;
    output += `│     ${cmd.description.substring(0, 30).padEnd(30)}│\n`;
    output += `│     ${cmd.warning || '⚠️ 高风险操作'}${' '.repeat(Math.max(0, 20 - (cmd.warning || '').length))}│\n`;
    output += `│     [执行]（需二次确认）${' '.repeat(24)}│\n`;
    
    if (index < hidden.length - 1) {
      output += `│                                                 │\n`;
    }
  });
  
  output += `│                                                 │\n`;
  output += `└─────────────────────────────────────────────────┘\n`;
  output += `\n确定要执行吗？这些操作不可逆。（回复"确定"或"取消"）\n`;
  
  return output;
}

/**
 * 搜索命令
 */
async function searchCommandsDisplay(query) {
  const results = searchCommands(query);
  
  if (results.length === 0) {
    return `没有找到与"${query}"相关的命令。`;
  }
  
  let output = `\n`;
  output += `找到 ${results.length} 个相关命令：\n\n`;
  
  results.forEach((cmd, index) => {
    const safetyIcon = getSafetyIcon(cmd.safety);
    const sourceIcon = getSourceIcon(cmd.source);
    
    output += `${safetyIcon.emoji} ${cmd.command}\n`;
    output += `   ${cmd.description}\n`;
    output += `   来源：${sourceIcon.emoji} ${sourceIcon.text}\n`;
    output += `   [执行] [详情]\n`;
    
    if (index < results.length - 1) {
      output += `\n`;
    }
  });
  
  return output;
}

/**
 * 导出命令列表为 Markdown
 */
async function exportToMarkdown() {
  const commands = getAllCommands(false);
  
  let markdown = `# 斜杠命令全览\n\n`;
  markdown += `**生成时间：** ${new Date().toLocaleString('zh-CN')}\n\n`;
  markdown += `---\n\n`;
  
  // 按来源分组
  const display = generateCommandsDisplay(commands);
  
  markdown += `## 🏷️ OpenClaw 原生技能\n\n`;
  display.native.forEach(cmd => {
    markdown += `### ${cmd.command}\n\n`;
    markdown += `- **说明：** ${cmd.description}\n`;
    markdown += `- **安全级别：** ${cmd.safety}\n`;
    markdown += `- **操作：** [执行] [详情]\n\n`;
  });
  
  markdown += `---\n\n`;
  markdown += `## 🛠️ 我们开发的技能\n\n`;
  display.ours.forEach(cmd => {
    markdown += `### ${cmd.command}\n\n`;
    markdown += `- **说明：** ${cmd.description}\n`;
    markdown += `- **安全级别：** ${cmd.safety}\n`;
    markdown += `- **操作：** [执行] [详情]\n\n`;
  });
  
  markdown += `---\n\n`;
  markdown += `## 🧩 第三方技能\n\n`;
  display.thirdParty.forEach(cmd => {
    markdown += `### ${cmd.command}\n\n`;
    markdown += `- **说明：** ${cmd.description}\n`;
    markdown += `- **安全级别：** ${cmd.safety}\n`;
    markdown += `- **操作：** [执行] [详情]\n\n`;
  });
  
  return markdown;
}

// 导出函数
module.exports = {
  showCommands,
  showHiddenCommands,
  searchCommandsDisplay,
  exportToMarkdown
};

// CLI 入口
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];
  const param = args[1];
  
  switch (command) {
    case 'show':
      showCommands(command === 'show-hidden').then(console.log);
      break;
    case 'show-hidden':
      showHiddenCommands().then(console.log);
      break;
    case 'search':
      if (param) {
        searchCommandsDisplay(param).then(console.log);
      } else {
        console.log('用法：node dashboard.js search <关键词>');
      }
      break;
    case 'export':
      exportToMarkdown().then(console.log);
      break;
    default:
      showCommands().then(console.log);
  }
}
