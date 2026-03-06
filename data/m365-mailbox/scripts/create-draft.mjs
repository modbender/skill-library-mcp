#!/usr/bin/env node
import { getArg, mustGetArg } from './_lib.mjs';
import { getAccessToken, graphFetch } from './_graph.mjs';
import { assertAllowed } from './_policy.mjs';

const profile = mustGetArg('profile');
const mailbox = getArg('mailbox', null);
const to = mustGetArg('to');
const subject = mustGetArg('subject');
const body = getArg('body', '');

assertAllowed(profile, 'draft');

const token = await getAccessToken(profile, ['Mail.ReadWrite']);
const base = mailbox
  ? `https://graph.microsoft.com/v1.0/users/${encodeURIComponent(mailbox)}`
  : 'https://graph.microsoft.com/v1.0/me';

const url = `${base}/messages`;
const payload = {
  subject,
  toRecipients: [{ emailAddress: { address: to } }],
  body: { contentType: 'Text', content: body },
};
const created = await graphFetch(url, {
  method: 'POST',
  token,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload),
});
console.log(`OK: draft id=${created.id}`);
