#!/usr/bin/env node
/**
 * Glitch Dashboard v3.2 - Fixed IP Detection
 */

const http=require('http'),fs=require('fs'),path=require('path'),{exec}=require('child_process'),os=require('os');
const PORT=process.env.GLITCH_PORT||3853;
const PLATFORM=os.platform();
const isWin=PLATFORM==='win32',isMac=PLATFORM==='darwin';

const DATA_DIR=path.join(os.homedir(),'.glitch-dashboard');
const CONFIG_FILE=path.join(os.homedir(),'.openclaw','openclaw.json');

async function execCmd(cmd,t=3000){
  return new Promise(r=>{
    exec(cmd,{timeout:t,shell:true,windowsHide:isWin},(e,so,se)=>r({out:so?.trim()||'',err:se?.trim()||'',code:e?.code||0}));
  });
}

function getTokens(){
  try{
    if(!fs.existsSync(CONFIG_FILE))return[];
    const cfg=JSON.parse(fs.readFileSync(CONFIG_FILE,'utf8'));
    const tokens=[];
    const providers=cfg.models?.providers||{};
    for(const[p,data]of Object.entries(providers)){
      if(data.apiKey&&data.apiKey!=='minimax-oauth'){
        const key=data.apiKey.length>12?data.apiKey.substring(0,8)+'...'+data.apiKey.substring(data.apiKey.length-4):data.apiKey;
        tokens.push({name:p.charAt(0).toUpperCase()+p.slice(1),key,enabled:true,provider:p,baseUrl:data.baseUrl});
      }
    }
    return tokens;
  }catch(e){return[];}
}

async function getLogs(){
  const logs=[];
  const journal=await execCmd('journalctl --user-unit openclaw-gateway --no-pager -n 30 2>/dev/null');
  if(journal.out){
    const lines=journal.out.split('\n').slice(0,15);
    for(const line of lines){
      if(line.trim()&&!line.includes('journal')){
        const ts=line.match(/^(\w+\s+\d+\s+[\d:]+)/)?.[1]||new Date().toISOString();
        const msg=line.replace(/^[^:]+:/,'').trim();
        if(msg)logs.push({t:ts,s:'gateway',m:msg.substring(0,100)});
      }
    }
  }
  const syslog=await execCmd('tail -30 /var/log/syslog 2>/dev/null || tail -30 /var/log/messages 2>/dev/null');
  if(syslog.out){
    const lines=syslog.out.split('\n').slice(0,10);
    for(const line of lines){
      if(line.includes('cron')||line.includes('CRON')||line.includes('systemd')){
        const ts=line.substring(0,15);
        const msg=line.substring(15).trim().substring(0,80);
        if(msg)logs.push({t:ts,s:'cron',m:msg});
      }
    }
  }
  if(logs.length===0)logs.push({t:new Date().toISOString(),s:'system',m:'No gateway/cron logs found'});
  return logs.slice(0,20);
}

function getTasks(){
  const queueFile=path.join(DATA_DIR,'queue.json');
  try{if(fs.existsSync(queueFile)){const data=JSON.parse(fs.readFileSync(queueFile,'utf8'));return data.tasks||[];}}catch(e){}
  return[];
}

function saveTasks(tasks){
  const queueFile=path.join(DATA_DIR,'queue.json');
  try{fs.writeFileSync(queueFile,JSON.stringify({tasks,updatedAt:new Date().toISOString()},null,2));return true;}catch(e){return false;}
}

// Get network info - properly detect LAN vs ZeroTier
function getNetworkInfo(){
  let lanIp='',ztIp='',ztAddr='?';
  const ifs=os.networkInterfaces();
  for(const name in ifs){
    for(const i of ifs[name]){
      if(i.family==='IPv4'&&!i.internal){
        // LAN: 192.168.x.x, 10.x.x.x, 172.16-31.x.x (not 172.26.x.x which is ZT)
        if(i.address.startsWith('192.168.')||i.address.startsWith('10.')||(i.address.startsWith('172.')&&!i.address.startsWith('172.26')&&!i.address.startsWith('172.17'))){
          if(!lanIp)lanIp=i.address;
        }
        // ZeroTier: 172.26.x.x
        if(i.address.startsWith('172.26.'))ztIp=i.address;
      }
    }
  }
  return{lanIp,ztIp};
}

