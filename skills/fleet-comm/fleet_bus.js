#!/usr/bin/env node
/**
 * Fleet Communication Bus v1.1 - simplified HTTP relay
 */
const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

const PORT = parseInt(process.env.FLEET_BUS_PORT || '18800');
const DATA_DIR = process.env.FLEET_DATA_DIR || path.join(__dirname, 'data');
const MSG_FILE = path.join(DATA_DIR, 'messages.jsonl');
const NODES_FILE = path.join(DATA_DIR, 'nodes.json');

if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });

let knownNodes = {};
try { if (fs.existsSync(NODES_FILE)) knownNodes = JSON.parse(fs.readFileSync(NODES_FILE, 'utf8')); } catch {}

function saveNodes() { fs.writeFileSync(NODES_FILE, JSON.stringify(knownNodes, null, 2)); }
function regNode(id, info) { knownNodes[id] = { ...info, lastSeen: Date.now() }; saveNodes(); }

function appendMsg(msg) {
  const entry = { ...msg, ts: Date.now(), id: Math.random().toString(36).slice(2, 10) };
  fs.appendFileSync(MSG_FILE, JSON.stringify(entry) + '\n');
  return entry;
}

function readMsgs(node, since) {
  if (!fs.existsSync(MSG_FILE)) return [];
  return fs.readFileSync(MSG_FILE, 'utf8').trim().split('\n').filter(Boolean)
    .map(l => { try { return JSON.parse(l); } catch { return null; } })
    .filter(m => m && (m.to === node || m.to === 'all') && m.ts > since);
}

function getBody(req, cb) {
  let d = '';
  req.on('data', c => d += c);
  req.on('end', () => { try { cb(null, JSON.parse(d)); } catch (e) { cb(e); } });
}

