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
    setTimeout(() => reject(new Error('timeout')), 15000);
  });
}

(async () => {
  const ws = new WebSocket(CDP_WS);
  await new Promise(r => ws.on('open', r));
  
  // GitHub 로그인 버튼 클릭
  console.log('🔐 GitHub 로그인 클릭...');
  await sendCDP(ws, 'Runtime.evaluate', {
    expression: `document.querySelector('.btn-primary')?.click(); 'clicked'`,
  });
  
  await new Promise(r => setTimeout(r, 5000));
  
  // 현재 URL 확인
  const urlResult = await sendCDP(ws, 'Runtime.evaluate', {
    expression: `window.location.href`
  });
  console.log('📍 현재 URL:', urlResult.result?.value);
  
  // 페이지 내용 확인
  const pageResult = await sendCDP(ws, 'Runtime.evaluate', {
    expression: `
      const inputs = [...document.querySelectorAll('input')].map(i => ({
        type: i.type, id: i.id, name: i.name, placeholder: i.placeholder
      }));
      const h1 = document.querySelector('h1')?.textContent;
      JSON.stringify({ h1, inputs });
    `
  });
  console.log('📄 페이지:', pageResult.result?.value);
  
  ws.close();
})().catch(e => console.error(e.message));
