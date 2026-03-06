#!/usr/bin/env node

/**
 * 키워드 기반 메일 필터링
 */

const { getAccountConfig, getAllConfiguredAccounts, DEFAULT_ACCOUNT } = require('./lib/config');
const ImapClient = require('./lib/imap-client');

function parseArgs() {
  const args = process.argv.slice(2);
  const options = { 
    account: 'all',
    keywords: '',
    recent: '7d',
    limit: 50
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--account' && args[i + 1]) {
      options.account = args[i + 1];
      i++;
    } else if (args[i] === '--keywords' && args[i + 1]) {
      options.keywords = args[i + 1];
      i++;
    } else if (args[i] === '--recent' && args[i + 1]) {
      options.recent = args[i + 1];
      i++;
    } else if (args[i] === '--limit' && args[i + 1]) {
      options.limit = parseInt(args[i + 1]);
      i++;
    }
  }

  return options;
}

function parseTimeString(timeStr) {
  const match = timeStr.match(/^(\d+)([mhd])$/);
  if (!match) return 7 * 24;

  const value = parseInt(match[1]);
  const unit = match[2];

  switch (unit) {
    case 'm': return value / 60;
    case 'h': return value;
    case 'd': return value * 24;
    default: return 7 * 24;
  }
}

async function filterAccount(accountName, keywords, hours, limit) {
  const config = getAccountConfig(accountName);
  const client = new ImapClient(config.imap);

  try {
    await client.connect();
    
    const keywordList = keywords.split(',').map(k => k.trim());
    const messages = await client.searchByKeywords(keywordList, limit);
    
    // 시간 필터링
    const cutoffTime = Date.now() - hours * 60 * 60 * 1000;
    const recentMessages = messages.filter(msg => new Date(msg.date).getTime() > cutoffTime);
    
    await client.disconnect();
    return recentMessages;
  } catch (err) {
    console.error(`❌ ${accountName} 오류:`, err.message);
    return [];
  }
}

async function main() {
  const options = parseArgs();
  
  if (!options.keywords) {
    console.error('❌ --keywords 옵션이 필요합니다.');
    console.error('예: node filter.js --keywords "결제,청구,승인"');
    process.exit(1);
  }

  const accounts = options.account === 'all' 
    ? getAllConfiguredAccounts() 
    : [options.account];

  if (accounts.length === 0) {
    console.error('❌ 설정된 계정이 없습니다.');
    process.exit(1);
  }

  const hours = parseTimeString(options.recent);
  console.log(`🔍 키워드 필터링 중: "${options.keywords}"`);
  console.log(`   기간: 최근 ${options.recent}\n`);

  let allMatches = [];

  for (const account of accounts) {
    console.log(`📂 ${account.toUpperCase()} 검색 중...`);
    const messages = await filterAccount(account, options.keywords, hours, options.limit);
    
    if (messages.length > 0) {
      allMatches.push({ account, messages });
      console.log(`   ✅ ${messages.length}건 발견\n`);
    } else {
      console.log(`   (일치하는 메일 없음)\n`);
    }
  }

  // 결과 출력
  if (allMatches.length === 0) {
    console.log('━'.repeat(50));
    console.log('🔍 일치하는 메일이 없습니다.');
    console.log('━'.repeat(50) + '\n');
    return;
  }

  console.log('━'.repeat(50));
  console.log('📋 필터링 결과\n');

  allMatches.forEach(({ account, messages }) => {
    console.log(`📬 ${account.toUpperCase()} (${messages.length}건)`);
    messages.forEach((msg, idx) => {
      const date = new Date(msg.date).toLocaleString('ko-KR');
      const subject = msg.subject || '(제목 없음)';
      const from = msg.from.split('<')[0].trim();
      
      console.log(`  ${idx + 1}. [${date}]`);
      console.log(`     ${subject}`);
      console.log(`     발신: ${from}`);
      console.log(`     UID: ${msg.uid}`);
      console.log('');
    });
  });

  const totalCount = allMatches.reduce((sum, { messages }) => sum + messages.length, 0);
  console.log('━'.repeat(50));
  console.log(`📊 총 ${totalCount}건 발견`);
  console.log('━'.repeat(50) + '\n');
}

main().catch(err => {
  console.error('오류:', err.message);
  process.exit(1);
});
