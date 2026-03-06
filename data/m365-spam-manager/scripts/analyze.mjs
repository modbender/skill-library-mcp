#!/usr/bin/env node
import { getArg, mustGetArg } from './_lib.mjs';
import { getAccessToken, graphFetch } from './_graph.mjs';

const profile = mustGetArg('profile');
const mailbox = getArg('mailbox', null);
const top = Number(getArg('top', '30'));

// Known spam senders (auto-high score)
const KNOWN_SPAM_SENDERS = [
  'tem', 'temu', 'bellessimo', 'lowes', 'louis vuitton', 'gucci', 'chanel',
  'futuresmarket', 'backblaze', 'brave', 'new relic', 'substack',
  'kaballeros', 'futuresmarketadvisor', 'danytechnologies', 'kaufensienexus'
];

// Free email domains
const FREE_EMAIL_DOMAINS = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com', 'icloud.com'];

// Suspicious TLDs
const SUSPICIOUS_TLDS = ['.click', '.shop', '.info', '.xyz', '.top', '.gq', '.ml', '.tk', '.buzz', '.work'];

// Known legit companies (reduce score)
const KNOWN_LEGIT_COMPANIES = ['microsoft', 'google', 'amazon', 'apple', 'meta', 'github', 'slack', 'zoom', 'dropbox', 'adobe', 'atlassian', 'stripe', 'shopify', 'hubspot', 'salesforce', 'linkedin', 'twitter', 'netflix', 'spotify', 'uber', 'lyft', 'airbnb', 'wise', 'paypal', 'coinbase', 'ratedpower'];

function calculateScore(email) {
  let score = 0;
  const reasons = [];
  
  const from = email.from?.emailAddress?.address || '';
  const subject = email.subject || '';
  const body = email.bodyPreview || '';
  const domain = from.split('@')[1]?.toLowerCase() || '';
  const text = (subject + ' ' + body).toLowerCase();

  // 1. KNOWN SPAM SENDERS (auto score 90+)
  for (const spammer of KNOWN_SPAM_SENDERS) {
    if (domain.includes(spammer) || text.includes(spammer)) {
      score += 90;
      reasons.push('Known spam sender: ' + spammer);
      return { score: Math.min(100, score), reasons };
    }
  }

  // 2. Suspicious TLDs
  for (const tld of SUSPICIOUS_TLDS) {
    if (domain.endsWith(tld)) {
      score += 30;
      reasons.push('Suspicious TLD: ' + tld);
    }
  }

  // 3. Free email in corporate context
  if (FREE_EMAIL_DOMAINS.includes(domain)) {
    score += 25;
    reasons.push('Free email provider');
  }

  // 4. "Attention - suspected SPAM" in subject
  if (subject.toLowerCase().includes('attention - suspected spam') || subject.toLowerCase().includes('suspected spam')) {
    score += 30;
    reasons.push('Marked as spam in subject');
  }

  // 5. No unsubscribe link
  if (!text.includes('unsubscribe') && !text.includes('abmelden') && !text.includes('opt out')) {
    score += 15;
    reasons.push('No unsubscribe link');
  }

  // 6. Excessive emojis
  if (/[🔥💰👍🎁$!]{3,}/.test(subject + body)) {
    score += 15;
    reasons.push('Excessive emojis/punctuation');
  }

  // 7. Urgency keywords
  const urgencyKw = ['urgent', 'immediately', 'act now', 'limited time', 'expires', '24 hours', '48 hours', 'last chance'];
  for (const kw of urgencyKw) {
    if (text.includes(kw)) {
      score += 10;
      reasons.push('Urgency keyword: ' + kw);
      break;
    }
  }

  // 8. Money keywords
  const moneyKw = ['bitcoin', 'crypto', 'dollar', 'euro', 'million', 'billion', 'win', 'winner', 'cash', 'prize', 'gift card', 'coupon', 'discount'];
  for (const kw of moneyKw) {
    if (text.includes(kw)) {
      score += 15;
      reasons.push('Money keyword: ' + kw);
      break;
    }
  }

  // 9. Scam keywords
  const scamKw = ['verify', 'password', 'reset', 'suspended', 'locked', 'unusual activity', 'confirm your account'];
  for (const kw of scamKw) {
    if (text.includes(kw)) {
      score += 20;
      reasons.push('Scam keyword: ' + kw);
      break;
    }
  }

  // 10. Legit company check (reduce score)
  for (const legit of KNOWN_LEGIT_COMPANIES) {
    if (domain.includes(legit)) {
      score = Math.max(0, score - 30);
      reasons.push('Known legit company: ' + legit);
      break;
    }
  }

  return { score: Math.min(100, score), reasons };
}

const token = await getAccessToken(profile, ['Mail.Read']);

const base = mailbox
  ? 'https://graph.microsoft.com/v1.0/users/' + encodeURIComponent(mailbox)
  : 'https://graph.microsoft.com/v1.0/me';

const folders = await graphFetch(base + '/mailFolders', { token });
const junkFolder = (folders.value || []).find(f =>
  f.displayName.toLowerCase().includes('junk') && !f.displayName.toLowerCase().includes('examples')
);
if (!junkFolder) { console.error('No Junk folder found'); process.exit(1); }

const qs = new URLSearchParams({
  '$top': String(top),
  '$select': 'id,subject,from,receivedDateTime,bodyPreview',
  '$orderby': 'receivedDateTime desc',
});

const url = base + '/mailFolders/' + junkFolder.id + '/messages?' + qs.toString();
const data = await graphFetch(url, { token });

console.log('\n📧 Junk folder analysis for ' + (mailbox || 'primary'));
console.log('Folder: ' + junkFolder.displayName);
console.log('Messages: ' + (data.value?.length || 0) + '\n');

let low = 0, medium = 0, high = 0;

for (const m of data.value || []) {
  const { score, reasons } = calculateScore(m);
  const from = m.from?.emailAddress?.address || '(no from)';

  if (score <= 30) low++;
  else if (score <= 70) medium++;
  else high++;

  const level = score <= 30 ? '🟢' : score <= 70 ? '🟡' : '🔴';
  console.log(level + ' [' + score + '] ' + from);
  console.log('   Subject: ' + (m.subject || '').slice(0, 60));
  if (reasons.length > 0) {
    console.log('   Reasons: ' + reasons.join(', '));
  }
  console.log('');
}

console.log('--- Summary ---');
console.log('🟢 Low (0-30): ' + low);
console.log('🟡 Medium (31-70): ' + medium);
console.log('🔴 High (71-100): ' + high);
