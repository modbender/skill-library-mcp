#!/usr/bin/env node
/**
 * daily-sales-digest/scripts/alert.js
 * 매출 이상 탐지 및 즉시 알림
 * 
 * 사용법:
 *   node alert.js --threshold 0.3 --deliver discord
 *   node alert.js --date yesterday
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 설정 파일 로드
function loadConfig() {
  const configPath = path.join(process.env.HOME, '.openclaw/workspace/config/daily-sales-digest.json');
  
  if (!fs.existsSync(configPath)) {
    console.error('❌ 설정 파일이 없습니다:', configPath);
    process.exit(1);
  }
  
  return JSON.parse(fs.readFileSync(configPath, 'utf8'));
}

// 날짜 파싱
function parseDate(dateStr) {
  if (dateStr === 'today') {
    return new Date();
  } else if (dateStr === 'yesterday') {
    const d = new Date();
    d.setDate(d.getDate() - 1);
    return d;
  } else {
    return new Date(dateStr);
  }
}

function formatDate(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

// 데이터 로드
function loadData(config, date) {
  const dataDir = config.dataDir.replace('~', process.env.HOME);
  const dateStr = formatDate(date);
  const filePath = path.join(dataDir, `${dateStr}.json`);
  
  if (!fs.existsSync(filePath)) {
    return null;
  }
  
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

// 변화율 계산
function calcChange(current, previous) {
  if (!previous || previous === 0) return null;
  return ((current - previous) / previous);
}

// 이상 탐지
function detectAnomaly(config, date, threshold) {
  const data = loadData(config, date);
  
  if (!data) {
    console.log('⚠️  데이터가 없습니다:', formatDate(date));
    return null;
  }
  
  // 전일 데이터
  const yesterday = new Date(date);
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayData = loadData(config, yesterday);
  
  if (!yesterdayData) {
    console.log('⚠️  비교할 전일 데이터가 없습니다.');
    return null;
  }
  
  const change = calcChange(data.total.revenue, yesterdayData.total.revenue);
  
  if (change === null) {
    return null;
  }
  
  // 임계값 초과 여부
  if (Math.abs(change) > threshold) {
    return {
      date: data.date,
      current: data.total,
      previous: yesterdayData.total,
      change,
      threshold,
      type: change > 0 ? 'surge' : 'drop'
    };
  }
  
  return null;
}

// 알림 메시지 생성
function formatAlert(alert) {
  const emoji = alert.type === 'surge' ? '🚀' : '⚠️';
  const verb = alert.type === 'surge' ? '급증' : '급감';
  const sign = alert.change >= 0 ? '+' : '';
  
  let message = `${emoji} 매출 이상 감지!\n\n`;
  message += `${alert.date} 매출이 전일 대비 ${Math.abs(alert.change * 100).toFixed(1)}% ${verb}했습니다.\n\n`;
  message += `💰 오늘: ₩${alert.current.revenue.toLocaleString()}\n`;
  message += `💰 어제: ₩${alert.previous.revenue.toLocaleString()}\n`;
  message += `📈 변화: ${sign}₩${(alert.current.revenue - alert.previous.revenue).toLocaleString()} (${sign}${(alert.change * 100).toFixed(1)}%)\n`;
  message += `\n원인 분석이 필요합니다.`;
  
  return message;
}

// Discord 전송
function deliverDiscord(config, message) {
  if (!config.delivery.discord.enabled) {
    console.error('❌ Discord 전송이 비활성화되어 있습니다.');
    return;
  }
  
  const channelId = config.delivery.discord.channelId;
  
  try {
    execSync(`openclaw message send --channel discord --target "${channelId}" --message "${message.replace(/"/g, '\\"')}"`, {
      stdio: 'inherit'
    });
    console.log('✅ Discord 알림 전송 완료');
  } catch (err) {
    console.error('❌ Discord 전송 실패:', err.message);
  }
}

// 메인 실행
function main() {
  const args = process.argv.slice(2);
  
  let dateStr = 'yesterday';
  let threshold = null;
  let deliver = null;
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--date' && i + 1 < args.length) {
      dateStr = args[i + 1];
      i++;
    } else if (args[i] === '--threshold' && i + 1 < args.length) {
      threshold = parseFloat(args[i + 1]);
      i++;
    } else if (args[i] === '--deliver' && i + 1 < args.length) {
      deliver = args[i + 1].split(',');
      i++;
    }
  }
  
  const config = loadConfig();
  const date = parseDate(dateStr);
  
  if (threshold === null) {
    threshold = config.alerts.threshold || 0.3;
  }
  
  console.log(`🔍 이상 탐지 중... (임계값: ±${(threshold * 100).toFixed(0)}%)`);
  
  const alert = detectAnomaly(config, date, threshold);
  
  if (!alert) {
    console.log('✅ 정상 범위 내입니다.');
    return;
  }
  
  const message = formatAlert(alert);
  console.log('\n' + message);
  
  // 전송
  if (deliver) {
    if (deliver.includes('discord')) {
      deliverDiscord(config, message);
    }
  } else if (config.alerts.enabled && config.alerts.channels) {
    // 설정 파일의 기본 채널로 전송
    if (config.alerts.channels.includes('discord')) {
      deliverDiscord(config, message);
    }
  }
}

main();
