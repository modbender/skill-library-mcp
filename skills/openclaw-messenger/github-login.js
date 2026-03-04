const WebSocket = require('ws');
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
    setTimeout(() => reject(new Error('timeout')), 20000);
  });
}
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
async function eval_(ws, expr) {
  const r = await sendCDP(ws, 'Runtime.evaluate', { expression: expr, awaitPromise: true });
  return r.result?.value;
}

(async () => {
  const ws = new WebSocket('ws://127.0.0.1:18800/devtools/page/05A159BAC2A7FE7547F5DA23AC3FC655');
  await new Promise(r => ws.on('open', r));
  
  // clawhub upload 페이지로 이동
  await sendCDP(ws, 'Page.navigate', { url: 'https://clawhub.ai/upload' });
  await sleep(3000);
  
  let url = await eval_(ws, 'location.href');
  console.log('1. URL:', url);
  
  // Sign in 버튼 클릭
  await eval_(ws, `
    const btns = document.querySelectorAll('button, a');
    for (const b of btns) {
      if (b.textContent?.includes('Sign in') || b.textContent?.includes('GitHub')) {
        b.click();
        break;
      }
    }
  `);
  await sleep(5000);
  
  url = await eval_(ws, 'location.href');
  console.log('2. URL after sign in click:', url);
  
  // GitHub 로그인 페이지라면
  if (url.includes('github.com/login')) {
    console.log('3. GitHub 로그인...');
    await eval_(ws, `
      const login = document.getElementById('login_field');
      const pw = document.getElementById('password');
      if (login) { login.value = 'tames@tags.kr'; login.dispatchEvent(new Event('input', {bubbles:true})); }
      if (pw) { pw.value = 'tames0210!'; pw.dispatchEvent(new Event('input', {bubbles:true})); }
    `);
    await sleep(500);
    await eval_(ws, `
      const form = document.querySelector('form[action="/session"]');
      if (form) form.submit();
    `);
    await sleep(8000);
    
    url = await eval_(ws, 'location.href');
    console.log('4. After login:', url);
  }
  
  // GitHub OAuth authorize 페이지
  if (url.includes('github.com') && url.includes('authorize')) {
    console.log('5. OAuth authorize...');
    await eval_(ws, `
      const btn = document.querySelector('button[type="submit"][name="authorize"]') ||
                  document.querySelector('#js-oauth-authorize-btn');
      if (btn) btn.click();
    `);
    await sleep(5000);
    url = await eval_(ws, 'location.href');
    console.log('6. After authorize:', url);
  }
  
  // session 페이지 (로그인 에러?)
  if (url.includes('github.com/session')) {
    const pageText = await eval_(ws, 'document.body?.innerText?.slice(0, 300)');
    console.log('⚠️ session 페이지:', pageText);
  }
  
  // clawhub으로 돌아왔으면
  if (url.includes('clawhub')) {
    const body = await eval_(ws, 'document.body?.innerText?.slice(0, 300)');
    console.log('✅ clawhub:', body);
  }
  
  ws.close();
})().catch(e => console.error('❌', e.message));
