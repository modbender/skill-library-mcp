#!/usr/bin/env node
// x402 Relay one-shot send — send a message and exit
// Usage: node relay-send.cjs --host <host> --port <port> --agent <name> --token <token> --to <target> --body "message"
const net = require('net');

const args = process.argv.slice(2);
const opts = {};
for (let i = 0; i < args.length; i += 2) opts[args[i].replace(/^--/, '')] = args[i + 1];

const HOST = opts.host || process.env.X402_RELAY_HOST || 'trolley.proxy.rlwy.net';
const PORT = parseInt(opts.port || process.env.X402_RELAY_PORT || '48582');
const AGENT = opts.agent || 'agent';
const TOKEN = opts.token || process.env.X402_RELAY_TOKEN || '';
const TO = opts.to;
const BODY = opts.body;

if (!TO || !BODY) { console.error('Usage: relay-send.cjs --to <agent> --body "message"'); process.exit(1); }

function frame(env) {
  const j = Buffer.from(JSON.stringify(env), 'utf8');
  const h = Buffer.alloc(4);
  h.writeUInt32BE(j.length, 0);
  return Buffer.concat([h, j]);
}

class Decoder {
  constructor() { this.buf = Buffer.alloc(0); }
  push(d) {
    this.buf = Buffer.concat([this.buf, d]);
    const out = [];
    while (this.buf.length >= 4) {
      const len = this.buf.readUInt32BE(0);
      if (len > 1048576) { this.buf = Buffer.alloc(0); break; }
      if (this.buf.length < 4 + len) break;
      try { out.push(JSON.parse(this.buf.slice(4, 4 + len).toString('utf8'))); } catch(e) {}
      this.buf = this.buf.slice(4 + len);
    }
    return out;
  }
}

const sock = net.createConnection({ host: HOST, port: PORT }, () => {
  sock.write(frame({
    v: 1, type: 'HELLO', id: `${AGENT}-${Date.now()}`, ts: Date.now(),
    payload: { agent: AGENT, version: '1.0.0', authToken: TOKEN }
  }));
});

const dec = new Decoder();
sock.on('data', (data) => {
  for (const f of dec.push(data)) {
    if (f.type === 'WELCOME') {
      sock.write(frame({ v: 1, type: 'SEND', id: `m-${Date.now()}`, ts: Date.now(), to: TO, payload: { kind: 'message', body: BODY } }));
      console.log(JSON.stringify({ ok: true, to: TO, body: BODY }));
      setTimeout(() => sock.end(), 300);
    }
    if (f.type === 'ERROR') { console.error(JSON.stringify({ error: f.payload?.message })); sock.end(); }
    if (f.type === 'PING') sock.write(frame({ v: 1, type: 'PONG', id: `p-${Date.now()}`, ts: Date.now(), payload: { nonce: f.payload?.nonce } }));
  }
});

sock.on('error', (e) => { console.error(JSON.stringify({ error: e.message })); process.exit(1); });
sock.on('close', () => process.exit(0));
setTimeout(() => { sock.destroy(); process.exit(1); }, 10000);
