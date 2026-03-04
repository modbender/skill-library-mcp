#!/usr/bin/env node
import { getArg, mustGetArg, tzPreferHeader } from './_lib.mjs';
import { getAccessToken, graphFetch } from './_graph.mjs';

const profile = mustGetArg('profile');
const id = mustGetArg('id');
const tz = getArg('tz', 'Europe/Vienna');

const url = `https://graph.microsoft.com/v1.0/me/events/${encodeURIComponent(id)}?$select=subject,start,end,attendees,organizer,location`;
const token = await getAccessToken(profile, ['Calendars.Read']);
const e = await graphFetch(url, { token, headers: { ...tzPreferHeader(tz) } });

console.log(`subject: ${e.subject}`);
console.log(`start: ${e.start?.dateTime} (${e.start?.timeZone})`);
console.log(`end:   ${e.end?.dateTime} (${e.end?.timeZone})`);

const attendees = (e.attendees || []).map(a => ({
  name: a.emailAddress?.name,
  address: a.emailAddress?.address,
  type: a.type,
  response: a.status?.response,
  time: a.status?.time,
}));

console.log('attendees:', JSON.stringify(attendees, null, 2));
