#!/usr/bin/env node

/**
 * Terminal Killer - Command Detector
 * 
 * Analyzes user input to determine if it's a shell command or AI task.
 * Returns confidence score and decision.
 * 
 * Usage: node detect-command.js "<user input>"
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Configuration
const CONFIG = {
  CONFIDENCE_EXECUTE: 5,
  CONFIDENCE_ASK: 3,
  MAX_HISTORY_CHECK: 100,
  DANGEROUS_PATTERNS: [
    'rm -rf',
    'rm -rf /',
    'sudo',
    'dd if=',
    'mkfs',
    'chmod 777',
    'chown -R',
    ':(){ :|:& };:',
    '> /dev/',
    'wget.*\\|.*sh',
    'curl.*\\|.*sh',
  ]
};

// Common development tools that should always be recognized as commands
const DEV_TOOLS = [
  'adb', 'fastboot',
  'git', 'svn', 'hg',
  'npm', 'yarn', 'pnpm', 'bun',
  'node', 'python', 'python3', 'ruby', 'perl',
  'go', 'rustc', 'cargo',
  'docker', 'docker-compose', 'kubectl', 'helm',
  'terraform', 'ansible',
  'aws', 'gcloud', 'az',
  'brew', 'apt', 'yum', 'dnf', 'pacman',
  'code', 'vim', 'nvim', 'emacs', 'nano',
  'make', 'cmake', 'gcc', 'clang',
  'curl', 'wget', 'httpie',
  'ssh', 'scp', 'rsync', 'sftp',
];

// OS detection
const PLATFORM = os.platform();
const IS_WINDOWS = PLATFORM === 'win32';

/**
 * Get the first word from input
 */
function getFirstWord(input) {
  return input.trim().split(/\s+/)[0].toLowerCase();
}

/**
 * Check if input contains shell operators
 */
function hasShellOperators(input) {
  const operators = ['|', '>', '<', '&&', '||', ';', '&', '$', '`', '\\', '>>', '2>', '&>', '|&'];
  return operators.some(op => input.includes(op));
}

/**
 * Check if input contains path references
 */
function hasPathReferences(input) {
  const patterns = [
    /^\//,           // Absolute path
    /^\.\//,         // Relative path ./
    /^\.\.\//,       // Parent path ../
    /^~/,            // Home directory
    /\$[A-Za-z_]/,   // Environment variable
  ];
  return patterns.some(pattern => pattern.test(input));
}

/**
 * Check if input looks like natural language question
 */
function isQuestion(input) {
  const questionWords = [
    'what', 'how', 'why', 'when', 'where', 'who', 'which',
    'can you', 'could you', 'would you', 'please', 'help me',
    'explain', 'tell me', 'show me how', 'i want', 'i need',
    'is there', 'are there', 'do you know'
  ];
  const lower = input.toLowerCase();
  return questionWords.some(word => lower.includes(word)) || input.includes('?');
}

/**
 * Load builtin commands for current platform
 */
function getBuiltinCommands() {
  const builtinsPath = path.join(__dirname, '..', 'references', 'builtins');
  const platformFile = IS_WINDOWS ? 'windows.txt' : (PLATFORM === 'darwin' ? 'macos.txt' : 'linux.txt');
  
  try {
    const content = fs.readFileSync(path.join(builtinsPath, platformFile), 'utf8');
    return content.split('\n').filter(line => line.trim() && !line.startsWith('#'));
  } catch (e) {
    // Fallback to minimal list
    return ['cd', 'ls', 'pwd', 'echo', 'cat', 'mkdir', 'rm', 'cp', 'mv', 'grep', 'find'];
  }
}

/**
 * Check if first word is a builtin command
 */
function isBuiltinCommand(input) {
  const firstWord = getFirstWord(input);
  const builtins = getBuiltinCommands();
  return builtins.includes(firstWord);
}

/**
 * Check if first word is a common development tool
 */
function isDevTool(input) {
  const firstWord = getFirstWord(input);
  return DEV_TOOLS.includes(firstWord);
}

/**
 * Get the shell initialization command to load user's environment
 * This ensures we use the same PATH and environment as interactive shells
 */
function getShellInitCommand() {
  const homeDir = os.homedir();
  const initFiles = [
    '.zshrc',
    '.bash_profile',
    '.bashrc',
    '.profile',
    '.zprofile'
  ];
  
  // Find the first existing init file
  for (const file of initFiles) {
    const fullPath = path.join(homeDir, file);
    if (fs.existsSync(fullPath)) {
      // For zsh, use -i (interactive) to load .zshrc
      if (file === '.zshrc' || file === '.zprofile') {
        return 'source ~/.zshrc 2>/dev/null; ';
      }
      // For bash, source the appropriate file
      return `source ~/${file} 2>/dev/null; `;
    }
  }
  
  // Fallback: try to detect shell and use appropriate init
  const shell = process.env.SHELL || '/bin/zsh';
  if (shell.includes('zsh')) {
    return 'source ~/.zshrc 2>/dev/null; ';
  } else if (shell.includes('bash')) {
    return 'source ~/.bash_profile 2>/dev/null || source ~/.bashrc 2>/dev/null; ';
  }
  
  return '';
}

