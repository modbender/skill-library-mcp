const WebSocket = require('ws');
const CDP_WS = 'ws://127.0.0.1:18800/devtools/page/05A159BAC2A7FE7547F5DA23AC3FC655';
let msgId = 1;

function sendCDP(ws, method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = msgId++;
    ws.send(JSON.stringify({ id, method, params }));
    const handler = (data) => {
      const msg = JSON.parse(data.toString());
      if (msg.id === id) {
        ws.removeListener('message', handler);
        if (msg.error) reject(new Error(msg.error.message));
        else resolve(msg.result);
      }
    };
    ws.on('message', handler);
    setTimeout(() => reject(new Error('timeout')), 10000);
  });
}

(async () => {
  const ws = new WebSocket(CDP_WS);
  await new Promise(r => ws.on('open', r));
  
  // 페이지 HTML 구조 파악
  const r = await sendCDP(ws, 'Runtime.evaluate', {
    expression: `
      // 모든 input 태그
      const inputs = [...document.querySelectorAll('input')].map((inp, i) => ({
        i, type: inp.type, placeholder: inp.placeholder, value: inp.value,
        id: inp.id, name: inp.name, className: inp.className?.slice(0,50)
      }));
      // 모든 button
      const buttons = [...document.querySelectorAll('button')].map((b, i) => ({
        i, text: b.textContent?.trim()?.slice(0,40), className: b.className?.slice(0,50)
      }));
      // drop zone 관련
      const divs = [...document.querySelectorAll('div')].filter(d => {
        const t = (d.className + ' ' + d.textContent).toLowerCase();
        return t.includes('drop') || t.includes('choose') || t.includes('folder') || t.includes('file');
      }).map(d => ({
        class: d.className?.slice(0,60),
        text: d.textContent?.trim()?.slice(0,80)
      })).slice(0, 10);
      
      JSON.stringify({ inputs, buttons, divs }, null, 2);
    `
  });
  console.log(r.result?.value);
  ws.close();
})().catch(e => console.error(e.message));