function send(res, code, obj) {
  res.writeHead(code, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
  res.end(JSON.stringify(obj));
}

function allMsgs(limit) {
  if (!fs.existsSync(MSG_FILE)) return [];
  return fs.readFileSync(MSG_FILE, 'utf8').trim().split('\n').filter(Boolean)
    .map(l => { try { return JSON.parse(l); } catch { return null; } })
    .filter(Boolean).slice(-limit);
}

const DASHBOARD_HTML = `<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>🚌 Fleet Bus</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,sans-serif;background:#1a1a2e;color:#e0e0e0;padding:16px}
h1{color:#00d4ff;margin-bottom:16px;font-size:1.5em}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px}
.card{background:#16213e;border-radius:8px;padding:12px;border:1px solid #0f3460}
.card h3{color:#00d4ff;font-size:.9em;margin-bottom:8px}
.node{display:inline-block;background:#0f3460;padding:4px 10px;border-radius:12px;margin:2px;font-size:.85em}
.node.online{border:1px solid #00ff88}
.msgs{max-height:400px;overflow-y:auto;background:#0d1b2a;border-radius:8px;padding:8px}
.msg{padding:6px 8px;border-bottom:1px solid #1a1a2e;font-size:.85em}
.msg .from{color:#00d4ff;font-weight:bold}
.msg .to{color:#ff6b6b}
.msg .time{color:#666;font-size:.8em}
.msg.broadcast{background:#1a2a1a}
.send-box{display:flex;gap:8px;margin-top:12px}
.send-box input,.send-box select{background:#16213e;border:1px solid #0f3460;color:#e0e0e0;padding:8px;border-radius:6px}
.send-box input[type=text]{flex:1}
.send-box button{background:#00d4ff;color:#000;border:none;padding:8px 16px;border-radius:6px;cursor:pointer;font-weight:bold}
@media(max-width:600px){.grid{grid-template-columns:1fr}}
</style></head><body>
<h1>🚌 Fleet Communication Bus</h1>
<div class="grid">
<div class="card"><h3>📡 状态</h3><div id="status">加载中...</div></div>
<div class="card"><h3>🖥️ 节点</h3><div id="nodes">加载中...</div></div>
</div>
<div class="card"><h3>💬 消息流</h3><div class="msgs" id="msgs"></div>
<div class="send-box">
<select id="from"><option value="human">human</option><option value="00">00</option><option value="01">01</option><option value="02">02</option></select>
<select id="to"><option value="all">广播</option><option value="00">00</option><option value="01">01</option><option value="02">02</option><option value="human">human</option></select>
<input type="text" id="msgInput" placeholder="输入消息...">
<button onclick="sendMsg()">发送</button>
</div></div>
<script>
const BASE='';
async function refresh(){
  const s=await(await fetch(BASE+'/status')).json();
  document.getElementById('status').innerHTML='消息: '+s.total+' | 运行: '+s.uptime+'秒';
  const n=await(await fetch(BASE+'/nodes')).json();
  document.getElementById('nodes').innerHTML=Object.entries(n).map(([k,v])=>'<span class="node online">'+k+' ('+( v.role||'agent')+')</span>').join(' ');
  const msgs=await(await fetch(BASE+'/messages?node=all&since=0')).json();
  const all=await(await fetch(BASE+'/status')).json();
  // get all messages via a trick - fetch for each node
  const r=await fetch(BASE+'/all');
  let allMsgs=[];
  try{allMsgs=await r.json();}catch{}
  const el=document.getElementById('msgs');
  el.innerHTML=allMsgs.map(m=>{
    const t=new Date(m.ts).toLocaleTimeString();
    const cls=m.to==='all'?'msg broadcast':'msg';
    return '<div class="'+cls+'"><span class="time">'+t+'</span> <span class="from">'+m.from+'</span> → <span class="to">'+m.to+'</span>: '+m.msg+'</div>';
  }).join('');
  el.scrollTop=el.scrollHeight;
}
async function sendMsg(){
  const from=document.getElementById('from').value;
  const to=document.getElementById('to').value;
  const msg=document.getElementById('msgInput').value;
  if(!msg)return;
  const ep=to==='all'?'/broadcast':'/send';
  await fetch(BASE+ep,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({from,to,msg})});
  document.getElementById('msgInput').value='';
  refresh();
}
document.getElementById('msgInput').addEventListener('keydown',e=>{if(e.key==='Enter')sendMsg()});
refresh();setInterval(refresh,3000);
</script></body></html>`;

const server = http.createServer((req, res) => {
  const parsed = new URL(req.url, 'http://localhost:' + PORT);
  const p = parsed.pathname;
  const m = req.method;

  if (m === 'GET' && (p === '/' || p === '/dashboard')) {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(DASHBOARD_HTML);
  }
  if (m === 'GET' && p === '/all') {
    return send(res, 200, allMsgs(100));
  }
  if (m === 'GET' && p === '/status') {
    const total = fs.existsSync(MSG_FILE) ? fs.readFileSync(MSG_FILE,'utf8').trim().split('\n').filter(Boolean).length : 0;
    return send(res, 200, { status:'ok', port:PORT, total, nodes:Object.keys(knownNodes), uptime: process.uptime()|0 });
  }
  if (m === 'GET' && p === '/nodes') return send(res, 200, knownNodes);
  if (m === 'GET' && p === '/messages') {
    const node = parsed.searchParams.get('node') || '00';
    const since = parseInt(parsed.searchParams.get('since') || '0');
    return send(res, 200, readMsgs(node, since));
  }
  if (m === 'POST' && p === '/register') {
    return getBody(req, (e, data) => {
      if (e) return send(res, 400, { error: e.message });
      regNode(data.nodeId, { ip: req.socket.remoteAddress, ...data });
      send(res, 200, { ok:true, nodes: Object.keys(knownNodes) });
    });
  }
  if (m === 'POST' && p === '/send') {
    return getBody(req, (e, msg) => {
      if (e) return send(res, 400, { error: e.message });
      if (!msg.from || !msg.to || !msg.msg) return send(res, 400, { error:'need from,to,msg' });
      regNode(msg.from, { lastAction:'send' });
      send(res, 200, { ok:true, entry: appendMsg(msg) });
    });
  }
  if (m === 'POST' && p === '/broadcast') {
    return getBody(req, (e, msg) => {
      if (e) return send(res, 400, { error: e.message });
      msg.to = 'all';
      if (!msg.from || !msg.msg) return send(res, 400, { error:'need from,msg' });
      regNode(msg.from, { lastAction:'broadcast' });
      send(res, 200, { ok:true, entry: appendMsg(msg) });
    });
  }
  send(res, 404, { error:'not found' });
});

server.listen(PORT, '0.0.0.0', () => console.log('🚌 Fleet Bus v1.1 on :' + PORT));
