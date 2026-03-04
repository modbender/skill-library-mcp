#!/usr/bin/env node

/**
 * Terminal Killer - OpenClaw Skill Entry Point
 * 
 * This is the main entry point for the terminal-killer skill.
 * It analyzes user input and either executes commands directly or passes to LLM.
 * 
 * Usage: This skill is triggered automatically by OpenClaw when user input
 *        matches command patterns.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Import detection logic
const { detectCommand } = require('./detect-command');
const { handleInteractive, isInteractiveCommand } = require('./interactive');

/**
 * Execute command with user's full environment loaded
 */
function executeCommand(command) {
  const homeDir = os.homedir();
  const shell = process.env.SHELL || '/bin/zsh';
  let initCmd = '';
  
  // Detect and source appropriate shell init file
  if (shell.includes('zsh')) {
    if (fs.existsSync(path.join(homeDir, '.zshrc'))) {
      initCmd = 'source ~/.zshrc 2>/dev/null; ';
    } else if (fs.existsSync(path.join(homeDir, '.zprofile'))) {
      initCmd = 'source ~/.zprofile 2>/dev/null; ';
    }
  } else if (shell.includes('bash')) {
    if (fs.existsSync(path.join(homeDir, '.bash_profile'))) {
      initCmd = 'source ~/.bash_profile 2>/dev/null; ';
    } else if (fs.existsSync(path.join(homeDir, '.bashrc'))) {
      initCmd = 'source ~/.bashrc 2>/dev/null; ';
    }
  }
  
  // Fallback: try common init files
  if (!initCmd) {
    const initFiles = ['.zshrc', '.bash_profile', '.bashrc', '.profile'];
    for (const file of initFiles) {
      if (fs.existsSync(path.join(homeDir, file))) {
        initCmd = `source ~/${file} 2>/dev/null; `;
        break;
      }
    }
  }
  
  const fullCommand = initCmd + command;
  
  try {
    const output = execSync(fullCommand, {
      encoding: 'utf8',
      timeout: 30000,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: process.env
    });
    
    return {
      success: true,
      output: output,
      command: command,
      isLong: output.length > 2000  // Mark as long output (>2KB)
    };
  } catch (error) {
    return {
      success: false,
      error: error.stderr || error.message,
      code: error.status || error.code,
      command: command
    };
  }
}

/**
 * Check if input should trigger command execution
 * Returns true if confidence is high enough (score >= 5)
 */
function shouldExecute(input) {
  const result = detectCommand(input);
  return result.decision === 'EXECUTE';
}

/**
 * Main entry point
 * 
 * @param {string} input - User input text
 * @returns {object} - Result object with decision and output
 */
function handleInput(input) {
  // First check if it's an interactive command
  if (isInteractiveCommand(input)) {
    return {
      action: 'interactive',
      message: `🔧 检测到交互式命令，正在打开新终端窗口...`,
      command: input
    };
  }
  
  const detection = detectCommand(input);
  
  // If decision is EXECUTE, run the command
  if (detection.decision === 'EXECUTE') {
    const execution = executeCommand(input);
    
    // Check if output is too long
    if (execution.success && execution.isLong) {
      const previewLength = 200;  // Show first 200 characters
      const preview = execution.output.substring(0, previewLength);
      const omittedBytes = execution.output.length - previewLength;
      
      return {
        action: 'long_output',
        detection: detection,
        execution: execution,
        command: input,  // Save original command
        preview: preview + '\n\n... (内容过长，已省略 ' + omittedBytes + ' 字节)',
        message: `📝 命令执行完成，但输出较长（${execution.output.length} 字节）\n\n预览：\n\`\`\`\n${preview}\n\`\`\`\n\n要在**新 Terminal 窗口**中查看完整输出吗？回复 **是** 或 **yes**`
      };
    }
    
    return {
      action: 'execute',
      detection: detection,
      execution: execution
    };
  }
  
  // If decision is ASK, prompt for confirmation
  if (detection.decision === 'ASK') {
    return {
      action: 'ask',
      detection: detection,
      message: `这看起来像是一个命令：\`${input}\`\n\n${detection.dangerous ? '⚠️ **危险命令！** ' : ''}确认要执行吗？`
    };
  }
  
  // Otherwise, let LLM handle it
  return {
    action: 'llm',
    detection: detection,
    message: 'Not a command - let LLM handle'
  };
}

// CLI execution for testing
if (require.main === module) {
  const input = process.argv.slice(2).join(' ');
  
  if (!input) {
    console.error('Usage: node index.js "<user input>"');
    process.exit(1);
  }
  
  console.error('🔍 Detecting...');
  const result = handleInput(input);
  
  console.error('\n📊 Decision:', result.action.toUpperCase());
  if (result.detection) {
    console.error('📈 Score:', result.detection.score);
  }
  console.error('');
  
  if (result.action === 'execute') {
    if (result.execution.success) {
      // Output raw text without any modification
      process.stdout.write(result.execution.output);
    } else {
      console.error(`❌ Error: ${result.execution.error}`);
      process.exit(1);
    }
  } else if (result.action === 'long_output') {
    // Show preview and ask to open in new terminal
    console.log(result.message);
  } else if (result.action === 'open_terminal') {
    // Open in new terminal window
    const { openInteractiveShell } = require('./interactive');
    console.error('🪟 正在打开新 Terminal 窗口显示完整输出...');
    openInteractiveShell(result.command);
  } else if (result.action === 'interactive') {
    // Open interactive shell
    const { openInteractiveShell } = require('./interactive');
    openInteractiveShell(result.command);
  } else if (result.action === 'ask') {
    console.log(result.message);
  } else {
    console.log('→ Pass to LLM for handling');
  }
}

/**
 * Handle user response to long output prompt
 */
function handleLongOutputResponse(originalCommand, userResponse) {
  const positiveResponses = ['是', 'yes', 'y', '好的', 'ok', 'open', '打开'];
  const shouldOpen = positiveResponses.some(r => userResponse.toLowerCase().includes(r));
  
  if (shouldOpen) {
    // Open in new terminal with the command
    const { openInteractiveShell } = require('./interactive');
    console.log('🪟 正在新 Terminal 窗口中执行命令...');
    openInteractiveShell(originalCommand);
    return { action: 'open_terminal', command: originalCommand };
  } else {
    return { action: 'declined', message: '已取消。如需查看完整输出，可以手动执行命令或输出到文件。' };
  }
}

module.exports = { handleInput, shouldExecute, executeCommand, detectCommand, handleLongOutputResponse };
