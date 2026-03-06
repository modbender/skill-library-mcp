import FormData from 'form-data';
import Mailgun from 'mailgun.js';
import { fileURLToPath } from 'url';

/**
 * Send an email via Mailgun API using variables from process.env.
 */
async function sendEmail({ 
    apiKey = process.env.MAILGUN_API_KEY, 
    domain = process.env.MAILGUN_DOMAIN || 'aicommander.dev', 
    region = process.env.MAILGUN_REGION || 'EU',
    from = process.env.MAILGUN_FROM || `Postmaster <postmaster@${domain}>`, 
    to, 
    subject, 
    text, 
    html 
}) {
    if (!apiKey) throw new Error('MAILGUN_API_KEY is not set in environment');

    const mailgun = new Mailgun(FormData);
    const mg = mailgun.client({
        username: 'api',
        key: apiKey,
        url: region.toUpperCase() === 'EU' ? 'https://api.eu.mailgun.net' : 'https://api.mailgun.net'
    });

    return mg.messages.create(domain, {
        from,
        to: Array.isArray(to) ? to : [to],
        subject,
        text,
        html
    });
}

const isMain = process.argv[1] === fileURLToPath(import.meta.url);

if (isMain) {
    if (!process.env.MAILGUN_API_KEY) {
        console.error(`
╔══════════════════════════════════════════════════════════════╗
║            MAILGUN SIMPLE — CONFIGURATION REQUIRED           ║
╚══════════════════════════════════════════════════════════════╝

Missing required environment variable: MAILGUN_API_KEY

This skill sends outbound emails via the Mailgun API and requires
an API key and a verified sending domain.

Usage:
  MAILGUN_API_KEY=your-key MAILGUN_DOMAIN=yourdomain.com node scripts/send_email.js <to> <subject> <text> [from]

Required:
  MAILGUN_API_KEY    Your Mailgun private API key (starts with key-)
  MAILGUN_DOMAIN     Your verified sending domain (e.g. example.com)

Optional:
  MAILGUN_REGION     API region: EU (default) or US
  MAILGUN_FROM       Sender address (default: postmaster@<domain>)

Get your API key at: https://app.mailgun.com/settings/api_security
`);
        process.exit(1);
    }

    const args = process.argv.slice(2);
    const [to, subject, text, from] = args;

    if (!to || !subject || !text) {
        console.error('Usage: node send_email.js <to> <subject> <text> [from]');
        process.exit(1);
    }

    sendEmail({ to, subject, text, from })
        .then(res => { 
            console.log('SUCCESS:', res.message); 
            process.exit(0);
        })
        .catch(err => { 
            console.error('FAILED:', err.message); 
            process.exit(1); 
        });
}

export { sendEmail };
