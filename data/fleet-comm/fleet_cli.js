#!/usr/bin/env node
/**
 * Fleet Communication CLI - interact with the fleet message bus
 * Usage: node fleet_cli.js <command> [args]
 */

const http = require('http');

const BUS_URL = process.env.FLEET_BUS_URL || 'http://127.0.0.1:18800';
const NODE_ID = process.env.FLEET_NODE_ID || '00';

function request(method, path, data) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, BUS_URL);
    const opts = { hostname: url.hostname, port: url.port, path: url.pathname + url.search, method, headers: { 'Content-Type': 'application/json' } };
    const req = http.request(opts, res => {
      let body = '';
      res.on('data', c => body += c);
      res.on('end', () => {
        try { resolve(JSON.parse(body)); } catch { resolve(body); }
      });
    });
    req.on('error', reject);
    if (data) req.write(JSON.stringify(data));
    req.end();
  });
}

async function main() {
  const [,, cmd, ...args] = process.argv;

  switch (cmd) {
    case 'status':
      console.log(JSON.stringify(await request('GET', '/status'), null, 2));
      break;

    case 'nodes':
      console.log(JSON.stringify(await request('GET', '/nodes'), null, 2));
      break;

    case 'register':
      console.log(JSON.stringify(await request('POST', '/register', { nodeId: NODE_ID, role: args[0] || 'worker' }), null, 2));
      break;

    case 'send':
      if (args.length < 2) { console.error('Usage: fleet_cli.js send <target> <message>'); process.exit(1); }
      const target = args[0];
      const msg = args.slice(1).join(' ');
      console.log(JSON.stringify(await request('POST', '/send', { from: NODE_ID, to: target, msg, type: 'info' }), null, 2));
      break;

    case 'broadcast':
      if (!args.length) { console.error('Usage: fleet_cli.js broadcast <message>'); process.exit(1); }
      console.log(JSON.stringify(await request('POST', '/broadcast', { from: NODE_ID, msg: args.join(' '), type: 'info' }), null, 2));
      break;

    case 'read': {
      const since = args[0] || '0';
      const msgs = await request('GET', `/messages?node=${NODE_ID}&since=${since}`);
      if (!msgs.length) { console.log('📭 无新消息'); break; }
      msgs.forEach(m => {
        const time = new Date(m.ts).toLocaleTimeString();
        console.log(`[${time}] ${m.from} → ${m.to}: ${m.msg}`);
      });
      break;
    }

    case 'task':
      if (args.length < 2) { console.error('Usage: fleet_cli.js task <target> <task description>'); process.exit(1); }
      console.log(JSON.stringify(await request('POST', '/send', { from: NODE_ID, to: args[0], msg: args.slice(1).join(' '), type: 'task' }), null, 2));
      break;

    case 'result':
      if (args.length < 2) { console.error('Usage: fleet_cli.js result <target> <result>'); process.exit(1); }
      console.log(JSON.stringify(await request('POST', '/send', { from: NODE_ID, to: args[0], msg: args.slice(1).join(' '), type: 'result' }), null, 2));
      break;

    default:
      console.log(`🚌 Fleet CLI (node: ${NODE_ID}, bus: ${BUS_URL})
Commands:
  status              - Bus status
  nodes               - List known nodes
  register [role]     - Register this node
  send <to> <msg>     - Send message to node
  broadcast <msg>     - Broadcast to all
  read [since_ts]     - Read messages for this node
  task <to> <desc>    - Send task to node
  result <to> <data>  - Send result back`);
  }
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
