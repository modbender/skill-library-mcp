#!/usr/bin/env node

// discord-connect-wizard: localhost wizard to bootstrap OpenClaw Discord bot config.
// Design goals:
// - No npm deps (Node 18+)
// - Token never logged
// - Writes OpenClaw config via `openclaw config set ... --json`
// - Guides user through 2 manual steps: copy token, click OAuth authorize

import http from 'http';
import { execFile } from 'child_process';
import { promisify } from 'util';
import { URL } from 'url';

const execFileAsync = promisify(execFile);

const HOST = '127.0.0.1';
const PORT = process.env.PORT ? Number(process.env.PORT) : 8787;
const DISCORD_API = 'https://discord.com/api/v10';

/** @type {{ accountId?: string, accountName?: string, token?: string, app?: any, botUser?: any, guilds?: any[], guildId?: string, userId?: string, pairingCode?: string }} */
const state = {};

function json(res, code, obj) {
  const body = JSON.stringify(obj, null, 2);
  res.writeHead(code, {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
  });
  res.end(body);
}

function text(res, code, body, contentType = 'text/plain; charset=utf-8') {
  res.writeHead(code, { 'Content-Type': contentType, 'Cache-Control': 'no-store' });
  res.end(body);
}

function htmlPage() {
  return `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>OpenClaw Discord Connect Wizard</title>
  <style>
    body{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial;max-width:900px;margin:32px auto;padding:0 16px;line-height:1.45}
    code,pre{background:#f6f8fa;padding:2px 6px;border-radius:6px}
    pre{padding:12px;overflow:auto}
    .row{display:flex;gap:12px;flex-wrap:wrap}
    input,select,button{font-size:14px;padding:8px 10px}
    button{cursor:pointer}
    .card{border:1px solid #e5e7eb;border-radius:12px;padding:14px 16px;margin:12px 0}
    .muted{color:#6b7280}
  </style>
</head>
<body>
  <h1>OpenClaw × Discord 连接向导</h1>
  <p class="muted">最少人工：复制 Bot Token + 点一次 OAuth 授权。其余自动完成。</p>

  <div class="card">
    <h3>Step 1/5：打开 Discord Developer Portal</h3>
    <div class="row">
      <input id="appName" placeholder="应用名" style="min-width:320px" />
      <button onclick="openPortal()">打开 Developer Portal</button>
    </div>
    <p class="muted">会自动建议应用名：oc-wizard-bot-XXX（XXX 自动生成，不含 discord）。登录/验证码需要你手动完成。</p>
  </div>

  <div class="card">
    <h3>Step 2/5：粘贴 Bot Token（仅本机使用）</h3>
    <div class="row">
      <input id="token" type="password" placeholder="Bot Token" style="min-width:520px" />
      <button onclick="saveToken()">保存并校验</button>
    </div>
    <pre id="tokenResult"></pre>
  </div>

  <div class="card">
    <h3>Step 3/5：生成 Invite 并授权进你的服务器</h3>
    <p class="muted">如果看到“正在打开 Discord APP”，属于正常跳转过程，等几秒即可。</p>
    <div class="row">
      <label>Reactions(可选) <input id="permReactions" type="checkbox" /></label>
      <button onclick="openInvite()">生成并打开授权链接</button>
    </div>
    <pre id="inviteResult"></pre>
  </div>

  <div class="card">
    <h3>Step 4/5：选择服务器（自动拉取，无需复制 ID）</h3>
    <div class="row">
      <button onclick="refreshGuilds()">刷新服务器列表</button>
      <select id="guildSelect" style="min-width:420px"></select>
      <button onclick="chooseGuild()">确认服务器</button>
      <button onclick="openCreateServer()">我没有服务器 → 去创建</button>
    </div>
    <pre id="guildResult"></pre>
  </div>

  <div class="card">
    <h3>Step 5/5：自动获取你的 User ID（不复制 ID）</h3>
    <p class="muted">输入你的 Discord 用户名（不含 # 号后四位也行），向导会在该服务器内搜索并让你点选。</p>
    <div class="row">
      <input id="userQuery" placeholder="例如: yourname" style="min-width:320px" />
      <button onclick="findUser()">搜索</button>
      <select id="userSelect" style="min-width:420px"></select>
      <button onclick="chooseUser()">确认用户</button>
    </div>
    <pre id="userResult"></pre>
  </div>

  <div class="card">
    <h3>完成：写入 OpenClaw 配置 + Pairing</h3>
    <ol>
      <li>在 Discord 里私聊你的 bot，发一句 <code>hi</code>（触发 pairing；若不回请到服务器隐私设置里开启“允许私信”）</li>
      <li>下面点“等待并自动完成”</li>
    </ol>
    <div class="row">
      <button onclick="finalize()">等待并自动完成</button>
    </div>
    <pre id="finalResult"></pre>
  </div>

<script>
ensureDefaults();
async function api(path, opts={}){
  const res = await fetch(path, {headers:{'Content-Type':'application/json'}, ...opts});
  const t = await res.text();
  let j; try{ j = JSON.parse(t);}catch{ j = t; }
  return {ok: res.ok, status: res.status, data: j};
}

function rand3(){
  return Math.random().toString(36).slice(2,5);
}

function ensureDefaults(){
  const suffix = rand3().toUpperCase();
  const appName = 'oc-wizard-bot-' + suffix;
  const a = document.getElementById('appName');
  if(a && !a.value) a.value = appName;
}

function openPortal(){
  window.open('https://discord.com/developers/applications', '_blank');
}

function openCreateServer(){
  // Official help article; actual server creation happens in Discord client UI.
  window.open('https://support.discord.com/hc/en-us/articles/204849977-How-do-I-create-a-server', '_blank');
}

async function saveToken(){
  const token = document.getElementById('token').value.trim();
  const out = document.getElementById('tokenResult');
  out.textContent = '...';
  const r = await api('/api/token', {method:'POST', body: JSON.stringify({token})});
  out.textContent = JSON.stringify(r.data, null, 2);
}

async function openInvite(){
  const out = document.getElementById('inviteResult');
  out.textContent = '...';
  const addReactions = document.getElementById('permReactions').checked;
  const r = await api('/api/invite', {method:'POST', body: JSON.stringify({addReactions})});
  out.textContent = JSON.stringify(r.data, null, 2);
  if(r.ok && r.data.url){ window.open(r.data.url, '_blank'); }
}

async function refreshGuilds(){
  const sel = document.getElementById('guildSelect');
  sel.innerHTML = '';
  const out = document.getElementById('guildResult');
  out.textContent = '...';
  const r = await api('/api/guilds');
  if(r.ok && Array.isArray(r.data.guilds) && r.data.guilds.length){
    out.textContent = '';
    for(const g of r.data.guilds){
      const opt = document.createElement('option');
      opt.value = g.id;
      opt.textContent = g.name + " (" + g.id + ")";
      sel.appendChild(opt);
    }
  } else {
    out.textContent = JSON.stringify({
      ok: false,
      error: '未检测到任何服务器。你需要先创建/加入一个 Discord 服务器，然后再把 bot 邀请进去。',
      help: '点击右侧“我没有服务器 → 去创建”查看官方创建方法。'
    }, null, 2);
  }
}

async function chooseGuild(){
  const guildId = document.getElementById('guildSelect').value;
  const out = document.getElementById('guildResult');
  out.textContent = '...';
  const r = await api('/api/guild', {method:'POST', body: JSON.stringify({guildId})});
  out.textContent = JSON.stringify(r.data, null, 2);
}

async function findUser(){
  const q = document.getElementById('userQuery').value.trim();
  const out = document.getElementById('userResult');
  out.textContent = '...';
  const r = await api('/api/user-search', {method:'POST', body: JSON.stringify({query:q})});
  out.textContent = JSON.stringify(r.data, null, 2);
  const sel = document.getElementById('userSelect');
  sel.innerHTML = '';
  if(r.ok && Array.isArray(r.data.users)){
    for(const u of r.data.users){
      const opt = document.createElement('option');
      opt.value = u.id;
      opt.textContent = u.label + " (" + u.id + ")";
      sel.appendChild(opt);
    }
  }
}

async function chooseUser(){
  const userId = document.getElementById('userSelect').value;
  const out = document.getElementById('userResult');
  out.textContent = '...';
  const r = await api('/api/user', {method:'POST', body: JSON.stringify({userId})});
  out.textContent = JSON.stringify(r.data, null, 2);
}

async function finalize(){
  const out = document.getElementById('finalResult');
  out.textContent = '等待你的 DM...';
  const r = await api('/api/finalize', {method:'POST'});
  out.textContent = JSON.stringify(r.data, null, 2);
}
</script>
</body>
</html>`;
}

