#!/usr/bin/env node
/**
 * ZeroTier Remote Web Access - Enable Remote Access
 * 自动配置 OpenClaw Gateway 以支持 ZeroTier 远程访问
 */

import { execSync } from 'child_process';
import { readFileSync, writeFileSync, copyFileSync } from 'fs';
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

function getZeroTierIP() {
  const ipOutput = runCommand('ip addr show | grep -A 5 "zt"', true);
  if (ipOutput) {
    const ipMatch = ipOutput.match(/inet\s+([\d.]+)\/(\d+)/);
    if (ipMatch) {
      return ipMatch[1];
    }
  }
  return null;
}

function backupConfig(configPath) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '').slice(0, 15);
  const backupPath = `${configPath}.backup-${timestamp}`;
  
  try {
    copyFileSync(configPath, backupPath);
    log(COLORS.green, `✅ 配置已备份：${backupPath}`);
    return backupPath;
  } catch (e) {
    log(COLORS.red, `❌ 备份失败：${e.message}`);
    return null;
  }
}

function updateConfig(configPath, ztIP) {
  try {
    const config = JSON.parse(readFileSync(configPath, 'utf8'));
    
    // 保存旧配置用于对比
    const oldPort = config.gateway?.port || 18789;
    const oldBind = config.gateway?.bind || 'loopback';
    
    // 更新配置
    config.gateway = {
      ...config.gateway,
      port: 1880,
      mode: 'local',
      bind: 'custom',
      customBindHost: '0.0.0.0',  // 绑定所有网络接口，支持本地和远程访问
      controlUi: {
        ...(config.gateway?.controlUi || {}),
        allowedOrigins: [
          `http://localhost:1880`,
          `http://127.0.0.1:1880`,
          `http://${ztIP}:1880`,
        ],
        allowInsecureAuth: true,
        dangerouslyDisableDeviceAuth: true,
      },
      auth: {
        ...(config.gateway?.auth || {}),
        mode: 'token',
        // 生成新 token 或保持原有
        token: config.gateway?.auth?.token || generateToken(),
      },
    };
    
    writeFileSync(configPath, JSON.stringify(config, null, 2) + '\n');
    log(COLORS.green, '✅ 配置文件已更新');
    
    return {
      oldPort,
      oldBind,
      newPort: 1880,
      newBind: 'custom',
      newHost: ztIP,
      token: config.gateway.auth.token,
    };
  } catch (e) {
    log(COLORS.red, `❌ 配置更新失败：${e.message}`);
    return null;
  }
}

function generateToken() {
  const crypto = await import('crypto');
  return crypto.randomBytes(20).toString('hex');
}

function restartGateway() {
  log(COLORS.blue, '🔄 正在重启 Gateway...');
  
  // 停止旧进程
  runCommand('pkill -f "openclaw-gateway"', true);
  runCommand('sleep 2', true);
  
  // 启动新进程
  const home = process.env.HOME;
  runCommand(`nohup openclaw gateway > /tmp/openclaw-gateway.log 2>&1 &`, true);
  runCommand('sleep 5', true);
  
  // 检查是否启动成功
  const checkOutput = runCommand('pgrep -f "openclaw-gateway"', true);
  if (checkOutput) {
    log(COLORS.green, '✅ Gateway 已重启');
    return true;
  }
  
  log(COLORS.red, '❌ Gateway 启动失败，查看日志：/tmp/openclaw-gateway.log');
  return false;
}

function verifyConfig(ztIP) {
  log(COLORS.blue, '🔍 验证配置...');
  
  const portOutput = runCommand(`ss -tlnp 2>/dev/null | grep :1880`, true);
  if (portOutput && portOutput.includes(ztIP)) {
    log(COLORS.green, `✅ 端口 1880 正在监听 ${ztIP}`);
    return true;
  }
  
  log(COLORS.yellow, '⚠️  端口监听验证未通过，但 Gateway 可能仍在启动中');
  return false;
}

function printSummary(ztIP, configChanges) {
  console.log('\n' + '='.repeat(60));
  log(COLORS.green, '🎉 远程 WEB 访问配置完成!');
  console.log('='.repeat(60));
  
  log(COLORS.cyan, '\n📋 配置变更:');
  console.log(`  端口：${configChanges.oldPort} → ${configChanges.newPort}`);
  console.log(`  绑定：${configChanges.oldBind} → ${configChanges.newBind}`);
  console.log(`  主机：- → 0.0.0.0 (所有网络接口)`);
  
  log(COLORS.cyan, '\n🌐 访问地址:');
  log(COLORS.green, `  本地：http://localhost:1880`);
  log(COLORS.green, `  SSH 登录后：http://<服务器内网 IP>:1880`);
  log(COLORS.green, `  远程 ZeroTier: http://${ztIP}:1880`);
  
  log(COLORS.cyan, '\n🔐 认证 Token:');
  log(COLORS.yellow, `  ${configChanges.token}`);
  
  log(COLORS.cyan, '\n📱 远程设备设置:');
  console.log('  1. 安装 ZeroTier 客户端');
  console.log('  2. 加入相同的 ZeroTier 网络');
  console.log('  3. 等待网络管理员授权');
  console.log(`  4. 访问 http://${ztIP}:1880 并输入 Token`);
  
  log(COLORS.cyan, '\n🔄 恢复方法:');
  console.log('  运行以下命令恢复到本地模式:');
  log(COLORS.green, `  node ${process.argv[1].replace('enable-remote.mjs', 'disable-remote.mjs')}`);
  
  console.log('\n' + '='.repeat(60) + '\n');
}

// Main
console.log('\n🚀 ZeroTier Remote Web Access - 启用远程访问\n');

// Step 1: 获取 ZeroTier IP
log(COLORS.blue, '步骤 1: 获取 ZeroTier IP...');
const ztIP = getZeroTierIP();
if (!ztIP) {
  log(COLORS.red, '❌ 未找到 ZeroTier IP，请检查 ZeroTier 是否已配置');
  process.exit(1);
}
log(COLORS.green, `✅ ZeroTier IP: ${ztIP}`);

// Step 2: 备份配置
console.log();
log(COLORS.blue, '步骤 2: 备份当前配置...');
const configPath = join(process.env.HOME, '.openclaw', 'openclaw.json');
const backupPath = backupConfig(configPath);
if (!backupPath) {
  log(COLORS.red, '❌ 备份失败，中止操作');
  process.exit(1);
}

// Step 3: 更新配置
console.log();
log(COLORS.blue, '步骤 3: 更新 Gateway 配置...');
const configChanges = updateConfig(configPath, ztIP);
if (!configChanges) {
  log(COLORS.red, '❌ 配置更新失败，可从备份恢复');
  log(COLORS.yellow, `  cp ${backupPath} ${configPath}`);
  process.exit(1);
}

// Step 4: 重启 Gateway
console.log();
log(COLORS.blue, '步骤 4: 重启 Gateway...');
const restartSuccess = restartGateway();
if (!restartSuccess) {
  log(COLORS.red, '❌ Gateway 重启失败');
  log(COLORS.yellow, '查看日志：/tmp/openclaw-gateway.log');
  process.exit(1);
}

// Step 5: 验证配置
console.log();
verifyConfig(ztIP);

// Print summary
printSummary(ztIP, configChanges);
