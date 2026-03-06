#!/usr/bin/env node

/**
 * 스마트 메일 요약 - 키워드 기반 분류
 */

const { getAccountConfig, DEFAULT_ACCOUNT, IMPORTANT_KEYWORDS, SPAM_KEYWORDS } = require('./lib/config');
const ImapClient = require('./lib/imap-client');

function parseArgs() {
  const args = process.argv.slice(2);
  const options = { 
    account: DEFAULT_ACCOUNT,
    recent: '24h'
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--account' && args[i + 1]) {
      options.account = args[i + 1];
      i++;
    } else if (args[i] === '--recent' && args[i + 1]) {
      options.recent = args[i + 1];
      i++;
    }
  }

  return options;
}

function parseTimeString(timeStr) {
  const match = timeStr.match(/^(\d+)([mhd])$/);
  if (!match) return 24; // default 24 hours

  const value = parseInt(match[1]);
  const unit = match[2];

  switch (unit) {
    case 'm': return value / 60;
    case 'h': return value;
    case 'd': return value * 24;
    default: return 24;
  }
}

function categorizeMessage(msg) {
  const text = `${msg.subject} ${msg.from}`.toLowerCase();
  
  // 중요 메일 체크
  for (const keyword of IMPORTANT_KEYWORDS) {
    if (text.includes(keyword.toLowerCase())) {
      return 'important';
    }
  }
  
  // 스팸/광고 체크
  for (const keyword of SPAM_KEYWORDS) {
    if (text.includes(keyword.toLowerCase())) {
      return 'spam';
    }
  }
  
  return 'normal';
}

async function main() {
  const options = parseArgs();
  const config = getAccountConfig(options.account);
  const client = new ImapClient(config.imap);

  try {
    console.log(`🔍 ${options.account.toUpperCase()} 메일 요약 생성 중...\n`);
    
    await client.connect();
    const hours = parseTimeString(options.recent);
    const messages = await client.getRecentMessages(hours, 100);
    
    // 읽지 않은 메일만 필터링
    const unreadMessages = messages.filter(msg => !msg.flags.includes('\\Seen'));
    
    // 카테고리별 분류
    const categorized = {
      important: [],
      normal: [],
      spam: []
    };

    unreadMessages.forEach(msg => {
      const category = categorizeMessage(msg);
      categorized[category].push(msg);
    });

    // 출력
    console.log(`📬 읽지 않은 메일 요약 (${options.account.toUpperCase()})`);
    console.log('━'.repeat(50) + '\n');

    // 중요 메일
    console.log(`🔴 중요 (${categorized.important.length}건)`);
    if (categorized.important.length > 0) {
      categorized.important.forEach((msg, idx) => {
        const subject = msg.subject || '(제목 없음)';
        const from = msg.from.split('<')[0].trim();
        console.log(`  ${idx + 1}. ${subject} (${from})`);
      });
    } else {
      console.log('  (없음)');
    }
    console.log('');

    // 일반 메일
    console.log(`🟡 일반 (${categorized.normal.length}건)`);
    if (categorized.normal.length > 0) {
      categorized.normal.slice(0, 10).forEach((msg, idx) => {
        const subject = msg.subject || '(제목 없음)';
        const from = msg.from.split('<')[0].trim();
        console.log(`  ${idx + 1}. ${subject} (${from})`);
      });
      if (categorized.normal.length > 10) {
        console.log(`  ... 외 ${categorized.normal.length - 10}건`);
      }
    } else {
      console.log('  (없음)');
    }
    console.log('');

    // 광고/스팸
    console.log(`🔵 광고/프로모션 (${categorized.spam.length}건)`);
    if (categorized.spam.length > 0) {
      categorized.spam.slice(0, 5).forEach((msg, idx) => {
        const subject = msg.subject || '(제목 없음)';
        console.log(`  ${idx + 1}. ${subject}`);
      });
      if (categorized.spam.length > 5) {
        console.log(`  ... 외 ${categorized.spam.length - 5}건`);
      }
    } else {
      console.log('  (없음)');
    }
    console.log('');

    console.log('━'.repeat(50));
    console.log(`📊 총 ${unreadMessages.length}건 (최근 ${options.recent})`);
    console.log('━'.repeat(50) + '\n');

    await client.disconnect();
  } catch (err) {
    console.error('❌ 오류:', err.message);
    process.exit(1);
  }
}

main().catch(err => {
  console.error('오류:', err.message);
  process.exit(1);
});
