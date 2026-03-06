#!/usr/bin/env node
import { getArg, mustGetArg, whenToRange, tzPreferHeader } from './_lib.mjs';
import { getAccessToken, graphFetch } from './_graph.mjs';

const profile = mustGetArg('profile');
const when = getArg('when', 'today'); // today|tomorrow
const tz = getArg('tz', 'Europe/Vienna');
const top = Number(getArg('top', '50'));

const { start, end } = whenToRange(when);

const qs = new URLSearchParams({
  startDateTime: start.toISOString(),
  endDateTime: end.toISOString(),
  '$top': String(top),
  '$orderby': 'start/dateTime',
  '$select': 'id,subject,start,end,location,organizer,attendees,responseStatus',
});

const url = `https://graph.microsoft.com/v1.0/me/calendarView?${qs.toString()}`;
const token = await getAccessToken(profile, ['Calendars.Read']);
const data = await graphFetch(url, { token, headers: { ...tzPreferHeader(tz) } });

for (const e of data.value || []) {
  console.log(`${e.start?.dateTime} → ${e.end?.dateTime} | ${e.subject} | id=${e.id}`);
}
