#!/usr/bin/env node
/**
 * RMN Soul Visualize — Standalone visualization server
 * Serves the neural graph visualization on a local port
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { RecursiveMemoryNetwork, computeMemoryMerkle } = require('./rmn-engine');

const WORKSPACE = process.env.OPENCLAW_WORKSPACE || path.resolve(__dirname, '../../../');
const DATA_DIR = path.join(WORKSPACE, 'rmn-soul-data');
const DB_PATH = path.join(DATA_DIR, 'memory.json');
const PORT = process.env.RMN_VIZ_PORT || 3457;

const HTML = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>🧠 AgentSoul — Neural Memory Visualization</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #0a0a0a; color: #e2e8f0; font-family: 'Courier New', monospace; overflow: hidden; }
#header { position: fixed; top: 0; left: 0; right: 0; z-index: 10; display: flex; align-items: center; justify-content: space-between; padding: 12px 20px; background: #0a0a0aee; border-bottom: 1px solid #1e293b; }
#header h1 { font-size: 18px; color: #f87171; }
#header .stats { font-size: 11px; color: #64748b; }
#canvas { display: block; }
#tooltip { position: fixed; display: none; padding: 10px 14px; background: #1e293bee; border: 1px solid #334155; font-size: 11px; max-width: 300px; z-index: 20; pointer-events: none; }
#tooltip .layer { font-weight: bold; margin-bottom: 4px; }
#tooltip .content { color: #cbd5e1; margin-bottom: 4px; }
#tooltip .meta { color: #64748b; font-size: 10px; }
#sidebar { position: fixed; top: 50px; right: 0; width: 260px; height: calc(100vh - 50px); background: #0f172aee; border-left: 1px solid #1e293b; padding: 16px; overflow-y: auto; font-size: 11px; }
#sidebar h3 { color: #f87171; margin-bottom: 12px; font-size: 13px; }
.layer-bar { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.layer-bar .name { width: 70px; }
.layer-bar .bar { flex: 1; height: 8px; background: #1e293b; }
.layer-bar .bar-fill { height: 100%; transition: width 0.3s; }
.layer-bar .count { width: 24px; text-align: right; color: #64748b; }
.merkle { margin-top: 16px; padding-top: 12px; border-top: 1px solid #1e293b; }
.merkle .label { color: #64748b; font-size: 10px; }
.merkle .hash { color: #60a5fa; font-size: 10px; word-break: break-all; margin-bottom: 8px; }
</style>
</head>
<body>
<div id="header">
  <h1>🧠 AgentSoul</h1>
  <div class="stats" id="stats"></div>
</div>
<canvas id="canvas"></canvas>
<div id="tooltip"></div>
<div id="sidebar">
  <h3>认知层级</h3>
  <div id="layers"></div>
  <div class="merkle" id="merkle"></div>
</div>
<script>
const LAYERS = [
  { name: 'Sensory', color: '#94a3b8', emoji: '👁️' },
  { name: 'Working', color: '#60a5fa', emoji: '⚡' },
  { name: 'Episodic', color: '#34d399', emoji: '📖' },
  { name: 'Semantic', color: '#fbbf24', emoji: '🧠' },
  { name: 'Identity', color: '#f87171', emoji: '🔥' },
];

let nodes = [], edges = [], graphNodes = [];
let hoveredNode = null;
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const tooltip = document.getElementById('tooltip');

function resize() {
  canvas.width = window.innerWidth - 260;
  canvas.height = window.innerHeight;
}
resize();
window.addEventListener('resize', resize);

async function loadData() {
  const res = await fetch('/api/graph');
  const data = await res.json();
  nodes = data.nodes || [];
  edges = data.edges || [];
  
  document.getElementById('stats').textContent = nodes.length + ' nodes · ' + edges.length + ' connections';
  
  // Layer bars
  const layersDiv = document.getElementById('layers');
  const maxCount = Math.max(1, ...LAYERS.map((_, i) => nodes.filter(n => n.layer === i).length));
  layersDiv.innerHTML = LAYERS.map((l, i) => {
    const count = nodes.filter(n => n.layer === i).length;
    return '<div class="layer-bar"><span class="name" style="color:' + l.color + '">' + l.emoji + ' ' + l.name + '</span><div class="bar"><div class="bar-fill" style="width:' + (count/maxCount*100) + '%;background:' + l.color + '"></div></div><span class="count">' + count + '</span></div>';
  }).join('');
  
  // Merkle
  if (data.merkle) {
    document.getElementById('merkle').innerHTML = '<div class="label">Memory Root</div><div class="hash">0x' + data.merkle.memoryRoot.slice(0,32) + '...</div><div class="label">Soul Hash</div><div class="hash">0x' + data.merkle.soulHash.slice(0,32) + '...</div>';
  }
  
  initGraph();
}

function initGraph() {
  const cx = canvas.width / 2, cy = canvas.height / 2;
  graphNodes = nodes.map((n, i) => {
    const r = 60 + n.layer * 90;
    const a = (i / nodes.length) * Math.PI * 2 + Math.random() * 0.3;
    return { ...n, x: cx + Math.cos(a) * r + (Math.random()-0.5)*30, y: cy + Math.sin(a) * r + (Math.random()-0.5)*30, vx: 0, vy: 0, radius: 3 + n.weight * 4 + n.layer * 1.5 };
  });
  const nodeMap = new Map(graphNodes.map(n => [n.id, n]));
  edges = edges.filter(e => nodeMap.has(e.source) && nodeMap.has(e.target)).map(e => [nodeMap.get(e.source), nodeMap.get(e.target)]);
  animate(0);
}

function animate(frame) {
  const cx = canvas.width / 2, cy = canvas.height / 2;
  const alpha = Math.max(0.001, 1 - frame / 300);
  
  for (const n of graphNodes) {
    n.vx += (cx - n.x) * 0.001 * alpha;
    n.vy += (cy - n.y) * 0.001 * alpha;
    const tr = 60 + n.layer * 90;
    const dx = n.x - cx, dy = n.y - cy;
    const d = Math.sqrt(dx*dx+dy*dy)||1;
    const rf = (tr - d) * 0.005 * alpha;
    n.vx += (dx/d)*rf; n.vy += (dy/d)*rf;
  }
  for (let i = 0; i < graphNodes.length; i++) for (let j = i+1; j < graphNodes.length; j++) {
    const a = graphNodes[i], b = graphNodes[j];
    const dx = b.x-a.x, dy = b.y-a.y, d = Math.sqrt(dx*dx+dy*dy)||1;
    if (d < 80) { const f = (80-d)*0.02*alpha; a.vx -= dx/d*f; a.vy -= dy/d*f; b.vx += dx/d*f; b.vy += dy/d*f; }
  }
  for (const [a,b] of edges) {
    const dx = b.x-a.x, dy = b.y-a.y, d = Math.sqrt(dx*dx+dy*dy)||1;
    const f = (d-60)*0.003*alpha;
    a.vx += dx/d*f; a.vy += dy/d*f; b.vx -= dx/d*f; b.vy -= dy/d*f;
  }
  for (const n of graphNodes) {
    n.vx *= 0.9; n.vy *= 0.9; n.x += n.vx; n.y += n.vy;
    n.x = Math.max(20, Math.min(canvas.width-20, n.x));
    n.y = Math.max(20, Math.min(canvas.height-20, n.y));
  }
  
  ctx.fillStyle = '#0a0a0a'; ctx.fillRect(0, 0, canvas.width, canvas.height);
  for (let l = 0; l < 5; l++) {
    ctx.beginPath(); ctx.arc(cx, cy, 60+l*90, 0, Math.PI*2);
    ctx.strokeStyle = LAYERS[l].color + '15'; ctx.lineWidth = 1; ctx.stroke();
  }
  for (const [a,b] of edges) {
    ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y);
    ctx.strokeStyle = (LAYERS[a.layer]?.color||'#334155') + '30'; ctx.lineWidth = 0.5; ctx.stroke();
  }
  for (const n of graphNodes) {
    const c = LAYERS[n.layer]?.color||'#94a3b8';
    if (n.weight > 1.2 || n === hoveredNode) { ctx.beginPath(); ctx.arc(n.x, n.y, n.radius+4, 0, Math.PI*2); ctx.fillStyle = c+'20'; ctx.fill(); }
    ctx.beginPath(); ctx.arc(n.x, n.y, n.radius, 0, Math.PI*2); ctx.fillStyle = n===hoveredNode?'#fff':c; ctx.fill();
    if (n.layer === 4) { const p = Math.sin(frame*0.05)*2; ctx.beginPath(); ctx.arc(n.x, n.y, n.radius+3+p, 0, Math.PI*2); ctx.strokeStyle = c+'40'; ctx.lineWidth = 1; ctx.stroke(); }
  }
  
  if (frame < 400) requestAnimationFrame(() => animate(frame + 1));
}

canvas.addEventListener('mousemove', e => {
  const rect = canvas.getBoundingClientRect();
  const mx = e.clientX - rect.left, my = e.clientY - rect.top;
  let closest = null, minD = 20;
  for (const n of graphNodes) { const d = Math.sqrt((n.x-mx)**2+(n.y-my)**2); if (d < minD) { minD = d; closest = n; } }
  hoveredNode = closest;
  if (closest) {
    tooltip.style.display = 'block';
    tooltip.style.left = (e.clientX + 15) + 'px';
    tooltip.style.top = (e.clientY - 10) + 'px';
    tooltip.innerHTML = '<div class="layer" style="color:' + (LAYERS[closest.layer]?.color) + '">' + (LAYERS[closest.layer]?.emoji) + ' ' + (LAYERS[closest.layer]?.name) + '</div><div class="content">' + closest.label.slice(0,100) + '</div><div class="meta">Weight: ' + closest.weight.toFixed(2) + ' | Tags: ' + (closest.tags||[]).slice(0,3).join(', ') + '</div>';
  } else { tooltip.style.display = 'none'; }
});

loadData();
</script>
</body>
</html>`;

// HTTP Server
const server = http.createServer((req, res) => {
  if (req.url === '/api/graph') {
    const rmn = new RecursiveMemoryNetwork(DB_PATH);
    const graph = rmn.exportGraph();
    const merkle = computeMemoryMerkle(rmn);
    res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
    res.end(JSON.stringify({ ...graph, merkle }));
  } else if (req.url === '/api/stats') {
    const rmn = new RecursiveMemoryNetwork(DB_PATH);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(rmn.stats()));
  } else {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(HTML);
  }
});

server.listen(PORT, () => {
  console.log("🧠 AgentSoul Visualization: http://localhost:" + PORT);
});
