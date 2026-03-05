#!/usr/bin/env node
// LAN Media Server — lightweight static file server for AI agent media sharing
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = parseInt(process.env.MEDIA_PORT || '18801', 10);
const MEDIA_ROOT = path.resolve(process.env.MEDIA_ROOT || path.join(process.env.HOME, 'projects/shared-media'));

const MIME = {
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
  '.gif': 'image/gif', '.webp': 'image/webp', '.svg': 'image/svg+xml',
  '.mp4': 'video/mp4', '.webm': 'video/webm', '.mp3': 'audio/mpeg',
  '.ogg': 'audio/ogg', '.wav': 'audio/wav', '.pdf': 'application/pdf',
  '.html': 'text/html', '.json': 'application/json', '.txt': 'text/plain',
  '.css': 'text/css', '.js': 'application/javascript', '.zip': 'application/zip',
};

const server = http.createServer((req, res) => {
  if (req.method !== 'GET') {
    res.writeHead(405); res.end('Method Not Allowed'); return;
  }

  let urlPath;
  try {
    urlPath = decodeURIComponent(req.url.split('?')[0]);
  } catch {
    res.writeHead(400); res.end('Bad request'); return;
  }

  // Block null bytes and double-encoded traversal
  if (urlPath.includes('\0') || urlPath.includes('..')) {
    res.writeHead(403); res.end('Forbidden'); return;
  }

  const safePath = path.normalize(urlPath);
  const filePath = path.join(MEDIA_ROOT, safePath);

  // Block path traversal
  if (!filePath.startsWith(MEDIA_ROOT + path.sep) && filePath !== MEDIA_ROOT) {
    res.writeHead(403); res.end('Forbidden'); return;
  }

  // Block directory listing (root path returns simple status)
  if (filePath === MEDIA_ROOT || filePath === MEDIA_ROOT + '/') {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('LAN Media Server OK\n');
    return;
  }

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404); res.end('Not found'); return;
    }
    const ext = path.extname(filePath).toLowerCase();
    res.writeHead(200, {
      'Content-Type': MIME[ext] || 'application/octet-stream',
      'Content-Length': stats.size,
      'Cache-Control': 'public, max-age=3600',
      'X-Content-Type-Options': 'nosniff',
      'Content-Security-Policy': "default-src 'none'; img-src 'self'; media-src 'self'; style-src 'unsafe-inline'",
    });
    fs.createReadStream(filePath).pipe(res);
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`LAN Media Server running on http://0.0.0.0:${PORT}`);
  console.log(`Serving: ${MEDIA_ROOT}`);
});
