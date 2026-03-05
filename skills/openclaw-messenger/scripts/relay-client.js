#!/usr/bin/env node
/**
 * OpenClaw Relay Client — 중계서버를 통한 메시징
 * 
 * 사용법:
 *   node relay-client.js register --id tames --name "Tames" --secret mysecret
 *   node relay-client.js send --to 친구 --message "안녕!"
 *   node relay-client.js poll
 *   node relay-client.js users
 *   node relay-client.js listen   (실시간 수신)
 */

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const WebSocket = require('ws');

const CONFIG_FILE = path.join(__dirname, '..', 'relay-config.json');
const DEFAULT_RELAY = 'http://localhost:3900';

function loadConfig() {
  if (!fs.existsSync(CONFIG_FILE)) return {};
  return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
}

function saveConfig(config) {
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}

function getRelay() {
  const config = loadConfig();
  return config.relay || DEFAULT_RELAY;
}

function fetch(url, opts = {}) {
  return new Promise((resolve, reject) => {
    const mod = url.startsWith('https') ? https : http;
    const urlObj = new URL(url);
    const reqOpts = {
      hostname: urlObj.hostname,
      port: urlObj.port,
      path: urlObj.pathname + urlObj.search,
      method: opts.method || 'GET',
      headers: { 'Content-Type': 'application/json', ...opts.headers },
    };
    
    const req = mod.request(reqOpts, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, data: JSON.parse(data) }); }
        catch { resolve({ status: res.statusCode, data }); }
      });
    });
    req.on('error', reject);
    if (opts.body) req.write(JSON.stringify(opts.body));
    req.end();
  });
}

const args = process.argv.slice(2);
const cmd = args[0];
function getArg(flag) {
  const idx = args.indexOf(flag);
  return idx >= 0 && args[idx + 1] ? args[idx + 1] : null;
}

(async () => {
  const config = loadConfig();
  const relay = getArg('--relay') || config.relay || DEFAULT_RELAY;

  switch (cmd) {
    case 'setup': {
      const relayUrl = getArg('--relay') || DEFAULT_RELAY;
      const cfg = loadConfig();
      cfg.relay = relayUrl;
      saveConfig(cfg);
      console.log(`✅ 릴레이 서버: ${relayUrl}`);
      break;
    }

    case 'register': {
      const id = getArg('--id');
      const name = getArg('--name') || id;
      const secret = getArg('--secret');
      if (!id || !secret) {
        console.log('❌ --id, --secret 필수');
        break;
      }
      
      const res = await fetch(`${relay}/register`, {
        method: 'POST',
        body: { id, name, secret },
      });
      
      if (res.status === 201) {
        const cfg = loadConfig();
        cfg.relay = relay;
        cfg.id = id;
        cfg.name = name;
        cfg.secret = secret;
        saveConfig(cfg);
        console.log(`✅ 등록 완료: ${id} (${name})`);
        console.log(`   릴레이: ${relay}`);
      } else {
        console.log(`❌ ${res.data.error || '등록 실패'}`);
      }
      break;
    }

    case 'send': {
      const to = getArg('--to');
      const message = getArg('--message') || getArg('-m');
      if (!to || !message) {
        console.log('❌ --to, --message 필수');
        break;
      }
      if (!config.id || !config.secret) {
        console.log('❌ 먼저 register 하세요');
        break;
      }
      
      const res = await fetch(`${relay}/send`, {
        method: 'POST',
        body: { from: config.id, to, message, secret: config.secret },
      });
      
      if (res.data.ok) {
        console.log(`✅ ${config.id} → ${to}: ${message}`);
      } else {
        console.log(`❌ ${res.data.error || '전송 실패'}`);
      }
      break;
    }

    case 'poll': {
      if (!config.id || !config.secret) {
        console.log('❌ 먼저 register 하세요');
        break;
      }
      
      const res = await fetch(`${relay}/poll?id=${config.id}&secret=${config.secret}`);
      
      if (res.data.count === 0) {
        console.log('📭 새 메시지 없음');
      } else {
        console.log(`📨 ${res.data.count}개 메시지:\n`);
        for (const msg of res.data.messages) {
          console.log(`  💬 [${msg.fromName || msg.from}] ${msg.message}`);
          console.log(`     ${msg.timestamp}\n`);
        }
      }
      break;
    }

    case 'users': {
      const res = await fetch(`${relay}/users`);
      if (res.data.users) {
        console.log(`👥 사용자 (${res.data.count}명):\n`);
        for (const u of res.data.users) {
          const status = u.online ? '🟢 온라인' : '⚪ 오프라인';
          console.log(`  ${status} ${u.name} (@${u.id})`);
        }
      }
      break;
    }

    case 'listen': {
      if (!config.id || !config.secret) {
        console.log('❌ 먼저 register 하세요');
        break;
      }
      
      const wsUrl = relay.replace(/^http/, 'ws') + `/ws?id=${config.id}&secret=${config.secret}`;
      console.log(`👂 실시간 수신 대기... (${config.id})`);
      
      const ws = new WebSocket(wsUrl);
      
      ws.on('message', (data) => {
        const msg = JSON.parse(data.toString());
        if (msg.type === 'message') {
          console.log(`\n📨 [${msg.data.fromName || msg.data.from}] ${msg.data.message}`);
          console.log(`   ${msg.data.timestamp}`);
        } else if (msg.type === 'connected') {
          console.log(`✅ 연결됨: ${msg.name} (@${msg.id})`);
        }
      });
      
      ws.on('close', () => console.log('🔌 연결 종료'));
      ws.on('error', (e) => console.log('❌', e.message));
      
      // 종료 안 되게
      process.on('SIGINT', () => { ws.close(); process.exit(); });
      break;
    }

    default:
      console.log(`
📬 OpenClaw Relay Client — 카톡처럼 메시지 주고받기

설정:
  node relay-client.js setup --relay http://relay-server:3900

등록:
  node relay-client.js register --id tames --name "Tames" --secret 비밀키

메시지:
  node relay-client.js send --to 친구ID --message "안녕!"
  node relay-client.js poll              (수신 확인)
  node relay-client.js listen            (실시간 수신)
  node relay-client.js users             (사용자 목록)
`);
  }
})().catch(e => console.error('❌', e.message));
