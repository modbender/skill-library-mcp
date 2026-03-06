#!/usr/bin/env node
import { getArg, mustGetArg, tzPreferHeader } from './_lib.mjs';
import { getAccessToken, graphFetch } from './_graph.mjs';

const profile = mustGetArg('profile');
const id = mustGetArg('id');
const start = mustGetArg('start'); // YYYY-MM-DDTHH:mm
const end = mustGetArg('end');
const tz = getArg('tz', 'Europe/Vienna');

const patch = {
  start: { dateTime: start, timeZone: tz },
  end: { dateTime: end, timeZone: tz },
};

const url = `https://graph.microsoft.com/v1.0/me/events/${encodeURIComponent(id)}`;
const token = await getAccessToken(profile, ['Calendars.ReadWrite']);
const updated = await graphFetch(url, {
  method: 'PATCH',
  token,
  headers: {
    'Content-Type': 'application/json',
    ...tzPreferHeader(tz),
  },
  body: JSON.stringify(patch),
});

console.log(`OK: moved event ${updated.id}`);
console.log(`start: ${updated.start?.dateTime} (${updated.start?.timeZone})`);
console.log(`end:   ${updated.end?.dateTime} (${updated.end?.timeZone})`);
