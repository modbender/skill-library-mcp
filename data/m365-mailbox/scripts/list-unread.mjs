#!/usr/bin/env node
import { getArg, mustGetArg } from './_lib.mjs';
import { getAccessToken, graphFetch } from './_graph.mjs';
import { assertAllowed } from './_policy.mjs';

const profile = mustGetArg('profile');
const mailbox = getArg('mailbox', null); // email address of shared mailbox (optional)
const top = Number(getArg('top', '20'));

assertAllowed(profile, 'read');

const token = await getAccessToken(profile, ['Mail.Read']);
const qs = new URLSearchParams({
  '$top': String(top),
  '$select': 'id,subject,from,receivedDateTime,isRead',
  '$orderby': 'receivedDateTime desc',
  '$filter': 'isRead eq false',
});

// Use /users/{mailbox}/... for shared mailboxes, /me/ for primary
const base = mailbox
  ? `https://graph.microsoft.com/v1.0/users/${encodeURIComponent(mailbox)}`
  : 'https://graph.microsoft.com/v1.0/me';

const url = `${base}/mailFolders/Inbox/messages?${qs.toString()}`;
const data = await graphFetch(url, { token });

for (const m of data.value || []) {
  const from = m.from?.emailAddress?.address || '';
  console.log(`${m.receivedDateTime} | ${from} | ${m.subject} | id=${m.id}`);
}
