/**
 * Lightweight HTTP relay server for CAPTCHA solving
 */
const http = require('http');
const fs = require('fs');
const path = require('path');

function createRelayServer({ type, sitekey, pageUrl, timeout = 120000 }) {
  return new Promise((resolve, reject) => {
    let tokenResolve;
    const tokenPromise = new Promise(r => { tokenResolve = r; });
    let server;
    let timer;

    const templateFile = path.join(__dirname, 'templates', `${type}.html`);
    let template;
    try {
      template = fs.readFileSync(templateFile, 'utf-8');
    } catch {
      reject(new Error(`No template for CAPTCHA type: ${type}`));
      return;
    }

    const html = template
      .replace(/\{\{SITEKEY\}\}/g, sitekey)
      .replace(/\{\{PAGE_URL\}\}/g, pageUrl || '');

    server = http.createServer((req, res) => {
      if (req.method === 'GET' && req.url === '/') {
        res.writeHead(200, { 'Content-Type': 'text/html', 'Access-Control-Allow-Origin': '*' });
        res.end(html);
      } else if (req.method === 'POST' && req.url === '/token') {
        let body = '';
        req.on('data', c => body += c);
        req.on('end', () => {
          try {
            const { token } = JSON.parse(body);
            res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
            res.end(JSON.stringify({ ok: true }));
            // Write token to predictable file for external consumers
            const tokenFile = path.join(require('os').tmpdir(), 'captcha-relay-token.txt');
            fs.writeFileSync(tokenFile, token);
            tokenResolve(token);
          } catch {
            res.writeHead(400);
            res.end('Bad request');
          }
        });
      } else if (req.method === 'OPTIONS') {
        res.writeHead(200, {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        });
        res.end();
      } else {
        res.writeHead(404);
        res.end('Not found');
      }
    });

    server.listen(0, '0.0.0.0', () => {
      const port = server.address().port;
      timer = setTimeout(() => {
        server.close();
        tokenResolve(null); // timeout
      }, timeout);

      resolve({
        port,
        waitForToken: async () => {
          const token = await tokenPromise;
          clearTimeout(timer);
          server.close();
          return token;
        },
        close: () => {
          clearTimeout(timer);
          server.close();
        },
      });
    });

    server.on('error', reject);
  });
}

module.exports = { createRelayServer };
