#!/usr/bin/env node
/**
 * ZeroTier Remote Web Access - Disable Remote Access
 * 恢复 OpenClaw Gateway 到本地绑定模式
 */

import { execSync } from 'child_process';
import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

const COLORS = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(color, message) {
  console.log(`${color}${message}${COLORS.reset}`);
}

function runCommand(cmd, silent = false) {
  try {
    const output = execSync(cmd, { encoding: 'utf8', stdio: silent ? 'pipe' : 'inherit' });
    return output;
  } catch (e) {
    if (!silent) {
      console.error(e.message);
    }
    return null;
  }
}

function restoreToLocal(configPath) {
  try {
    const config = JSON.parse(readFileSync(configPath, 'utf8'));
    
    const oldPort = config.gateway?.port || 1880;
    const oldHost = config.gateway?.customBindHost || 'N/A';
    
    // 恢复到本地绑定
    config.gateway = {
      ...config.gateway,
      port: 18789,
      bind: 'loopback',
      controlUi: {
        ...(config.gateway?.controlUi || {}),
        allowedOrigins: [
          'http://localhost:18789',
          'http://127.0.0.1:18789',
        ],
      },
    };
    
    // 删除 customBindHost
    delete config.gateway.customBindHost;
    
    writeFileSync(configPath, JSON.stringify(config, null, 2) + '\n');
    log(COLORS.green, '✅ 配置已恢复到本地模式');
    
    return {
      oldPort,
      oldHost,
      newPort: 18789,
    };
  } catch (e) {
    log(COLORS.red, `❌ 配置恢复失败：${e.message}`);
    return null;
  }
}

function restartGateway() {
  log(COLORS.blue, '🔄 正在重启 Gateway...');
  
  runCommand('pkill -f "openclaw-gateway"', true);
  runCommand('sleep 2', true);
  runCommand(`nohup openclaw gateway > /tmp/openclaw-gateway.log 2>&1 &`, true);
  runCommand('sleep 5', true);
  
  const checkOutput = runCommand('pgrep -f "openclaw-gateway"', true);
  if (checkOutput) {
    log(COLORS.green, '✅ Gateway 已重启');
    return true;
  }
  
  log(COLORS.red, '❌ Gateway 启动失败');
  return false;
}

function listBackups() {
  const { execSync } = await import('child_process');
  try {
    const output = execSync('ls -lt ~/.openclaw/openclaw.json.backup-* 2>/dev/null | head -5', { encoding: 'utf8' });
    if (output.trim()) {
      log(COLORS.blue, '\n📦 最近的备份文件:');
      console.log(output);
    }
  } catch (e) {
    // 没有备份文件
  }
}

function printSummary(configChanges) {
  console.log('\n' + '='.repeat(60));
  log(COLORS.green, '✅ 已恢复到本地模式');
  console.log('='.repeat(60));
  
  log(COLORS.cyan, '\n📋 配置变更:');
  console.log(`  端口：${configChanges.oldPort} → ${configChanges.newPort}`);
  console.log(`  绑定：${configChanges.oldHost} → localhost`);
  
  log(COLORS.cyan, '\n🌐 访问地址:');
  log(COLORS.green, `  http://localhost:18789`);
  
  log(COLORS.yellow, '\n⚠️  远程访问已禁用');
  console.log('  如需重新启用，运行:');
  log(COLORS.green, `  node ${process.argv[1].replace('disable-remote.mjs', 'enable-remote.mjs')}`);
  
  console.log('\n' + '='.repeat(60) + '\n');
}

// Main
console.log('\n🔄 ZeroTier Remote Web Access - 恢复到本地模式\n');

// Step 1: 显示备份文件
log(COLORS.blue, '步骤 1: 查看可用备份...');
await listBackups();

// Step 2: 恢复配置
console.log();
log(COLORS.blue, '步骤 2: 恢复 Gateway 配置...');
const configPath = join(process.env.HOME, '.openclaw', 'openclaw.json');
const configChanges = restoreToLocal(configPath);
if (!configChanges) {
  log(COLORS.red, '❌ 配置恢复失败');
  process.exit(1);
}

// Step 3: 重启 Gateway
console.log();
restartGateway();

// Print summary
printSummary(configChanges);
