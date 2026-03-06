#!/usr/bin/env node
/**
 * 오늘 일정 리마인더 (cron용)
 * 사용: node remind.js [--channel DISCORD_CHANNEL_ID]
 */

const { getCalendar } = require('./lib/gcal');
const { execSync } = require('child_process');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

const argv = yargs(hideBin(process.argv))
  .option('channel', {
    type: 'string',
    description: 'Discord 채널 ID (메시지 전송)',
  })
  .option('calendar', {
    type: 'string',
    description: '캘린더 ID',
    default: process.env.GOOGLE_CALENDAR_ID || 'primary',
  })
  .help()
  .argv;

async function remind() {
  const calendar = await getCalendar();

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  const res = await calendar.events.list({
    calendarId: argv.calendar,
    timeMin: today.toISOString(),
    timeMax: tomorrow.toISOString(),
    singleEvents: true,
    orderBy: 'startTime',
  });

  const events = res.data.items || [];

  if (events.length === 0) {
    console.log('📅 오늘 일정 없음');
    return;
  }

  // 메시지 생성
  const dayOfWeek = ['일', '월', '화', '수', '목', '금', '토'][today.getDay()];
  const dateStr = today.toISOString().split('T')[0];
  let message = `📅 오늘 일정 (${dateStr} ${dayOfWeek})\n\n`;

  events.forEach(event => {
    const start = event.start.dateTime || event.start.date;
    if (event.start.dateTime) {
      const time = new Date(start).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', hour12: false });
      message += `⏰ ${time} - ${event.summary}\n`;
      if (event.location) message += `   📍 ${event.location}\n`;
    } else {
      message += `📌 종일 - ${event.summary}\n`;
    }
  });

  console.log(message);

  // Discord 전송
  if (argv.channel) {
    try {
      execSync(`openclaw message send --target "${argv.channel}" --message "${message.replace(/"/g, '\\"')}"`, {
        stdio: 'inherit',
      });
      console.log('\n✅ Discord 전송 완료');
    } catch (err) {
      console.error('❌ Discord 전송 실패:', err.message);
    }
  }
}

remind().catch(console.error);
