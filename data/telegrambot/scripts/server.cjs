const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

const ROOT = path.resolve(process.env.GOD_MODE_ROOT || 'C:\\');
const HOST = process.env.GOD_MODE_HOST || '127.0.0.1';
const PORT = Number(process.env.GOD_MODE_PORT || 8888);
const TOKEN = process.env.GOD_MODE_TOKEN || '';
const TOKEN_REQUIRED = process.env.GOD_MODE_TOKEN_REQUIRED !== 'false';
const MAX_READ_BYTES = Number(process.env.GOD_MODE_MAX_READ_BYTES || 1024 * 1024);
const ASSETS_DIR = path.resolve(__dirname, '../assets');

const MIME = {
  '.txt': 'text/plain; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.mp4': 'video/mp4',
  '.mp3': 'audio/mpeg',
  '.pdf': 'application/pdf',
};

if (TOKEN_REQUIRED && !TOKEN) {
  console.error('[god-mode-manager] GOD_MODE_TOKEN is required unless GOD_MODE_TOKEN_REQUIRED=false');
  process.exit(1);
}

function sendJSON(res, status, data) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(data, null, 2));
}

function sendText(res, status, text) {
  res.writeHead(status, { 'Content-Type': 'text/plain; charset=utf-8' });
  res.end(text);
}