async function getData(){
  const[sys,zt,mihomo,tokens,tasks,logs,netInfo]=await Promise.all([
    (async()=>{
      const cpus=os.cpus();let ti=0,tt=0;
      for(const c of cpus){for(const k in c.times)tt+=c.times[k];ti+=c.times.idle}
      const u=100-ti/tt*100,mb=b=>b>1e9?(b/1e9).toFixed(1)+'GB':(b/1e6|0)+'MB';
      const tm=os.totalmem(),fm=os.freemem();
      const net=getNetworkInfo();
      return{cpu:{use:u.toFixed(1),n:cpus.length},mem:{pct:((tm-fm)/tm*100).toFixed(1),used:mb(tm-fm),tot:mb(tm)},up:os.uptime(),host:os.hostname(),plat:PLATFORM,arch:os.arch(),lanIp:net.lanIp,ztIp:net.ztIp};
    })(),
    (async()=>{
      const cmd=isWin?'"C:\\Program Files (x86)\\ZeroTier\\One\\zerotier-cli.exe"':isMac?'/usr/local/bin/zerotier-cli':'sudo zerotier-cli';
      const n=await execCmd(`${cmd} listnetworks`),i=await execCmd(`${cmd} info`);
      const m=n.out.match(/(\d+\.\d+\.\d+\.\d+)/),id=n.out.match(/([a-f0-9]{16})/);
      return{on:!n.err&&n.out.includes('OK'),addr:i.out.match(/([a-f0-9]{10})/)?.[1]||'?',ip:m?.[1]||'Not connected',net:id?.[1]||null}
    })(),
    (async()=>{return{run:(await execCmd(isWin?'tasklist /FI "IMAGENAME eq mihomo.exe"':'pgrep -f mihomo')).code===0}}),
    (async()=>{const t=getTokens();return t.length?t:[{name:'No tokens',key:'Configure in openclaw.json',enabled:false}]})(),
    (async()=>{const t=getTasks();return{stats:{p:t.filter(x=>x.st==='pending').length,c:t.filter(x=>x.st==='completed').length},list:t}})(),
    getLogs()
  ]);
  return{sys,zt,mihomo,tokens,tasks,logs,plat:PLATFORM};
}

