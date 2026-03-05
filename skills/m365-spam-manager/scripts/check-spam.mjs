#!/usr/bin/env node
import { getArg, mustGetArg } from './_lib.mjs';
import { getAccessToken, graphFetch } from './_graph.mjs';

const profile = mustGetArg('profile');
const mailbox = getArg('mailbox', null);
const threshold = Number(getArg('threshold', '70')); // above this = spam, below = ok
const dryRun = getArg('dryRun', 'false') === 'true';

// Suspicious patterns (same as analyze.mjs)
const SCAM_KEYWORDS = [
  'crypto', 'bitcoin', 'win', 'winner', 'free', 'urgent', 'verify',
  'bank', 'password', 'account', 'suspended', 'limited', 'confirm',
  'inheritance', 'million', 'dollar', 'euro', 'transfer', 'fund',
  'kredit', 'darlehen', 'gewonnen', 'gratis', 'sofort', 'konto'
];
const FREE_EMAIL_DOMAINS = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com'];

function calculateScore(email) {
  let score = 0;
  const from = email.from?.emailAddress?.address || '';
  const subject = email.subject || '';
  const body = email.bodyPreview || '';

  if (!body.toLowerCase().includes('unsubscribe') && !body.toLowerCase().includes('abmelden')) {
    score += 20;
  }

  const domain = from.split('@')[1]?.toLowerCase();
  if (domain) {
    if (FREE_EMAIL_DOMAINS.includes(domain)) score += 10;
    if (domain.includes('kaballeros') || domain.includes('bellessimo') || domain.includes('futuresmarket')) score += 15;
    if (/^[a-z0-9]{10,}\.[a-z]{2,}/.test(domain)) score += 15;
  }

  if (subject === subject.toUpperCase() && subject.length > 5) score += 10;
  if (/[{$}!]{3,}/.test(subject) || /[{$}!]{5,}/.test(body)) score += 10;

  const text = (subject + ' ' + body).toLowerCase();
  for (const kw of SCAM_KEYWORDS) {
    if (text.includes(kw)) { score += 15; break; }
  }

  if (/[äöüß]/i.test(subject) && /\b(the|and|for|you|your)\b/i.test(subject)) score += 10;

  if (subject.includes('Attention - suspected SPAM') || subject.includes('suspected spam')) score += 25;
  if (/^[a-zA-Z0-9]{20,}$/.test(subject.replace(/\s/g, ''))) score += 10;

  return Math.min(100, score);
}

const token = await getAccessToken(profile, ['Mail.ReadWrite']);

const base = mailbox
  ? `https://graph.microsoft.com/v1.0/users/${encodeURIComponent(mailbox)}`
  : 'https://graph.microsoft.com/v1.0/me';

// Get or create categories
const categoriesUrl = `${base}/outlook/masterCategories`;
const categoriesRes = await graphFetch(categoriesUrl, { token });
const existingCats = categoriesRes.value || [];

const spamCat = existingCats.find(c => c.displayName === 'Spam');
const okCat = existingCats.find(c => c.displayName === 'OK');

let spamCatId = spamCat?.id;
let okCatId = okCat?.id;

if (!spamCatId) {
  const created = await graphFetch(categoriesUrl, {
    method: 'POST',
    token,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ displayName: 'Spam', color: 'preset0' }),
  });
  spamCatId = created.id;
  console.log('✅ Created category: Spam');
}
if (!okCatId) {
  const created = await graphFetch(categoriesUrl, {
    method: 'POST',
    token,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ displayName: 'OK', color: 'preset7' }),
  });
  okCatId = created.id;
  console.log('✅ Created category: OK');
}

// Get junk folder
const folders = await graphFetch(`${base}/mailFolders`, { token });
const junkFolder = (folders.value || []).find(f =>
  f.displayName.toLowerCase().includes('junk') && !f.displayName.toLowerCase().includes('examples')
);
if (!junkFolder) throw new Error('No Junk folder found');

const qs = new URLSearchParams({
  '$top': '50',
  '$select': 'id,subject,from,categories',
  '$orderby': 'receivedDateTime desc',
});
const url = `${base}/mailFolders/${junkFolder.id}/messages?${qs.toString()}`;
const data = await graphFetch(url, { token });

console.log(`\n📧 Processing ${data.value?.length || 0} messages in Junk folder...`);
console.log(`Threshold: ${threshold} (above=spam, below=ok)\n`);

let spamCount = 0, okCount = 0, skipCount = 0;

for (const m of data.value || []) {
  const score = calculateScore(m);
  const isSpam = score > threshold;
  const label = isSpam ? 'Spam' : 'OK';
  const labelId = isSpam ? spamCatId : okCatId;
  
  // Check if already labeled
  const existing = m.categories || [];
  if (existing.includes('Spam') || existing.includes('OK')) {
    skipCount++;
    continue;
  }

  if (dryRun) {
    console.log(`[DRY RUN] Would label "${m.subject?.slice(0,40)}..." as ${label} (score: ${score})`);
    if (isSpam) spamCount++; else okCount++;
    continue;
  }

  // Update categories
  const newCats = [...existing, label];
  await graphFetch(`${base}/messages/${encodeURIComponent(m.id)}`, {
    method: 'PATCH',
    token,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ categories: newCats }),
  });

  if (isSpam) spamCount++; else okCount++;
  console.log(`✅ Labeled: ${label} (score ${score}) - ${m.subject?.slice(0,40)}...`);
}

console.log(`\n--- Summary ---`);
if (dryRun) console.log(`[DRY RUN] Would label:`);
console.log(`🔴 Spam: ${spamCount}`);
console.log(`🟢 OK: ${okCount}`);
console.log(`⏭️ Skipped (already labeled): ${skipCount}`);
console.log(`\nDone!`);
