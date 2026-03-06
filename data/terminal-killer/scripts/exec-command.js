#!/usr/bin/env node

/**
 * Terminal Killer - Command Executor
 * 
 * Executes shell commands with user's full environment loaded.
 * Sources ~/.zshrc, ~/.bash_profile, etc. to get complete PATH.
 * 
 * Usage: node exec-command.js "<command>"
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

/**
 * Get shell initialization command to load user's environment
 */
function getShellInitCommand() {
  const homeDir = os.homedir();
  const shell = process.env.SHELL || '/bin/zsh';
  
  // Detect shell type
  if (shell.includes('zsh')) {
    // For zsh, check for .zshrc
    if (fs.existsSync(path.join(homeDir, '.zshrc'))) {
      return 'source ~/.zshrc 2>/dev/null; ';
    }
    if (fs.existsSync(path.join(homeDir, '.zprofile'))) {
      return 'source ~/.zprofile 2>/dev/null; ';
    }
  } else if (shell.includes('bash')) {
    // For bash, try .bash_profile first, then .bashrc
    if (fs.existsSync(path.join(homeDir, '.bash_profile'))) {
      return 'source ~/.bash_profile 2>/dev/null; ';
    }
    if (fs.existsSync(path.join(homeDir, '.bashrc'))) {
      return 'source ~/.bashrc 2>/dev/null; ';
    }
    if (fs.existsSync(path.join(homeDir, '.profile'))) {
      return 'source ~/.profile 2>/dev/null; ';
    }
  }
  
  // Fallback: try common init files
  const initFiles = ['.zshrc', '.bash_profile', '.bashrc', '.profile'];
  for (const file of initFiles) {
    if (fs.existsSync(path.join(homeDir, file))) {
      return `source ~/${file} 2>/dev/null; `;
    }
  }
  
  return '';
}

/**
 * Execute command with user's full environment
 */
function executeCommand(command) {
  const initCmd = getShellInitCommand();
  const fullCommand = initCmd + command;
  
  console.error(`🔧 Loading shell environment...`);
  console.error(`📝 Executing: ${command}`);
  console.error('');
  
  try {
    const output = execSync(fullCommand, {
      encoding: 'utf8',
      timeout: 30000, // 30 second timeout
      stdio: ['pipe', 'pipe', 'pipe'],
      env: process.env // Inherit current environment
    });
    
    console.log(output);
    return { success: true, output };
  } catch (error) {
    const stderr = error.stderr || error.message;
    console.error(`❌ Error: ${stderr}`);
    return { 
      success: false, 
      error: stderr,
      code: error.status || error.code
    };
  }
}

// CLI execution
if (require.main === module) {
  const command = process.argv.slice(2).join(' ');
  
  if (!command) {
    console.error('Usage: node exec-command.js "<command>"');
    process.exit(1);
  }
  
  const result = executeCommand(command);
  process.exit(result.success ? 0 : 1);
}

module.exports = { executeCommand, getShellInitCommand };
