/**
 * Browser Relay — streams a headless Chrome tab over WebSocket
 * so a human can see and interact with it remotely (via Tailscale/LAN).
 *
 * Uses CDP Page.startScreencast for frames + Input.dispatch* for interaction.
 */
const http = require('http');
const fs = require('fs');
const path = require('path');
const WebSocket = require('ws');
const { getPageTargets } = require('./cdp');

const TEMPLATE = path.join(__dirname, 'templates', 'browser-relay.html');

/** Minimal CDP connection that supports both commands and events */
class CdpConnection {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.ws = null;
    this.msgId = 0;
    this.pending = new Map();
    this.onEvent = null; // callback for CDP events
  }

  connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.wsUrl, { perMessageDeflate: false });
      this.ws.on('open', resolve);
      this.ws.on('message', (raw) => {
        const msg = JSON.parse(raw);
        if (msg.id && this.pending.has(msg.id)) {
          const { resolve, reject } = this.pending.get(msg.id);
          this.pending.delete(msg.id);
          if (msg.error) reject(new Error(msg.error.message));
          else resolve(msg.result);
        } else if (msg.method && this.onEvent) {
          this.onEvent(msg.method, msg.params);
        }
      });
      this.ws.on('error', reject);
    });
  }

  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = ++this.msgId;
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
      setTimeout(() => {
        if (this.pending.has(id)) {
          this.pending.delete(id);
          reject(new Error('CDP timeout'));
        }
      }, 15000);
    });
  }

  close() {
    if (this.ws) this.ws.close();
  }
}

async function createBrowserRelay({
  cdpPort = 18800,
  targetId,
  port = 0,
  host = '0.0.0.0',
  timeout = 300000,
  quality = 60,
  maxWidth = 1280,
  maxHeight = 900,
  everyNthFrame = 1,
} = {}) {
  // Find the target page
  if (!targetId) {
    const pages = await getPageTargets(cdpPort);
    if (!pages.length) throw new Error('No browser pages found');
    targetId = pages[0].id;
  }

  const wsUrl = `ws://127.0.0.1:${cdpPort}/devtools/page/${targetId}`;
  const cdp = new CdpConnection(wsUrl);
  await cdp.connect();
  console.log('[browser-relay] CDP connected to', targetId);

  // Get viewport size
  const layoutMetrics = await cdp.send('Page.getLayoutMetrics').catch(() => null);
  const viewportWidth = layoutMetrics?.cssVisualViewport?.clientWidth || 1280;
  const viewportHeight = layoutMetrics?.cssVisualViewport?.clientHeight || 800;
  console.log(`[browser-relay] viewport: ${viewportWidth}x${viewportHeight}`);

  const html = fs.readFileSync(TEMPLATE, 'utf-8')
    .replace('{{VIEWPORT_WIDTH}}', viewportWidth)
    .replace('{{VIEWPORT_HEIGHT}}', viewportHeight);

  // Track connected clients
  const clients = new Set();
  let frameCount = 0;

  // Handle CDP events (screencast frames)
  cdp.onEvent = (method, params) => {
    if (method === 'Page.screencastFrame') {
      frameCount++;
      const { data, sessionId, metadata } = params;
      // Ack the frame so Chrome sends the next one
      cdp.send('Page.screencastFrameAck', { sessionId }).catch(() => {});
      // Broadcast to all connected clients
      const payload = JSON.stringify({ type: 'frame', data, metadata });
      for (const ws of clients) {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(payload);
        }
      }
      if (frameCount % 50 === 1) {
        console.log(`[browser-relay] frame #${frameCount}, clients: ${clients.size}`);
      }
    }
  };

  // Enable Page domain and start screencast
  await cdp.send('Page.enable');
  await cdp.send('Page.startScreencast', {
    format: 'jpeg',
    quality,
    maxWidth,
    maxHeight,
    everyNthFrame,
  });
  console.log('[browser-relay] screencast started');

  // HTTP server
  const server = http.createServer((req, res) => {
    if (req.method === 'GET' && (req.url === '/' || req.url === '/index.html')) {
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(html);
    } else {
      res.writeHead(404);
      res.end('Not found');
    }
  });

  // WebSocket server for client interaction
  const wss = new WebSocket.Server({ server });

  wss.on('connection', async (ws) => {
    clients.add(ws);
    console.log(`[browser-relay] client connected (${clients.size} total)`);
    // Restart screencast so frames flow to new clients
    try {
      await cdp.send('Page.stopScreencast').catch(() => {});
      await cdp.send('Page.startScreencast', {
        format: 'jpeg', quality, maxWidth, maxHeight, everyNthFrame,
      });
      console.log('[browser-relay] screencast restarted for new client');
    } catch (e) {
      console.error('[browser-relay] screencast restart failed:', e.message);
    }

    ws.on('message', async (raw) => {
      try {
        const msg = JSON.parse(raw);
        await handleInput(cdp, msg, viewportWidth, viewportHeight);
      } catch (e) {
        console.error('[browser-relay] input error:', e.message);
      }
    });

    ws.on('close', () => {
      clients.delete(ws);
      console.log(`[browser-relay] client disconnected (${clients.size} total)`);
    });
  });

  // Timeout
  let timer;
  const cleanup = () => {
    clearTimeout(timer);
    cdp.send('Page.stopScreencast').catch(() => {});
    cdp.close();
    wss.close();
    server.close();
    console.log('[browser-relay] shut down');
  };

  if (timeout > 0) {
    timer = setTimeout(cleanup, timeout);
  }

  return new Promise((resolve, reject) => {
    server.listen(port, host, () => {
      const actualPort = server.address().port;
      console.log(`[browser-relay] listening on ${host}:${actualPort}`);
      resolve({ port: actualPort, url: `http://${host}:${actualPort}`, cleanup, clients });
    });
    server.on('error', reject);
  });
}

