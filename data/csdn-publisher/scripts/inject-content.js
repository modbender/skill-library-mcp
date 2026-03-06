#!/usr/bin/env node
/**
 * CSDN Content Injector
 * 
 * 通过 CDP (Chrome DevTools Protocol) 将 Markdown 内容注入 CSDN 编辑器。
 * 解决了 browser evaluate 参数长度限制、execCommand 换行符丢失、
 * clipboard API 无权限等问题。
 * 
 * 用法：
 *   node inject-content.js <markdown-file> [--cdp-port 18800]
 * 
 * 前置条件：
 *   - OpenClaw browser (profile=openclaw) 已启动
 *   - 已打开 CSDN 编辑器页面 (https://editor.csdn.net/md)
 *   - npm install ws (或全局安装)
 * 
 * 原理：
 *   1. 通过 CDP /json 接口找到 CSDN 编辑器 tab
 *   2. 用 Runtime.evaluate + JSON.stringify 将内容存入 window 变量（绕过长度限制）
 *   3. 用 editor.textContent = content + dispatchEvent('input') 注入（cledit 编辑器兼容）
 */

const fs = require('fs');
const http = require('http');
const path = require('path');

// Parse args
const args = process.argv.slice(2);
let filePath = null;
let cdpPort = 18800;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--cdp-port' && args[i + 1]) {
    cdpPort = parseInt(args[i + 1]);
    i++;
  } else if (!filePath) {
    filePath = args[i];
  }
}

if (!filePath) {
  console.error('Usage: node inject-content.js <markdown-file> [--cdp-port 18800]');
  process.exit(1);
}

// Read content, strip frontmatter if present
let content = fs.readFileSync(filePath, 'utf-8');
if (content.startsWith('---')) {
  const endIdx = content.indexOf('---', 3);
  if (endIdx !== -1) {
    content = content.slice(endIdx + 3).replace(/^\n+/, '');
  }
}
console.log(`Content: ${content.length} chars, ${content.split('\n').length} lines`);

// CDP helpers
const cdpUrl = `http://127.0.0.1:${cdpPort}`;

function getTargets() {
  return new Promise((resolve, reject) => {
    http.get(`${cdpUrl}/json`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(JSON.parse(data)));
    }).on('error', reject);
  });
}

let ws = null;
let msgId = 0;

function connect(wsUrl) {
  const WebSocket = require('ws');
  return new Promise((resolve, reject) => {
    ws = new WebSocket(wsUrl);
    ws.on('open', resolve);
    ws.on('error', reject);
  });
}

function cdp(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++msgId;
    ws.send(JSON.stringify({ id, method, params }));
    const handler = (msg) => {
      const data = JSON.parse(msg.toString());
      if (data.id === id) {
        ws.removeListener('message', handler);
        resolve(data);
      }
    };
    ws.on('message', handler);
    setTimeout(() => { ws.removeListener('message', handler); reject(new Error('CDP timeout')); }, 15000);
  });
}

function evaluate(expression) {
  return cdp('Runtime.evaluate', { expression, returnByValue: true });
}

async function main() {
  // Find CSDN editor tab
  const targets = await getTargets();
  const page = targets.find(t => t.url.includes('editor.csdn.net'));
  if (!page) {
    console.error('ERROR: CSDN editor tab not found. Make sure https://editor.csdn.net/md is open.');
    process.exit(1);
  }
  console.log('Found tab:', page.url);

  await connect(page.webSocketDebuggerUrl);

  // Step 1: Store content in window variable via CDP
  // JSON.stringify handles all escaping (quotes, newlines, unicode)
  const escaped = JSON.stringify(content);
  let r = await evaluate(`window.__csdnContent = ${escaped}; 'stored ' + window.__csdnContent.length + ' chars'`);
  if (!r.result?.value) {
    console.error('ERROR: Failed to store content:', JSON.stringify(r));
    process.exit(1);
  }
  console.log('Store:', r.result.value);

  // Step 2: Clear editor and inject content
  r = await evaluate(`(function(){
    var editor = document.querySelector('pre.editor__inner');
    if (!editor) return 'ERROR: editor element not found';
    editor.focus();
    document.execCommand('selectAll');
    document.execCommand('delete');
    editor.textContent = window.__csdnContent;
    editor.dispatchEvent(new Event('input', {bubbles: true}));
    return 'injected ' + editor.textContent.length + ' chars';
  })()`);
  console.log('Inject:', r.result?.value || JSON.stringify(r));

  // Step 3: Wait for editor to process, then verify
  await new Promise(r => setTimeout(r, 1500));
  r = await evaluate(`(function(){
    var t = document.body.innerText;
    var m = t.match(/Markdown\\s+(\\d+)\\s+.+?(\\d+)\\s+行/);
    if (m) return 'OK: ' + m[1] + ' words, ' + m[2] + ' lines';
    var i = t.indexOf('Markdown');
    return 'Status: ' + (i >= 0 ? t.substring(i, i + 60) : 'not found');
  })()`);
  console.log('Verify:', r.result?.value || JSON.stringify(r));

  // Cleanup
  await evaluate('delete window.__csdnContent; "cleaned"');
  ws.close();
  console.log('Done.');
}

main().catch(e => {
  console.error('FATAL:', e.message);
  if (ws) ws.close();
  process.exit(1);
});
