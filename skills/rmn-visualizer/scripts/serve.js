#!/usr/bin/env node
/**
 * RMN Visualizer — Parse agent memory files into 5-layer neural network + serve D3 visualization
 * Zero external dependencies. Pure Node.js.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const PORT = parseInt(process.env.RMN_PORT || '3459');
const WORKSPACE = process.env.RMN_WORKSPACE || process.env.OPENCLAW_WORKSPACE || findWorkspace();

function findWorkspace() {
  // Walk up from cwd looking for MEMORY.md or memory/
  let dir = process.cwd();
  for (let i = 0; i < 10; i++) {
    if (fs.existsSync(path.join(dir, 'MEMORY.md')) || fs.existsSync(path.join(dir, 'memory'))) return dir;
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return process.cwd();
}

// ─── Memory Parser ───

const LAYERS = {
  identity: { level: 4, decay: 0, color: '#ff6b6b' },
  semantic: { level: 3, decay: 0.001, color: '#ffa94d' },
  episodic: { level: 2, decay: 0.005, color: '#ffd43b' },
  working:  { level: 1, decay: 0.01,  color: '#69db7c' },
  sensory:  { level: 0, decay: 0.02,  color: '#74c0fc' },
};

function classifyEntry(text, source) {
  const t = text.toLowerCase();
  // Identity markers
  if (/^#+\s*\[?p0\]?\s*(瓜农|核心|身份|identity|who|soul|目标)/i.test(text)) return 'identity';
  if (/我是|i am|core.*principle|核心原则/i.test(t)) return 'identity';
  // Semantic — lessons, knowledge, tools
  if (/教训|lesson|技巧|tip|注意|warning|已安装|技术栈|配置/i.test(t)) return 'semantic';
  if (/^#+\s*\[?p[012]\]?\s*(基础设施|教训|已取消)/i.test(text)) return 'semantic';
  // Episodic — events, dates, history
  if (/\d{4}-\d{2}-\d{2}|发布|部署|完成|中奖|created|deployed/i.test(t)) return 'episodic';
  if (source.includes('memory/') && /^\d{4}-\d{2}-\d{2}/.test(path.basename(source))) return 'episodic';
  // Working — active tasks, issues
  if (source.includes('.issues/')) return 'working';
  if (/待做|todo|进行中|in.?progress|下一步|next/i.test(t)) return 'working';
  // Sensory — heartbeat, raw data
  if (/heartbeat|心跳|状态|status|log|raw/i.test(t)) return 'sensory';
  // Default by source
  if (source.includes('MEMORY.md')) return 'semantic';
  if (source.includes('memory/')) return 'episodic';
  return 'working';
}

function hash(s) { return crypto.createHash('sha256').update(s).digest('hex').slice(0, 12); }

function parseMemoryFiles() {
  const nodes = [];
  const connections = [];
  const nodeMap = {};

  function addNode(text, source, layer) {
    const id = hash(text + source);
    if (nodeMap[id]) return id;
    const weight = layer === 'identity' ? 1.5 : (1.0 + Math.random() * 0.3);
    const node = { id, text: text.slice(0, 200), source, layer, weight, tags: extractTags(text) };
    nodes.push(node);
    nodeMap[id] = node;
    return id;
  }

  function extractTags(text) {
    const tags = new Set();
    const patterns = [
      /\b(NFT|IPFS|ERC-\d+|Base|Solana|ETH|BTC)\b/gi,
      /\b(ClawWork|ClawHub|AgentAwaken|AgentSoul|RMN|Conway)\b/gi,
      /\b(pnpm|npm|node|next\.js|tailwind|wagmi|viem)\b/gi,
    ];
    for (const p of patterns) {
      const m = text.match(p);
      if (m) m.forEach(t => tags.add(t.toLowerCase()));
    }
    return [...tags];
  }

  function parseMarkdownSections(content, source) {
    const sections = content.split(/^(?=#{1,3}\s)/m).filter(s => s.trim());
    const ids = [];
    for (const section of sections) {
      const lines = section.trim().split('\n');
      const heading = lines[0] || '';
      const body = lines.slice(1).join('\n').trim();
      if (!body && heading.length < 10) continue;
      const fullText = heading + '\n' + body;
      const layer = classifyEntry(fullText, source);
      const id = addNode(fullText, source, layer);
      ids.push(id);
    }
    // Connect sequential sections
    for (let i = 1; i < ids.length; i++) {
      connections.push({ source: ids[i - 1], target: ids[i], strength: 0.3 });
    }
    return ids;
  }

  function parseBulletList(content, source) {
    const items = content.split(/^[-*]\s/m).filter(s => s.trim());
    const ids = [];
    for (const item of items) {
      if (item.trim().length < 5) continue;
      const layer = classifyEntry(item, source);
      const id = addNode(item.trim(), source, layer);
      ids.push(id);
    }
    return ids;
  }

  // Scan files
  const files = [];
  const memoryMd = path.join(WORKSPACE, 'MEMORY.md');
  if (fs.existsSync(memoryMd)) files.push(memoryMd);

  const memoryDir = path.join(WORKSPACE, 'memory');
  if (fs.existsSync(memoryDir)) {
    for (const f of fs.readdirSync(memoryDir)) {
      if (f.endsWith('.md')) files.push(path.join(memoryDir, f));
    }
  }

  const issuesDir = path.join(WORKSPACE, '.issues');
  if (fs.existsSync(issuesDir)) {
    for (const f of fs.readdirSync(issuesDir)) {
      if (f.endsWith('.md')) files.push(path.join(issuesDir, f));
    }
  }

  const soulMd = path.join(WORKSPACE, 'SOUL.md');
  if (fs.existsSync(soulMd)) files.push(soulMd);

  // Parse each file
  const fileNodeIds = {};
  for (const file of files) {
    try {
      const content = fs.readFileSync(file, 'utf-8');
      const rel = path.relative(WORKSPACE, file);
      const ids = parseMarkdownSections(content, rel);
      fileNodeIds[rel] = ids;
    } catch (e) { /* skip unreadable */ }
  }

  // Cross-file connections by shared tags
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const shared = nodes[i].tags.filter(t => nodes[j].tags.includes(t));
      if (shared.length > 0) {
        connections.push({
          source: nodes[i].id,
          target: nodes[j].id,
          strength: Math.min(shared.length * 0.2, 0.8),
          tags: shared,
        });
      }
    }
  }

  // Stats
  const stats = {
    totalNodes: nodes.length,
    totalConnections: connections.length,
    layers: {},
    avgWeight: 0,
    files: files.length,
  };
  for (const l of Object.keys(LAYERS)) stats.layers[l] = 0;
  let totalW = 0;
  for (const n of nodes) { stats.layers[n.layer]++; totalW += n.weight; }
  stats.avgWeight = nodes.length ? (totalW / nodes.length).toFixed(3) : '0';

  return { nodes, connections, stats, layers: LAYERS };
}

