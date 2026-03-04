/**
 * CDP를 이용해 clawhub.ai/upload 페이지에서 스킬 퍼블리시
 */
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
    setTimeout(() => reject(new Error('CDP timeout')), 15000);
  });
}

async function run() {
  const ws = new WebSocket(CDP_WS);
  
  await new Promise((resolve, reject) => {
    ws.on('open', resolve);
    ws.on('error', reject);
  });
  
  console.log('✅ CDP 연결');
  
  // 1. upload 페이지로 이동
  await sendCDP(ws, 'Page.navigate', { url: 'https://clawhub.ai/upload' });
  await new Promise(r => setTimeout(r, 3000));
  console.log('📄 upload 페이지 로드');
  
  // 2. 폼 채우기
  const fillScript = `
    (async () => {
      // 잠시 대기
      await new Promise(r => setTimeout(r, 1000));
      
      // slug 입력
      const slugInput = document.querySelector('input[placeholder*="claw"]') || document.querySelectorAll('input')[0];
      if (slugInput) {
        slugInput.value = '';
        slugInput.focus();
        document.execCommand('selectAll');
        document.execCommand('insertText', false, 'openclaw-messenger');
        slugInput.dispatchEvent(new Event('input', {bubbles:true}));
        slugInput.dispatchEvent(new Event('change', {bubbles:true}));
      }
      
      // display name
      const inputs = document.querySelectorAll('input');
      for (const inp of inputs) {
        const label = inp.closest('div')?.previousElementSibling?.textContent?.trim() || 
                     inp.getAttribute('placeholder') || '';
        if (label.includes('DISPLAY') || label.includes('My skill') || label.includes('display')) {
          inp.value = '';
          inp.focus();
          document.execCommand('selectAll');
          document.execCommand('insertText', false, 'OpenClaw Messenger');
          inp.dispatchEvent(new Event('input', {bubbles:true}));
          inp.dispatchEvent(new Event('change', {bubbles:true}));
        }
      }
      
      // version - should already be 1.0.0
      
      // changelog
      const textareas = document.querySelectorAll('textarea');
      for (const ta of textareas) {
        ta.focus();
        document.execCommand('selectAll');
        document.execCommand('insertText', false, 'Initial release - Send messages between OpenClaw instances. Supports contacts, ping, send, and listen.');
        ta.dispatchEvent(new Event('input', {bubbles:true}));
      }
      
      return 'form filled';
    })()
  `;
  
  const result = await sendCDP(ws, 'Runtime.evaluate', { 
    expression: fillScript, 
    awaitPromise: true 
  });
  console.log('📝 폼 채움:', result.result?.value);
  
  // 3. 파일 업로드는 File API로 직접 해야 함
  // 스킬 폴더의 파일들을 읽어서 DataTransfer로 주입
  const fs = require('fs');
  const path = require('path');
  const skillDir = '/Users/tag/.openclaw/workspace/skills/openclaw-messenger';
  
  // 파일 목록 수집 (node_modules 제외)
  function getFiles(dir, base = '') {
    let files = [];
    for (const item of fs.readdirSync(dir)) {
      if (item === 'node_modules' || item === 'publish-helper.js' || item === 'contacts.json' || item === 'package-lock.json') continue;
      const full = path.join(dir, item);
      const rel = base ? `${base}/${item}` : item;
      if (fs.statSync(full).isDirectory()) {
        files = files.concat(getFiles(full, rel));
      } else {
        files.push({ path: rel, content: fs.readFileSync(full, 'utf-8') });
      }
    }
    return files;
  }
  
  const files = getFiles(skillDir);
  console.log(`📦 파일 ${files.length}개 준비`);
  
  // 파일을 브라우저에 주입
  const injectScript = `
    (async () => {
      const files = ${JSON.stringify(files)};
      const dt = new DataTransfer();
      
      for (const f of files) {
        const blob = new Blob([f.content], { type: 'text/plain' });
        const file = new File([blob], f.path, { type: 'text/plain' });
        dt.items.add(file);
      }
      
      // 드롭존 찾기
      const dropZone = document.querySelector('[class*="drop"]') || 
                       document.querySelector('[class*="Drop"]') ||
                       document.querySelector('[class*="upload"]');
      
      if (dropZone) {
        const dropEvent = new DragEvent('drop', {
          bubbles: true,
          dataTransfer: dt
        });
        dropZone.dispatchEvent(dropEvent);
        return 'dropped ' + files.length + ' files';
      }
      
      // input[type=file] 찾기
      const fileInput = document.querySelector('input[type="file"]');
      if (fileInput) {
        fileInput.files = dt.files;
        fileInput.dispatchEvent(new Event('change', {bubbles:true}));
        return 'input ' + files.length + ' files';
      }
      
      return 'no drop zone found';
    })()
  `;
  
  const injectResult = await sendCDP(ws, 'Runtime.evaluate', {
    expression: injectScript,
    awaitPromise: true
  });
  console.log('📂 파일 업로드:', injectResult.result?.value);
  
  await new Promise(r => setTimeout(r, 2000));
  
  // 현재 페이지 상태 확인
  const checkScript = `
    document.querySelector('[class*="Validation"]')?.textContent || 
    document.querySelector('[class*="validation"]')?.textContent || 
    'no validation info'
  `;
  const checkResult = await sendCDP(ws, 'Runtime.evaluate', { expression: checkScript });
  console.log('🔍 상태:', checkResult.result?.value);
  
  ws.close();
  console.log('\n완료! 브라우저에서 확인 후 Publish skill 버튼을 눌러주세요.');
}

run().catch(e => console.error('❌', e.message));
