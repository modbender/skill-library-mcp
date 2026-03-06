#!/usr/bin/env node
// Contract Diagram Engine - Read/Write Server

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = 8080;
const ENGINE_DIR = __dirname;

const mimeTypes = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.md': 'text/markdown',
};

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  
  // REALPATH endpoint (GET /realpath?path=...)
  if (req.method === 'GET' && parsedUrl.pathname === '/realpath') {
    try {
      const filePath = parsedUrl.query.path;
      const fullPath = path.join(ENGINE_DIR, filePath);
      const realPath = fs.realpathSync(fullPath);
      const basename = path.basename(realPath);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ basename }));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }
  
  // WRITE endpoint (POST /write)
  if (req.method === 'POST' && parsedUrl.pathname === '/write') {
    let body = '';
    req.on('data', chunk => { body += chunk.toString(); });
    req.on('end', () => {
      try {
        const { path: filePath, content } = JSON.parse(body);
        const fullPath = path.join(ENGINE_DIR, filePath);
        
        // Security: only allow writes within engine directory
        if (!fullPath.startsWith(ENGINE_DIR)) {
          res.writeHead(403, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Path outside engine directory' }));
          return;
        }
        
        fs.writeFileSync(fullPath, content, 'utf8');
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: true }));
      } catch (error) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: error.message }));
      }
    });
    return;
  }
  
  // READ endpoint (GET files)
  let filePath = parsedUrl.pathname === '/' ? '/index.html' : parsedUrl.pathname;
  filePath = path.join(ENGINE_DIR, filePath);
  
  const ext = path.extname(filePath);
  const contentType = mimeTypes[ext] || 'application/octet-stream';
  
  fs.readFile(filePath, (error, content) => {
    if (error) {
      if (error.code === 'ENOENT') {
        res.writeHead(404);
        res.end('File not found');
      } else {
        res.writeHead(500);
        res.end(`Server error: ${error.code}`);
      }
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content, 'utf-8');
    }
  });
});

server.listen(PORT, () => {
  console.log('🏴 Contract Diagram Engine starting...');
  console.log(`Engine: ${ENGINE_DIR}`);
  console.log(`Port: ${PORT}`);
  console.log('');
  console.log(`Usage: http://localhost:${PORT}/?md=/path/to/file.md`);
  console.log('');
  console.log('Example tape:');
  console.log(`  http://localhost:${PORT}/?md=contract-skill.md`);
  console.log('');
  console.log('Press Ctrl+C to stop');
});
