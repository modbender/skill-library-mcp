/**
 * 环境变量工具 - 安全版本 v1.0.4
 * 仅使用 ~/.cuecue 目录，不写入共享配置文件
 */

import fs from 'fs-extra';
import path from 'path';
import { homedir } from 'os';
import { createLogger } from '../core/logger.js';

const logger = createLogger('EnvUtils');

// ✅ 安全修复：仅使用技能自己的目录
const CUECUE_DIR = path.join(homedir(), '.cuecue');
const SECURE_ENV_FILE = path.join(CUECUE_DIR, '.env.secure');

/**
 * 确保目录存在并设置权限
 * @param {string} dir - 目录路径
 * @param {number} mode - 权限模式 (默认 0o700)
 */
async function ensureSecureDir(dir, mode = 0o700) {
  await fs.ensureDir(dir);
  
  // 设置权限：仅所有者可读写执行
  try {
    await fs.chmod(dir, mode);
  } catch (error) {
    await logger.warn(`Failed to set directory permissions for ${dir}`, error);
  }
}

/**
 * 加载环境变量文件
 * @returns {Promise<Map<string, string>>}
 */
export async function loadEnvFile() {
  const env = new Map();
  
  try {
    const content = await fs.readFile(SECURE_ENV_FILE, 'utf-8');
    const lines = content.split('\n');
    
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      
      const match = trimmed.match(/^export\s+(\w+)="([^"]*)"$/);
      if (match) {
        env.set(match[1], match[2]);
      }
    }
  } catch (error) {
    // 文件不存在，返回空 Map
  }
  
  return env;
}

/**
 * 保存环境变量到文件
 * @param {Map<string, string>} env - 环境变量 Map
 */
export async function saveEnvFile(env) {
  // ✅ 安全修复：确保目录存在并设置权限
  await ensureSecureDir(CUECUE_DIR, 0o700);
  
  const lines = ['# Cue v1.0.4 - Secure Environment Variables', '# DO NOT SHARE THIS FILE'];
  for (const [key, value] of env) {
    lines.push(`export ${key}="${value}"`);
  }
  
  await fs.writeFile(SECURE_ENV_FILE, lines.join('\n') + '\n');
  
  // ✅ 安全修复：设置文件权限 600 (仅所有者可读写)
  try {
    await fs.chmod(SECURE_ENV_FILE, 0o600);
    await logger.info('Secure env file created with permissions 600');
  } catch (error) {
    await logger.warn('Failed to set secure file permissions', error);
  }
}

/**
 * 获取 API Key
 * 优先从环境变量读取，其次从安全文件读取
 * @param {string} keyName - Key 名称
 * @returns {Promise<string|null>}
 */
export async function getApiKey(keyName) {
  // 1. 首先检查 process.env (由 OpenClaw 注入)
  if (process.env[keyName]) {
    return process.env[keyName];
  }
  
  // 2. 然后检查技能自己的安全文件
  const env = await loadEnvFile();
  return env.get(keyName) || null;
}

/**
 * 设置 API Key
 * 仅保存到技能自己的目录，不写入共享配置文件
 * @param {string} keyName - Key 名称
 * @param {string} value - Key 值
 */
export async function setApiKey(keyName, value) {
  // 更新当前进程环境变量
  process.env[keyName] = value;
  
  // ✅ 安全修复：仅保存到 ~/.cuecue/.env.secure
  const env = await loadEnvFile();
  env.set(keyName, value);
  await saveEnvFile(env);
  
  await logger.info(`API Key ${keyName} saved to secure storage`);
}

/**
 * 检测 API Key 对应的服务
 * @param {string} apiKey - API Key
 * @returns {{service: string, name: string, url: string}|null}
 */
export function detectServiceFromKey(apiKey) {
  if (!apiKey || apiKey.length < 10) {
    return null;
  }
  
  // Tavily: tvly-xxxxx
  if (apiKey.startsWith('tvly-')) {
    return {
      service: 'tavily',
      name: 'Tavily',
      url: 'https://tavily.com'
    };
  }
  
  // CueCue: skb... 开头
  if (apiKey.startsWith('skb')) {
    return {
      service: 'cuecue',
      name: 'CueCue',
      url: 'https://cuecue.cn'
    };
  }
  
  // 根据长度区分 CueCue 和 QVeris
  if (apiKey.startsWith('sk-')) {
    if (apiKey.length > 40) {
      return {
        service: 'qveris',
        name: 'QVeris',
        url: 'https://qveris.ai'
      };
    } else {
      return {
        service: 'cuecue',
        name: 'CueCue',
        url: 'https://cuecue.cn'
      };
    }
  }
  
  return null;
}

/**
 * 获取所有 API Key 状态
 * @returns {Promise<Array<{name: string, key: string, configured: boolean, masked: string}>>}
 */
export async function getApiKeyStatus() {
  const keys = [
    { name: 'CueCue', key: 'CUECUE_API_KEY' },
    { name: 'Tavily', key: 'TAVILY_API_KEY' },
    { name: 'QVeris', key: 'QVERIS_API_KEY' }
  ];
  
  const results = [];
  for (const { name, key } of keys) {
    const value = await getApiKey(key);
    const masked = value 
      ? (value.length > 16 
        ? `${value.slice(0, 4)}****${value.slice(-4)}`
        : `${value.slice(0, 2)}****`)
      : null;
    
    results.push({
      name,
      key,
      configured: !!value,
      masked
    });
  }
  
  return results;
}

/**
 * 获取当前渠道配置
 * @returns {{channel: string, chatId: string}}
 */
export function getChannelConfig() {
  return {
    channel: process.env.OPENCLAW_CHANNEL || 'feishu',
    chatId: process.env.CHAT_ID || process.env.FEISHU_CHAT_ID || 'default'
  };
}

/**
 * 验证安全设置
 * 检查目录和文件权限
 * @returns {Promise<{secure: boolean, issues: string[]}>}
 */
export async function validateSecurity() {
  const issues = [];
  
  // 检查目录权限
  try {
    const stats = await fs.stat(CUECUE_DIR);
    const mode = stats.mode & 0o777;
    if (mode !== 0o700) {
      issues.push(`Directory permissions should be 700, got ${mode.toString(8)}`);
    }
  } catch (error) {
    issues.push('CueCue directory does not exist');
  }
  
  // 检查文件权限
  try {
    const stats = await fs.stat(SECURE_ENV_FILE);
    const mode = stats.mode & 0o777;
    if (mode !== 0o600) {
      issues.push(`Env file permissions should be 600, got ${mode.toString(8)}`);
    }
  } catch (error) {
    // 文件不存在不算错误
  }
  
  return {
    secure: issues.length === 0,
    issues
  };
}
