#!/usr/bin/env node
/**
 * OpenClaw Messenger — 다른 OpenClaw 인스턴스에 메시지 전송
 * 
 * 방식: 상대방의 Gateway에 WebSocket으로 연결하여 시스템 이벤트 전송
 * 
 * 사용법:
 *   node messenger.js send --url <gateway-url> --token <token> --message "안녕!"
 *   node messenger.js listen --port <port>
 *   node messenger.js contacts list
 *   node messenger.js contacts add --name <name> --url <url> --token <token>
 */

const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');
const http = require('http');

const CONTACTS_FILE = path.join(__dirname, '..', 'contacts.json');

// ═══════════════════════════════════════
// Contacts Management
// ═══════════════════════════════════════

function loadContacts() {
  if (!fs.existsSync(CONTACTS_FILE)) return {};
  return JSON.parse(fs.readFileSync(CONTACTS_FILE, 'utf-8'));
}

function saveContacts(contacts) {
  fs.writeFileSync(CONTACTS_FILE, JSON.stringify(contacts, null, 2));
}

function addContact(name, url, token, description = '') {
  const contacts = loadContacts();
  contacts[name] = { url, token, description, addedAt: new Date().toISOString() };
  saveContacts(contacts);
  console.log(`✅ 연락처 추가: ${name} (${url})`);
}

function listContacts() {
  const contacts = loadContacts();
  const entries = Object.entries(contacts);
  if (entries.length === 0) {
    console.log('📭 등록된 연락처 없음');
    console.log('추가: node messenger.js contacts add --name <이름> --url <gateway-url> --token <토큰>');
    return;
  }
  console.log(`📋 연락처 (${entries.length}개)\n`);
  for (const [name, info] of entries) {
    console.log(`  👤 ${name}`);
    console.log(`     URL: ${info.url}`);
    console.log(`     설명: ${info.description || '-'}`);
    console.log(`     추가일: ${info.addedAt || '-'}`);
    console.log('');
  }
}

function removeContact(name) {
  const contacts = loadContacts();
  if (!contacts[name]) {
    console.log(`❌ 연락처 '${name}' 없음`);
    return;
  }
  delete contacts[name];
  saveContacts(contacts);
  console.log(`✅ 연락처 삭제: ${name}`);
}

// ═══════════════════════════════════════
// Send Message
// ═══════════════════════════════════════

async function sendMessage(targetUrl, token, message, from = 'unknown') {
  return new Promise((resolve, reject) => {
    const wsUrl = targetUrl.replace(/^http/, 'ws');
    const fullUrl = `${wsUrl}?token=${encodeURIComponent(token)}`;
    
    console.log(`📤 전송 중: ${targetUrl}`);
    console.log(`   From: ${from}`);
    console.log(`   Message: ${message.slice(0, 100)}${message.length > 100 ? '...' : ''}`);
    
    const ws = new WebSocket(fullUrl);
    let responded = false;
    
    const timeout = setTimeout(() => {
      if (!responded) {
        responded = true;
        ws.close();
        reject(new Error('타임아웃 (10초)'));
      }
    }, 10000);
    
    ws.on('open', () => {
      // 시스템 이벤트로 메시지 전송
      const payload = {
        type: 'system_event',
        event: 'openclaw_message',
        data: {
          from,
          message,
          timestamp: new Date().toISOString(),
        }
      };
      ws.send(JSON.stringify(payload));
      
      // 잠시 대기 후 종료
      setTimeout(() => {
        if (!responded) {
          responded = true;
          clearTimeout(timeout);
          ws.close();
          console.log('✅ 전송 완료');
          resolve(true);
        }
      }, 1000);
    });
    
    ws.on('error', (err) => {
      if (!responded) {
        responded = true;
        clearTimeout(timeout);
        console.log(`❌ 연결 실패: ${err.message}`);
        reject(err);
      }
    });
    
    ws.on('close', () => {
      if (!responded) {
        responded = true;
        clearTimeout(timeout);
        resolve(true);
      }
    });
  });
}

async function sendToContact(name, message, from) {
  const contacts = loadContacts();
  if (!contacts[name]) {
    console.log(`❌ 연락처 '${name}' 없음`);
    console.log('등록된 연락처:');
    listContacts();
    return;
  }
  const { url, token } = contacts[name];
  await sendMessage(url, token, message, from);
}

// ═══════════════════════════════════════
// Listen for Messages (Webhook Receiver)
// ═══════════════════════════════════════