function html(d,p){
  const{sys,zt,mihomo,tokens,tasks,logs,plat}=d;
  const col=v=>v>80?'#a06060':v>50?'#a09060':'#609060';
  const colT=s=>s==='completed'?'#609060':s==='processing'?'#5c8cb0':'#a09060';
  const lanIp=sys.lanIp||sys.ztIp||'N/A';
  
  return`<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Glitch Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{--bg:#0c0e14;--sb:#11131a;--c:#181b24;--ch:#1e222c;--b:#2a2f3a;--t:#c4c8d0;--tm:#6c7484;--ac:#5c8cb0;--gr:#609060;--yl:#a09060;--rd:#a06060}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--t);min-height:100vh;display:flex}
.sb{width:72px;background:var(--sb);border-right:1px solid var(--b);display:flex;flex-direction:column;align-items:center;padding:20px 0;position:fixed;height:100vh}
.logo{width:44px;height:44px;background:linear-gradient(135deg,#4a6070,#5c6070);border-radius:12px;display:flex;align-items:center;justify-content:center;font-weight:600;font-size:18px;margin-bottom:28px}
.nav{width:52px;height:48px;border-radius:10px;display:flex;align-items:center;justify-content:center;margin-bottom:6px;cursor:pointer;color:var(--tm);font-size:18px;position:relative;transition:all .2s}
.nav:hover{background:var(--ch);color:var(--t)}.nav.act{background:rgba(92,140,176,.12);color:var(--ac)}.nav.act::before{content:'';position:absolute;left:0;top:50%;transform:translateY(-50%);width:3px;height:20px;background:var(--ac);border-radius:0 2px 2px 0}
.tip{position:absolute;left:60px;background:var(--c);padding:8px 12px;border-radius:8px;font-size:12px;white-space:nowrap;opacity:0;transition:opacity .2s;border:1px solid var(--b);box-shadow:0 4px 16px rgba(0,0,0,.4);z-index:200}
.nav:hover .tip{opacity:1}
.main{flex:1;margin-left:72px;padding:24px 32px;max-width:1400px}
.hdr{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid var(--b)}
.hdr h1{font-size:22px;font-weight:600}
.st{display:flex;align-items:center;gap:12px;font-size:13px}
.st-item{display:flex;align-items:center;gap:6px;color:var(--tm)}.st-dot{width:8px;height:8px;background:var(--gr);border-radius:50%;animation:pulse 2.5s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}.refresh{font-size:12px;color:var(--tm);cursor:pointer}.refresh:hover{color:var(--ac)}
.card{background:var(--c);border:1px solid var(--b);border-radius:12px;padding:20px;margin-bottom:16px}
.card-tit{font-size:14px;font-weight:600;margin-bottom:16px;display:flex;align-items:center;gap:10px}
.ic{width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:13px}
.ic-s{background:rgba(92,140,176,.15);color:var(--ac)}.ic-n{background:rgba(92,106,160,.15);color:#5c6aa0}.ic-t{background:rgba(92,144,96,.15);color:var(--gr)}.ic-x{background:rgba(160,106,140,.15);color:#a06a8c}.ic-l{background:rgba(160,140,92,.15);color:var(--yl)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px}
.grid-item{background:var(--c);border:1px solid var(--b);border-radius:10px;padding:20px;cursor:pointer;transition:all .2s}.grid-item:hover{border-color:var(--ac);transform:translateY(-2px)}
.grid-val{font-size:32px;font-weight:600;font-family:'JetBrains Mono',monospace;margin-bottom:6px}
.grid-lab{font-size:13px;color:var(--tm)}
.prog{margin:14px 0}.prog-hd{display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;color:var(--tm)}.prog-bar{height:6px;background:var(--b);border-radius:3px;overflow:hidden}.prog-fill{height:100%;border-radius:3px;transition:width .3s ease}
.task{background:var(--ch);border-radius:8px;padding:14px;margin-bottom:10px;border-left:3px solid var(--yl)}.task.proc{border-left-color:var(--ac)}.task.comp{border-left-color:var(--gr);opacity:.7}
.task-hd{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px}.task-tit{font-size:14px;font-weight:500;flex:1;line-height:1.4;margin-right:12px}
.task-btns{display:flex;gap:6px}.btn-sm{padding:4px 10px;font-size:11px;border:none;border-radius:4px;cursor:pointer;transition:all .15s;background:var(--b);color:var(--tm)}.btn-sm:hover{background:var(--ac);color:#000}
.btn-c:hover{background:var(--gr);color:#fff}.btn-d:hover{background:var(--rd);color:#fff}
.task-meta{font-size:12px;color:var(--tm);display:flex;gap:12px;margin-top:6px}
.subs{margin-top:10px;padding-left:12px;border-left:2px solid var(--b)}.sub{display:flex;align-items:center;gap:8px;padding:4px 0;font-size:12px;color:var(--tm)}.sub.done{text-decoration:line-through;opacity:.5}
.tok{display:flex;justify-content:space-between;align-items:center;padding:14px 0;border-bottom:1px solid var(--b)}.tok:last-child{border:none}.tok-n{font-weight:500;font-size:14px}.tok-k{font-size:12px;color:var(--tm);font-family:'JetBrains Mono',monospace}
.tog{position:relative;width:44px;height:24px}.tog input{opacity:0;width:0;height:0}.tog-sl{position:absolute;cursor:pointer;inset:0;background:var(--b);border-radius:24px;transition:.25s}.tog-sl:before{content:"";position:absolute;height:18px;width:18px;left:3px;bottom:3px;background:#8c94a4;border-radius:50%;transition:.25s}.tog input:checked+.tog-sl{background:var(--gr)}.tog input:checked+.tog-sl:before{transform:translateX(20px)}.tog input:disabled+.tog-sl{opacity:.5;cursor:not-allowed}
.gw{margin-top:20px;padding-top:20px;border-top:1px solid var(--b)}.gw-l{font-size:12px;color:var(--tm);margin-bottom:8px}.gw-v{font-family:'JetBrains Mono',monospace;font-size:13px;background:var(--ch);padding:12px;border-radius:8px;word-break:break-all;color:var(--ac)}
.log{display:flex;gap:12px;padding:10px 0;border-bottom:1px solid var(--b);font-size:12px;font-family:'JetBrains Mono',monospace}.log:last-child{border:none}.log-t{color:var(--tm);white-space:nowrap}.log-s{color:var(--yl);white-space:nowrap;min-width:60px}.log-m{color:var(--t);word-break:break-word}
.pg{display:none}.pg.act{display:block}
.edit-modal{position:fixed;inset:0;background:rgba(0,0,0,.7);display:none;align-items:center;justify-content:center;z-index:1000}.edit-modal.show{display:flex}
.edit-box{background:var(--c);border:1px solid var(--b);border-radius:12px;padding:24px;width:400px;max-width:90vw}
.edit-box h3{font-size:16px;margin-bottom:16px}.edit-box input,.edit-box select{width:100%;background:var(--ch);border:1px solid var(--b);border-radius:6px;padding:10px;color:var(--t);font-size:14px;margin-bottom:12px}
.edit-box .btns{display:flex;gap:8px;justify-content:flex-end}
@media(max-width:900px){.sb{width:60px}.main{margin-left:60px;padding:16px}.grid{grid-template-columns:repeat(2,1fr)}}
</style></head>
<body>
<nav class="sb">
<div class="logo">G</div>
<div class="nav ${p==='overview'?'act':''}" onclick="go('overview')"><span>⌂</span><span class="tip">Overview</span></div>
<div class="nav ${p==='system'?'act':''}" onclick="go('system')"><span>⚙</span><span class="tip">System</span></div>
<div class="nav ${p==='network'?'act':''}" onclick="go('network')"><span>🌐</span><span class="tip">Network</span></div>
<div class="nav ${p==='tasks'?'act':''}" onclick="go('tasks')"><span>☰</span><span class="tip">Tasks</span></div>
<div class="nav ${p==='tokens'?'act':''}" onclick="go('tokens')"><span>🔑</span><span class="tip">Tokens</span></div>
<div class="nav ${p==='logs'?'act':''}" onclick="go('logs')"><span>📋</span><span class="tip">Logs</span></div>
</nav>
<main class="main">
<header class="hdr"><h1>Glitch Dashboard</h1><div class="st"><span class="st-item"><span class="refresh" onclick="location.reload()">↻ Refresh</span></span><span class="st-item">${plat}</span><div class="st-item"><div class="st-dot"></div>Online</div></div></header>

<div class="pg ${p==='overview'?'act':''}" id="overview">
<div class="grid">
<div class="grid-item" onclick="go('system')"><div class="grid-val" style="color:${col(parseFloat(sys.cpu.use))}">${sys.cpu.use}%</div><div class="grid-lab">CPU Usage</div></div>
<div class="grid-item" onclick="go('system')"><div class="grid-val" style="color:${col(parseFloat(sys.mem.pct))}">${sys.mem.pct}%</div><div class="grid-lab">Memory</div></div>
<div class="grid-item" onclick="go('network')"><div class="grid-val" style="color:var(--ac)">${sys.ztIp.split('.')[3]||'--'}</div><div class="grid-lab">ZeroTier IP</div></div>
<div class="grid-item" onclick="go('tasks')"><div class="grid-val" style="color:var(--yl)">${tasks.stats.p}</div><div class="grid-lab">Pending Tasks</div></div>
<div class="grid-item"><div class="grid-val" style="color:var(--gr)">${mihomo.run?'ON':'OFF'}</div><div class="grid-lab">Mihomo</div></div>
<div class="grid-item"><div class="grid-val" style="color:var(--ac)">${tokens.length}</div><div class="grid-lab">Tokens</div></div>
</div>
<div class="card" style="margin-top:20px"><div class="card-tit"><div class="ic ic-s">⚙</div>System Status</div>
<div class="prog"><div class="prog-hd"><span>CPU</span><span>${sys.cpu.use}% / ${sys.cpu.n} cores</span></div><div class="prog-bar"><div class="prog-fill" style="width:${sys.cpu.use}%;background:${col(parseFloat(sys.cpu.use))}"></div></div></div>
<div class="prog"><div class="prog-hd"><span>Memory</span><span>${sys.mem.used} / ${sys.mem.tot}</span></div><div class="prog-bar"><div class="prog-fill" style="width:${sys.mem.pct}%;background:${col(parseFloat(sys.mem.pct))}"></div></div></div>
</div>
</div>

<div class="pg ${p==='system'?'act':''}" id="system">
<div class="card"><div class="card-tit"><div class="ic ic-s">⚙</div>System Monitor</div>
<div class="prog"><div class="prog-hd"><span>CPU Usage</span><span>${sys.cpu.use}% (${sys.cpu.n} cores)</span></div><div class="prog-bar"><div class="prog-fill" style="width:${sys.cpu.use}%;background:${col(parseFloat(sys.cpu.use))}"></div></div></div>
<div class="prog"><div class="prog-hd"><span>Memory Usage</span><span>${sys.mem.used} / ${sys.mem.tot}</span></div><div class="prog-bar"><div class="prog-fill" style="width:${sys.mem.pct}%;background:${col(parseFloat(sys.mem.pct))}"></div></div></div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px">
<div style="background:var(--ch);padding:14px;border-radius:8px"><div style="font-size:12px;color:var(--tm)">Hostname</div><div style="font-size:14px;font-weight:500">${sys.host}</div></div>
<div style="background:var(--ch);padding:14px;border-radius:8px"><div style="font-size:12px;color:var(--tm)">Uptime</div><div style="font-size:14px;font-weight:500">${(sys.up/3600).toFixed(1)}h</div></div>
<div style="background:var(--ch);padding:14px;border-radius:8px"><div style="font-size:12px;color:var(--tm)">Platform</div><div style="font-size:14px;font-weight:500">${sys.plat}/${sys.arch}</div></div>
</div>
</div></div>

<div class="pg ${p==='network'?'act':''}" id="network">
<div class="card"><div class="card-tit"><div class="ic ic-n">🌐</div>ZeroTier Network</div>
<div style="background:var(--ch);border-radius:10px;padding:24px;text-align:center;margin:12px 0"><div style="font-size:12px;color:var(--tm);margin-bottom:8px">ZeroTier Virtual IP</div><div style="font-family:'JetBrains Mono',monospace;font-size:28px;font-weight:600;color:var(--ac)">${zt.ip}</div></div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px"><div style="background:var(--ch);padding:14px;border-radius:8px"><div style="font-size:12px;color:var(--tm)">Network ID</div><div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:500;margin-top:4px">${zt.net||'Not connected'}</div></div><div style="background:var(--ch);padding:14px;border-radius:8px"><div style="font-size:12px;color:var(--tm)">ZT Address</div><div style="font-family:'JetBrains Mono',monospace;font-size:12px;margin-top:4px">${zt.addr}</div></div><div style="background:var(--ch);padding:14px;border-radius:8px"><div style="font-size:12px;color:var(--tm)">LAN IP</div><div style="font-family:'JetBrains Mono',monospace;font-size:12px;margin-top:4px">${sys.lanIp}</div></div></div>
</div>
<div class="card"><div class="card-tit"><div class="ic ic-n">⚙</div>Network Configuration</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px"><div><div style="font-size:12px;color:var(--tm);margin-bottom:6px">Gateway IP</div><input type="text" id="gatewayIp" placeholder="e.g., 192.168.192.1" style="width:100%;background:var(--ch);border:1px solid var(--b);border-radius:6px;padding:10px;color:var(--t);font-size:14px"></div><div><div style="font-size:12px;color:var(--tm);margin-bottom:6px">DNS Servers</div><input type="text" id="dnsServers" placeholder="e.g., 1.1.1.1, 8.8.8.8" style="width:100%;background:var(--ch);border:1px solid var(--b);border-radius:6px;padding:10px;color:var(--t);font-size:14px"></div></div>
<div style="display:flex;gap:8px"><button class="btn-sm" onclick="saveNetworkConfig()" style="background:var(--ac);color:#000;padding:8px 16px">Apply Configuration</button><button class="btn-sm" onclick="leaveNetwork()" style="background:var(--rd);color:#fff;padding:8px 16px">Leave Network</button></div>
</div></div>

<div class="pg ${p==='tasks'?'act':''}" id="tasks">
<div class="card"><div class="card-tit"><div class="ic ic-t">☰</div>Task Queue (${tasks.stats.p} pending, ${tasks.stats.c} completed) <button class="btn-sm" onclick="showAdd()" style="margin-left:auto">+ Add Task</button></div>
${tasks.list.length?tasks.list.map(t=>`<div class="task ${t.st}"><div class="task-hd"><div class="task-tit">${t.t}</div><div class="task-btns"><button class="btn-sm btn-c" onclick="taskAct('complete',${t.id})">✓</button><button class="btn-sm" onclick="showEdit(${t.id},'${t.t.replace(/'/g,"\\'")}',${t.pr})">✎</button><button class="btn-sm btn-d" onclick="taskAct('delete',${t.id})">✕</button></div></div><div class="task-meta"><span style="color:${colT(t.st)}">[${t.st}]</span><span>Priority: ${t.pr}</span></div>${t.sub?.length?`<div class="subs">${t.sub.map(s=>`<div class="sub ${s.s?'done':''}"><input type="checkbox" ${s.s?'checked':''} onclick="subtask(${t.id},${t.sub.indexOf(s)})"> <span>${s.c}</span></div>`).join('')}</div>`:''}</div>`).join(''):'<div style="padding:20px;text-align:center;color:var(--tm)">No tasks. Click "+ Add Task" to create one.</div>'}
</div></div>

