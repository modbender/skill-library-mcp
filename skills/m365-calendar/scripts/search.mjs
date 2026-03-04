#!/usr/bin/env node
import { getArg, mustGetArg, whenToRange, tzPreferHeader } from './_lib.mjs';
import { getAccessToken, graphFetch } from './_graph.mjs';

const profile = mustGetArg('profile');
const query = mustGetArg('query');
const when = getArg('when', 'tomorrow');
const tz = getArg('tz', 'Europe/Vienna');

const { start, end } = whenToRange(when);

const qs = new URLSearchParams({
  startDateTime: start.toISOString(),
  endDateTime: end.toISOString(),
  '$top': '50',
  '$orderby': 'start/dateTime',
  '$select': 'id,subject,start,end,attendees',
});

const url = `https://graph.microsoft.com/v1.0/me/calendarView?${qs.toString()}`;
const token = await getAccessToken(profile, ['Calendars.Read']);
const data = await graphFetch(url, { token, headers: { ...tzPreferHeader(tz) } });

const q = query.toLowerCase();
const hits = (data.value || []).filter(e => (e.subject || '').toLowerCase().includes(q));
for (const e of hits) {
  console.log(`${e.start?.dateTime} → ${e.end?.dateTime} | ${e.subject} | id=${e.id}`);
}
if (!hits.length) process.exitCode = 2;
