// Example Resend inbound webhook transform for Clawdbot
// Fetches full email content via Resend receiving API and formats a reply prompt.

const fs = require('fs');

const RESEND_API_KEY = process.env.RESEND_API_KEY || (() => {
  try {
    const creds = JSON.parse(fs.readFileSync(`${process.env.HOME}/.config/resend/credentials.json`, 'utf-8'));
    return creds.api_key;
  } catch {
    return null;
  }
})();

async function fetchEmailContent(emailId) {
  if (!RESEND_API_KEY) return null;
  const res = await fetch(`https://api.resend.com/emails/receiving/${emailId}`, {
    headers: { 'Authorization': `Bearer ${RESEND_API_KEY}` }
  });
  if (!res.ok) return null;
  return await res.json();
}

async function transform(payload) {
  if (!payload || payload.type !== 'email.received') return { action: 'skip' };
  const data = payload.data || {};
  const content = await fetchEmailContent(data.email_id);
  const body = (content && (content.text || content.html)) || '(No body content)';

  const message = `📧 New Email Received\n\nFrom: ${data.from}\nTo: ${(data.to || []).join(', ')}\nSubject: ${data.subject}\nDate: ${payload.created_at}\n\n---\n\n${body}`;

  return { action: 'agent', message };
}

module.exports = { transform };