<div class="pg ${p==='tokens'?'act':''}" id="tokens">
<div class="card"><div class="card-tit"><div class="ic ic-x">🔑</div>API Tokens</div>
${tokens.map(t=>`<div class="tok"><div><div class="tok-n">${t.name}</div><div class="tok-k">${t.key}</div></div><div style="font-size:12px;color:var(--tm)">${t.baseUrl||''}</div><label class="tog"><input type="checkbox" ${t.enabled?'checked':''} disabled><span class="tog-sl"></span></label></div>`).join('')}
<div class="gw"><div class="gw-l">Gateway Token</div><div class="gw-v">${(()=>{try{const cf=path.join(os.homedir(),'.openclaw','openclaw.json');return fs.existsSync(cf)?JSON.parse(fs.readFileSync(cf,'utf8')).gateway?.auth?.token?.substring(0,12)+'...':'Not configured'}catch(e){return'Error'}})()}</div></div>
</div></div>

<div class="pg ${p==='logs'?'act':''}" id="logs">
<div class="card"><div class="card-tit"><div class="ic ic-l">📋</div>System Logs <button class="btn-sm" onclick="loadLogs()" style="margin-left:auto">↻</button></div>
${logs.map(l=>`<div class="log"><span class="log-t">${l.t.substring(0,16)}</span><span class="log-s">[${l.s}]</span><span class="log-m">${l.m}</span></div>`).join('')}
</div></div>

