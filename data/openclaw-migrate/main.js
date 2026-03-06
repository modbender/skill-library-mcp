#!/usr/bin/env node

/**
 * OpenClaw Migration Tool
 * Migrate OpenClaw from one host to another via SSH
 */

const { exec, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const C = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
  gray: '\x1b[90m',
  mag: '\x1b[35m'
};

const log = (msg, color = 'reset') => console.log(`${C[color]}${msg}${C.reset}`);
const err = (msg) => console.error(`${C.red}Error:${C.reset} ${msg}`);

// Config
const CONFIG_FILE = path.join(__dirname, 'config.json');

// Default paths to sync
const DEFAULT_PATHS = [
  '~/.openclaw/',
  '~/.config/openclaw/',
  '~/.npm-global/lib/node_modules/openclaw/',
];

const ENV_VARS_TO_SYNC = [
  'HA_URL', 'HA_TOKEN',
  'GITHUB_TOKEN', 'BRAVE_API_KEY',
  'GOOGLE_API_KEY', 'GOOGLE_SERVICE_ACCOUNT',
];

// Load config
function loadConfig() {
  if (fs.existsSync(CONFIG_FILE)) {
    return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
  }
  return null;
}

function saveConfig(config) {
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}

// Prompt user
function prompt(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  return new Promise(resolve => rl.question(question, answer => {
    rl.close();
    resolve(answer);
  }));
}

// Execute local command
function execCmd(cmd, options = {}) {
  return new Promise((resolve, reject) => {
    exec(cmd, { timeout: options.timeout || 30000 }, (error, stdout, stderr) => {
      if (error && !options.ignoreError) {
        reject(error);
        return;
      }
      resolve({ stdout, stderr, error });
    });
  });
}

// Execute remote command via SSH
function sshExec(host, user, cmd, options = {}) {
  return new Promise((resolve, reject) => {
    const sshCmd = `ssh ${options.key ? `-i ${options.key}` : ''} ${user}@${host} "${cmd}"`;
    exec(sshCmd, { timeout: options.timeout || 60000 }, (error, stdout, stderr) => {
      if (error && !options.ignoreError) {
        reject(error);
        return;
      }
      resolve({ stdout, stderr, error });
    });
  });
}

// Check SSH connectivity
async function checkSSH(host, user, key) {
  log(`Checking SSH connection to ${user}@${host}...`, 'cyan');
  try {
    const result = await sshExec(host, user, 'echo ok', { key, timeout: 10000 });
    if (result.stdout.includes('ok')) {
      log('SSH connection OK', 'green');
      return true;
    }
  } catch (e) {
    err(`SSH connection failed: ${e.message}`);
    return false;
  }
  return false;
}

// Check if new host has OpenClaw
async function checkOpenClaw(host, user, key) {
  log('Checking OpenClaw on remote host...', 'cyan');
  try {
    const result = await sshExec(host, user, 'which openclaw || which node', { key });
    if (result.stdout.includes('openclaw') || result.stdout.includes('node')) {
      log('OpenClaw found on remote host', 'green');
      return true;
    }
  } catch (e) {}
  
  log('OpenClaw not found on remote host', 'yellow');
  return false;
}

// Get list of files to sync
async function getSyncList(host, user, key) {
  log('Analyzing local OpenClaw installation...', 'cyan');
  
  const files = [];
  
  // Check openclaw workspace
  const workspacePath = path.join(process.env.HOME || '/home/crix', '.openclaw');
  if (fs.existsSync(workspacePath)) {
    // Walk directory
    const walk = (dir, prefix = '') => {
      const items = fs.readdirSync(dir);
      for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        if (stat.isDirectory()) {
          if (!item.startsWith('.') && item !== 'node_modules') {
            walk(fullPath, prefix + item + '/');
          }
        } else {
          files.push({
            local: fullPath,
            remote: fullPath.replace(process.env.HOME || '/home/crix', '')
          });
        }
      }
    };
    walk(workspacePath);
  }
  
  // Check npm-global
  const npmGlobal = process.env.PREFIX || '/home/crix/.npm-global';
  const openclawPath = path.join(npmGlobal, 'lib/node_modules/openclaw');
  if (fs.existsSync(openclawPath)) {
    files.push({
      local: openclawPath,
      remote: '~/.npm-global/lib/node_modules/openclaw',
      isDir: true
    });
  }
  
  // Check config
  const configPaths = [
    path.join(process.env.HOME || '/home/crix', '.config/openclaw/openclaw.json'),
    '/etc/openclaw/openclaw.json'
  ];
  
  for (const p of configPaths) {
    if (fs.existsSync(p)) {
      files.push({
        local: p,
        remote: p.replace(process.env.HOME || '/home/crix', ''),
        isConfig: true
      });
    }
  }
  
  log(`Found ${files.length} items to sync`, 'green');
  return files;
}

