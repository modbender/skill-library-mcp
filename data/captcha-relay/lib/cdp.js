/**
 * Minimal CDP (Chrome DevTools Protocol) client
 */
const WebSocket = require('ws');
const http = require('http');

let msgId = 0;

function getCdpWsUrl(port = 18800) {
  return new Promise((resolve, reject) => {
    http.get(`http://127.0.0.1:${port}/json/version`, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data).webSocketDebuggerUrl);
        } catch (e) { reject(e); }
      });
    }).on('error', reject);
  });
}

function getPageTargets(port = 18800) {
  return new Promise((resolve, reject) => {
    http.get(`http://127.0.0.1:${port}/json/list`, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try {
          const targets = JSON.parse(data).filter(t => t.type === 'page');
          resolve(targets);
        } catch (e) { reject(e); }
      });
    }).on('error', reject);
  });
}

function cdpSend(wsUrl, method, params = {}) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl, { perMessageDeflate: false });
    const id = ++msgId;
    ws.on('open', () => {
      ws.send(JSON.stringify({ id, method, params }));
    });
    ws.on('message', (data) => {
      const msg = JSON.parse(data);
      if (msg.id === id) {
        ws.close();
        if (msg.error) reject(new Error(msg.error.message));
        else resolve(msg.result);
      }
    });
    ws.on('error', reject);
    setTimeout(() => { ws.close(); reject(new Error('CDP timeout')); }, 10000);
  });
}

/**
 * Long-lived CDP session for multiple commands
 */
class CdpSession {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.ws = null;
    this.pending = new Map();
  }

  connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.wsUrl, { perMessageDeflate: false });
      this.ws.on('open', resolve);
      this.ws.on('message', (data) => {
        const msg = JSON.parse(data);
        if (msg.id && this.pending.has(msg.id)) {
          const { resolve, reject } = this.pending.get(msg.id);
          this.pending.delete(msg.id);
          if (msg.error) reject(new Error(msg.error.message));
          else resolve(msg.result);
        }
      });
      this.ws.on('error', reject);
    });
  }

  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = ++msgId;
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

module.exports = { getCdpWsUrl, getPageTargets, cdpSend, CdpSession };
