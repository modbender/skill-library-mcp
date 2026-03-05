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

// Get "Junk Examples" folder (learning folder)
const folders = await graphFetch(`${base}/mailFolders`, { token });
const learning = (folders.value || []).find(f =>
  f.displayName.toLowerCase().includes('junk examples') ||
  f.displayName.toLowerCase().includes('spam beispiele')
);

if (!learning) {
  // Create it if it doesn't exist
  const created = await graphFetch(`${base}/mailFolders`, {
    method: 'POST',
    token,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ displayName: 'Junk Examples' }),
  });
  console.log(`📁 Created learning folder: "Junk Examples"`);
  var learningFolderId = created.id;
} else {
  var learningFolderId = learning.id;
  console.log(`📁 Using existing learning folder: "${learning.displayName}"`);
}

// Move to learning folder
const url = `${base}/messages/${encodeURIComponent(id)}/move`;
const result = await graphFetch(url, {
  method: 'POST',
  token,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ destinationId: learningFolderId }),
});

console.log(`✅ Moved message ${id} to learning folder`);