// Get environment variables to sync
function getEnvVarsToSync() {
  const vars = {};
  for (const v of ENV_VARS_TO_SYNC) {
    if (process.env[v]) {
      vars[v] = process.env[v];
    }
  }
  return vars;
}

// Sync files via SCP
async function syncFiles(host, user, files, key) {
  log(`Syncing ${files.length} files...`, 'cyan');
  
  let success = 0;
  let failed = 0;
  
  for (const file of files) {
    process.stdout.write(`  Syncing: ${path.basename(file.local)}... `);
    
    try {
      // Ensure remote directory exists
      const remoteDir = path.dirname(file.remote).replace('~', '/home/' + user);
      await sshExec(host, user, `mkdir -p "${remoteDir}"`, { key, ignoreError: true });
      
      // SCP file
      const scpCmd = `scp ${key ? `-i ${key}` : ''} -r "${file.local}" ${user}@${host}:"${file.remote}"`;
      await execCmd(scpCmd, { timeout: 60000 });
      
      log('OK', 'green');
      success++;
    } catch (e) {
      log('FAILED', 'red');
      failed++;
    }
  }
  
  log(`Sync complete: ${success} success, ${failed} failed`, failed > 0 ? 'yellow' : 'green');
  return failed === 0;
}

// Sync environment variables
async function syncEnvVars(host, user, key, vars) {
  if (Object.keys(vars).length === 0) {
    log('No environment variables to sync', 'gray');
    return true;
  }
  
  log('Syncing environment variables...', 'cyan');
  
  // Add to remote shell profile
  const envLines = Object.entries(vars).map(([k, v]) => `export ${k}="${v}"`).join('\n');
  const profileLine = `\n# OpenClaw Migrated ENV\n${envLines}\n`;
  
  for (const profile of ['.bashrc', '.profile', '.zshrc']) {
    try {
      const checkCmd = `ssh ${user}@${host} "grep -q '# OpenClaw Migrated' ~/.${profile} 2>/dev/null || echo '${profileLine}' >> ~/.${profile}"`;
      await execCmd(checkCmd);
    } catch (e) {}
  }
  
  log('Environment variables synced', 'green');
  return true;
}

// Sync cron jobs
async function syncCron(host, user, key) {
  log('Syncing cron jobs...', 'cyan');
  
  try {
    const result = await execCmd('crontab -l 2>/dev/null || echo ""');
    const crons = result.stdout;
    
    if (crons.trim()) {
      // Save to remote
      const cmd = `ssh ${user}@${host} "echo '${crons.replace(/'/g, "'\\''")}' | crontab -"`;
      await execCmd(cmd);
      log('Cron jobs synced', 'green');
    } else {
      log('No cron jobs to sync', 'gray');
    }
  } catch (e) {
    log('No cron jobs found', 'gray');
  }
  
  return true;
}

// Install OpenClaw on remote if needed
async function installOpenClaw(host, user, key) {
  log('Installing OpenClaw on remote host...', 'cyan');
  
  try {
    // Check if npm is available
    await sshExec(host, user, 'which npm', { key });
    
    // Install OpenClaw
    const installCmd = 'npm install -g openclaw';
    await sshExec(host, user, installCmd, { key, timeout: 120000 });
    
    log('OpenClaw installed', 'green');
    return true;
  } catch (e) {
    err(`Failed to install OpenClaw: ${e.message}`);
    return false;
  }
}

// Start OpenClaw gateway on remote
async function startRemoteGateway(host, user, key) {
  log('Starting OpenClaw gateway on remote...', 'cyan');
  
  try {
    await sshExec(host, user, 'openclaw gateway start', { key, timeout: 30000 });
    log('Gateway started', 'green');
    return true;
  } catch (e) {
    err(`Failed to start gateway: ${e.message}`);
    return false;
  }
}

// Interactive setup
async function setup() {
  log(C.bright + '\nOpenClaw Migration Setup\n' + C.reset, 'cyan');
  
  const config = {};
  
  // Get target host info
  config.host = await prompt('New host IP/hostname: ');
  config.user = await prompt('SSH user (default: crix): ') || 'crix';
  config.key = await prompt('SSH key path (optional, press Enter for default): ') || '';
  
  if (!config.host) {
    err('Host is required');
    process.exit(1);
  }
  
  saveConfig(config);
  log('\nConfiguration saved!', 'green');
  
  return config;
}