function startListener(port = 19900) {
  const messages = [];
  
  const server = http.createServer((req, res) => {
    if (req.method === 'POST' && req.url === '/message') {
      let body = '';
      req.on('data', chunk => body += chunk);
      req.on('end', () => {
        try {
          const msg = JSON.parse(body);
          msg.receivedAt = new Date().toISOString();
          messages.push(msg);
          console.log(`\n📨 새 메시지!`);
          console.log(`   From: ${msg.from || 'unknown'}`);
          console.log(`   Message: ${msg.message}`);
          console.log(`   Time: ${msg.receivedAt}`);
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ ok: true }));
        } catch (e) {
          res.writeHead(400);
          res.end(JSON.stringify({ error: 'Invalid JSON' }));
        }
      });
    } else if (req.method === 'GET' && req.url === '/messages') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(messages));
    } else if (req.method === 'GET' && req.url === '/health') {
      res.writeHead(200);
      res.end(JSON.stringify({ ok: true, messages: messages.length }));
    } else {
      res.writeHead(404);
      res.end('Not found');
    }
  });
  
  server.listen(port, () => {
    console.log(`👂 메시지 수신 대기 중: http://localhost:${port}`);
    console.log(`   POST /message — 메시지 수신`);
    console.log(`   GET /messages — 수신 내역`);
    console.log(`   GET /health — 상태 확인`);
  });
}

// ═══════════════════════════════════════
// Ping (연결 테스트)
// ═══════════════════════════════════════

async function ping(targetUrl) {
  return new Promise((resolve) => {
    const wsUrl = targetUrl.replace(/^http/, 'ws');
    console.log(`🏓 핑: ${targetUrl}`);
    
    const ws = new WebSocket(wsUrl);
    const start = Date.now();
    
    const timeout = setTimeout(() => {
      ws.close();
      console.log('❌ 타임아웃 (5초)');
      resolve(false);
    }, 5000);
    
    ws.on('open', () => {
      const ms = Date.now() - start;
      clearTimeout(timeout);
      ws.close();
      console.log(`✅ 응답: ${ms}ms`);
      resolve(true);
    });
    
    ws.on('error', (err) => {
      clearTimeout(timeout);
      console.log(`❌ 연결 실패: ${err.message}`);
      resolve(false);
    });
  });
}

// ═══════════════════════════════════════
// CLI
// ═══════════════════════════════════════

const args = process.argv.slice(2);
const cmd = args[0];
const subcmd = args[1];

function getArg(flag) {
  const idx = args.indexOf(flag);
  return idx >= 0 && args[idx + 1] ? args[idx + 1] : null;
}

(async () => {
  switch (cmd) {
    case 'send': {
      const name = getArg('--to') || getArg('--name');
      const url = getArg('--url');
      const token = getArg('--token');
      const message = getArg('--message') || getArg('-m');
      const from = getArg('--from') || 'Tames';
      
      if (!message) {
        console.log('❌ --message 필수');
        break;
      }
      
      if (name) {
        await sendToContact(name, message, from);
      } else if (url && token) {
        await sendMessage(url, token, message, from);
      } else {
        console.log('❌ --to <연락처이름> 또는 --url <url> --token <token> 필요');
      }
      break;
    }
    
    case 'contacts': {
      switch (subcmd) {
        case 'add': {
          const name = getArg('--name');
          const url = getArg('--url');
          const token = getArg('--token');
          const desc = getArg('--desc') || '';
          if (!name || !url || !token) {
            console.log('❌ --name, --url, --token 모두 필요');
            break;
          }
          addContact(name, url, token, desc);
          break;
        }
        case 'remove': {
          const name = getArg('--name');
          if (!name) { console.log('❌ --name 필요'); break; }
          removeContact(name);
          break;
        }
        case 'list':
        default:
          listContacts();
          break;
      }
      break;
    }
    
    case 'listen': {
      const port = parseInt(getArg('--port') || '19900');
      startListener(port);
      break;
    }
    
    case 'ping': {
      const url = getArg('--url');
      const name = getArg('--to');
      if (name) {
        const contacts = loadContacts();
        if (contacts[name]) {
          await ping(contacts[name].url);
        } else {
          console.log(`❌ 연락처 '${name}' 없음`);
        }
      } else if (url) {
        await ping(url);
      } else {
        console.log('❌ --url 또는 --to 필요');
      }
      break;
    }
    
    default:
      console.log(`
📬 OpenClaw Messenger — 다른 OpenClaw에게 메시지 보내기

사용법:
  node messenger.js send --to <연락처> --message "안녕!"
  node messenger.js send --url <url> --token <token> --message "안녕!" --from "Tames"
  node messenger.js contacts list
  node messenger.js contacts add --name <이름> --url <url> --token <token> --desc "설명"
  node messenger.js contacts remove --name <이름>
  node messenger.js ping --to <연락처>
  node messenger.js ping --url <url>
  node messenger.js listen --port 19900
`);
  }
})().catch(e => {
  console.error(`❌ 오류: ${e.message}`);
  process.exit(1);
});
