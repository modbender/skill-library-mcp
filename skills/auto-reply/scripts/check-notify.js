#!/usr/bin/env node
/**
 * Instagram DM 알림 체커 (cron용)
 * 
 * 새 메시지가 있으면 요약 출력, 없으면 "no_new" 출력.
 * cron의 systemEvent로 세션에 주입하면 알아서 처리.
 * 
 * 출력:
 *   새 메시지 있을 때: "📩 인스타 DM 알림: [username] '메시지 미리보기...'"
 *   없을 때: "no_new"
 */

const http = require('http');
const https = require('https');
const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

const BROWSER_PORT = process.env.BROWSER_PORT || '18800';
const STATE_FILE = path.join(__dirname, 'dm-state.json');

async function getPageTarget() {
  return new Promise((resolve, reject) => {
    http.get(`http://127.0.0.1:${BROWSER_PORT}/json`, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        const pages = JSON.parse(data);
        // Prefer DM inbox tab, then any non-login instagram tab
        const ig = pages.find(p => p.url && p.url.includes('instagram.com/direct/')) ||
                   pages.find(p => p.url && p.url.includes('instagram.com') && !p.url.includes('/accounts/login'));
        if (ig) resolve(ig.webSocketDebuggerUrl);
        else reject(new Error('No Instagram tab'));
      });
    }).on('error', reject);
  });
}

async function extractCookies() {
  const wsUrl = await getPageTarget();
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl);
    const timeout = setTimeout(() => { ws.close(); reject(new Error('timeout')); }, 5000);
    ws.on('open', () => ws.send(JSON.stringify({ id: 1, method: 'Network.enable', params: {} })));
    ws.on('message', (msg) => {
      const resp = JSON.parse(msg.toString());
      if (resp.id === 1) ws.send(JSON.stringify({ id: 2, method: 'Network.getCookies', params: { urls: ['https://www.instagram.com'] } }));
      if (resp.id === 2) {
        clearTimeout(timeout);
        const cookies = resp.result.cookies;
        ws.close();
        resolve({
          cookieStr: cookies.map(c => `${c.name}=${c.value}`).join('; '),
          csrftoken: cookies.find(c => c.name === 'csrftoken')?.value,
          userId: cookies.find(c => c.name === 'ds_user_id')?.value
        });
      }
    });
    ws.on('error', (e) => { clearTimeout(timeout); reject(e); });
  });
}

async function main() {
  try {
    const cookies = await extractCookies();
    
    const resp = await new Promise((resolve, reject) => {
      const req = https.request({
        hostname: 'www.instagram.com',
        path: '/api/v1/direct_v2/inbox/?persistentBadging=true&folder=&limit=20&thread_message_limit=1',
        method: 'GET',
        headers: {
          'Cookie': cookies.cookieStr,
          'X-CSRFToken': cookies.csrftoken,
          'X-IG-App-ID': '936619743392459',
          'X-Requested-With': 'XMLHttpRequest',
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
          'Accept': '*/*',
          'Referer': 'https://www.instagram.com/direct/inbox/'
        }
      }, (res) => {
        let data = '';
        res.on('data', c => data += c);
        res.on('end', () => {
          try { resolve({ status: res.statusCode, data: JSON.parse(data) }); }
          catch (e) { resolve({ status: res.statusCode, data: null }); }
        });
      });
      req.on('error', reject);
      req.end();
    });
    
    if (resp.status !== 200 || !resp.data?.inbox) {
      console.log('no_new');
      return;
    }
    
    // Load previous state
    let prevState = {};
    try { prevState = JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8')); } catch {}
    
    // Find new messages from others
    const newMessages = [];
    const currentState = {};
    
    for (const t of resp.data.inbox.threads) {
      const lastItem = t.last_permanent_item;
      if (!lastItem) continue;
      
      const username = t.users?.[0]?.username || 'unknown';
      const ts = lastItem.timestamp;
      currentState[username] = ts;
      
      // Skip if message is from me
      if (lastItem.user_id == cookies.userId) continue;
      
      // Skip if we already saw this message
      if (prevState[username] && prevState[username] >= ts) continue;
      
      newMessages.push({
        username,
        fullName: t.users?.[0]?.full_name || '',
        text: (lastItem.text || lastItem.item_type || '').substring(0, 60),
        timestamp: new Date(ts / 1000).toISOString()
      });
    }
    
    // Save state
    fs.writeFileSync(STATE_FILE, JSON.stringify(currentState, null, 2));
    
    if (newMessages.length === 0) {
      console.log('no_new');
      return;
    }
    
    // Format notification
    const lines = newMessages.map(m => 
      `• ${m.fullName || m.username} (@${m.username}): "${m.text}"`
    );
    console.log(`📩 인스타 새 DM ${newMessages.length}건:\n${lines.join('\n')}`);
    
  } catch (e) {
    // 브라우저 꺼져있거나 인스타 탭 없으면 조용히
    console.log('no_new');
  }
}

main();
