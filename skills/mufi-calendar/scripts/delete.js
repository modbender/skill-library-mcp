#!/usr/bin/env node
/**
 * Google Calendar 일정 삭제
 * 사용: node delete.js EVENT_ID
 */

const { getCalendar } = require('./lib/gcal');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

const argv = yargs(hideBin(process.argv))
  .demandCommand(1, '이벤트 ID 필요')
  .option('calendar', {
    type: 'string',
    description: '캘린더 ID',
    default: process.env.GOOGLE_CALENDAR_ID || 'primary',
  })
  .help()
  .argv;

async function deleteEvent() {
  const eventId = argv._[0];
  const calendar = await getCalendar();

  // 삭제 전 확인
  const event = await calendar.events.get({
    calendarId: argv.calendar,
    eventId,
  });

  console.log(`삭제 대상: ${event.data.summary}`);
  console.log(`시작: ${event.data.start.dateTime || event.data.start.date}`);

  await calendar.events.delete({
    calendarId: argv.calendar,
    eventId,
  });

  console.log('✅ 일정 삭제 완료');
}

deleteEvent().catch(console.error);