/**
 * Check if command exists in PATH (with user's shell environment loaded)
 */
function existsInPath(cmd) {
  try {
    const initCmd = getShellInitCommand();
    if (IS_WINDOWS) {
      execSync(`where ${cmd}`, { stdio: 'ignore' });
    } else {
      // Source user's shell init files to get full PATH
      execSync(`${initCmd}which ${cmd}`, { stdio: 'ignore', timeout: 5000 });
    }
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Check against shell history
 */
function matchesHistory(input) {
  const historyFiles = IS_WINDOWS 
    ? [path.join(os.homedir(), 'AppData', 'Roaming', 'Microsoft', 'Windows', 'PowerShell', 'PSReadLine', 'ConsoleHost_history.txt')]
    : [
        path.join(os.homedir(), '.zsh_history'),
        path.join(os.homedir(), '.bash_history'),
        path.join(os.homedir(), '.sh_history'),
      ];
  
  const firstWord = getFirstWord(input);
  
  for (const historyFile of historyFiles) {
    try {
      if (fs.existsSync(historyFile)) {
        const content = fs.readFileSync(historyFile, 'utf8');
        const lines = content.split('\n').slice(-CONFIG.MAX_HISTORY_CHECK);
        
        // Check for exact matches or same starting command
        for (const line of lines) {
          const cleanLine = line.replace(/^\d+:\d+;/, '').trim(); // Remove zsh timestamp
          if (cleanLine.startsWith(firstWord)) {
            return true;
          }
        }
      }
    } catch (e) {
      // Ignore history read errors
    }
  }
  
  return false;
}

/**
 * Calculate confidence score for command detection
 */
function calculateScore(input) {
  let score = 0;
  const firstWord = getFirstWord(input);
  
  // Rule 1: System builtin (+3)
  if (isBuiltinCommand(input)) {
    score += 3;
  }
  
  // Rule 1.5: Common dev tool (+2)
  if (isDevTool(input)) {
    score += 2;
  }
  
  // Rule 2: Exists in PATH (+3)
  if (existsInPath(firstWord)) {
    score += 3;
  }
  
  // Rule 3: History match (+2)
  if (matchesHistory(input)) {
    score += 2;
  }
  
  // Rule 4: Shell operators (+2)
  if (hasShellOperators(input)) {
    score += 2;
  }
  
  // Rule 5: Path references (+2)
  if (hasPathReferences(input)) {
    score += 2;
  }
  
  // Rule 6: Short input, likely command (+1)
  if (input.split(/\s+/).length < 10) {
    score += 1;
  }
  
  // Rule 7: Contains common command flags (+1)
  if (/^(-[a-zA-Z]|--\w+)/.test(input.split(/\s+/)[1] || '')) {
    score += 1;
  }
  
  // Penalties
  
  // Natural language question (-3)
  if (isQuestion(input)) {
    score -= 3;
  }
  
  // Contains polite words (-2)
  if (/please|could you|would you|can you/i.test(input)) {
    score -= 2;
  }
  
  // Very long input (-2)
  if (input.length > 200) {
    score -= 2;
  }
  
  return Math.max(0, score);
}

/**
 * Check for dangerous patterns
 */
function isDangerous(input) {
  const lower = input.toLowerCase();
  return CONFIG.DANGEROUS_PATTERNS.some(pattern => 
    new RegExp(pattern, 'i').test(lower)
  );
}

/**
 * Main detection function
 */
function detectCommand(input) {
  const score = calculateScore(input);
  const dangerous = isDangerous(input);
  
  let decision, confidence;
  
  if (score >= CONFIG.CONFIDENCE_EXECUTE) {
    decision = 'EXECUTE';
    confidence = 'HIGH';
  } else if (score >= CONFIG.CONFIDENCE_ASK) {
    decision = 'ASK';
    confidence = 'MEDIUM';
  } else {
    decision = 'LLM';
    confidence = 'LOW';
  }
  
  // Dangerous commands always require approval
  if (dangerous && decision === 'EXECUTE') {
    decision = 'ASK';
  }
  
  return {
    input,
    decision,
    confidence,
    score,
    dangerous,
    platform: PLATFORM,
    timestamp: new Date().toISOString()
  };
}

// CLI execution
if (require.main === module) {
  const input = process.argv.slice(2).join(' ');
  
  if (!input) {
    console.error('Usage: node detect-command.js "<user input>"');
    process.exit(1);
  }
  
  const result = detectCommand(input);
  console.log(JSON.stringify(result, null, 2));
}

module.exports = { detectCommand, calculateScore, isDangerous };
