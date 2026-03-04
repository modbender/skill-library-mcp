const WebSocket = require('ws');
const CDP_WS = 'ws://127.0.0.1:18800/devtools/page/05A159BAC2A7FE7547F5DA23AC3FC655';
let msgId = 1;
function sendCDP(ws, method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = msgId++;
    ws.send(JSON.stringify({ id, method, params }));
    const handler = (data) => {
      const msg = JSON.parse(data.toString());
      if (msg.id === id) { ws.removeListener('message', handler); resolve(msg.result); }
    };
    ws.on('message', handler);
    setTimeout(() => reject(new Error('timeout')), 10000);
  });
}
(async () => {
  const ws = new WebSocket(CDP_WS);
  await new Promise(r => ws.on('open', r));
  const r = await sendCDP(ws, 'Runtime.evaluate', {
    expression: `JSON.stringify({ url: location.href, title: document.title, body: document.body?.innerText?.slice(0, 500) })`
  });
  console.log(r.result?.value);
  ws.close();
})().catch(e => console.error(e.message));
