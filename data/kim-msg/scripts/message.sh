#!/usr/bin/env node
/**
 * Kim 消息号发送脚本
 * 用法: message.sh -u <用户名> -m <消息内容>
 * 环境变量: KIM_APP_KEY, KIM_SECRET_KEY
 * 
 * 支持两种接口:
 * - 单用户: /openapi/v2/message/send (username)
 * - 批量用户: /openapi/v2/message/batch/send (usernames 数组)
 * 自动尝试两个接口，哪个成功用哪个
 */

const https = require('https');

const APP_KEY = process.env.KIM_APP_KEY;
const SECRET_KEY = process.env.KIM_SECRET_KEY;
const BASE_URL = 'https://is-gateway.corp.kuaishou.com';

if (!APP_KEY || !SECRET_KEY) {
  console.error('Error: KIM_APP_KEY and KIM_SECRET_KEY must be set');
  console.error('请提供 appKey 和 secretKey');
  process.exit(1);
}

// 解析参数
const args = process.argv.slice(2);
let username = '';
let message = '';

for (let i = 0; i < args.length; i++) {
  if (args[i] === '-u' || args[i] === '--user') {
    username = args[i + 1] ?? '';
    i++;
  } else if (args[i] === '-m' || args[i] === '--message') {
    message = args[i + 1] ?? '';
    i++;
  }
}

if (!username || !message) {
  console.error('用法: message.sh -u <用户名> -m <消息内容>');
  console.error('  -u, --user     目标用户名 (必填)');
  console.error('  -m, --message  消息内容 (必填)');
  process.exit(1);
}

function httpsGet(url) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => resolve(data));
    });
    req.on('error', reject);
  });
}

function httpsPost(url, body, headers) {
  const u = new URL(url);
  const options = {
    hostname: u.hostname,
    port: u.port || 443,
    path: u.pathname + u.search,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(body, 'utf8'),
      ...headers,
    },
  };
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => resolve(data));
    });
    req.on('error', reject);
    req.write(body, 'utf8');
    req.end();
  });
}

async function getAccessToken() {
  const params = new URLSearchParams({ appKey: APP_KEY, secretKey: SECRET_KEY });
  const url = `${BASE_URL}/token/get?${params}`;
  const raw = await httpsGet(url);
  const data = JSON.parse(raw);
  if (data.code !== 0) {
    throw new Error(`获取 accessToken 失败: ${JSON.stringify(data)}`);
  }
  return data.result.accessToken;
}

/**
 * 单用户发送 - /openapi/v2/message/send
 */
async function sendSingleUser(token, targetUser, msg) {
  const url = `${BASE_URL}/openapi/v2/message/send`;
  const payload = JSON.stringify({
    msgType: 'markdown',
    markdown: { content: msg },
    username: targetUser,
  });
  const raw = await httpsPost(url, payload, {
    Authorization: `Bearer ${token}`,
  });
  return JSON.parse(raw);
}

/**
 * 批量用户发送 - /openapi/v2/message/batch/send
 */
async function sendBatchUsers(token, targetUser, msg) {
  const url = `${BASE_URL}/openapi/v2/message/batch/send`;
  const payload = JSON.stringify({
    msgType: 'markdown',
    markdown: { content: msg },
    usernames: [targetUser],
  });
  const raw = await httpsPost(url, payload, {
    Authorization: `Bearer ${token}`,
  });
  return JSON.parse(raw);
}

async function main() {
  console.log(`📤 正在发送消息给用户: ${username}`);
  
  const token = await getAccessToken();
  console.log(`🔑 获取到 accessToken`);
  
  // 尝试单用户接口
  console.log(`📝 尝试单用户接口...`);
  let result = await sendSingleUser(token, username, message);
  
  if (result.code === 0) {
    console.log('✅ 单用户接口发送成功！');
    console.log(JSON.stringify(result, null, 2));
    return;
  }
  
  console.log(`⚠️ 单用户接口失败，尝试批量用户接口...`, result);
  
  // 单用户失败，尝试批量用户接口
  result = await sendBatchUsers(token, username, message);
  
  if (result.code === 0) {
    console.log('✅ 批量用户接口发送成功！');
    console.log(JSON.stringify(result, null, 2));
    return;
  }
  
  console.error('❌ 两个接口都失败了:', result);
  process.exit(1);
}

main().catch((err) => {
  console.error('Error:', err.message);
  process.exit(1);
});