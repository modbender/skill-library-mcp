/**
 * 🛡️ OpenClaw Security Guard - Dashboard Server
 * 
 * Password-protected real-time security dashboard
 * 
 * NO TELEMETRY - 100% PRIVATE
 * 
 * Author: Miloud Belarebia
 * Website: https://2pidata.com
 */

import http from 'http';
import crypto from 'crypto';
import { WebSocketServer, WebSocket } from 'ws';
import fs from 'fs';
import path from 'path';
import os from 'os';

const VERSION = '1.0.0';
const AUTHOR = 'Miloud Belarebia';
const WEBSITE = 'https://2pidata.com';

// ============================================================
// CONFIGURATION
// ============================================================

const CONFIG_DIR = path.join(os.homedir(), '.openclaw-security-guard');
const AUTH_FILE = path.join(CONFIG_DIR, 'auth.json');

function ensureConfigDir() {
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true, mode: 0o700 });
  }
}

// ============================================================
// AUTHENTICATION
// ============================================================

class AuthManager {
  constructor() {
    ensureConfigDir();
    this.sessions = new Map();
    this.config = this.loadConfig();
  }
  
  loadConfig() {
    try {
      if (fs.existsSync(AUTH_FILE)) {
        return JSON.parse(fs.readFileSync(AUTH_FILE, 'utf-8'));
      }
    } catch {}
    return { passwordHash: null, salt: null, setupComplete: false };
  }
  
  saveConfig() {
    fs.writeFileSync(AUTH_FILE, JSON.stringify(this.config, null, 2), { mode: 0o600 });
  }
  
  isSetupComplete() {
    return this.config.setupComplete && this.config.passwordHash;
  }
  
  hashPassword(password, salt = null) {
    salt = salt || crypto.randomBytes(16).toString('hex');
    const hash = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex');
    return { hash, salt };
  }
  
  setupPassword(password) {
    if (!password || password.length < 8) {
      throw new Error('Password must be at least 8 characters');
    }
    const { hash, salt } = this.hashPassword(password);
    this.config.passwordHash = hash;
    this.config.salt = salt;
    this.config.setupComplete = true;
    this.config.createdAt = new Date().toISOString();
    this.saveConfig();
    return true;
  }
  
  verifyPassword(password) {
    if (!this.config.passwordHash || !this.config.salt) return false;
    const { hash } = this.hashPassword(password, this.config.salt);
    try {
      return crypto.timingSafeEqual(Buffer.from(hash, 'hex'), Buffer.from(this.config.passwordHash, 'hex'));
    } catch {
      return false;
    }
  }
  
  createSession() {
    const sessionId = crypto.randomBytes(32).toString('hex');
    this.sessions.set(sessionId, {
      createdAt: Date.now(),
      expiresAt: Date.now() + 24 * 60 * 60 * 1000
    });
    this.cleanupSessions();
    return sessionId;
  }
  
  validateSession(sessionId) {
    if (!sessionId) return false;
    const session = this.sessions.get(sessionId);
    if (!session || Date.now() > session.expiresAt) {
      this.sessions.delete(sessionId);
      return false;
    }
    return true;
  }
  
  cleanupSessions() {
    const now = Date.now();
    for (const [id, s] of this.sessions) {
      if (now > s.expiresAt) this.sessions.delete(id);
    }
  }
}

// ============================================================
// SECURITY MONITOR
// ============================================================

class SecurityMonitor {
  constructor() {
    this.clients = new Set();
    this.state = {
      status: 'initializing',
      securityScore: 75,
      lastScan: null,
      metrics: { requestsPerMinute: 0, costToday: 0, activeSessions: 0 },
      findings: { critical: 0, high: 0, medium: 0, low: 0 },
      threats: { blocked: 0, injectionAttempts: 0, rateLimitHits: 0 },
      configStatus: {},
      recentAlerts: []
    };
  }

  connectToOpenClaw(gatewayUrl) {
    try {
      const ws = new WebSocket(gatewayUrl);
      ws.on('open', () => {
        console.log('✅ Connected to OpenClaw Gateway');
        this.state.status = 'connected';
        this.broadcast({ type: 'update', data: this.state });
      });
      ws.on('message', (data) => {
        try { this.processEvent(JSON.parse(data.toString())); } catch {}
      });
      ws.on('close', () => {
        this.state.status = 'disconnected';
        this.broadcast({ type: 'update', data: this.state });
        setTimeout(() => this.connectToOpenClaw(gatewayUrl), 5000);
      });
      ws.on('error', () => { this.state.status = 'error'; });
    } catch {
      this.state.status = 'offline';
      setTimeout(() => this.connectToOpenClaw(gatewayUrl), 5000);
    }
  }