</main>

<div class="edit-modal" id="editModal" onclick="if(event.target===this)this.style.display='none'">
<div class="edit-box">
<h3 id="editTitle">Edit Task</h3>
<input type="hidden" id="editId">
<input type="text" id="editContent" placeholder="Task description">
<select id="editPriority"><option value="1">Priority 1 (Low)</option><option value="2">Priority 2 (Medium)</option><option value="3">Priority 3 (High)</option></select>
<div class="btns"><button class="btn-sm" onclick="document.getElementById('editModal').style.display='none'">Cancel</button><button class="btn-sm" onclick="saveEdit()" style="background:var(--ac);color:#000">Save</button></div>
</div>
</div>

<script>
let tasks=${JSON.stringify(tasks.list)};
function go(p){sessionStorage.setItem('page',p);location.href='?page='+p}
const s=sessionStorage.getItem('page');if(s&&s!=='${p}'){document.querySelectorAll('.pg').forEach(x=>x.classList.remove('act'));document.getElementById(s)?.classList.add('act')}
function taskAct(action,id){fetch('/api/task',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action,id})}).then(()=>location.reload());}
function showEdit(id,content,pr){document.getElementById('editId').value=id;document.getElementById('editContent').value=content;document.getElementById('editPriority').value=pr;document.getElementById('editTitle').textContent='Edit Task';document.getElementById('editModal').style.display='flex';}
function showAdd(){document.getElementById('editId').value='';document.getElementById('editContent').value='';document.getElementById('editPriority').value='1';document.getElementById('editTitle').textContent='Add Task';document.getElementById('editModal').style.display='flex';}
function saveEdit(){const id=document.getElementById('editId').value;const content=document.getElementById('editContent').value;const priority=parseInt(document.getElementById('editPriority').value);fetch('/api/task',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:id?'update':'add',id:id?parseInt(id):null,content,priority})}).then(()=>location.reload());}
function subtask(taskId,idx){fetch('/api/task',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:'subtask',taskId,idx})}).then(()=>location.reload());}
function loadLogs(){location.reload();}
function saveNetworkConfig(){const g=document.getElementById('gatewayIp').value;const d=document.getElementById('dnsServers').value;fetch('/api/network',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({gateway:g,dns:d})}).then(()=>alert('Configuration saved'));}
function leaveNetwork(){if(confirm('Leave ZeroTier network?')){fetch('/api/network',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({leave:true})}).then(()=>alert('Left network - refresh to see changes'));}}
setTimeout(()=>location.reload(),30000);
</script></body></html>`;
}

const server=http.createServer(async(req,res)=>{
  const u=new URL(req.url,'http://localhost:'+PORT);
  res.setHeader('Access-Control-Allow-Origin','*');
  res.setHeader('Access-Control-Allow-Methods','GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers','Content-Type');
  if(req.method==='OPTIONS'){res.end();return;}
  if(u.pathname==='/api/task'){
    let body='';req.on('data',c=>body+=c);req.on('end',() => {
      try{
        const d=JSON.parse(body);
        const tasks=getTasks();
        if(d.action==='add'){const newTask={id:Date.now(),t:d.content,st:'pending',pr:d.priority||1,sub:[]};tasks.push(newTask);saveTasks(tasks);}
        else if(d.action==='complete'){const idx=tasks.findIndex(t=>t.id==d.id);if(idx>-1){tasks[idx].st='completed';saveTasks(tasks);}}
        else if(d.action==='delete'){const idx=tasks.findIndex(t=>t.id==d.id);if(idx>-1){tasks.splice(idx,1);saveTasks(tasks);}}
        else if(d.action==='update'){const idx=tasks.findIndex(t=>t.id==d.id);if(idx>-1){tasks[idx].t=d.content;tasks[idx].pr=d.priority;saveTasks(tasks);}}
        else if(d.action==='subtask'){const idx=tasks.findIndex(t=>t.id==d.taskId);if(idx>-1&&tasks[idx].sub&&tasks[idx].sub[d.idx]){tasks[idx].sub[d.idx].s=!tasks[idx].sub[d.idx].s;saveTasks(tasks);}}
        res.end('ok');
      }catch(e){res.end('error:'+e.message);}
    });return;
  }
  if(u.pathname==='/api/network'){
    let body='';req.on('data',c=>body+=c);req.on('end',async() => {
      try{
        const d=JSON.parse(body);
        if(d.leave){
          await execCmd('sudo zerotier-cli leave af415e486fc5fca0');
          res.end('left');
        }else if(d.gateway||d.dns){
          const cfg=path.join(DATA_DIR,'network.json');
          const current=fs.existsSync(cfg)?JSON.parse(fs.readFileSync(cfg,'utf8')):{};
          fs.writeFileSync(cfg,JSON.stringify({...current,gateway:d.gateway,dns:d.dns,updatedAt:new Date().toISOString()},null,2));
          res.end('saved');
        }else{res.end('ok');}
      }catch(e){res.end('error:'+e.message);}
    });return;
  }
  const p=u.searchParams.get('page')||'overview';
  const d=await getData();
  res.setHeader('Content-Type','text/html;charset=utf-8');
  res.end(html(d,p));
});

server.listen(PORT,'0.0.0.0',()=>{
  const ip=Object.values(os.networkInterfaces()).flat().find(i=>i.family==='IPv4'&&!i.internal)?.address||'0.0.0.0';
  console.log(`Glitch Dashboard v3.2`);
  console.log(`Platform: ${PLATFORM}`);
  console.log(`URL: http://localhost:${PORT}`);
  console.log(`LAN: http://${ip}:${PORT}`);
});
