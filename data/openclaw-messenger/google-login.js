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
    setTimeout(() => reject(new Error('timeout')), 30000);
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
  
  let url = await eval_(ws, 'location.href');
  console.log('현재:', url);
  
  // "Continue with Google" 버튼 클릭
  console.log('🔐 Continue with Google 클릭...');
  await eval_(ws, `
    const links = document.querySelectorAll('a, button');
    for (const el of links) {
      if (el.textContent?.includes('Continue with Google') || el.textContent?.includes('Google')) {
        el.click();
        break;
      }
    }
  `);
  await sleep(5000);
  
  url = await eval_(ws, 'location.href');
  console.log('Google 로그인 URL:', url);
  
  // Google 로그인 - 이메일 입력
  if (url.includes('accounts.google.com')) {
    console.log('📧 이메일 입력...');
    await eval_(ws, `
      const emailInput = document.querySelector('input[type="email"]');
      if (emailInput) {
        emailInput.value = 'tames@tags.kr';
        emailInput.dispatchEvent(new Event('input', {bubbles:true}));
      }
    `);
    await sleep(1000);
    
    // Next 버튼
    await eval_(ws, `
      const btns = document.querySelectorAll('button, div[role="button"]');
      for (const b of btns) {
        if (b.textContent?.includes('Next') || b.textContent?.includes('다음') || b.id === 'identifierNext') {
          b.click();
          break;
        }
      }
    `);
    await sleep(5000);
    
    url = await eval_(ws, 'location.href');
    console.log('비밀번호 페이지:', url);
    
    // 비밀번호 입력
    console.log('🔑 비밀번호 입력...');
    await eval_(ws, `
      const pwInput = document.querySelector('input[type="password"]');
      if (pwInput) {
        pwInput.focus();
        pwInput.value = 'tames0210!';
        pwInput.dispatchEvent(new Event('input', {bubbles:true}));
      }
    `);
    await sleep(1000);
    
    // Next 버튼
    await eval_(ws, `
      const btns = document.querySelectorAll('button, div[role="button"]');
      for (const b of btns) {
        if (b.textContent?.includes('Next') || b.textContent?.includes('다음') || b.id === 'passwordNext') {
          b.click();
          break;
        }
      }
    `);
    await sleep(8000);
    
    url = await eval_(ws, 'location.href');
    console.log('로그인 후:', url);
    
    // 2FA나 추가 확인이 있을 수 있음
    const bodyText = await eval_(ws, 'document.body?.innerText?.slice(0, 300)');
    console.log('페이지 내용:', bodyText);
  }
  
  // 최종 확인
  await sleep(3000);
  url = await eval_(ws, 'location.href');
  console.log('최종 URL:', url);
  
  if (url.includes('clawhub')) {
    const body = await eval_(ws, 'document.body?.innerText?.slice(0, 200)');
    console.log('✅ clawhub 복귀:', body);
  }
  
  ws.close();
})().catch(e => console.error('❌', e.message));