  processEvent(event) {
    if (event.type === 'message') {
      this.state.metrics.requestsPerMinute++;
      if (this.detectInjection(event.content)) {
        this.state.threats.injectionAttempts++;
        this.addAlert('critical', 'Prompt injection detected');
      }
    }
    this.broadcast({ type: 'update', data: this.state });
  }

  detectInjection(content) {
    if (!content) return false;
    return [/ignore\s+previous/i, /system\s*:/i, /jailbreak/i].some(p => p.test(content));
  }

  addAlert(severity, message) {
    this.state.recentAlerts.unshift({ timestamp: new Date().toISOString(), severity, message });
    if (this.state.recentAlerts.length > 50) this.state.recentAlerts.length = 50;
    this.updateScore();
  }

  updateScore() {
    let score = 100;
    if (this.state.configStatus.sandboxMode !== 'always') score -= 20;
    if (this.state.configStatus.dmPolicy === 'open') score -= 15;
    if (this.state.configStatus.gatewayBind !== 'loopback') score -= 15;
    score -= this.state.findings.critical * 10;
    score -= this.state.findings.high * 5;
    this.state.securityScore = Math.max(0, Math.min(100, score));
  }

  async runScan() {
    this.state.lastScan = new Date().toISOString();
    try {
      const configPath = path.join(os.homedir(), '.openclaw', 'openclaw.json');
      if (fs.existsSync(configPath)) {
        const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
        this.state.configStatus = {
          sandboxMode: config.agents?.defaults?.sandbox?.mode || 'unknown',
          dmPolicy: config.channels?.whatsapp?.dmPolicy || 'unknown',
          gatewayBind: config.gateway?.bind || 'unknown',
          rateLimiting: config.security?.rateLimiting?.enabled ? 'enabled' : 'disabled',
          elevated: config.agents?.defaults?.tools?.elevated?.enabled ? 'enabled' : 'disabled'
        };
        this.state.findings = { critical: 0, high: 0, medium: 0, low: 0 };
        if (this.state.configStatus.sandboxMode !== 'always') this.state.findings.critical++;
        if (this.state.configStatus.dmPolicy === 'open') this.state.findings.high++;
        if (this.state.configStatus.gatewayBind !== 'loopback') this.state.findings.critical++;
      }
    } catch {}
    this.updateScore();
    this.broadcast({ type: 'scan', data: this.state });
  }

  broadcast(message) {
    const data = JSON.stringify(message);
    for (const client of this.clients) {
      if (client.readyState === WebSocket.OPEN && client.authenticated) {
        client.send(data);
      }
    }
  }
}

// ============================================================
// HTML PAGES
// ============================================================

const getSetupPage = () => `<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>🛡️ Setup</title><script src="https://cdn.tailwindcss.com"></script>
<style>body{background:linear-gradient(135deg,#0f172a,#1e293b);min-height:100vh}</style></head>
<body class="flex items-center justify-center p-4">
<div class="bg-slate-800 rounded-2xl p-8 w-full max-w-md border border-slate-700">
<div class="text-center mb-8"><div class="text-5xl mb-4">🛡️</div>
<h1 class="text-2xl font-bold text-white">Welcome!</h1>
<p class="text-slate-400 text-sm mt-2">Create a password to secure your dashboard</p></div>
<form id="f" class="space-y-4">
<div><label class="block text-slate-300 text-sm mb-2">Password</label>
<input type="password" id="p1" class="w-full px-4 py-3 bg-slate-900 border border-slate-600 rounded-lg text-white" placeholder="Min 8 chars" minlength="8" required></div>
<div><label class="block text-slate-300 text-sm mb-2">Confirm</label>
<input type="password" id="p2" class="w-full px-4 py-3 bg-slate-900 border border-slate-600 rounded-lg text-white" required></div>
<div id="e" class="text-red-400 text-sm hidden"></div>
<button class="w-full py-3 bg-gradient-to-r from-cyan-500 to-emerald-500 text-white font-semibold rounded-lg">Create</button></form>
<p class="mt-6 text-center text-slate-500 text-xs">By <a href="${WEBSITE}" class="text-cyan-400">${AUTHOR}</a> • No telemetry</p></div>
<script>document.getElementById('f').onsubmit=async e=>{e.preventDefault();const p=document.getElementById('p1').value,c=document.getElementById('p2').value,err=document.getElementById('e');if(p!==c){err.textContent='Passwords do not match';err.classList.remove('hidden');return}try{const r=await fetch('/api/setup',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:p})});const d=await r.json();if(d.success){localStorage.setItem('session',d.sessionId);location.href='/dashboard'}else{err.textContent=d.error;err.classList.remove('hidden')}}catch{err.textContent='Error';err.classList.remove('hidden')}}</script></body></html>`;

