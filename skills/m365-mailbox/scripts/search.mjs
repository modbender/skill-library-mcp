#!/usr/bin/env node
import { getArg, mustGetArg } from './_lib.mjs';
import { getAccessToken, graphFetch } from './_graph.mjs';
import { assertAllowed } from './_policy.mjs';

const profile = mustGetArg('profile');
const mailbox = getArg('mailbox', null);
const query = mustGetArg('query');
const top = Number(getArg('top', '20'));

assertAllowed(profile, 'read');

const token = await getAccessToken(profile, ['Mail.Read']);
const base = mailbox
  ? `https://graph.microsoft.com/v1.0/users/${encodeURIComponent(mailbox)}`
  : 'https://graph.microsoft.com/v1.0/me';

const url = `${base}/messages?$top=${top}&$select=id,subject,from,receivedDateTime,isRead`;
const data = await graphFetch(url, {
  token,
  headers: { 'ConsistencyLevel': 'eventual' },
});

const q = query.toLowerCase();
const hits = (data.value || []).filter(m => (m.subject || '').toLowerCase().includes(q));
for (const m of hits) {
  const from = m.from?.emailAddress?.address || '';
  console.log(`${m.receivedDateTime} | ${from} | ${m.subject} | id=${m.id}`);
}
if (!hits.length) process.exitCode = 2;
