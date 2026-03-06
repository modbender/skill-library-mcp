const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const { chromium } = require('playwright-core');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

/**
 * Start a secure remote browser tunnel for manual user authentication.
 */
async function startServer({ 
    port = 19191, 
    host = '127.0.0.1',
    chromiumPath = '/usr/bin/chromium-browser', 
    sessionFile = 'session.json',
    token = crypto.randomBytes(16).toString('hex'),
    proxy = process.env.BROWSER_PROXY || null
}) {
    const app = express();
    const server = http.createServer(app);
    const io = new Server(server);

    const ASSET_PATH = path.resolve(__dirname, '..', 'assets', 'index.html');

    // Security Headers
    app.use((req, res, next) => {
        res.setHeader('Referrer-Policy', 'no-referrer');
        res.setHeader('X-Content-Type-Options', 'nosniff');
        res.setHeader('X-Frame-Options', 'DENY');
        next();
    });

    app.get('/', (req, res) => {
        if (req.query.token !== token) {
            console.warn(`[AUTH] Unauthorized access attempt from ${req.ip}`);
            return res.status(403).send('Forbidden: Invalid or missing token');
        }
        
        try {
            const html = fs.readFileSync(ASSET_PATH, 'utf8');
            res.send(html);
        } catch (e) {
            console.error(`[ERROR] Failed to read asset: ${e.message}`);
            res.status(500).send(`Critical Error: Could not load frontend assets`);
        }
    });

    io.use((socket, next) => {
        const socketToken = socket.handshake.query.token;
        if (socketToken === token) {
            return next();
        }
        return next(new Error('Authentication error'));
    });

    io.on('connection', async (socket) => {
        console.log(`[OK] User connected via tunnel`);
        
        const launchArgs = [
            '--disable-dev-shm-usage',
            '--no-first-run',
            '--no-zygote'
        ];

        const browser = await chromium.launch({
            executablePath: chromiumPath,
            headless: true,
            proxy: proxy ? { server: proxy } : undefined,
            args: launchArgs
        });
        
        const context = await browser.newContext({
            viewport: { width: 1280, height: 720 },
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        });
        
        const page = await context.newPage();
        await page.goto('https://google.com');

        const sendScreenshot = async () => {
            try {
                if (page.isClosed()) return;
                const buffer = await page.screenshot({ type: 'jpeg', quality: 50 });
                socket.emit('screenshot', buffer.toString('base64'));
            } catch (e) {}
        };

        const interval = setInterval(sendScreenshot, 400);

        socket.on('mouseClick', async ({ x, y }) => {
            try { await page.mouse.click(x, y); await sendScreenshot(); } catch (e) {}
        });

        socket.on('type', async ({ text }) => {
            try { await page.keyboard.type(text); await sendScreenshot(); } catch (e) {}
        });

        socket.on('key', async ({ key }) => {
            try { await page.keyboard.press(key); await sendScreenshot(); } catch (e) {}
        });

        socket.on('goto', async ({ url }) => {
            try {
                const target = url.startsWith('http') ? url : `https://${url}`;
                if (!target.startsWith('http')) return;
                await page.goto(target);
                await sendScreenshot();
            } catch (e) { console.error('Goto error:', e.message); }
        });

        socket.on('done', async () => {
            const cookies = await context.cookies();
            const storage = await page.evaluate(() => JSON.stringify(localStorage));
            fs.writeFileSync(sessionFile, JSON.stringify({ cookies, storage }, null, 2));
            console.log(`[OK] Session saved to ${sessionFile}`);
            socket.emit('captured', { success: true });
        });

        socket.on('disconnect', async () => {
            clearInterval(interval);
            await browser.close();
        });
    });

    server.listen(port, host, () => {
        const displayHost = host === '0.0.0.0' ? 'YOUR_IP' : host;
        console.log(`\n🚀 BROWSER AUTH SERVER READY`);
        console.log(`Access Link: http://${displayHost}:${port}/?token=${token}\n`);
    });

    return server;
}

if (require.main === module) {
    const args = process.argv.slice(2);
    const port = parseInt(args[0]) || 19191;
    const sessionFile = args[1] || 'session.json';
    const host = process.env.AUTH_HOST || '0.0.0.0';
    const token = process.env.AUTH_TOKEN || crypto.randomBytes(16).toString('hex');
    startServer({ port, host, sessionFile, token });
}

module.exports = { startServer };
