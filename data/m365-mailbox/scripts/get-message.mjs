#!/usr/bin/env node
import { getArg, mustGetArg } from './_lib.mjs';
import { getAccessToken, graphFetch } from './_graph.mjs';
import { assertAllowed } from './_policy.mjs';

const profile = mustGetArg('profile');
const mailbox = getArg('mailbox', null);
const id = mustGetArg('id');

assertAllowed(profile, 'read');

const token = await getAccessToken(profile, ['Mail.Read']);
const base = mailbox
  ? `https://graph.microsoft.com/v1.0/users/${encodeURIComponent(mailbox)}`
  : 'https://graph.microsoft.com/v1.0/me';

const url = `${base}/messages/${encodeURIComponent(id)}?$select=subject,from,toRecipients,ccRecipients,receivedDateTime,bodyPreview,isRead`;
const m = await graphFetch(url, { token });

console.log(`subject: ${m.subject}`);
console.log(`from: ${m.from?.emailAddress?.address || ''}`);
console.log(`received: ${m.receivedDateTime}`);
console.log(`isRead: ${m.isRead}`);
console.log(`preview: ${m.bodyPreview}`);
