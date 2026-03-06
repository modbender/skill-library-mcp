#!/usr/bin/env node

/**
 * Terminal Killer - Interactive Shell Handler
 * 
 * Opens an interactive shell session for commands like:
 * - adb shell
 * - ssh user@host
 * - docker exec -it container bash
 * - mysql -u root -p
 * 
 * Usage: node interactive.js "<command>"
 */

const { spawn } = require('child_process');
const os = require('os');
const path = require('path');
const fs = require('fs');

/**
 * Get shell initialization command
 */
function getShellInitCommand() {
  const homeDir = os.homedir();
  const shell = process.env.SHELL || '/bin/zsh';
  
  if (shell.includes('zsh')) {
    if (fs.existsSync(path.join(homeDir, '.zshrc'))) {
      return 'source ~/.zshrc 2>/dev/null; ';
    }
  } else if (shell.includes('bash')) {
    if (fs.existsSync(path.join(homeDir, '.bash_profile'))) {
      return 'source ~/.bash_profile 2>/dev/null; ';
    }
    if (fs.existsSync(path.join(homeDir, '.bashrc'))) {
      return 'source ~/.bashrc 2>/dev/null; ';
    }
  }
  
  return '';
}

/**
 * Detect if command is interactive
 */
function isInteractiveCommand(command) {
  const interactivePatterns = [
    /^adb\s+shell\s*$/,           // adb shell (no additional command)
    /^ssh\s+/,                    // ssh user@host
    /^docker\s+exec\s+-it\s+/,    // docker exec -it
    /^docker\s+attach\s+/,        // docker attach
    /^mysql\s+/,                  // mysql client
    /^psql\s+/,                   // postgres client
    /^sqlite3\s+/,                // sqlite3
    /^mongo\s+/,                  // mongodb shell
    /^redis-cli\s*/,              // redis cli
    /^ftp\s+/,                    // ftp
    /^sftp\s+/,                   // sftp
    /^telnet\s+/,                 // telnet
    /^nc\s+/,                     // netcat
    /^screen\s+/,                 // screen
    /^tmux\s+/,                   // tmux
    /^bash\s*$/,                  // bash (interactive)
    /^sh\s*$/,                    // sh (interactive)
    /^zsh\s*$/,                   // zsh (interactive)
    /^python\s*$/,                // python repl
    /^python3\s*$/,               // python3 repl
    /^node\s*$/,                  // node repl
    /^irb\s*$/,                   // ruby repl
  ];
  
  return interactivePatterns.some(pattern => pattern.test(command.trim()));
}

/**
 * Open interactive shell in new terminal window
 */
function openInteractiveShell(command) {
  const platform = os.platform();
  const initCmd = getShellInitCommand();
  const fullCommand = initCmd + command;
  
  console.log('🔧 Opening interactive shell...');
  console.log(`📝 Command: ${command}`);
  console.log('');
  
  if (platform === 'darwin') {
    // macOS - Open new Terminal window
    const appleScript = `
      tell app "Terminal"
        activate
        do script "${fullCommand}"
      end tell
    `;
    
    const osa = spawn('osascript', ['-e', appleScript]);
    
    osa.stdout.on('data', (data) => {
      console.log(`AppleScript: ${data}`);
    });
    
    osa.stderr.on('data', (data) => {
      console.error(`AppleScript Error: ${data}`);
    });
    
    osa.on('close', (code) => {
      if (code === 0) {
        console.log('✅ Interactive shell opened in new Terminal window');
      } else {
        console.log('⚠️  Could not open Terminal. Trying alternative...');
        openAlternativeShell(fullCommand);
      }
    });
    
  } else if (platform === 'linux') {
    // Linux - Try common terminal emulators
    const terminals = [
      ['gnome-terminal', '--', 'bash', '-c', fullCommand],
      ['konsole', '-e', 'bash', '-c', fullCommand],
      ['xfce4-terminal', '-e', fullCommand],
      ['xterm', '-e', fullCommand],
    ];
    
    for (const [cmd, ...args] of terminals) {
      try {
        const proc = spawn(cmd, args, { detached: true, stdio: 'ignore' });
        proc.unref();
        console.log(`✅ Opened in ${cmd}`);
        return;
      } catch (e) {
        continue;
      }
    }
    
    console.log('⚠️  No supported terminal emulator found');
    openAlternativeShell(fullCommand);
    
  } else if (platform === 'win32') {
    // Windows - Open new Command Prompt or PowerShell window
    const spawn = require('child_process').spawn;
    const cmd = `start cmd /k "${fullCommand}"`;
    spawn('cmd', ['/c', cmd], { detached: true, shell: true });
    console.log('✅ Opened in new Command Prompt window');
  }
}

/**
 * Alternative: Provide instructions for manual execution
 */
function openAlternativeShell(command) {
  console.log('');
  console.log('═'.repeat(60));
  console.log('📋 Interactive Shell Instructions');
  console.log('═'.repeat(60));
  console.log('');
  console.log('Cannot automatically open terminal. Please:');
  console.log('');
  console.log('1. Open a new terminal window');
  console.log('2. Run this command:');
  console.log('');
  console.log(`   ${command}`);
  console.log('');
  console.log('═'.repeat(60));
  console.log('');
}

/**
 * Main entry point
 */
function handleInteractive(command) {
  if (isInteractiveCommand(command)) {
    console.log('🔍 Detected interactive command');
    openInteractiveShell(command);
    return { action: 'interactive', command };
  } else {
    console.log('ℹ️  Not an interactive command');
    return { action: 'not_interactive', command };
  }
}

// CLI execution
if (require.main === module) {
  const command = process.argv.slice(2).join(' ');
  
  if (!command) {
    console.error('Usage: node interactive.js "<command>"');
    console.error('');
    console.error('Examples:');
    console.error('  node interactive.js "adb shell"');
    console.error('  node interactive.js "ssh user@host"');
    console.error('  node interactive.js "docker exec -it container bash"');
    process.exit(1);
  }
  
  handleInteractive(command);
}

module.exports = { handleInteractive, isInteractiveCommand, openInteractiveShell };