function sendHTML(res, status, html) {
  res.writeHead(status, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(html);
}

function serveUI(res, tokenRequired) {
  try {
    const indexPath = path.join(ASSETS_DIR, 'index.html');
    const html = fs.readFileSync(indexPath, 'utf8').replace('__TOKEN_REQUIRED__', tokenRequired ? 'true' : 'false');
    return sendHTML(res, 200, html);
  } catch (err) {
    return sendText(res, 500, `UI load failed: ${err.message}`);
  }
}

function getToken(req, parsedUrl) {
  const xToken = req.headers['x-god-mode-token'];
  if (typeof xToken === 'string' && xToken) return xToken;

  const auth = req.headers.authorization;
  if (typeof auth === 'string' && auth.toLowerCase().startsWith('bearer ')) {
    return auth.slice(7).trim();
  }

  const qToken = parsedUrl.searchParams.get('token');
  if (qToken) return qToken;
  return '';
}

function isAuthenticated(req, parsedUrl) {
  if (!TOKEN_REQUIRED) return true;
  return getToken(req, parsedUrl) === TOKEN;
}

function resolveSafePath(rawPath) {
  const requested = (rawPath || '').replace(/^[/\\]+/, '');
  const fullPath = path.resolve(ROOT, requested);
  const rel = path.relative(ROOT, fullPath);
  const safe = rel === '' || (!rel.startsWith('..') && !path.isAbsolute(rel));
  return { safe, fullPath };
}

function mapEntry(fullPath, dirent) {
  const itemPath = path.join(fullPath, dirent.name);
  const st = fs.statSync(itemPath);
  return {
    name: dirent.name,
    isDirectory: dirent.isDirectory(),
    isFile: dirent.isFile(),
    size: dirent.isFile() ? st.size : 0,
    modified: st.mtime.toISOString(),
  };
}

function respondWithFile(res, filePath, rangeHeader) {
  const st = fs.statSync(filePath);
  const size = st.size;
  const ext = path.extname(filePath).toLowerCase();
  const mime = MIME[ext] || 'application/octet-stream';

  if (!rangeHeader) {
    res.writeHead(200, {
      'Content-Type': mime,
      'Content-Length': size,
      'Accept-Ranges': 'bytes',
    });
    return fs.createReadStream(filePath).pipe(res);
  }

  const parts = rangeHeader.replace(/bytes=/, '').split('-');
  const start = Number.parseInt(parts[0], 10);
  const end = parts[1] ? Number.parseInt(parts[1], 10) : size - 1;
  const invalid = Number.isNaN(start) || Number.isNaN(end) || start < 0 || end < start || end >= size;
  if (invalid) {
    res.writeHead(416, { 'Content-Range': `bytes */${size}` });
    return res.end();
  }

  const chunkSize = end - start + 1;
  res.writeHead(206, {
    'Content-Range': `bytes ${start}-${end}/${size}`,
    'Accept-Ranges': 'bytes',
    'Content-Length': chunkSize,
    'Content-Type': mime,
  });
  return fs.createReadStream(filePath, { start, end }).pipe(res);
}

const server = http.createServer((req, res) => {
  const parsedUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const route = parsedUrl.pathname;
  const accept = req.headers.accept || '';
  const wantsHtml = typeof accept === 'string' && accept.includes('text/html');

  if ((route === '/' || route === '/ui') && req.method === 'GET' && wantsHtml) {
    return serveUI(res, TOKEN_REQUIRED);
  }

  if (!isAuthenticated(req, parsedUrl)) {
    return sendJSON(res, 401, { error: 'Unauthorized' });
  }

  if (route === '/' && req.method === 'GET') {
    return sendJSON(res, 200, {
      ok: true,
      service: 'god-mode-manager',
      host: HOST,
      port: PORT,
      root: ROOT,
      tokenRequired: TOKEN_REQUIRED,
    });
  }

  if (route === '/list' && req.method === 'GET') {
    const rawPath = parsedUrl.searchParams.get('path') || '';
    const { safe, fullPath } = resolveSafePath(rawPath);
    if (!safe) return sendJSON(res, 403, { error: 'Path traversal detected' });

    try {
      const st = fs.statSync(fullPath);
      if (!st.isDirectory()) return sendJSON(res, 400, { error: 'Target path is not a directory' });
      const entries = fs.readdirSync(fullPath, { withFileTypes: true }).map((d) => mapEntry(fullPath, d));
      return sendJSON(res, 200, { path: fullPath, entries });
    } catch (err) {
      return sendJSON(res, 500, { error: `List failed: ${err.message}` });
    }
  }

  if (route === '/read' && req.method === 'GET') {
    const rawPath = parsedUrl.searchParams.get('path') || '';
    const { safe, fullPath } = resolveSafePath(rawPath);
    if (!safe) return sendJSON(res, 403, { error: 'Path traversal detected' });

    try {
      const st = fs.statSync(fullPath);
      if (!st.isFile()) return sendJSON(res, 400, { error: 'Target path is not a file' });
      if (st.size > MAX_READ_BYTES) {
        return sendJSON(res, 413, {
          error: `File too large for /read (${st.size} bytes > ${MAX_READ_BYTES} bytes). Use /download.`,
        });
      }
      const content = fs.readFileSync(fullPath, 'utf8');
      return sendJSON(res, 200, { path: fullPath, bytes: st.size, content });
    } catch (err) {
      return sendJSON(res, 500, { error: `Read failed: ${err.message}` });
    }
  }

  if (route === '/download' && req.method === 'GET') {
    const rawPath = parsedUrl.searchParams.get('path') || '';
    const { safe, fullPath } = resolveSafePath(rawPath);
    if (!safe) return sendJSON(res, 403, { error: 'Path traversal detected' });

    try {
      const st = fs.statSync(fullPath);
      if (!st.isFile()) return sendJSON(res, 400, { error: 'Target path is not a file' });
      return respondWithFile(res, fullPath, req.headers.range);
    } catch (err) {
      return sendJSON(res, 500, { error: `Download failed: ${err.message}` });
    }
  }

  return sendText(res, 404, `Not Found: ${req.method} ${route}`);
});

server.listen(PORT, HOST, () => {
  console.log(`[god-mode-manager] listening on http://${HOST}:${PORT}`);
  console.log(`[god-mode-manager] root=${ROOT}`);
  console.log(`[god-mode-manager] tokenRequired=${TOKEN_REQUIRED}`);
});

process.on('SIGINT', () => {
  console.log('[god-mode-manager] shutting down...');
  server.close(() => process.exit(0));
});
