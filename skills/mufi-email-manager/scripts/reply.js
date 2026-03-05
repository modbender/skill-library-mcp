#!/usr/bin/env node

/**
 * 자동 답장 (템플릿 기반)
 */

const fs = require('fs');
const path = require('path');
const { getAccountConfig, DEFAULT_ACCOUNT } = require('./lib/config');
const ImapClient = require('./lib/imap-client');
const SmtpClient = require('./lib/smtp-client');

const TEMPLATES_FILE = path.join(__dirname, 'templates.json');

function parseArgs() {
  const args = process.argv.slice(2);
  const options = { 
    account: DEFAULT_ACCOUNT,
    uid: null,
    template: null,
    body: null,
    list: false
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--account' && args[i + 1]) {
      options.account = args[i + 1];
      i++;
    } else if (args[i] === '--uid' && args[i + 1]) {
      options.uid = parseInt(args[i + 1]);
      i++;
    } else if (args[i] === '--template' && args[i + 1]) {
      options.template = args[i + 1];
      i++;
    } else if (args[i] === '--body' && args[i + 1]) {
      options.body = args[i + 1];
      i++;
    } else if (args[i] === '--list') {
      options.list = true;
    }
  }

  return options;
}

function loadTemplates() {
  if (!fs.existsSync(TEMPLATES_FILE)) {
    return {};
  }
  return JSON.parse(fs.readFileSync(TEMPLATES_FILE, 'utf8'));
}

function listTemplates() {
  const templates = loadTemplates();
  
  console.log('📝 사용 가능한 답장 템플릿\n');
  console.log('━'.repeat(50));
  
  Object.entries(templates).forEach(([name, template]) => {
    console.log(`\n🏷️  ${name}`);
    console.log(`   제목: ${template.subject}`);
    console.log(`   내용:`);
    template.body.split('\n').forEach(line => {
      console.log(`     ${line}`);
    });
  });
  
  console.log('\n' + '━'.repeat(50));
  console.log(`\n사용법: node reply.js --uid <UID> --template ${Object.keys(templates)[0]} --account gmail\n`);
}

async function main() {
  const options = parseArgs();

  if (options.list) {
    listTemplates();
    return;
  }

  if (!options.uid) {
    console.error('❌ --uid 옵션이 필요합니다.');
    console.error('예: node reply.js --uid 12345 --template thanks --account gmail');
    process.exit(1);
  }

  if (!options.template && !options.body) {
    console.error('❌ --template 또는 --body 옵션이 필요합니다.');
    console.error('템플릿 목록: node reply.js --list');
    process.exit(1);
  }

  const config = getAccountConfig(options.account);
  const imapClient = new ImapClient(config.imap);
  const smtpClient = new SmtpClient(config.smtp);

  try {
    // 원본 메일 조회
    console.log(`🔍 원본 메일 조회 중... (UID: ${options.uid})\n`);
    await imapClient.connect();
    const messages = await imapClient.fetchMessages([options.uid]);
    
    if (messages.length === 0) {
      console.error('❌ 메일을 찾을 수 없습니다.');
      await imapClient.disconnect();
      process.exit(1);
    }

    const originalMessage = messages[0];
    console.log(`📧 원본 메일:`);
    console.log(`   제목: ${originalMessage.subject}`);
    console.log(`   발신: ${originalMessage.from}\n`);

    // 답장 내용 준비
    let replyBody = options.body;
    let replySubject = `Re: ${originalMessage.subject}`;

    if (options.template) {
      const templates = loadTemplates();
      const template = templates[options.template];
      
      if (!template) {
        console.error(`❌ 템플릿 '${options.template}'을 찾을 수 없습니다.`);
        console.error('템플릿 목록: node reply.js --list');
        await imapClient.disconnect();
        process.exit(1);
      }

      replyBody = template.body.replace('{original_subject}', originalMessage.subject);
      replySubject = template.subject.replace('{original_subject}', originalMessage.subject);
    }

    // 답장 발송
    console.log(`📤 답장 발송 중...\n`);
    await smtpClient.sendMail({
      to: originalMessage.from,
      subject: replySubject,
      text: replyBody
    });

    console.log('✅ 답장을 성공적으로 발송했습니다.\n');
    console.log(`━`.repeat(50));
    console.log(`제목: ${replySubject}`);
    console.log(`수신: ${originalMessage.from}`);
    console.log(`내용:\n${replyBody}`);
    console.log(`━`.repeat(50) + '\n');

    await imapClient.disconnect();
  } catch (err) {
    console.error('❌ 오류:', err.message);
    process.exit(1);
  }
}

main().catch(err => {
  console.error('오류:', err.message);
  process.exit(1);
});
