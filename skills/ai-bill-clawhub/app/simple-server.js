import { createServer } from 'http';
import { readFile } from 'fs/promises';
import { extname } from 'path';

const PORT = 8003;

const server = createServer(async (req, res) => {
  console.log(`${req.method} ${req.url}`);
  
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  let filePath = '.' + req.url;
  if (filePath === './') {
    filePath = './dist/index.html';
  }
  
  // Handle API endpoints
  if (req.url === '/api/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'online',
      service: 'ai-bill',
      port: PORT,
      timestamp: new Date().toISOString()
    }));
    return;
  }
  
  if (req.url === '/api/usage') {
    try {
      const usageData = JSON.parse(await readFile('./dist/usage.json', 'utf8'));
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        status: 'success',
        timestamp: new Date().toISOString(),
        data: usageData
      }));
    } catch (error) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        status: 'error',
        message: 'Usage data not available',
        timestamp: new Date().toISOString()
      }));
    }
    return;
  }
  
  // Handle static files
  const extnameStr = extname(filePath);
  let contentType = 'text/html';
  
  switch (extnameStr) {
    case '.js':
      contentType = 'text/javascript';
      break;
    case '.css':
      contentType = 'text/css';
      break;
    case '.json':
      contentType = 'application/json';
      break;
    case '.png':
      contentType = 'image/png';
      break;
    case '.jpg':
      contentType = 'image/jpg';
      break;
    case '.ico':
      contentType = 'image/x-icon';
      break;
  }
  
  try {
    const content = await readFile(filePath);
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(content);
  } catch (error) {
    if (error.code === 'ENOENT') {
      // File not found
      if (req.url === '/usage_live.json') {
        // Redirect to dist/usage.json
        try {
          const data = await readFile('./dist/usage.json');
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(data);
        } catch (err) {
          res.writeHead(404);
          res.end('File not found');
        }
      } else {
        res.writeHead(404);
        res.end('File not found');
      }
    } else {
      // Server error
      res.writeHead(500);
      res.end('Server error: ' + error.code);
    }
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`AI Billing System running on port ${PORT} (IPv4 & IPv6).`);
});