async function discordGet(path) {
  if (!state.token) throw new Error('Token not set');
  const res = await fetch(`${DISCORD_API}${path}`, {
    headers: { Authorization: `Bot ${state.token}` },
  });
  const txt = await res.text();
  let data;
  try { data = JSON.parse(txt); } catch { data = txt; }
  if (!res.ok) throw new Error(`Discord API ${res.status}: ${typeof data === 'string' ? data : JSON.stringify(data)}`);
  return data;
}

async function openclaw(args) {
  const { stdout, stderr } = await execFileAsync('openclaw', args, { env: process.env });
  return { stdout: stdout?.toString() ?? '', stderr: stderr?.toString() ?? '' };
}

async function writeBaselineConfig() {
  if (!state.accountId) throw new Error('accountId missing');
  if (!state.token) throw new Error('Token missing');
  if (!state.guildId) throw new Error('guildId missing');
  if (!state.userId) throw new Error('userId missing');

  await openclaw(['config', 'set', `channels.discord.enabled`, 'true', '--json']);

  const acct = `channels.discord.accounts.${state.accountId}`;
  await openclaw(['config', 'set', `${acct}.enabled`, 'true', '--json']);
  if (state.accountName) {
    await openclaw(['config', 'set', `${acct}.name`, JSON.stringify(state.accountName), '--json']);
  }
  await openclaw(['config', 'set', `${acct}.token`, JSON.stringify(state.token), '--json']);
  await openclaw(['config', 'set', `${acct}.groupPolicy`, JSON.stringify('allowlist'), '--json']);
  await openclaw(['config', 'set', `${acct}.guilds.${state.guildId}.requireMention`, 'false', '--json']);
  await openclaw(['config', 'set', `${acct}.guilds.${state.guildId}.users`, JSON.stringify([state.userId]), '--json']);
}

