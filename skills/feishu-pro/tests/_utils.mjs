import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const ERROR_HINTS = {
  99991663: 'app_access_token 无效：检查 FEISHU_APP_ID/FEISHU_APP_SECRET，或确认应用是否被禁用。',
  99991401: '请求频率过高：稍后重试或降低并发。',
  99991402: '超过配额：检查应用配额与调用量。',
  99991668: '租户无权限：检查应用权限范围并在管理后台审批。',
  99991669: '无权限：检查应用是否具备对应 API 的 scope。',
  99991407: '参数错误：检查 ID/类型/格式是否正确。',
  99991403: '数据不存在：检查对象是否已被删除或 ID 是否正确。',
};

export function createStats() {
  return { total: 0, passed: 0, failed: 0, skipped: 0 };
}

function resolveOpenclawHome() {
  const here = path.dirname(fileURLToPath(import.meta.url));
  return process.env.OPENCLAW_HOME || path.resolve(here, '..', '..', '..', '..', '..');
}

function readJson(filePath) {
  try {
    if (!fs.existsSync(filePath)) return null;
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch {
    return null;
  }
}

function readEnvFile(filePath) {
  if (!fs.existsSync(filePath)) return {};
  const content = fs.readFileSync(filePath, 'utf8');
  const out = {};
  for (const line of content.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const idx = trimmed.indexOf('=');
    if (idx === -1) continue;
    const key = trimmed.slice(0, idx).trim();
    const value = trimmed.slice(idx + 1).trim();
    if (key) out[key] = value;
  }
  return out;
}

function scanLogsForIds(logPaths) {
  const ids = { chatId: undefined, userId: undefined };
  const chatRegex = /oc_[0-9a-z]+/g;
  const userRegex = /ou_[0-9a-z]+/g;
  for (const logPath of logPaths) {
    if (!fs.existsSync(logPath)) continue;
    const content = fs.readFileSync(logPath, 'utf8');
    if (!ids.chatId) {
      const match = content.match(chatRegex);
      if (match && match.length) ids.chatId = match[0];
    }
    if (!ids.userId) {
      const match = content.match(userRegex);
      if (match && match.length) ids.userId = match[0];
    }
    if (ids.chatId && ids.userId) break;
  }
  return ids;
}

function setEnvIfMissing(key, value) {
  if (!process.env[key] && value) process.env[key] = value;
}

export function applyFeishuDefaults() {
  if (process.env.__FEISHU_DEFAULTS_APPLIED === '1') return;
  process.env.__FEISHU_DEFAULTS_APPLIED = '1';

  const openclawHome = resolveOpenclawHome();
  const config = readJson(path.join(openclawHome, 'openclaw.json'));
  const accounts = config?.channels?.feishu?.accounts || {};
  const account = accounts.main || Object.values(accounts).find((item) => item?.enabled);

  setEnvIfMissing('FEISHU_APP_ID', account?.appId);
  setEnvIfMissing('FEISHU_APP_SECRET', account?.appSecret);

  const envVars = readEnvFile(path.join(openclawHome, '.env'));
  setEnvIfMissing('FEISHU_APP_ID', envVars.FEISHU_APP_ID);
  setEnvIfMissing('FEISHU_APP_SECRET', envVars.FEISHU_APP_SECRET);

  const groupKeys = Object.keys(config?.channels?.feishu?.groups || {});
  const chatIdFromConfig = groupKeys.find((key) => key.startsWith('oc_'));
  const userIdFromConfig = groupKeys.find((key) => key.startsWith('ou_'));

  const logIds = scanLogsForIds([
    path.join(openclawHome, 'logs', 'gateway.err.log'),
    path.join(openclawHome, 'logs', 'gateway.log'),
    path.join(openclawHome, 'logs', 'node.log'),
  ]);

  setEnvIfMissing('TEST_CHAT_ID', chatIdFromConfig || logIds.chatId);
  setEnvIfMissing('TEST_USER_ID', userIdFromConfig || logIds.userId);
}

export function logSuiteStart(name) {
  console.log(`\n📦 ${name}`);
  console.log('----------------------------------------');
}

export function logSuiteEnd(name, stats) {
  console.log('');
  console.log(`✅ ${name} 完成`);
  console.log(`  - 总数: ${stats.total}`);
  console.log(`  - 通过: ${stats.passed}`);
  console.log(`  - 失败: ${stats.failed}`);
  console.log(`  - 跳过: ${stats.skipped}`);
}

function missingEnv(keys) {
  return keys.filter((key) => !process.env[key]);
}

function logSelfCheck(context) {
  const { error, response } = context || {};
  const code = response?.code || error?.code;
  const message = response?.error || error?.message || String(error || '');

  console.log('    自查建议:');
  console.log('    - 确认 `FEISHU_APP_ID` / `FEISHU_APP_SECRET` 已正确配置');
  console.log('    - 确认应用已授权对应 API scope，并在管理后台审批通过');
  console.log('    - 确认测试用的 ID / token / 文件路径真实存在');

  if (code && ERROR_HINTS[code]) {
    console.log(`    - 可能原因: ${ERROR_HINTS[code]}`);
  }
  if (message?.includes('Missing FEISHU_APP_ID') || message?.includes('Missing FEISHU_APP_SECRET')) {
    console.log('    - 缺少 FEISHU_APP_ID/FEISHU_APP_SECRET，先设置环境变量再试');
  }
  if (message?.includes('文件不存在')) {
    console.log('    - 文件路径不存在：检查本地文件是否存在或路径是否正确');
  }
}

export async function runCase(stats, options) {
  const {
    name,
    fn,
    requires = [],
    sideEffect = false,
    destructive = false,
  } = options;

  stats.total += 1;

  if (destructive && process.env.ALLOW_DESTRUCTIVE !== '1') {
    console.log(`  [SKIP] ${name} (需要 ALLOW_DESTRUCTIVE=1)`);
    stats.skipped += 1;
    return;
  }

  if (sideEffect && process.env.ALLOW_SIDE_EFFECTS !== '1') {
    console.log(`  [SKIP] ${name} (需要 ALLOW_SIDE_EFFECTS=1)`);
    stats.skipped += 1;
    return;
  }

  const missing = missingEnv(requires);
  if (missing.length) {
    console.log(`  [SKIP] ${name} (缺少环境变量: ${missing.join(', ')})`);
    stats.skipped += 1;
    return;
  }

  try {
    const response = await fn();
    if (response && typeof response === 'object' && 'ok' in response && response.ok === false) {
      console.log(`  [FAIL] ${name} -> ${response.error || 'unknown error'}`);
      stats.failed += 1;
      logSelfCheck({ response });
      return;
    }

    console.log(`  [PASS] ${name}`);
    stats.passed += 1;
  } catch (error) {
    console.log(`  [FAIL] ${name} -> ${error?.message || error}`);
    stats.failed += 1;
    logSelfCheck({ error });
  }
}