const getLoginPage = () => `<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>🛡️ Login</title><script src="https://cdn.tailwindcss.com"></script>
<style>body{background:linear-gradient(135deg,#0f172a,#1e293b);min-height:100vh}</style></head>
<body class="flex items-center justify-center p-4">
<div class="bg-slate-800 rounded-2xl p-8 w-full max-w-md border border-slate-700">
<div class="text-center mb-8"><div class="text-5xl mb-4">🛡️</div>
<h1 class="text-2xl font-bold text-white">OpenClaw Security Guard</h1>
<p class="text-slate-400 text-sm mt-2">Enter your password</p></div>
<form id="f" class="space-y-4">
<input type="password" id="p" class="w-full px-4 py-3 bg-slate-900 border border-slate-600 rounded-lg text-white" placeholder="Password" required>
<div id="e" class="text-red-400 text-sm hidden"></div>
<button class="w-full py-3 bg-gradient-to-r from-cyan-500 to-emerald-500 text-white font-semibold rounded-lg">Login</button></form>
<p class="mt-6 text-center text-slate-500 text-xs">By <a href="${WEBSITE}" class="text-cyan-400">${AUTHOR}</a></p></div>
<script>document.getElementById('f').onsubmit=async e=>{e.preventDefault();const p=document.getElementById('p').value,err=document.getElementById('e');try{const r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:p})});const d=await r.json();if(d.success){localStorage.setItem('session',d.sessionId);location.href='/dashboard'}else{err.textContent='Invalid password';err.classList.remove('hidden')}}catch{err.textContent='Error';err.classList.remove('hidden')}}</script></body></html>`;

