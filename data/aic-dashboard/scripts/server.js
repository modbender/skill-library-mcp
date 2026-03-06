const express = require('express');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

function startDashboard({ 
    port = 19195, 
    host = '0.0.0.0', 
    token = crypto.randomBytes(12).toString('hex'),
    inboxPath = process.env.INBOX_PATH || path.resolve(__dirname, '../data/inbox.jsonl'),
    sessionPath = process.env.SESSION_PATH || path.resolve(__dirname, '../data/session.json')
}) {

    const app = express();

    // Auth middleware
    app.use((req, res, next) => {
        const authHeader = req.headers['authorization'];
        const bearerToken = authHeader && authHeader.startsWith('Bearer ') ? authHeader.split(' ')[1] : null;
        const queryToken = req.query.token || req.headers['x-dashboard-token'] || bearerToken;

        if (queryToken !== token) {
            return res.status(403).send('Forbidden: Invalid dashboard token.');
        }
        next();
    });

    app.get('/', (req, res) => {
        const html = fs.readFileSync(path.resolve(__dirname, '../assets/index.html'), 'utf8');
        res.setHeader('Content-Type', 'text/html');
        res.send(html);
    });

    // API: Get Emails
    app.get('/api/emails', (req, res) => {
        try {
            if (!fs.existsSync(inboxPath)) return res.json([]);
            const content = fs.readFileSync(inboxPath, 'utf8');
            const emails = content.trim().split('\n').filter(Boolean).map(line => JSON.parse(line));
            res.json(emails.reverse().slice(0, 50));
        } catch (e) {
            res.status(500).json({ error: e.message });
        }
    });

    // API: Get Session Status
    app.get('/api/session', (req, res) => {
        try {
            if (!fs.existsSync(sessionPath)) return res.json({ active: false });
            const stats = fs.statSync(sessionPath);
            res.json({ active: true, updatedAt: stats.mtime });
        } catch (e) {
            res.json({ active: false });
        }
    });

    app.listen(port, host, () => {
        const displayHost = host === '0.0.0.0' ? 'YOUR_IP' : host;
        console.log(`\n🏠 AI COMMANDER DASHBOARD READY`);
        console.log(`Access URL: http://${displayHost}:${port}/?token=${token}\n`);
    });
}

if (require.main === module) {
    const port = parseInt(process.env.PORT) || 19195;
    const host = process.env.DASHBOARD_HOST || '0.0.0.0';
    const token = process.env.DASHBOARD_TOKEN || crypto.randomBytes(12).toString('hex');
    startDashboard({ port, host, token });
}

module.exports = { startDashboard };
