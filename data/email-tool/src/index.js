const nodemailer = require('nodemailer');
const imaps = require('imap-simple');
const fs = require('fs');
const path = require('path');

const CONFIG = (() => {
    // Load once at startup.
    // If you rotate credentials, restart the skill runner / OpenClaw gateway to reload.
    return loadConfig();
})();

function loadConfig() {
    // Prefer an external secrets file so skills can be shared safely.
    // Path: %OPENCLAW_SECRETS_DIR%/email-tool.json or ~/.openclaw/secrets/email-tool.json
    const secretsDir = process.env.OPENCLAW_SECRETS_DIR
        ? process.env.OPENCLAW_SECRETS_DIR
        : path.join(process.env.USERPROFILE || process.env.HOME || '.', '.openclaw', 'secrets');

    const secretsPath = path.join(secretsDir, 'email-tool.json');

    let fileCfg = {};
    if (fs.existsSync(secretsPath)) {
        try {
            fileCfg = JSON.parse(fs.readFileSync(secretsPath, 'utf8'));
        } catch (e) {
            throw new Error(`Failed to parse secrets file at ${secretsPath}: ${e.message}`);
        }
    }

    const cfg = {
        user: fileCfg.EMAIL_USER || process.env.EMAIL_USER,
        pass: fileCfg.EMAIL_PASS || process.env.EMAIL_PASS,
        hostImap: fileCfg.HOST_IMAP || process.env.HOST_IMAP || 'imap.zoho.com',
        portImap: Number(fileCfg.PORT_IMAP || process.env.PORT_IMAP || 993),
        hostSmtp: fileCfg.HOST_SMTP || process.env.HOST_SMTP || 'smtp.zoho.com',
        portSmtp: Number(fileCfg.PORT_SMTP || process.env.PORT_SMTP || 465),
        secureSmtp: String(fileCfg.SECURE_SMTP ?? process.env.SECURE_SMTP ?? 'true').toLowerCase() === 'true'
    };

    if (!cfg.user || !cfg.pass) {
        throw new Error('Missing EMAIL_USER/EMAIL_PASS. Set env vars or create secrets file email-tool.json.');
    }

    return cfg;
}

async function sendEmail(args) {
    const { to, subject, body, cc, bcc } = args;

    const transporter = nodemailer.createTransport({
        host: CONFIG.hostSmtp,
        port: CONFIG.portSmtp,
        secure: CONFIG.secureSmtp,
        auth: {
            user: CONFIG.user,
            pass: CONFIG.pass
        }
    });

    const info = await transporter.sendMail({
        from: `"Pestward Info" <${CONFIG.user}>`,
        to,
        subject,
        html: body,
        cc,
        bcc
    });

    return `Email sent: ${info.messageId}`;
}

async function searchEmails(args) {
    const { query, limit = 10, markRead = false } = args;

    const connection = await imaps.connect({
        imap: {
            user: CONFIG.user,
            password: CONFIG.pass,
            host: CONFIG.hostImap,
            port: CONFIG.portImap,
            tls: true,
            authTimeout: 3000
        }
    });

    await connection.openBox('INBOX');

    // Simple search (UNSEEN, etc.) - complex queries might need parsing
    // For now, support simple "UNSEEN" or generic keyword search
    let searchCriteria = ['UNSEEN']; 
    if (query && query !== 'UNSEEN') {
        // If specific criteria provided, use it (simplified for now)
        // Ideally parse "from:foo" to ['FROM', 'foo']
        // Fallback to text search on BODY/SUBJECT
        searchCriteria = [['OR', ['SUBJECT', query], ['BODY', query]]];
    }

    const fetchOptions = {
        bodies: ['HEADER', 'TEXT', ''],
        markSeen: markRead
    };

    const messages = await connection.search(searchCriteria, fetchOptions);
    
    // Sort recent first and limit
    const results = messages.reverse().slice(0, limit).map(item => {
        const subject = item.parts.find(p => p.which === 'HEADER').body.subject[0];
        const from = item.parts.find(p => p.which === 'HEADER').body.from[0];
        const date = item.parts.find(p => p.which === 'HEADER').body.date[0];
        const body = item.parts.find(p => p.which === 'TEXT')?.body || '(No text body)';
        return `From: ${from}\nDate: ${date}\nSubject: ${subject}\nBody: ${body.substring(0, 200)}...`;
    });

    connection.end();
    return results.length > 0 ? results.join('\n---\n') : 'No matching emails found.';
}

// Simple export for potential direct use or testing
module.exports = { sendEmail, searchEmails };

// Basic CLI runner for the skill (OpenClaw style)
if (require.main === module) {
    const args = process.argv.slice(2);
    const command = args[0];
    const jsonArgs = args[1] ? JSON.parse(args[1]) : {};

    if (command === 'send') {
        sendEmail(jsonArgs).then(console.log).catch(console.error);
    } else if (command === 'search') {
        searchEmails(jsonArgs).then(console.log).catch(console.error);
    } else {
        console.log('Usage: node index.js <send|search> <json-args>');
    }
}