// ─── HTML Template ───

function getHTML() {
  return `<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>RMN Visualizer — 递归记忆神经网络</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#0a0a0a; color:#e0e0e0; font-family:'Courier New',monospace; overflow:hidden; }
#canvas { width:100vw; height:100vh; }
svg { width:100%; height:100%; }

.panel {
  position:fixed; top:16px; left:16px; background:rgba(10,10,10,0.92);
  border:2px solid #333; padding:16px; min-width:240px; z-index:10;
  font-size:13px; border-radius:4px;
}
.panel h1 { font-size:18px; color:#00ff88; margin-bottom:8px; }
.panel .stat { display:flex; justify-content:space-between; padding:3px 0; border-bottom:1px solid #222; }
.panel .stat-val { color:#00ff88; font-weight:bold; }
.layer-row { display:flex; align-items:center; gap:6px; padding:2px 0; }
.layer-dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }
.layer-name { flex:1; }
.layer-count { color:#888; }

.legend {
  position:fixed; bottom:16px; left:16px; background:rgba(10,10,10,0.92);
  border:2px solid #333; padding:12px; font-size:12px; border-radius:4px; z-index:10;
}
.legend h3 { color:#00ff88; margin-bottom:6px; font-size:13px; }

.tooltip {
  position:fixed; display:none; background:rgba(0,0,0,0.95); border:1px solid #00ff88;
  padding:10px 14px; max-width:360px; font-size:12px; z-index:20; border-radius:4px;
  pointer-events:none; line-height:1.5;
}
.tooltip .tt-layer { color:#00ff88; font-weight:bold; text-transform:uppercase; font-size:11px; }
.tooltip .tt-source { color:#888; font-size:11px; }
.tooltip .tt-text { margin-top:4px; color:#ccc; word-break:break-word; }
.tooltip .tt-tags { margin-top:4px; }
.tooltip .tt-tag { display:inline-block; background:#222; color:#ffa94d; padding:1px 5px; margin:1px; border-radius:2px; font-size:10px; }

.controls {
  position:fixed; top:16px; right:16px; background:rgba(10,10,10,0.92);
  border:2px solid #333; padding:12px; font-size:12px; border-radius:4px; z-index:10;
}
.controls button {
  background:#222; color:#e0e0e0; border:1px solid #444; padding:4px 10px;
  cursor:pointer; margin:2px; font-family:inherit; font-size:12px; border-radius:2px;
}
.controls button:hover { background:#00ff88; color:#000; }
.controls button.active { background:#00ff88; color:#000; }
</style>
</head>
<body>

<div class="panel" id="stats"></div>
<div class="legend">
  <h3>◈ 记忆层级</h3>
  <div class="layer-row"><div class="layer-dot" style="background:#ff6b6b"></div><span>Identity — 永不衰减</span></div>
  <div class="layer-row"><div class="layer-dot" style="background:#ffa94d"></div><span>Semantic — 知识教训</span></div>
  <div class="layer-row"><div class="layer-dot" style="background:#ffd43b"></div><span>Episodic — 事件记录</span></div>
  <div class="layer-row"><div class="layer-dot" style="background:#69db7c"></div><span>Working — 当前任务</span></div>
  <div class="layer-row"><div class="layer-dot" style="background:#74c0fc"></div><span>Sensory — 感知数据</span></div>
</div>
<div class="tooltip" id="tooltip"></div>
<div class="controls" id="controls">
  <div style="color:#00ff88;font-weight:bold;margin-bottom:6px">◈ 控制</div>
  <button onclick="resetZoom()">重置视图</button>
  <button onclick="toggleLabels()" id="btnLabels">标签: ON</button>
  <br>
  <div style="margin-top:6px;color:#888">过滤层级:</div>
  <button class="active" data-layer="all" onclick="filterLayer('all',this)">全部</button>
  <button data-layer="identity" onclick="filterLayer('identity',this)">Identity</button>
  <button data-layer="semantic" onclick="filterLayer('semantic',this)">Semantic</button>
  <button data-layer="episodic" onclick="filterLayer('episodic',this)">Episodic</button>
  <button data-layer="working" onclick="filterLayer('working',this)">Working</button>
  <button data-layer="sensory" onclick="filterLayer('sensory',this)">Sensory</button>
</div>

<div id="canvas"></div>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
let data, simulation, svg, g, link, node, label;
let showLabels = true;
let activeLayer = 'all';

async function init() {
  const res = await fetch('/api/data');
  data = await res.json();
  renderStats();
  renderGraph();
}

function renderStats() {
  const s = data.stats;
  document.getElementById('stats').innerHTML =
    '<h1>🧠 RMN Visualizer</h1>' +
    '<div class="stat"><span>节点总数</span><span class="stat-val">' + s.totalNodes + '</span></div>' +
    '<div class="stat"><span>连接数</span><span class="stat-val">' + s.totalConnections + '</span></div>' +
    '<div class="stat"><span>平均权重</span><span class="stat-val">' + s.avgWeight + '</span></div>' +
    '<div class="stat"><span>文件数</span><span class="stat-val">' + s.files + '</span></div>' +
    '<div style="margin-top:8px;border-top:1px solid #333;padding-top:6px">' +
    Object.entries(s.layers).map(([k,v]) =>
      '<div class="layer-row"><div class="layer-dot" style="background:' + data.layers[k].color + '"></div>' +
      '<span class="layer-name">' + k + '</span><span class="layer-count">' + v + '</span></div>'
    ).join('') + '</div>';
}

function renderGraph() {
  const W = window.innerWidth, H = window.innerHeight;
  svg = d3.select('#canvas').append('svg').attr('viewBox', [0, 0, W, H]);

  // Zoom
  const zoom = d3.zoom().scaleExtent([0.1, 8]).on('zoom', e => g.attr('transform', e.transform));
  svg.call(zoom);
  window._zoom = zoom;

  g = svg.append('g');

  // Links
  link = g.append('g').selectAll('line')
    .data(data.connections)
    .join('line')
    .attr('stroke', '#333')
    .attr('stroke-width', d => Math.max(0.5, d.strength * 3))
    .attr('stroke-opacity', 0.4);

  // Nodes
  node = g.append('g').selectAll('circle')
    .data(data.nodes)
    .join('circle')
    .attr('r', d => 4 + d.weight * 6)
    .attr('fill', d => data.layers[d.layer].color)
    .attr('stroke', '#000')
    .attr('stroke-width', 0.5)
    .attr('opacity', d => 0.5 + d.weight * 0.35)
    .attr('cursor', 'pointer')
    .on('mouseover', showTooltip)
    .on('mousemove', moveTooltip)
    .on('mouseout', hideTooltip)
    .call(d3.drag().on('start', dragStart).on('drag', dragging).on('end', dragEnd));

  // Labels
  label = g.append('g').selectAll('text')
    .data(data.nodes)
    .join('text')
    .text(d => d.text.split('\\n')[0].replace(/^#+\\s*/, '').slice(0, 30))
    .attr('font-size', 9)
    .attr('fill', '#888')
    .attr('dx', d => 6 + d.weight * 6)
    .attr('dy', 3)
    .attr('display', showLabels ? 'block' : 'none');

  // Simulation
  simulation = d3.forceSimulation(data.nodes)
    .force('link', d3.forceLink(data.connections).id(d => d.id).distance(80).strength(d => d.strength || 0.3))
    .force('charge', d3.forceManyBody().strength(-120))
    .force('center', d3.forceCenter(W / 2, H / 2))
    .force('collision', d3.forceCollide().radius(d => 8 + d.weight * 6))
    .force('y', d3.forceY().y(d => {
      const layerY = { identity: 0.15, semantic: 0.3, episodic: 0.5, working: 0.7, sensory: 0.85 };
      return H * (layerY[d.layer] || 0.5);
    }).strength(0.08))
    .on('tick', ticked);
}

function ticked() {
  link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
  node.attr('cx', d => d.x).attr('cy', d => d.y);
  label.attr('x', d => d.x).attr('y', d => d.y);
}

function dragStart(e, d) { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }
function dragging(e, d) { d.fx = e.x; d.fy = e.y; }
function dragEnd(e, d) { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }

const tt = document.getElementById('tooltip');
function showTooltip(e, d) {
  tt.style.display = 'block';
  tt.innerHTML =
    '<div class="tt-layer">' + d.layer + ' (weight: ' + d.weight.toFixed(2) + ')</div>' +
    '<div class="tt-source">' + d.source + '</div>' +
    '<div class="tt-text">' + d.text.replace(/</g,'&lt;').slice(0, 300) + '</div>' +
    (d.tags.length ? '<div class="tt-tags">' + d.tags.map(t => '<span class="tt-tag">' + t + '</span>').join('') + '</div>' : '');
}
function moveTooltip(e) { tt.style.left = (e.clientX + 16) + 'px'; tt.style.top = (e.clientY + 16) + 'px'; }
function hideTooltip() { tt.style.display = 'none'; }

function resetZoom() { svg.transition().duration(500).call(window._zoom.transform, d3.zoomIdentity); }
function toggleLabels() {
  showLabels = !showLabels;
  label.attr('display', showLabels ? 'block' : 'none');
  document.getElementById('btnLabels').textContent = '标签: ' + (showLabels ? 'ON' : 'OFF');
}
function filterLayer(layer, btn) {
  activeLayer = layer;
  document.querySelectorAll('.controls button[data-layer]').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  node.attr('opacity', d => (layer === 'all' || d.layer === layer) ? (0.5 + d.weight * 0.35) : 0.05);
  link.attr('stroke-opacity', d => {
    if (layer === 'all') return 0.4;
    const sn = data.nodes.find(n => n.id === (d.source.id || d.source));
    const tn = data.nodes.find(n => n.id === (d.target.id || d.target));
    return (sn && sn.layer === layer) || (tn && tn.layer === layer) ? 0.6 : 0.03;
  });
  label.attr('opacity', d => (layer === 'all' || d.layer === layer) ? 1 : 0.1);
}

init();
</script>
</body>
</html>`;
}

// ─── HTTP Server ───

const server = http.createServer((req, res) => {
  if (req.url === '/api/data') {
    const data = parseMemoryFiles();
    res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
    res.end(JSON.stringify(data));
  } else {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(getHTML());
  }
});

server.listen(PORT, () => {
  console.log('🧠 RMN Visualizer running at http://localhost:' + PORT);
  console.log('📂 Workspace: ' + WORKSPACE);
  console.log('');
  console.log('Open in browser to see your agent\'s recursive memory neural network.');
});