async function handleInput(cdp, msg, viewportWidth, viewportHeight) {
  console.log(`[browser-relay] input: ${msg.type}`, msg.x !== undefined ? `(${msg.x},${msg.y})` : '');
  switch (msg.type) {
    case 'mousedown':
    case 'mouseup':
    case 'mousemove':
      await cdp.send('Input.dispatchMouseEvent', {
        type: msg.type === 'mousemove' ? 'mouseMoved' :
              msg.type === 'mousedown' ? 'mousePressed' : 'mouseReleased',
        x: msg.x,
        y: msg.y,
        button: msg.button || 'left',
        clickCount: msg.clickCount || (msg.type === 'mousedown' ? 1 : 0),
      });
      break;

    case 'click':
      await cdp.send('Input.dispatchMouseEvent', {
        type: 'mousePressed', x: msg.x, y: msg.y, button: 'left', clickCount: 1,
      });
      await cdp.send('Input.dispatchMouseEvent', {
        type: 'mouseReleased', x: msg.x, y: msg.y, button: 'left', clickCount: 1,
      });
      break;

    case 'keydown':
    case 'keyup': {
      const cdpType = msg.type === 'keydown' ? 'keyDown' : 'keyUp';
      const params = {
        type: cdpType,
        key: msg.key,
        code: msg.code || '',
        windowsVirtualKeyCode: msg.keyCode || 0,
        nativeVirtualKeyCode: msg.keyCode || 0,
      };
      if (msg.text && msg.type === 'keydown') {
        params.text = msg.text;
      }
      await cdp.send('Input.dispatchKeyEvent', params);
      break;
    }

    case 'scroll':
      await cdp.send('Input.dispatchMouseEvent', {
        type: 'mouseWheel',
        x: msg.x || viewportWidth / 2,
        y: msg.y || viewportHeight / 2,
        deltaX: msg.deltaX || 0,
        deltaY: msg.deltaY || 0,
      });
      break;

    case 'touch':
      await cdp.send('Input.dispatchMouseEvent', {
        type: msg.action === 'start' ? 'mousePressed' :
              msg.action === 'end' ? 'mouseReleased' : 'mouseMoved',
        x: msg.x,
        y: msg.y,
        button: 'left',
        clickCount: msg.action === 'start' ? 1 : 0,
      });
      break;
  }
}

module.exports = { createBrowserRelay };
