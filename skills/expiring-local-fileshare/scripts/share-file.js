#!/usr/bin/env node

/**
 * Internal Single-File Share (Tom-only)
 * - Serves a single file with a time-limited token URL
 * - Max 24h validity
 * - LAN-only (192.168.0.0/24)
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const os = require('os');

const args = process.argv.slice(2);
const filePath = args[0];
const port = parseInt(args[1] || '8888');
const validityHours = parseInt(args[2] || '1');
const oneTime = (args[3] || '0') === '1';

if (!filePath || !fs.existsSync(filePath)) {
    console.error('Usage: node share-file.js <file-path> [port=8888] [validity-hours=1] [one-time=0|1]');
    process.exit(1);
}

// Max 24h
if (validityHours > 24) {
    console.error('⚠️  Max validity is 24h, capping at 24h');
}
const effectiveHours = Math.min(validityHours, 24);

const WORKSPACE_DIR = process.env.OPENCLAW_WORKSPACE || path.join(os.homedir(), '.openclaw', 'workspace');

// Enforce that only files under the OpenClaw workspace can be shared by default.
// Override ONLY if you explicitly know what you're doing.
const allowAnyPath = (process.env.FILESHARE_ALLOW_ANY_PATH || '0') === '1';
const resolved = fs.realpathSync(filePath);
const workspaceResolved = fs.realpathSync(WORKSPACE_DIR);

if (!allowAnyPath && !resolved.startsWith(workspaceResolved + path.sep)) {
    console.error(`❌ Refusing to share file outside workspace: ${resolved}`);
    console.error(`   Workspace: ${workspaceResolved}`);
    console.error('   Set FILESHARE_ALLOW_ANY_PATH=1 to override (not recommended).');
    process.exit(2);
}

const token = crypto.randomBytes(16).toString('hex');
const expiresAt = Date.now() + (effectiveHours * 60 * 60 * 1000);
let consumed = false;
const fileName = path.basename(filePath);
const fileSize = fs.statSync(resolved).size;

function normalizeIp(rawIp) {
    if (!rawIp) return '';
    // Handle IPv6-mapped IPv4 addresses like ::ffff:192.168.0.10
    if (rawIp.startsWith('::ffff:')) return rawIp.replace('::ffff:', '');
    return rawIp;
}

function isPrivateIPv4(ip) {
    const parts = ip.split('.').map(n => parseInt(n, 10));
    if (parts.length !== 4 || parts.some(n => Number.isNaN(n))) return false;

    const [a, b] = parts;
    if (a === 10) return true;
    if (a === 192 && b === 168) return true;
    if (a === 172 && b >= 16 && b <= 31) return true;
    return false;
}

const server = http.createServer((req, res) => {
    const clientIpRaw = req.socket.remoteAddress;
    const clientIp = normalizeIp(clientIpRaw);

    // Local-only check (RFC1918 + localhost)
    const isLocalhost = clientIp === '127.0.0.1' || clientIp === '::1';
    const isAllowed = isLocalhost || isPrivateIPv4(clientIp);

    if (!isAllowed) {
        res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
        res.end('Access denied: local-network/VPN only');
        console.log(`❌ Blocked access from ${clientIpRaw}`);
        return;
    }

    const url = new URL(req.url, `http://localhost:${port}`);

    // Check token
    if (url.searchParams.get('token') !== token) {
        res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
        res.end('Invalid or missing token');
        console.log(`❌ Invalid token from ${clientIpRaw}`);
        return;
    }

    // One-time token support
    if (oneTime && consumed) {
        res.writeHead(410, { 'Content-Type': 'text/plain; charset=utf-8' });
        res.end('Link already used (one-time access)');
        console.log(`⛔ One-time link already used; blocked ${clientIpRaw}`);
        return;
    }

    // Expiry check
    if (Date.now() > expiresAt) {
        res.writeHead(410, { 'Content-Type': 'text/plain; charset=utf-8' });
        res.end('Link expired');
        console.log(`⏰ Expired link access from ${clientIpRaw}`);
        return;
    }

    // Serve file
    const mimeType = fileName.endsWith('.png') ? 'image/png' :
                     fileName.endsWith('.jpg') || fileName.endsWith('.jpeg') ? 'image/jpeg' :
                     fileName.endsWith('.md') ? 'text/markdown; charset=utf-8' :
                     fileName.endsWith('.txt') ? 'text/plain; charset=utf-8' :
                     'application/octet-stream';

    res.writeHead(200, {
        'Content-Type': mimeType,
        'Content-Length': fileSize,
        'Content-Disposition': `inline; filename="${fileName}"`,
        'Cache-Control': 'no-cache, no-store, must-revalidate'
    });

    const fileStream = fs.createReadStream(resolved);
    fileStream.pipe(res);

    fileStream.on('end', () => {
        if (oneTime) consumed = true;
    });

    console.log(`✅ Served ${fileName} to ${clientIpRaw}${oneTime ? ' (one-time)' : ''}`);
});

server.listen(port, '0.0.0.0', () => {
    const ifaces = os.networkInterfaces();
    const allAddrs = Object.values(ifaces).flat().filter(Boolean);
    const ipv4 = allAddrs.find(a => a.family === 'IPv4' && !a.internal);
    const localIp = ipv4?.address || '127.0.0.1';
    const shareUrl = `http://${localIp}:${port}/?token=${token}`;
    const expiresIn = Math.round((expiresAt - Date.now()) / 1000 / 60 / 60);

    console.log(`\n📤 File Share Active`);
    console.log(`   File: ${fileName} (${(fileSize / 1024).toFixed(1)} KB)`);
    console.log(`   Link: ${shareUrl}`);
    console.log(`   Expires: ${new Date(expiresAt).toISOString()} (in ${expiresIn}h)`);
    console.log(`   Scope: local-network/VPN only (RFC1918 + localhost)`);
    console.log(`   One-time: ${oneTime ? 'yes' : 'no'}\n`);
    console.log(`Press Ctrl+C to stop.\n`);
});
