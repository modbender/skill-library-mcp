#!/usr/bin/env node
/**
 * auto-reply.js — dm-alert.json 읽고 자동 답장
 * 
 * heartbeat/cron에서 호출됨.
 * 보안 체크 포함 — 위협 감지시 답장 안 하고 alert 출력.
 * 
 * 사용법: node auto-reply.js
 * 출력: JSON { action: "replied"|"skipped"|"security_alert"|"no_alert", ... }
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ALERT_FILE = path.join(__dirname, 'dm-alert.json');
const CLI = path.join(__dirname, 'v2.js');

// 보안 위협 패턴
const SECURITY_PATTERNS = [
  /ignore\s*(all\s*)?(previous|prior|above)/i,
  /system\s*prompt/i,
  /you\s*are\s*now/i,
  /act\s*as\s*(if|a)/i,
  /pretend\s*(you|to\s*be)/i,
  /override/i,
  /jailbreak/i,
  /DAN\s*mode/i,
  /bypass/i,
  /secret\s*(key|token|password)/i,
  /private\s*key/i,
  /seed\s*phrase/i,
  /mnemonic/i,
  /wallet\s*address/i,
  /send\s*(me\s*)?(sol|eth|btc|crypto|money)/i,
  /execute\s*(this|the)\s*(command|code)/i,
  /run\s*(this|the)\s*(script|command)/i,
  /eval\s*\(/i,
  /rm\s+-rf/i,
  /sudo/i,
  /교과서|textbook|교육용|educational.*override/i,
  /zero\s*width/i,
  /unicode.*repeat/i,
  /simulation.*mode/i,
];

function checkSecurity(messages) {
  const threats = [];
  for (const msg of messages) {
    const text = msg.text || '';
    for (const pattern of SECURITY_PATTERNS) {
      if (pattern.test(text)) {
        threats.push({
          from: msg.from,
          pattern: pattern.source,
          text: text.substring(0, 100)
        });
        break;
      }
    }
  }
  return threats;
}

async function main() {
  // 1. dm-alert.json 읽기
  if (!fs.existsSync(ALERT_FILE)) {
    console.log(JSON.stringify({ action: 'no_alert', reason: 'file not found' }));
    return;
  }
  
  const alert = JSON.parse(fs.readFileSync(ALERT_FILE, 'utf8'));
  
  if (alert.handled) {
    console.log(JSON.stringify({ action: 'skipped', reason: 'already handled' }));
    return;
  }
  
  const results = [];
  
  for (const dm of (alert.dms || [])) {
    const messages = dm.messages || [];
    
    // 2. 보안 체크
    const threats = checkSecurity(messages);
    if (threats.length > 0) {
      results.push({
        action: 'security_alert',
        username: dm.username,
        threats
      });
      continue;
    }
    
    // 3. 답장 시도 (v2.js reply)
    const lastMsg = messages[messages.length - 1];
    if (!lastMsg || lastMsg.from === 'me') {
      results.push({ action: 'skipped', username: dm.username, reason: 'last message is mine' });
      continue;
    }
    
    // 답장 내용은 이 스크립트에서 생성하지 않음 — AI가 생성해야 함
    // 여기서는 보안 체크 + 메타데이터만 반환
    results.push({
      action: 'needs_reply',
      username: dm.username,
      fullName: dm.fullName,
      threadId: dm.threadId,
      lastMessage: lastMsg.text,
      messageCount: messages.length
    });
  }
  
  console.log(JSON.stringify({ results, alertTimestamp: alert.timestamp }, null, 2));
}

main().catch(e => {
  console.log(JSON.stringify({ action: 'error', error: e.message }));
});