function extractPairingCode(text) {
  // best-effort: look for something that resembles a pairing code token
  // If OpenClaw changes format, user can paste code manually in a future iteration.
  const m = text.match(/\b([A-Z0-9]{4,8}-[A-Z0-9]{4,8})\b/);
  return m?.[1];
}

async function wait(ms) {
  return new Promise(r => setTimeout(r, ms));
}

const server = http.createServer(async (req, res) => {
  try {
    const u = new URL(req.url, `http://${req.headers.host}`);

    if (req.method === 'GET' && u.pathname === '/') {
      return text(res, 200, htmlPage(), 'text/html; charset=utf-8');
    }

    if (u.pathname.startsWith('/api/')) {
      let body = '';
      req.on('data', c => (body += c));
      await new Promise(r => req.on('end', r));
      const payload = body ? JSON.parse(body) : {};

      if (req.method === 'POST' && u.pathname === '/api/token') {
        const token = (payload.token || '').trim();
        if (!token) return json(res, 400, { ok: false, error: 'missing token' });
        state.token = token;

        const botUser = await discordGet('/users/@me');
        state.botUser = botUser;

        // Prefer canonical app name from Discord API (not user input)
        let appName = '';
        try {
          const app = await discordGet('/oauth2/applications/@me');
          state.app = app;
          appName = app?.name || '';
        } catch {}

        const raw = appName || botUser.username || 'wizardbot';
        const accountId = raw.toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_+|_+$/g,'').slice(0,32) || 'wizardbot';
        state.accountId = accountId;
        state.accountName = raw;

        return json(res, 200, { ok: true, bot: { id: botUser.id, username: botUser.username }, accountId, appName: raw });
      }

      if (req.method === 'POST' && u.pathname === '/api/invite') {
        if (!state.token) return json(res, 400, { ok: false, error: 'set token first' });

        // permissions bitset
        // View Channels(1024) + Send Messages(2048) + Read History(65536) + Embed Links(16384) + Attach Files(32768)
        // Add Reactions(64) optional
        let perms = 1024 + 2048 + 65536 + 16384 + 32768;
        if (payload.addReactions) perms += 64;

        // Need application id. We can get it via /oauth2/applications/@me
        const app = await discordGet('/oauth2/applications/@me');
        state.app = app;
        const clientId = app.id;

        const scopes = encodeURIComponent('bot applications.commands');
        const url = `https://discord.com/api/oauth2/authorize?client_id=${clientId}&permissions=${perms}&scope=${scopes}`;
        return json(res, 200, { ok: true, url, note: 'Open this URL and click Authorize.' });
      }

      if (req.method === 'GET' && u.pathname === '/api/guilds') {
        if (!state.token) return json(res, 400, { ok: false, error: 'set token first' });
        const guilds = await discordGet('/users/@me/guilds');
        state.guilds = guilds;
        return json(res, 200, { ok: true, guilds: guilds.map(g => ({ id: g.id, name: g.name })) });
      }

      if (req.method === 'POST' && u.pathname === '/api/guild') {
        const guildId = (payload.guildId || '').trim();
        if (!guildId) return json(res, 400, { ok: false, error: 'missing guildId' });
        state.guildId = guildId;
        return json(res, 200, { ok: true, guildId });
      }

      if (req.method === 'POST' && u.pathname === '/api/user-search') {
        if (!state.guildId) return json(res, 400, { ok: false, error: 'pick a guild first' });
        const q = (payload.query || '').trim();
        if (!q) return json(res, 400, { ok: false, error: 'missing query' });
        // Discord supports member search by query.
        const users = await discordGet(`/guilds/${state.guildId}/members/search?limit=10&query=${encodeURIComponent(q)}`);
        const simplified = (users || []).map(m => {
          const u = m.user || {};
          const label = [u.username, u.global_name, m.nick].filter(Boolean).join(' / ');
          return { id: u.id, label: label || u.id };
        }).filter(x => x.id);
        return json(res, 200, { ok: true, users: simplified });
      }

      if (req.method === 'POST' && u.pathname === '/api/user') {
        const userId = (payload.userId || '').trim();
        if (!userId) return json(res, 400, { ok: false, error: 'missing userId' });
        state.userId = userId;
        return json(res, 200, { ok: true, userId });
      }

      if (req.method === 'POST' && u.pathname === '/api/finalize') {
        if (!state.accountId) return json(res, 400, { ok: false, error: 'set accountId first' });
        if (!state.guildId) return json(res, 400, { ok: false, error: 'pick a guild first' });
        if (!state.userId) return json(res, 400, { ok: false, error: 'pick your user first' });

        await writeBaselineConfig();
        await openclaw(['gateway', 'restart']);

        // Wait for pairing request for THIS account.
        const deadline = Date.now() + 5 * 60 * 1000;
        while (Date.now() < deadline) {
          const { stdout } = await openclaw(['pairing', 'list', 'discord', '--account', state.accountId, '--json']);
          let data;
          try { data = JSON.parse(stdout); } catch { data = null; }
          const reqs = data?.requests || data || [];
          if (Array.isArray(reqs) && reqs.length) {
            const code = reqs[0]?.code;
            if (code) {
              state.pairingCode = code;
              await openclaw(['pairing', 'approve', 'discord', code]);
              return json(res, 200, { ok: true, pairingApproved: true });
            }
          }
          await wait(2000);
        }

        return json(res, 408, { ok: false, error: 'Timeout waiting for pairing. Ensure Discord allows DMs from server members, then DM the bot and retry.' });
      }

      return json(res, 404, { ok: false, error: 'not found' });
    }

    text(res, 404, 'Not found');
  } catch (e) {
    json(res, 500, { ok: false, error: String(e?.message || e) });
  }
});

server.listen(PORT, HOST, () => {
  console.log(`Discord Connect Wizard running: http://${HOST}:${PORT}`);
});
