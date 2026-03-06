#!/usr/bin/env node
/**
 * Google Calendar 일정 추가
 * 사용: node add.js "내일 3시 미팅"
 *       node add.js --title "회의" --start "2026-02-20T10:00:00+09:00" --end "2026-02-20T11:00:00+09:00"
 */

const { getCalendar } = require('./lib/gcal');
const { parseKoreanEvent } = require('./lib/parse-korean');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

const argv = yargs(hideBin(process.argv))
  .option('title', {
    type: 'string',
    description: '일정 제목',
  })
  .option('start', {
    type: 'string',
    description: '시작 시간 (ISO 8601)',
  })
  .option('end', {
    type: 'string',
    description: '종료 시간 (ISO 8601)',
  })
  .option('location', {
    type: 'string',
    description: '장소',
  })
  .option('description', {
    type: 'string',
    description: '설명',
  })
  .option('calendar', {
    type: 'string',
    description: '캘린더 ID',
    default: process.env.GOOGLE_CALENDAR_ID || 'primary',
  })
  .help()
  .argv;

async function addEvent() {
  let event;

  if (argv.title && argv.start) {
    // 명시적 파라미터
    event = {
      summary: argv.title,
      start: { dateTime: argv.start, timeZone: 'Asia/Seoul' },
      end: { dateTime: argv.end || argv.start, timeZone: 'Asia/Seoul' },
      location: argv.location,
      description: argv.description,
    };
  } else if (argv._[0]) {
    // 한국어 자연어 파싱
    const text = argv._.join(' ');
    event = parseKoreanEvent(text);
    if (!event) {
      console.error('❌ 파싱 실패. 형식: "내일 3시 미팅" 또는 --title, --start 사용');
      process.exit(1);
    }
  } else {
    console.error('❌ 일정 정보 필요. --help 참고');
    process.exit(1);
  }

  const calendar = await getCalendar();
  const res = await calendar.events.insert({
    calendarId: argv.calendar,
    requestBody: event,
  });

  console.log(`✅ 일정 추가 완료: ${res.data.summary}`);
  console.log(`   시작: ${res.data.start.dateTime || res.data.start.date}`);
  console.log(`   종료: ${res.data.end.dateTime || res.data.end.date}`);
  console.log(`   ID: ${res.data.id}`);
  console.log(`   링크: ${res.data.htmlLink}`);
}

addEvent().catch(console.error);
