#!/usr/bin/env node
/**
 * Google Calendar 일정 수정
 * 사용: node update.js EVENT_ID --title "새 제목" --start "2026-02-20T15:00:00+09:00"
 */

const { getCalendar } = require('./lib/gcal');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

const argv = yargs(hideBin(process.argv))
  .demandCommand(1, '이벤트 ID 필요')
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

async function updateEvent() {
  const eventId = argv._[0];
  const calendar = await getCalendar();

  // 기존 이벤트 조회
  const existing = await calendar.events.get({
    calendarId: argv.calendar,
    eventId,
  });

  // 수정할 필드만 업데이트
  const updates = {};
  if (argv.title) updates.summary = argv.title;
  if (argv.start) updates.start = { dateTime: argv.start, timeZone: 'Asia/Seoul' };
  if (argv.end) updates.end = { dateTime: argv.end, timeZone: 'Asia/Seoul' };
  if (argv.location) updates.location = argv.location;
  if (argv.description) updates.description = argv.description;

  const res = await calendar.events.patch({
    calendarId: argv.calendar,
    eventId,
    requestBody: updates,
  });

  console.log(`✅ 일정 수정 완료: ${res.data.summary}`);
  console.log(`   시작: ${res.data.start.dateTime || res.data.start.date}`);
  console.log(`   종료: ${res.data.end.dateTime || res.data.end.date}`);
}

updateEvent().catch(console.error);