const getDashboardPage = () => `<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>🛡️ Dashboard</title>
<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
<script src="https://cdn.tailwindcss.com"></script>
<style>*{font-family:system-ui}body{background:#0f172a;color:#e2e8f0;margin:0}.card{background:#1e293b;border-radius:12px;border:1px solid #334155}.glow-g{box-shadow:0 0 30px rgba(34,197,94,.2)}.glow-y{box-shadow:0 0 30px rgba(234,179,8,.2)}.glow-r{box-shadow:0 0 30px rgba(239,68,68,.2)}@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}.pulse{animation:pulse 2s infinite}</style></head>
<body><div id="root"></div>
<script type="text/babel">
const{useState,useEffect}=React;

const Score=({v})=>{const c=v>=80?'#22c55e':v>=60?'#eab308':'#ef4444',g=v>=80?'glow-g':v>=60?'glow-y':'glow-r',r=45,circ=2*Math.PI*r,off=circ-(v/100)*circ;
return<div className={\`card p-6 text-center \${g}\`}><h3 className="text-gray-400 text-sm mb-4">Security Score</h3><div className="relative inline-block"><svg width="140" height="140" className="-rotate-90"><circle cx="70" cy="70" r={r} fill="none" stroke="#334155" strokeWidth="12"/><circle cx="70" cy="70" r={r} fill="none" stroke={c} strokeWidth="12" strokeDasharray={circ} strokeDashoffset={off} strokeLinecap="round"/></svg><div className="absolute inset-0 flex items-center justify-center"><span className="text-4xl font-bold" style={{color:c}}>{v}</span></div></div><div className="mt-3 text-sm" style={{color:c}}>{v>=80?'✅ Healthy':v>=60?'⚠️ Attention':'🔴 Critical'}</div></div>};

const Metric=({t,v,i})=><div className="card p-4"><div className="flex justify-between"><span className="text-gray-400 text-sm">{t}</span><span className="text-2xl">{i}</span></div><div className="text-3xl font-bold mt-2">{v}</div></div>;

const Config=({c})=>{const items=[['sandboxMode','Sandbox','always'],['dmPolicy','DM Policy','pairing'],['gatewayBind','Gateway','loopback'],['rateLimiting','Rate Limit','enabled']];return<div className="card p-4"><h3 className="text-gray-400 text-sm mb-3">Config</h3><div className="space-y-2">{items.map(([k,l,g])=>{const v=c[k]||'?',ok=v===g;return<div key={k} className="flex justify-between"><span className="text-sm">{l}</span><span className={\`text-xs px-2 py-1 rounded \${ok?'bg-green-500/20 text-green-400':'bg-red-500/20 text-red-400'}\`}>{ok?'✓':'✗'} {v}</span></div>})}</div></div>};

const Alerts=({a})=><div className="card p-4"><h3 className="text-gray-400 text-sm mb-3">Alerts ({a.length})</h3><div className="space-y-2 max-h-80 overflow-y-auto">{a.length===0?<div className="text-center py-8 text-gray-500">✅ No alerts</div>:a.map((x,i)=><div key={i} className="p-2 rounded border-l-4 border-red-500 bg-red-500/10"><span className="text-sm">{x.message}</span><div className="text-xs text-gray-500">{new Date(x.timestamp).toLocaleTimeString()}</div></div>)}</div></div>;

const Threats=({t})=><div className="card p-4"><h3 className="text-gray-400 text-sm mb-3">Threats</h3><div className="grid grid-cols-3 gap-4 text-center">{[['💉',t.injectionAttempts,'Injections','red'],['⏱️',t.rateLimitHits,'Rate Limits','yellow'],['🛑',t.blocked,'Blocked','green']].map(([icon,val,label,col])=><div key={label} className="p-3 bg-slate-800/50 rounded-lg"><div className="text-2xl">{icon}</div><div className={\`text-2xl font-bold text-\${col}-400\`}>{val||0}</div><div className="text-xs text-gray-400">{label}</div></div>)}</div></div>;

const Badge=({s})=>{const m={connected:['🟢','Connected'],disconnected:['🟡','Disconnected'],error:['🔴','Error'],initializing:['🔵','Starting']};const[i,t]=m[s]||m.initializing;return<div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-700"><span className="pulse">{i}</span><span className="text-sm">{t}</span></div>};

const App=()=>{
  const[state,setState]=useState({status:'initializing',securityScore:0,metrics:{requestsPerMinute:0,costToday:0},findings:{critical:0,high:0,medium:0,low:0},threats:{blocked:0,injectionAttempts:0,rateLimitHits:0},configStatus:{},recentAlerts:[]});
  const logout=()=>{localStorage.removeItem('session');location.href='/'};
  useEffect(()=>{
    const sid=localStorage.getItem('session');
    if(!sid){location.href='/';return}
    const ws=new WebSocket('ws://'+location.host+'?session='+sid);
    ws.onopen=()=>setState(s=>({...s,status:'connected'}));
    ws.onmessage=e=>{try{const m=JSON.parse(e.data);if(m.type==='auth_error'){localStorage.removeItem('session');location.href='/';return}if(m.data)setState(s=>({...s,...m.data}))}catch{}};
    ws.onclose=()=>setState(s=>({...s,status:'disconnected'}));
    return()=>ws.close();
  },[]);
  return<div className="min-h-screen p-6">
    <header className="flex justify-between items-center mb-6">
      <div className="flex items-center gap-3"><span className="text-4xl">🛡️</span><div><h1 className="text-2xl font-bold">OpenClaw Security Guard</h1><p className="text-gray-400 text-sm">By <a href="${WEBSITE}" className="text-cyan-400">${AUTHOR}</a></p></div></div>
      <div className="flex items-center gap-4"><Badge s={state.status}/><button onClick={logout} className="px-4 py-2 bg-slate-700 rounded-lg text-sm">Logout</button></div>
    </header>
    <div className="grid grid-cols-12 gap-4">
      <div className="col-span-3 space-y-4"><Score v={state.securityScore}/><Config c={state.configStatus}/></div>
      <div className="col-span-6 space-y-4">
        <div className="grid grid-cols-4 gap-4"><Metric t="Requests/min" v={state.metrics.requestsPerMinute} i="📊"/><Metric t="Cost Today" v={'$'+(state.metrics.costToday||0).toFixed(2)} i="💰"/><Metric t="Critical" v={state.findings.critical} i="🔴"/><Metric t="High" v={state.findings.high} i="🟡"/></div>
        <Threats t={state.threats}/>
        <div className="card p-4"><h3 className="text-gray-400 text-sm mb-3">Findings</h3><div className="grid grid-cols-4 gap-4 text-center">{[['critical','Critical','red'],['high','High','orange'],['medium','Medium','yellow'],['low','Low','gray']].map(([k,l,c])=><div key={k}><div className={\`text-2xl font-bold text-\${c}-400\`}>{state.findings[k]}</div><div className="text-xs text-gray-400">{l}</div></div>)}</div></div>
      </div>
      <div className="col-span-3"><Alerts a={state.recentAlerts}/></div>
    </div>
    <footer className="mt-6 text-center text-gray-500 text-sm"><p>v${VERSION} • No telemetry • 100% private</p><p className="mt-1">Need help? <a href="${WEBSITE}" className="text-cyan-400">${WEBSITE}</a></p></footer>
  </div>;
};
ReactDOM.createRoot(document.getElementById('root')).render(<App/>);
</script></body></html>`;

