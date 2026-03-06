#!/usr/bin/env node
import { getArg, mustGetArg } from './_lib.mjs';
import { getAccessToken, graphFetch } from './_graph.mjs';
import { assertAllowed, needsConfirm } from './_policy.mjs';

const profile = mustGetArg('profile');
const mailbox = getArg('mailbox', null);
const id = mustGetArg('id');

assertAllowed(profile, 'send');
if (needsConfirm(profile, 'send')) {
  throw new Error('Policy requires confirmation for send. Update profile policy if you want autonomous sending.');
}

const token = await getAccessToken(profile, ['Mail.Send']);
const base = mailbox
  ? `https://graph.microsoft.com/v1.0/users/${encodeURIComponent(mailbox)}`
  : 'https://graph.microsoft.com/v1.0/me';

const url = `${base}/messages/${encodeURIComponent(id)}/send`;
await graphFetch(url, { method: 'POST', token });
console.log('OK: sent');
