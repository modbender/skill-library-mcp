#!/usr/bin/env node
/**
 * Azure OpenAI Proxy for OpenClaw
 * 
 * Bridges Azure OpenAI with OpenClaw by handling the api-version
 * query parameter that OpenClaw's URL construction doesn't support.
 * 
 * @author Clawfinger (github.com/BenediktSchackenberg)
 * @license MIT
 */

const http = require('http');
const https = require('https');

// ═══════════════════════════════════════════════════════════════
//                        CONFIGURATION
// ═══════════════════════════════════════════════════════════════

const config = {
  port: parseInt(process.env.AZURE_PROXY_PORT || '18790'),
  bind: process.env.AZURE_PROXY_BIND || '127.0.0.1',
  
  azure: {
    endpoint: process.env.AZURE_OPENAI_ENDPOINT || 'YOUR_RESOURCE.openai.azure.com',
    deployment: process.env.AZURE_OPENAI_DEPLOYMENT || 'gpt-4o',
    apiVersion: process.env.AZURE_OPENAI_API_VERSION || '2025-01-01-preview'
  }
};

// ═══════════════════════════════════════════════════════════════
//                        PROXY SERVER
// ═══════════════════════════════════════════════════════════════

const server = http.createServer((req, res) => {
  // Health check
  if (req.method === 'GET' && req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', deployment: config.azure.deployment }));
    return;
  }

  // Only POST /chat/completions
  if (req.method !== 'POST' || !req.url.includes('/chat/completions')) {
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Not found', hint: 'POST /chat/completions only' }));
    return;
  }

  let body = '';
  req.on('data', chunk => { body += chunk; });
  
  req.on('end', () => {
    const azurePath = `/openai/deployments/${config.azure.deployment}/chat/completions?api-version=${config.azure.apiVersion}`;
    const apiKey = req.headers['api-key'] || req.headers['authorization']?.replace('Bearer ', '') || '';

    const options = {
      hostname: config.azure.endpoint,
      port: 443,
      path: azurePath,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'api-key': apiKey,
        'Content-Length': Buffer.byteLength(body)
      }
    };

    const ts = new Date().toISOString();
    console.log(`[${ts}] → ${config.azure.deployment}`);

    const proxyReq = https.request(options, (proxyRes) => {
      console.log(`[${ts}] ${proxyRes.statusCode >= 400 ? '✗' : '✓'} ${proxyRes.statusCode}`);
      res.writeHead(proxyRes.statusCode, proxyRes.headers);
      proxyRes.pipe(res);
    });

    proxyReq.on('error', (err) => {
      console.error(`[${ts}] ✗ ${err.message}`);
      res.writeHead(502, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Bad Gateway', message: err.message }));
    });

    proxyReq.write(body);
    proxyReq.end();
  });
});

// ═══════════════════════════════════════════════════════════════
//                          STARTUP
// ═══════════════════════════════════════════════════════════════

server.listen(config.port, config.bind, () => {
  console.log(`
╔══════════════════════════════════════════════════════════╗
║         🚀 Azure OpenAI Proxy for OpenClaw               ║
╠══════════════════════════════════════════════════════════╣
║  Proxy:      http://${config.bind}:${config.port}`.padEnd(59) + `║
║  Deployment: ${config.azure.deployment}`.padEnd(59) + `║
║  API Ver:    ${config.azure.apiVersion}`.padEnd(59) + `║
║  Target:     ${config.azure.endpoint}`.padEnd(59) + `║
╚══════════════════════════════════════════════════════════╝
`);
});

process.on('SIGTERM', () => { server.close(() => process.exit(0)); });
process.on('SIGINT', () => { server.close(() => process.exit(0)); });
