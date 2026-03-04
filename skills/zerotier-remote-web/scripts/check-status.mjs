#!/usr/bin/env node
/**
 * ZeroTier Remote Web Access - Status Check
 * 检查 ZeroTier 和 OpenClaw Gateway 配置状态
 */

import { execSync } from 'child_process';
import { readFileSync } from 'fs';
import { join } from 'path';

const COLORS = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
};

function log(color, message) {
  console.log(`${color}${message}${COLORS.reset}`);
}

function runCommand(cmd) {
  try {
    return execSync(cmd, { encoding: 'utf8', stdio: ['pipe', 'pipe', 'ignore'] });
  } catch (e) {
    return null;
  }
}

function checkZeroTierService() {
  const output = runCommand('systemctl is-active zerotier-one');
  if (output?.trim() === 'active') {
    log(COLORS.green, '✅ ZeroTier 服务：运行中');
    return true;
  }
  log(COLORS.red, '❌ ZeroTier 服务：未运行');
  return false;
}

function getZeroTierInfo() {
  // 尝试从 ip addr 获取信息
  const ipOutput = runCommand('ip addr show | grep -A 5 "zt"');
  if (ipOutput) {
    const interfaceMatch = ipOutput.match(/(\d+):\s+(zt\w+):/);
    const ipMatch = ipOutput.match(/inet\s+([\d.]+)\/(\d+)/);
    
    if (interfaceMatch && ipMatch) {
      log(COLORS.green, `✅ 网络接口：${interfaceMatch[2]}`);
      log(COLORS.green, `✅ ZeroTier IP: ${ipMatch[1]}`);
      return { interface: interfaceMatch[2], ip: ipMatch[1] };
    }
  }
  
  log(COLORS.red, '❌ 未找到 ZeroTier 网络接口');
  return null;
}

function checkGatewayConfig() {
  const configPath = join(process.env.HOME, '.openclaw', 'openclaw.json');
  
  try {
    const config = JSON.parse(readFileSync(configPath, 'utf8'));
    const gateway = config.gateway || {};
    
    const bind = gateway.bind || 'loopback';
    const port = gateway.port || 18789;
    const customHost = gateway.customBindHost;
    
    log(COLORS.blue, `📡 Gateway 端口：${port}`);
    log(COLORS.blue, `📡 绑定模式：${bind}`);
    
    if (bind === 'custom' && customHost) {
      log(COLORS.green, `✅ Gateway 绑定：${customHost}:${port} (可远程访问)`);
      return { bind, port, customHost, remoteEnabled: true };
    } else if (bind === 'lan' || bind === 'any' || customHost === '0.0.0.0') {
      log(COLORS.green, `✅ Gateway 绑定：${bind} (可远程访问)`);
      return { bind, port, customHost, remoteEnabled: true };
    } else if (bind === 'loopback' || bind === 'localhost') {
      log(COLORS.yellow, '❌ Gateway 绑定：loopback (仅本地访问)');
      return { bind, port, customHost, remoteEnabled: false };
    } else {
      log(COLORS.yellow, `⚠️  Gateway 绑定：${bind}`);
      return { bind, port, customHost, remoteEnabled: false };
    }
  } catch (e) {
    log(COLORS.red, `❌ 无法读取配置文件：${e.message}`);
    return null;
  }
}

function checkGatewayProcess() {
  const output = runCommand('pgrep -f "openclaw-gateway"');
  if (output) {
    const pids = output.trim().split('\n');
    log(COLORS.green, `✅ Gateway 进程：运行中 (PID: ${pids.join(', ')})`);
    return true;
  }
  log(COLORS.red, '❌ Gateway 进程：未运行');
  return false;
}

function checkPortListening() {
  const configPath = join(process.env.HOME, '.openclaw', 'openclaw.json');
  let port = 1880;
  
  try {
    const config = JSON.parse(readFileSync(configPath, 'utf8'));
    port = config.gateway?.port || 1880;
  } catch (e) {}
  
  const output = runCommand(`ss -tlnp 2>/dev/null | grep :${port}`);
  if (output) {
    log(COLORS.green, `✅ 端口监听：${port} 已开放`);
    return true;
  }
  log(COLORS.red, `❌ 端口监听：${port} 未开放`);
  return false;
}

function printSummary(ztInfo, gatewayConfig) {
  console.log('\n' + '='.repeat(50));
  log(COLORS.blue, '📊 状态总结');
  console.log('='.repeat(50));
  
  if (ztInfo && gatewayConfig?.remoteEnabled) {
    log(COLORS.green, '\n🎉 远程 WEB 访问已启用!');
    log(COLORS.blue, `\n访问地址：http://${ztInfo.ip}:${gatewayConfig.port}`);
    log(COLORS.yellow, '\n提示：远程设备需要安装 ZeroTier 并加入同一网络');
  } else if (ztInfo && !gatewayConfig?.remoteEnabled) {
    log(COLORS.yellow, '\n⚠️  ZeroTier 已就绪，但 Gateway 未配置远程访问');
    log(COLORS.blue, '\n运行以下命令启用：');
    log(COLORS.green, `  node ${process.argv[1].replace('check-status.mjs', 'enable-remote.mjs')}`);
  } else {
    log(COLORS.red, '\n❌ ZeroTier 未就绪，请先安装并配置 ZeroTier');
  }
  
  console.log('='.repeat(50) + '\n');
}

// Main
console.log('\n🔍 ZeroTier Remote Web Access - 状态检查\n');

const ztService = checkZeroTierService();
const ztInfo = ztService ? getZeroTierInfo() : null;
console.log();
const gatewayConfig = checkGatewayConfig();
const gatewayProcess = checkGatewayProcess();
const portListening = checkPortListening();

printSummary(ztInfo, gatewayConfig);