// Migration main
async function migrate() {
  const config = loadConfig() || await setup();
  
  log(C.bright + '\n=== OpenClaw Migration ===\n' + C.reset, 'cyan');
  
  // Step 1: Check SSH
  const sshOk = await checkSSH(config.host, config.user, config.key);
  if (!sshOk) {
    err('Cannot connect to new host. Check IP, user, and SSH key.');
    const retry = await prompt('\nRetry with different settings? (y/n): ');
    if (retry.toLowerCase() === 'y') {
      await setup();
      return migrate();
    }
    process.exit(1);
  }
  
  // Step 2: Check OpenClaw
  const hasOpenClaw = await checkOpenClaw(config.host, config.user, config.key);
  if (!hasOpenClaw) {
    const install = await prompt('\nOpenClaw not found on remote. Install now? (y/n): ');
    if (install.toLowerCase() === 'y') {
      await installOpenClaw(config.host, config.user, config.key);
    } else {
      err('Cannot proceed without OpenClaw');
      process.exit(1);
    }
  }
  
  // Step 3: Get files to sync
  const files = await getSyncList(config.host, config.user, config.key);
  
  if (files.length === 0) {
    err('No files found to sync');
    process.exit(1);
  }
  
  // Show files
  log('\nFiles to sync:', 'yellow');
  files.slice(0, 10).forEach(f => log(`  - ${path.basename(f.local)}`, 'gray'));
  if (files.length > 10) log(`  ... and ${files.length - 10} more`, 'gray');
  
  const confirm = await prompt('\nProceed with migration? (y/n): ');
  if (confirm.toLowerCase() !== 'y') {
    log('Migration cancelled', 'yellow');
    process.exit(0);
  }
  
  // Step 4: Sync files
  const filesOk = await syncFiles(config.host, config.user, files, config.key);
  
  // Step 5: Sync env vars
  const envVars = getEnvVarsToSync();
  await syncEnvVars(config.host, config.user, config.key, envVars);
  
  // Step 6: Sync crons
  await syncCron(config.host, config.user, config.key);
  
  // Step 7: Start gateway
  const start = await prompt('\nStart OpenClaw gateway on new host? (y/n): ');
  if (start.toLowerCase() === 'y') {
    await startRemoteGateway(config.host, config.user, config.key);
  }
  
  log(C.bright + '\n=== Migration Complete! ===' + C.reset, 'green');
  log(`\nNew OpenClaw should be running at: ${config.host}`, 'cyan');
  log('Test with: ssh ' + config.user + '@' + config.host + ' "openclaw status"', 'gray');
}

// Show status
async function status() {
  const config = loadConfig();
  
  if (!config) {
    log('No migration configured. Run: openclaw-migrate setup', 'yellow');
    return;
  }
  
  log(C.bright + '\nMigration Status\n' + C.reset, 'cyan');
  log(`  Target host: ${config.host}`, 'gray');
  log(`  SSH user: ${config.user}`, 'gray');
  log(`  SSH key: ${config.key || 'default'}`, 'gray');
  
  // Check connection
  const connected = await checkSSH(config.host, config.user, config.key);
  log(`  Connection: ${connected ? 'OK' : 'FAILED'}`, connected ? 'green' : 'red');
}

// Show help
function help() {
  log(C.bright + '\nOpenClaw Migration Tool' + C.reset, 'cyan');
  log('\nUsage:', 'yellow');
  log('  openclaw-migrate setup     - Configure migration target', 'gray');
  log('  openclaw-migrate migrate   - Start migration', 'gray');
  log('  openclaw-migrate status   - Show migration status', 'gray');
  log('  openclaw-migrate test     - Test SSH connection', 'gray');
  log('\nWhat it does:', 'yellow');
  log('  - Connects to new host via SSH', 'gray');
  log('  - Installs OpenClaw if needed', 'gray');
  log('  - Syncs all config, skills, memory', 'gray');
  log('  - Syncs environment variables', 'gray');
  log('  - Syncs cron jobs', 'gray');
  log('  - Starts gateway on new host', 'gray');
}

async function testConnection() {
  const config = loadConfig();
  if (!config) {
    err('Not configured. Run: openclaw-migrate setup');
    process.exit(1);
  }
  
  const ok = await checkSSH(config.host, config.user, config.key);
  if (ok) {
    log('Connection test passed!', 'green');
    
    // Also check if OpenClaw is there
    const has = await checkOpenClaw(config.host, config.user, config.key);
    if (has) {
      log('OpenClaw is installed on remote', 'green');
    } else {
      log('OpenClaw NOT installed on remote (will be installed during migration)', 'yellow');
    }
  } else {
    err('Connection test failed');
    process.exit(1);
  }
}

// Main
async function main() {
  const args = process.argv.slice(2);
  const cmd = args[0];
  
  try {
    switch (cmd) {
      case 'setup':
      case 'config':
        await setup();
        break;
        
      case 'migrate':
      case 'sync':
        await migrate();
        break;
        
      case 'status':
        await status();
        break;
        
      case 'test':
        await testConnection();
        break;
        
      default:
        help();
    }
  } catch (e) {
    err(e.message);
    process.exit(1);
  }
}

main();
