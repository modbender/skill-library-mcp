#!/usr/bin/env node
import { getArg, mustGetArg } from './_lib.mjs';
import { getAccessToken, graphFetch } from './_graph.mjs';

const profile = mustGetArg('profile');
const mailbox = getArg('mailbox', null);
const id = mustGetArg('id');

const token = await getAccessToken(profile, ['Mail.ReadWrite']);

const base = mailbox
  ? `https://graph.microsoft.com/v1.0/users/${encodeURIComponent(mailbox)}`
  : 'https://graph.microsoft.com/v1.0/me';

// Get Inbox folder ID
const folders = await graphFetch(`${base}/mailFolders`, { token });
const inbox = (folders.value || []).find(f => f.displayName.toLowerCase() === 'inbox' || f.displayName.toLowerCase() === 'posteingang');
if (!inbox) throw new Error('Inbox folder not found');

// Move to Inbox (POST to move)
const url = `${base}/messages/${encodeURIComponent(id)}/move`;
const result = await graphFetch(url, {
  method: 'POST',
  token,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ destinationId: inbox.id }),
});

console.log(`✅ Moved message ${id} to Inbox`);
console.log(`   New location: ${inbox.displayName}`);