// ============================================================
// HTTP SERVER
// ============================================================

export async function startDashboard(options = {}) {
  const { port = 18790, gatewayUrl = 'ws://127.0.0.1:18789', openBrowser = true } = options;
  
  const auth = new AuthManager();
  const monitor = new SecurityMonitor();
  
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, `http://localhost:${port}`);
    
    // Routes
    if (url.pathname === '/' || url.pathname === '/login') {
      if (!auth.isSetupComplete()) { res.writeHead(302, { Location: '/setup' }); res.end(); return; }
      res.writeHead(200, { 'Content-Type': 'text/html' }); res.end(getLoginPage()); return;
    }
    
    if (url.pathname === '/setup') {
      if (auth.isSetupComplete()) { res.writeHead(302, { Location: '/' }); res.end(); return; }
      res.writeHead(200, { 'Content-Type': 'text/html' }); res.end(getSetupPage()); return;
    }
    
    if (url.pathname === '/dashboard') {
      res.writeHead(200, { 'Content-Type': 'text/html' }); res.end(getDashboardPage()); return;
    }
    
    // API: Setup
    if (url.pathname === '/api/setup' && req.method === 'POST') {
      let body = '';
      req.on('data', c => body += c);
      req.on('end', () => {
        try {
          const { password } = JSON.parse(body);
          auth.setupPassword(password);
          const sessionId = auth.createSession();
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ success: true, sessionId }));
        } catch (e) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ success: false, error: e.message }));
        }
      });
      return;
    }
    
    // API: Login
    if (url.pathname === '/api/login' && req.method === 'POST') {
      let body = '';
      req.on('data', c => body += c);
      req.on('end', () => {
        try {
          const { password } = JSON.parse(body);
          if (auth.verifyPassword(password)) {
            const sessionId = auth.createSession();
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: true, sessionId }));
          } else {
            res.writeHead(401, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: false, error: 'Invalid password' }));
          }
        } catch {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ success: false, error: 'Invalid request' }));
        }
      });
      return;
    }
    
    // Health check
    if (url.pathname === '/health') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'ok', version: VERSION }));
      return;
    }
    
    res.writeHead(404); res.end('Not found');
  });
  
  // WebSocket with auth
  const wss = new WebSocketServer({ server });
  wss.on('connection', (ws, req) => {
    const url = new URL(req.url, `http://localhost:${port}`);
    const sessionId = url.searchParams.get('session');
    
    if (!auth.validateSession(sessionId)) {
      ws.send(JSON.stringify({ type: 'auth_error' }));
      ws.close();
      return;
    }
    
    ws.authenticated = true;
    monitor.clients.add(ws);
    ws.send(JSON.stringify({ type: 'init', data: monitor.state }));
    ws.on('close', () => monitor.clients.delete(ws));
  });
  
  // Start
  server.listen(port, '127.0.0.1', () => {
    console.log(`
╔═══════════════════════════════════════════════════════════════╗
║  🛡️  OpenClaw Security Guard - Dashboard                      ║
║                                                               ║
║  URL:     http://localhost:${port}                              ║
║  Status:  ${auth.isSetupComplete() ? '🔐 Password protected' : '⚠️  Setup required'}                              ║
║                                                               ║
║  Author:  ${AUTHOR}                               ║
║  Website: ${WEBSITE}                            ║
║                                                               ║
║  ✅ No telemetry • 100% private                               ║
╚═══════════════════════════════════════════════════════════════╝
`);
  });
  
  monitor.connectToOpenClaw(gatewayUrl);
  setTimeout(() => monitor.runScan(), 2000);
  setInterval(() => monitor.runScan(), 5 * 60 * 1000);
  setInterval(() => { monitor.state.metrics.requestsPerMinute = 0; }, 60000);
  
  if (openBrowser) {
    try {
      const open = await import('open');
      setTimeout(() => open.default(`http://localhost:${port}`), 1500);
    } catch {}
  }
  
  return { server, monitor, auth };
}

export default { startDashboard };
