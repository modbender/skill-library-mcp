#!/usr/bin/env node

const https = require('https');
const http = require('http');
const crypto = require('crypto');
const { URL } = require('url');

// 配置
const NODE_ID = 'node_41349a7fe0f7c472';
const HUB_URL = 'https://evomap.ai';

// 辅助函数：发送请求
function request(path, method, data) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, HUB_URL);
    const protocol = url.protocol === 'https:' ? https : http;
    
    const options = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname,
      method: method,
      headers: {
        'Content-Type': 'application/json'
      }
    };
    
    const req = protocol.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(body));
        } catch {
          resolve(body);
        }
      });
    });
    
    req.on('error', reject);
    if (data) req.write(JSON.stringify(data));
    req.end();
  });
}

// 规范 JSON 排序
function canonicalJSON(obj) {
  if (obj === null) return 'null';
  if (typeof obj !== 'object') return JSON.stringify(obj);
  if (Array.isArray(obj)) return '[' + obj.map(canonicalJSON).join(',') + ']';
  const keys = Object.keys(obj).sort();
  const pairs = keys.map(k => JSON.stringify(k) + ':' + canonicalJSON(obj[k]));
  return '{' + pairs.join(',') + '}';
}

// 计算 asset_id
function computeAssetId(obj) {
  const json = canonicalJSON(obj);
  return 'sha256:' + crypto.createHash('sha256').update(json).digest('hex');
}

// 命令处理
const args = process.argv.slice(2);
const cmd = args[0];

async function main() {
  switch(cmd) {
    case 'status':
      const status = await request(`/a2a/nodes/${NODE_ID}`, 'GET');
      console.log(JSON.stringify(status, null, 2));
      break;
      
    case 'fetch':
      const result = await request('/a2a/fetch', 'POST', {
        protocol: 'gep-a2a',
        protocol_version: '1.0.0',
        message_type: 'fetch',
        message_id: `msg_${Date.now()}_fetch`,
        sender_id: NODE_ID,
        timestamp: new Date().toISOString(),
        payload: { asset_type: 'Capsule' }
      });
      console.log(JSON.stringify(result, null, 2));
      break;
      
    case 'ranked':
      const ranked = await request(`/a2a/assets/ranked?type=Capsule&limit=${args[1]||10}`, 'GET');
      console.log(JSON.stringify(ranked, null, 2));
      break;
      
    case 'publish':
      // 简化版：需要传入参数
      console.log('Usage: evomap-tools publish --gene "描述" --capsule "内容" --triggers "A,B"');
      break;
      
    default:
      console.log('EvoMap Tools');
      console.log('');
      console.log('Commands:');
      console.log('  status        - 查看节点状态');
      console.log('  fetch         - 获取 Capsule 列表');
      console.log('  ranked [n]    - 获取 Top N Capsule');
      console.log('  publish       - 发布 Capsule');
  }
}

main().catch(console.error);
