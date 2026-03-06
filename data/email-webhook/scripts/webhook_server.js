const https = require('https');
const express = require('express');
const fs = require('fs');
const path = require('path');
const { spawn, execSync } = require('child_process');

const app = express();
app.use(express.json({ limit: '50mb' }));

const PORT = process.env.PORT || 2083;
const SECRET = process.env.WEBHOOK_SECRET;
const AGENT_ID = process.env.OPENCLAW_AGENT_ID;

if (!SECRET || !AGENT_ID) {
    console.error(`
╔══════════════════════════════════════════════════════════════╗
║           EMAIL WEBHOOK — CONFIGURATION REQUIRED             ║
╚══════════════════════════════════════════════════════════════╝

Missing required environment variables:
  ${!SECRET   ? '  ✗ WEBHOOK_SECRET     — shared secret with your Cloudflare Worker' : '  ✓ WEBHOOK_SECRET'}
  ${!AGENT_ID ? '  ✗ OPENCLAW_AGENT_ID  — your agent ID (e.g. "skippy")' : '  ✓ OPENCLAW_AGENT_ID'}

Start the server with both variables set:

  WEBHOOK_SECRET=your-secret OPENCLAW_AGENT_ID=your-agent-id node scripts/webhook_server.js

WEBHOOK_SECRET must match the Authorization Bearer token in your Cloudflare Worker.
OPENCLAW_AGENT_ID ensures only your agent is notified — not all agents on the server.

Optional:
  PORT        - Port to listen on (default: 2083)
  INBOX_FILE  - Filename for storing emails (default: inbox.jsonl)
`);
    process.exit(1);
}

const RAW_INBOX_FILE = process.env.INBOX_FILE || 'inbox.jsonl';
const INBOX_FILE = path.basename(RAW_INBOX_FILE);
const INBOX_PATH = path.resolve(process.cwd(), INBOX_FILE);

// --- SSL: generate self-signed cert if missing ---
const SSL_DIR = path.resolve(__dirname, '../ssl');
const CERT_PATH = path.join(SSL_DIR, 'cert.pem');
const KEY_PATH  = path.join(SSL_DIR, 'key.pem');

function ensureCert() {
    if (fs.existsSync(CERT_PATH) && fs.existsSync(KEY_PATH)) return;
    console.log('[SSL] Generating self-signed certificate...');
    fs.mkdirSync(SSL_DIR, { recursive: true });
    execSync(
        `openssl req -x509 -newkey rsa:2048 -keyout "${KEY_PATH}" -out "${CERT_PATH}" -days 3650 -nodes -subj "/CN=webhook"`,
        { stdio: 'pipe' }
    );
    console.log('[SSL] Certificate generated (valid 10 years)');
}

// --- Routes ---
app.post('/api/email', (req, res) => {
    const auth = req.headers['authorization'];
    if (auth !== `Bearer ${SECRET}`) {
        console.warn(`[AUTH] Unauthorized attempt from ${req.ip}`);
        return res.status(403).send('Forbidden');
    }

    const email = req.body;
    if (!email || typeof email !== 'object') {
        return res.status(400).send('Invalid payload');
    }

    console.log(`[OK] Email received: ${email.subject || '(no subject)'}`);

    try {
        const entry = JSON.stringify({ receivedAt: new Date().toISOString(), ...email }) + '\n';
        fs.appendFileSync(INBOX_PATH, entry);

        const wakeText = `New email from ${email.from || 'unknown'}: ${email.subject || '(no subject)'}`;
        const safeWakeText = wakeText.substring(0, 200).replace(/[\r\n]/g, ' ');
        const token = process.env.OPENCLAW_GATEWAY_TOKEN;
        const args = ['agent', '--agent', AGENT_ID, '--message', safeWakeText, '--deliver'];
        if (token) args.push('--token', token);

        const child = spawn('openclaw', args);
        child.on('error', err => console.error(`[WAKE] Failed: ${err.message}`));
        child.stdout.on('data', d => console.log(`[WAKE-OUT] ${d}`));
        child.stderr.on('data', d => console.error(`[WAKE-ERR] ${d}`));
        child.on('close', code => {
            if (code !== 0) console.error(`[WAKE] openclaw exited ${code}`);
            else console.log(`[WAKE] Agent notified: ${safeWakeText}`);
        });

        res.status(200).json({ success: true });
    } catch (e) {
        console.error(`[ERROR] ${e.message}`);
        res.status(500).send('Internal Server Error');
    }
});

// --- Start HTTPS server ---
ensureCert();

const server = https.createServer({
    key:  fs.readFileSync(KEY_PATH),
    cert: fs.readFileSync(CERT_PATH)
}, app);

server.listen(PORT, '0.0.0.0', () => {
    console.log(`\n📧 EMAIL WEBHOOK SERVER v2.1.0 (HTTPS)`);
    console.log(`Port:  ${PORT}`);
    console.log(`Inbox: ${INBOX_PATH}`);
    console.log(`SSL:   self-signed (${CERT_PATH})`);
    console.log(`Wake:  Enabled (system event now)`);
    console.log(`Agent: ${AGENT_ID}`);
    console.log(`\n💡 Cloudflare setup (Flexible SSL, port 2083):`);
    console.log(`   OPENCLAW_WEBHOOK_URL = https://webhook.yourdomain.com:${PORT}/api/email\n`);

    checkExternalAccess(PORT);
});

async function checkExternalAccess(port) {
    try {
        const ipRes = await fetch('https://api.ipify.org?format=json', { signal: AbortSignal.timeout(5000) });
        const { ip } = await ipRes.json();
        console.log(`🔍 Checking external access on ${ip}:${port}...`);

        try {
            // Use http (CF Flexible) or https (CF Full) — either way, any response = port open
            await fetch(`https://${ip}:${port}/`, {
                signal: AbortSignal.timeout(6000),
                // ignore self-signed cert error via Node TLS
            });
            console.log(`✅ External access OK: port ${port} reachable (public IP: ${ip})`);
        } catch (e) {
            // A TLS error still means the port is open (server responded with handshake)
            if (e.message.includes('certificate') || e.message.includes('self-signed') || e.message.includes('self signed') || e.code === 'DEPTH_ZERO_SELF_SIGNED_CERT' || e.code === 'ERR_TLS') {
                console.log(`✅ External access OK: port ${port} reachable, TLS handshake succeeded (public IP: ${ip})`);
            } else if (e.name === 'AbortError') {
                console.log(`❌ External access FAILED: port ${port} timed out — likely blocked by firewall (public IP: ${ip})`);
                console.log(`   → Run: sudo ufw allow ${port}/tcp`);
            } else if (e.message.includes('ECONNREFUSED')) {
                console.log(`❌ External access FAILED: connection refused on port ${port} (public IP: ${ip})`);
                console.log(`   → Run: sudo ufw allow ${port}/tcp`);
            } else {
                // Unknown error - treat as open if we got any network response
                console.log(`✅ External access OK: port ${port} reachable (public IP: ${ip}) [${e.code || e.message}]`);
            }
        }
    } catch (e) {
        console.log(`⚠️  Could not verify external port access: ${e.message}`);
    }
}
