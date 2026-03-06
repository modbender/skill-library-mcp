#!/usr/bin/env node
// visualize.mjs — Generate interactive HTML visualization of the Knowledge Graph
// Output: data/kg-viz.html (self-contained, offline, no CDN)
// Usage: node scripts/visualize.mjs [--output <path>]

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { load } from '../lib/graph.mjs';
import { loadConfig } from '../lib/config.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));

function flag(name) {
  const args = process.argv.slice(2);
  const i = args.indexOf('--' + name);
  return i !== -1 ? args[i + 1] : null;
}

const outputPath = flag('output') || join(__dirname, '..', 'data', 'kg-viz.html');

const store = load();
const vizConfig = loadConfig().visualization;
const nodes = Object.values(store.nodes);
const edges = store.edges;

// Compute connection counts for node sizing
const connCount = {};
for (const n of nodes) connCount[n.id] = 0;
for (const e of edges) {
  connCount[e.from] = (connCount[e.from] || 0) + 1;
  connCount[e.to] = (connCount[e.to] || 0) + 1;
}
// Children also add to parent count
for (const n of nodes) {
  if (n.parent) {
    connCount[n.parent] = (connCount[n.parent] || 0) + 1;
    connCount[n.id] = (connCount[n.id] || 0) + 1;
  }
}

// Color map by type
const TYPE_COLORS = {
  human:      '#4A90D9',
  ai:         '#9B59B6',
  device:     '#27AE60',
  platform:   '#E67E22',
  project:    '#E74C3C',
  decision:   '#F39C12',
  concept:    '#1ABC9C',
  skill:      '#3498DB',
  network:    '#2ECC71',
  credential: '#C0392B',
  org:        '#8E44AD',
  service:    '#16A085',
  runtime:    '#D35400',
  agent:      '#7F8C8D',
  entity:     '#95A5A6',
  // life & world types
  place:      '#00BCD4',
  event:      '#FF5722',
  media:      '#E91E63',
  product:    '#795548',
  account:    '#607D8B',
  routine:    '#CDDC39',
  knowledge:  '#FFD700',
};

function getColor(type) {
  return TYPE_COLORS[type] || '#95A5A6';
}

// Build graph data for embedding
const graphData = {
  nodes: nodes.map(n => ({
    id: n.id,
    label: n.label,
    alias: n.alias,
    type: n.type,
    parent: n.parent,
    tags: n.tags || [],
    attrs: n.attrs || {},
    created: n.created,
    updated: n.updated,
    confidence: n.confidence,
    color: getColor(n.type),
    size: 8 + Math.min((connCount[n.id] || 0) * 3, 24), // 8-32 radius
    connections: connCount[n.id] || 0
  })),
  edges: edges.map(e => ({ from: e.from, to: e.to, rel: e.rel, attrs: e.attrs || {} })),
  // Parent-child edges (virtual)
  parentEdges: nodes
    .filter(n => n.parent)
    .map(n => ({ from: n.parent, to: n.id, rel: 'parent-of', virtual: true })),
  categories: store.categories,
  meta: store.meta
};

const graphJSON = JSON.stringify(graphData);

const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Knowledge Graph Visualization</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #1a1a2e; color: #e0e0e0; font-family: 'Segoe UI', system-ui, sans-serif; overflow: hidden; height: 100vh; }
  #canvas { display: block; cursor: grab; touch-action: none; }
  #canvas.dragging { cursor: grabbing; }
  #sidebar {
    position: fixed; top: 0; right: 0; width: 300px; height: 100vh;
    background: #16213e; border-left: 1px solid #0f3460;
    overflow-y: auto; padding: 16px; transform: translateX(100%);
    transition: transform 0.2s ease; z-index: 10;
  }
  #sidebar.open { transform: translateX(0); }
  #sidebar h2 { color: #e94560; margin-bottom: 8px; font-size: 1rem; }
  #sidebar .node-label { font-size: 1.2rem; font-weight: bold; margin-bottom: 4px; }
  #sidebar .node-type { font-size: 0.8rem; color: #888; margin-bottom: 12px; }
  #sidebar .section { margin-bottom: 12px; }
  #sidebar .section h3 { font-size: 0.75rem; text-transform: uppercase; color: #888; margin-bottom: 6px; letter-spacing: 1px; }
  #sidebar .tag { display: inline-block; background: #0f3460; color: #e94560; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin: 2px; }
  #sidebar .attr { font-size: 0.85rem; line-height: 1.6; }
  #sidebar .attr span { color: #888; }
  #sidebar .rel-item { font-size: 0.82rem; padding: 4px 0; border-bottom: 1px solid #0f3460; }
  #sidebar .node-link { color: #5dade2; text-decoration: none; cursor: pointer; }
  #sidebar .node-link:hover { color: #e94560; text-decoration: underline; }
  #sidebar .confidence { padding: 4px 8px; border-radius: 4px; font-size: 0.85rem; display: inline-block; margin-bottom: 8px; }
  #sidebar .conf-high { background: #1e4620; color: #4caf50; }
  #sidebar .conf-med { background: #3e2e00; color: #ff9800; }
  #sidebar .conf-low { background: #3e1010; color: #f44336; }
  #close-btn { position: absolute; top: 12px; right: 12px; background: none; border: none; color: #888; font-size: 1.2rem; cursor: pointer; }
  #close-btn:hover { color: #e94560; }
  #toolbar {
    position: fixed; top: 0; left: 0; right: 300px; height: 48px;
    background: #16213e; border-bottom: 1px solid #0f3460;
    display: flex; align-items: center; padding: 0 16px; gap: 12px; z-index: 10;
  }
  #toolbar.no-sidebar { right: 0; }
  #toolbar h1 { font-size: 0.95rem; color: #e94560; font-weight: 600; white-space: nowrap; }
  #toolbar .stats { font-size: 0.78rem; color: #888; }
  #legend {
    position: fixed; bottom: 16px; left: 16px;
    background: #16213e; border: 1px solid #0f3460;
    padding: 12px; border-radius: 8px; z-index: 10; max-width: 220px;
  }
  #legend h3 { font-size: 0.7rem; text-transform: uppercase; color: #888; margin-bottom: 8px; }
  #legend .leg-item { display: flex; align-items: center; gap: 8px; font-size: 0.75rem; margin-bottom: 4px; }
  #legend .leg-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }
  #search-box {
    background: #0f3460; border: 1px solid #e94560; color: #e0e0e0;
    padding: 4px 10px; border-radius: 4px; font-size: 0.85rem; width: 180px;
  }
  #search-box::placeholder { color: #888; }
  #controls { display: flex; gap: 8px; }
  .ctrl-btn {
    background: #0f3460; border: 1px solid #e94560; color: #e0e0e0;
    padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 0.8rem;
  }
  .ctrl-btn:hover { background: #e94560; }
  .zoom-btn { font-size: 1.1rem; font-weight: bold; padding: 2px 10px; min-width: 32px; }
  #canvas-wrap { position: fixed; top: 48px; left: 0; right: 0; bottom: 0; }
  #canvas-wrap.sidebar-open { right: 300px; }
  #tooltip {
    position: fixed; pointer-events: none; background: #16213e;
    border: 1px solid #e94560; padding: 6px 10px; border-radius: 6px;
    font-size: 0.8rem; display: none; z-index: 20; white-space: nowrap;
  }
</style>
</head>
<body>
<div id="toolbar" class="no-sidebar">
  <h1>🧠 Knowledge Graph</h1>
  <div class="stats" id="stats-label"></div>
  <input type="text" id="search-box" placeholder="Search nodes…" />
  <div id="controls">
    <button class="ctrl-btn zoom-btn" onclick="zoomIn()" title="Zoom in to see more detail">＋</button>
    <button class="ctrl-btn zoom-btn" onclick="zoomOut()" title="Zoom out to see the full graph">－</button>
    <button class="ctrl-btn" onclick="resetView()" title="Reset view to default position and zoom level">Reset</button>
    <button class="ctrl-btn" onclick="toggleParentEdges()" id="btn-hierarchy" title="Toggle parent-child hierarchy lines (blue dashed)">Hierarchy</button>
    <button class="ctrl-btn" onclick="toggleLabels()" title="Toggle node labels on/off — hide labels when zoomed out for a cleaner view">Labels</button>
  </div>
</div>
<div id="canvas-wrap">
  <canvas id="canvas"></canvas>
</div>
<div id="sidebar">
  <button id="close-btn" onclick="closeSidebar()">✕</button>
  <div id="sidebar-content"></div>
</div>
<div id="legend">
  <h3>Node Types</h3>
  <div id="legend-items"></div>
</div>
<div id="tooltip"></div>

<script>
const DATA = ${graphJSON};
const VIZ_CONFIG = ${JSON.stringify(vizConfig)};

// ── State ──
let nodes = DATA.nodes.map(n => ({ ...n, x: 0, y: 0, vx: 0, vy: 0, fx: null, fy: null }));
let edges = DATA.edges;
let parentEdges = DATA.parentEdges;
let showParentEdges = true;
let showLabels = true;
let transform = { x: 0, y: 0, scale: 1 };
let panStart = null;
let searchFilter = '';
let animFrame = null;
let running = true;
let selectedId = null;

const nodeById = {};
for (const n of nodes) nodeById[n.id] = n;

// ── Canvas setup ──
const wrap = document.getElementById('canvas-wrap');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

function resize() {
  canvas.width = wrap.clientWidth;
  canvas.height = wrap.clientHeight;
}
resize();
window.addEventListener('resize', () => { resize(); draw(); });

// ── Force-directed layout ──
const W = () => canvas.width;
const H = () => canvas.height;
const CX = () => W() / 2;
const CY = () => H() / 2;

function initPositions() {
  // Place nodes in a wider circle initially so they start more spread out
  const n = nodes.length;
  const r = Math.min(W(), H()) * 0.3 * VIZ_CONFIG.initialSpread;
  nodes.forEach((nd, i) => {
    const angle = (2 * Math.PI * i) / n;
    // Add a bit of randomness to break symmetry
    const jitter = 1 + (Math.random() - 0.5) * 0.3;
    nd.x = CX() + r * Math.cos(angle) * jitter;
    nd.y = CY() + r * Math.sin(angle) * jitter;
  });
}
initPositions();

// Update transform initial offset after init
transform.x = 0;
transform.y = 0;

function simulate() {
  const alpha = 0.3;
  const baseRepulsion = VIZ_CONFIG.repulsion;
  const attraction = 0.025;
  const parentAttraction = 0.05;
  const damping = 0.82;
  const centerGravity = 0.003;

  // Repulsion (all pairs) — scale by node sizes to prevent overlap
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i], b = nodes[j];
      const dx = b.x - a.x, dy = b.y - a.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      // Min distance = sum of radii + padding
      const minDist = a.size + b.size + 20;
      // Stronger repulsion when nodes overlap, normal otherwise
      const repulsion = dist < minDist
        ? baseRepulsion * VIZ_CONFIG.overlapPenalty / (dist * dist)
        : baseRepulsion / (dist * dist);
      const fx = (dx / dist) * repulsion;
      const fy = (dy / dist) * repulsion;
      a.vx -= fx; a.vy -= fy;
      b.vx += fx; b.vy += fy;
    }
  }

  // Attraction along edges — longer rest length to give nodes space
  const allEdges = [...edges, ...(showParentEdges ? parentEdges : [])];
  for (const e of allEdges) {
    const a = nodeById[e.from], b = nodeById[e.to];
    if (!a || !b) continue;
    const dx = b.x - a.x, dy = b.y - a.y;
    const dist = Math.sqrt(dx * dx + dy * dy) || 1;
    // Rest length scales with node sizes
    const baseLen = e.virtual ? VIZ_CONFIG.edgeRestLength - 20 : VIZ_CONFIG.edgeRestLength + 20;
    const targetLen = baseLen + (a.size + b.size) * 0.5;
    const force = (dist - targetLen) * (e.virtual ? parentAttraction : attraction);
    const fx = (dx / dist) * force;
    const fy = (dy / dist) * force;
    a.vx += fx; a.vy += fy;
    b.vx -= fx; b.vy -= fy;
  }

  // Center gravity
  for (const n of nodes) {
    n.vx += (CX() - n.x) * centerGravity;
    n.vy += (CY() - n.y) * centerGravity;
  }

  // Integrate
  for (const n of nodes) {
    if (n.fx !== null) { n.x = n.fx; n.y = n.fy; n.vx = 0; n.vy = 0; continue; }
    n.vx *= damping;
    n.vy *= damping;
    n.x += n.vx * alpha;
    n.y += n.vy * alpha;
  }
}

// ── Draw ──
function worldToScreen(x, y) {
  return {
    x: (x + transform.x) * transform.scale + W() / 2 - CX() * transform.scale,
    y: (y + transform.y) * transform.scale + H() / 2 - CY() * transform.scale
  };
}
function screenToWorld(x, y) {
  return {
    x: (x - W() / 2 + CX() * transform.scale) / transform.scale - transform.x,
    y: (y - H() / 2 + CY() * transform.scale) / transform.scale - transform.y
  };
}

function isHighlighted(n) {
  if (!searchFilter) return true;
  const q = searchFilter.toLowerCase();
  return (
    n.id.includes(q) || n.label.toLowerCase().includes(q) ||
    n.type.includes(q) || (n.tags || []).some(t => t.toLowerCase().includes(q))
  );
}

function draw() {
  ctx.clearRect(0, 0, W(), H());
  ctx.fillStyle = '#1a1a2e';
  ctx.fillRect(0, 0, W(), H());

  const allEdges = [...edges, ...(showParentEdges ? parentEdges : [])];

  // Draw edges
  for (const e of allEdges) {
    const a = nodeById[e.from], b = nodeById[e.to];
    if (!a || !b) continue;
    const pa = worldToScreen(a.x, a.y);
    const pb = worldToScreen(b.x, b.y);
    const hiA = isHighlighted(a), hiB = isHighlighted(b);
    ctx.save();
    ctx.globalAlpha = (searchFilter && !hiA && !hiB) ? 0.08 : (e.virtual ? 0.6 : 0.5);
    ctx.strokeStyle = e.virtual ? '#5b9bd5' : '#e94560';
    ctx.lineWidth = e.virtual ? 1.5 : 1.5;
    if (e.virtual) ctx.setLineDash([6, 3]);
    ctx.beginPath();
    ctx.moveTo(pa.x, pa.y);
    ctx.lineTo(pb.x, pb.y);
    ctx.stroke();
    ctx.setLineDash([]);
    // Edge label
    if (showLabels && !e.virtual && transform.scale > 0.6) {
      const mx = (pa.x + pb.x) / 2, my = (pa.y + pb.y) / 2;
      ctx.globalAlpha = (searchFilter && !hiA && !hiB) ? 0.1 : 0.7;
      ctx.fillStyle = '#aaa';
      ctx.font = \`\${Math.max(9, 10 * transform.scale)}px sans-serif\`;
      ctx.textAlign = 'center';
      ctx.fillText(e.rel, mx, my - 4);
    }
    // Arrowhead
    {
      const angle = Math.atan2(pb.y - pa.y, pb.x - pa.x);
      const ar = b.size * transform.scale;
      const ax = pb.x - Math.cos(angle) * ar;
      const ay = pb.y - Math.sin(angle) * ar;
      ctx.globalAlpha = (searchFilter && !hiA && !hiB) ? 0.08 : (e.virtual ? 0.6 : 0.5);
      ctx.fillStyle = e.virtual ? '#5b9bd5' : '#e94560';
      ctx.beginPath();
      ctx.moveTo(ax, ay);
      ctx.lineTo(ax - Math.cos(angle - 0.4) * 10, ay - Math.sin(angle - 0.4) * 10);
      ctx.lineTo(ax - Math.cos(angle + 0.4) * 10, ay - Math.sin(angle + 0.4) * 10);
      ctx.closePath();
      ctx.fill();
    }
    ctx.restore();
  }

  // Draw nodes
  for (const n of nodes) {
    const p = worldToScreen(n.x, n.y);
    const r = n.size * transform.scale;
    const hi = isHighlighted(n);
    ctx.save();
    ctx.globalAlpha = searchFilter ? (hi ? 1 : 0.15) : 1;

    // Glow for selected
    if (n.id === selectedId) {
      ctx.shadowBlur = 20;
      ctx.shadowColor = '#fff';
    }

    // Circle
    ctx.beginPath();
    ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
    ctx.fillStyle = n.color;
    ctx.fill();
    ctx.strokeStyle = n.id === selectedId ? '#fff' : 'rgba(255,255,255,0.2)';
    ctx.lineWidth = n.id === selectedId ? 2 : 1;
    ctx.stroke();

    // Confidence ring if low
    if (n.confidence !== undefined && n.confidence < 0.7) {
      ctx.beginPath();
      ctx.arc(p.x, p.y, r + 3, 0, Math.PI * 2 * n.confidence);
      ctx.strokeStyle = n.confidence < 0.5 ? '#f44336' : '#ff9800';
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    // Label
    if (showLabels && (transform.scale > 0.5 || n.id === selectedId)) {
      ctx.shadowBlur = 0;
      ctx.font = \`\${Math.max(9, Math.round(11 * transform.scale))}px sans-serif\`;
      ctx.textAlign = 'center';
      ctx.fillStyle = '#fff';
      ctx.fillText(n.label, p.x, p.y + r + Math.max(11, 14 * transform.scale));
    }

    ctx.restore();
  }
}

// ── Animation loop ──
let simSteps = 0;
const MAX_SIM = VIZ_CONFIG.simulationSteps;

function loop() {
  if (running && simSteps < MAX_SIM) {
    simulate();
    simSteps++;
  }
  draw();
  animFrame = requestAnimationFrame(loop);
}
loop();

// ── Interaction ──
function getNodeAt(sx, sy) {
  const w = screenToWorld(sx, sy);
  let best = null, bestDist = Infinity;
  for (const n of nodes) {
    const dx = n.x - w.x, dy = n.y - w.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist < n.size / transform.scale + 10 && dist < bestDist) {
      best = n; bestDist = dist;
    }
  }
  return best;
}

// Mouse events — NO node dragging, only pan + click
let mouseDownPos = null;

canvas.addEventListener('mousedown', e => {
  mouseDownPos = { x: e.clientX, y: e.clientY };
  panStart = { mx: e.clientX, my: e.clientY, tx: transform.x, ty: transform.y };
  canvas.classList.add('dragging');
});

canvas.addEventListener('mousemove', e => {
  const cy = e.clientY - 48;
  if (panStart) {
    transform.x = panStart.tx + (e.clientX - panStart.mx) / transform.scale;
    transform.y = panStart.ty + (e.clientY - panStart.my) / transform.scale;
  } else {
    // Tooltip
    const n = getNodeAt(e.clientX, cy);
    const tip = document.getElementById('tooltip');
    if (n) {
      tip.style.display = 'block';
      tip.style.left = (e.clientX + 12) + 'px';
      tip.style.top = (e.clientY + 12) + 'px';
      const conf = n.confidence !== undefined ? \` | conf:\${n.confidence.toFixed(2)}\` : '';
      tip.textContent = \`\${n.label} (\${n.type})\${conf} — \${n.connections} connections\`;
    } else {
      tip.style.display = 'none';
    }
  }
});

canvas.addEventListener('mouseup', e => {
  // Detect click (tiny move) vs drag
  if (mouseDownPos) {
    const dx = e.clientX - mouseDownPos.x;
    const dy = e.clientY - mouseDownPos.y;
    if (Math.abs(dx) < 5 && Math.abs(dy) < 5) {
      const n = getNodeAt(e.clientX, e.clientY - 48);
      if (n) {
        openSidebar(n);
      } else {
        selectedId = null;
        closeSidebar();
      }
    }
  }
  panStart = null;
  mouseDownPos = null;
  canvas.classList.remove('dragging');
});

// Wheel zoom — zoom toward cursor position
canvas.addEventListener('wheel', e => {
  e.preventDefault();
  const factor = e.deltaY > 0 ? 0.9 : 1.1;
  const newScale = Math.max(0.1, Math.min(8, transform.scale * factor));
  // Zoom toward mouse position
  const rect = canvas.getBoundingClientRect();
  const mx = e.clientX - rect.left;
  const my = e.clientY - rect.top;
  const wx = (mx - W() / 2 + CX() * transform.scale) / transform.scale - transform.x;
  const wy = (my - H() / 2 + CY() * transform.scale) / transform.scale - transform.y;
  transform.scale = newScale;
  transform.x = (mx - W() / 2 + CX() * newScale) / newScale - wx;
  transform.y = (my - H() / 2 + CY() * newScale) / newScale - wy;
}, { passive: false });

// Touch support — pan (1 finger), pinch-to-zoom (2 fingers), tap to select
let lastPinchDist = null;
let lastPinchCenter = null;

function getTouchDist(t1, t2) {
  const dx = t2.clientX - t1.clientX;
  const dy = t2.clientY - t1.clientY;
  return Math.sqrt(dx * dx + dy * dy);
}

canvas.addEventListener('touchstart', e => {
  if (e.touches.length === 1) {
    const t = e.touches[0];
    mouseDownPos = { x: t.clientX, y: t.clientY };
    panStart = { mx: t.clientX, my: t.clientY, tx: transform.x, ty: transform.y };
    lastPinchDist = null;
  } else if (e.touches.length === 2) {
    // Start pinch
    panStart = null;
    lastPinchDist = getTouchDist(e.touches[0], e.touches[1]);
    lastPinchCenter = {
      x: (e.touches[0].clientX + e.touches[1].clientX) / 2,
      y: (e.touches[0].clientY + e.touches[1].clientY) / 2
    };
  }
});

canvas.addEventListener('touchmove', e => {
  e.preventDefault();
  if (e.touches.length === 2 && lastPinchDist !== null) {
    // Pinch-to-zoom
    const newDist = getTouchDist(e.touches[0], e.touches[1]);
    const factor = newDist / lastPinchDist;
    const newScale = Math.max(0.1, Math.min(8, transform.scale * factor));
    // Zoom toward pinch center
    const cx = (e.touches[0].clientX + e.touches[1].clientX) / 2;
    const cy = (e.touches[0].clientY + e.touches[1].clientY) / 2;
    const rect = canvas.getBoundingClientRect();
    const mx = cx - rect.left;
    const my = cy - rect.top - 48;
    const wx = (mx - W() / 2 + CX() * transform.scale) / transform.scale - transform.x;
    const wy = (my - H() / 2 + CY() * transform.scale) / transform.scale - transform.y;
    transform.scale = newScale;
    transform.x = (mx - W() / 2 + CX() * newScale) / newScale - wx;
    transform.y = (my - H() / 2 + CY() * newScale) / newScale - wy;
    lastPinchDist = newDist;
    lastPinchCenter = { x: cx, y: cy };
  } else if (e.touches.length === 1 && panStart) {
    const t = e.touches[0];
    transform.x = panStart.tx + (t.clientX - panStart.mx) / transform.scale;
    transform.y = panStart.ty + (t.clientY - panStart.my) / transform.scale;
  }
}, { passive: false });

canvas.addEventListener('touchend', e => {
  if (e.touches.length === 0) {
    // Check if it was a tap
    if (mouseDownPos && panStart) {
      // Estimate if it was a tap (no significant movement)
      const n = getNodeAt(mouseDownPos.x, mouseDownPos.y - 48);
      if (n) openSidebar(n);
    }
    panStart = null;
    mouseDownPos = null;
    lastPinchDist = null;
    lastPinchCenter = null;
  } else if (e.touches.length === 1) {
    // Went from 2 fingers back to 1 — reset pan
    lastPinchDist = null;
    const t = e.touches[0];
    panStart = { mx: t.clientX, my: t.clientY, tx: transform.x, ty: transform.y };
  }
});

// ── Sidebar ──
function openSidebar(n) {
  selectedId = n.id;
  const sidebar = document.getElementById('sidebar');
  const content = document.getElementById('sidebar-content');
  const toolbar = document.getElementById('toolbar');

  // Build sidebar content
  let html = \`<div class="node-label">\${n.label}</div>\`;
  html += \`<div class="node-type">\${n.alias} · \${n.type}</div>\`;

  if (n.confidence !== undefined) {
    const cls = n.confidence >= 0.7 ? 'conf-high' : n.confidence >= 0.5 ? 'conf-med' : 'conf-low';
    html += \`<div class="confidence \${cls}">confidence: \${(n.confidence * 100).toFixed(0)}%</div>\`;
  }

  if (n.tags && n.tags.length) {
    html += \`<div class="section"><h3>Tags</h3>\`;
    html += n.tags.map(t => \`<span class="tag">\${t}</span>\`).join('');
    html += \`</div>\`;
  }

  const attrEntries = Object.entries(n.attrs || {}).filter(([k]) => !k.startsWith('vault'));
  if (attrEntries.length) {
    html += \`<div class="section"><h3>Attributes</h3><div class="attr">\`;
    for (const [k, v] of attrEntries) {
      html += \`<span>\${k}:</span> \${v}<br>\`;
    }
    html += \`</div></div>\`;
  }

  // Relations — clickable links
  const rels = DATA.edges.filter(e => e.from === n.id || e.to === n.id);
  if (rels.length) {
    html += \`<div class="section"><h3>Relations</h3>\`;
    for (const e of rels) {
      const dir = e.from === n.id ? '→' : '←';
      const other = e.from === n.id ? e.to : e.from;
      const otherNode = nodeById[other];
      const otherLabel = otherNode ? otherNode.label : other;
      html += \`<div class="rel-item">\${dir} <strong>\${e.rel}</strong> <a href="#" class="node-link" data-id="\${other}">\${otherLabel}</a></div>\`;
    }
    html += \`</div>\`;
  }

  // Parent/children — clickable links
  if (n.parent) {
    const p = nodeById[n.parent];
    html += \`<div class="section"><h3>Parent</h3><div class="rel-item">↑ <a href="#" class="node-link" data-id="\${n.parent}">\${p ? p.label : n.parent}</a></div></div>\`;
  }
  const children = nodes.filter(c => c.parent === n.id);
  if (children.length) {
    html += \`<div class="section"><h3>Children (\${children.length})</h3>\`;
    for (const c of children) html += \`<div class="rel-item">↓ <a href="#" class="node-link" data-id="\${c.id}">\${c.label}</a> <span style="color:#888">(\${c.type})</span></div>\`;
    html += \`</div>\`;
  }

  html += \`<div class="section"><h3>Dates</h3><div class="attr">
    <span>created:</span> \${n.created}<br>
    <span>updated:</span> \${n.updated}
  </div></div>\`;

  content.innerHTML = html;
  sidebar.classList.add('open');
  toolbar.classList.remove('no-sidebar');
  wrap.classList.add('sidebar-open');
  resize();

  // Bind click handlers for node links in sidebar
  content.querySelectorAll('.node-link').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const targetId = link.dataset.id;
      const targetNode = nodeById[targetId];
      if (targetNode) navigateToNode(targetNode);
    });
  });
}

// Navigate to a node: animated pan + zoom to center it on screen
function navigateToNode(n) {
  // First open sidebar so canvas resizes, then animate to center
  selectedId = n.id;
  const sidebar = document.getElementById('sidebar');
  const isSidebarOpen = sidebar.classList.contains('open');

  // Open sidebar first to get correct canvas dimensions
  if (!isSidebarOpen) {
    sidebar.classList.add('open');
    document.getElementById('toolbar').classList.remove('no-sidebar');
    wrap.classList.add('sidebar-open');
    resize();
  }

  // Target: center node on visible canvas area, zoom to 1.5x
  const targetScale = Math.max(1.5, transform.scale);
  // To center node (n.x, n.y) on screen:
  // worldToScreen(n.x, n.y) should equal (W()/2, H()/2)
  // (n.x + tx) * s + W/2 - CX*s = W/2  →  tx = CX - n.x  (when simplified with CX = W/2)
  // Actually: (n.x + tx) * s + W/2 - (W/2)*s = W/2
  //           (n.x + tx) * s = W/2 * s
  //           n.x + tx = W/2
  //           tx = W/2 - n.x  ... but W/2 = CX()
  // Wait, CX() returns W()/2 which is the canvas center in world-ish coords.
  // Let's just compute directly:
  // We want worldToScreen(n.x, n.y) = (W()/2, H()/2)
  // worldToScreen: sx = (x + tx) * scale + W/2 - CX*scale
  //              = (x + tx) * scale + W/2 - W/2 * scale
  // Want sx = W/2:
  //   (n.x + tx) * scale + W/2 - W/2*scale = W/2
  //   (n.x + tx) * scale = W/2 * scale
  //   n.x + tx = W/2
  //   tx = W/2 - n.x
  // Similarly ty = H/2 - n.y ... but H needs the toolbar offset accounted for?
  // Actually CX() = W()/2 and the formula simplifies:
  // tx = CX() - n.x, ty = CY() - n.y  (this centers the node)

  const targetTx = CX() - n.x;
  const targetTy = CY() - n.y;

  // Animate smoothly
  const startTx = transform.x;
  const startTy = transform.y;
  const startScale = transform.scale;
  const duration = VIZ_CONFIG.zoomAnimationMs;
  const startTime = performance.now();

  function easeInOut(t) { return t < 0.5 ? 2*t*t : -1+(4-2*t)*t; }

  function animateStep(now) {
    const elapsed = now - startTime;
    const t = Math.min(1, elapsed / duration);
    const e = easeInOut(t);

    transform.x = startTx + (targetTx - startTx) * e;
    transform.y = startTy + (targetTy - startTy) * e;
    transform.scale = startScale + (targetScale - startScale) * e;

    if (t < 1) {
      requestAnimationFrame(animateStep);
    } else {
      // Animation done, now build sidebar content
      openSidebar(n);
    }
  }
  requestAnimationFrame(animateStep);
}

function closeSidebar() {
  selectedId = null;
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('toolbar').classList.add('no-sidebar');
  wrap.classList.remove('sidebar-open');
  resize();
}

// ── Controls ──
function zoomBy(factor) {
  // Zoom toward center of visible canvas
  const newScale = Math.max(0.1, Math.min(8, transform.scale * factor));
  const cx = W() / 2;
  const cy = H() / 2;
  const wx = (cx - W() / 2 + CX() * transform.scale) / transform.scale - transform.x;
  const wy = (cy - H() / 2 + CY() * transform.scale) / transform.scale - transform.y;
  transform.scale = newScale;
  transform.x = (cx - W() / 2 + CX() * newScale) / newScale - wx;
  transform.y = (cy - H() / 2 + CY() * newScale) / newScale - wy;
}

function zoomIn() { zoomBy(1.3); }
function zoomOut() { zoomBy(0.7); }

function resetView() {
  transform = { x: 0, y: 0, scale: 1 };
  initPositions();
  simSteps = 0;
}

function toggleParentEdges() {
  showParentEdges = !showParentEdges;
}

function toggleLabels() {
  showLabels = !showLabels;
}

// Search
document.getElementById('search-box').addEventListener('input', e => {
  searchFilter = e.target.value.trim();
});

// ── Legend ──
function buildLegend() {
  const types = [...new Set(nodes.map(n => n.type))].sort();
  const colors = {
    human:'#4A90D9', ai:'#9B59B6', device:'#27AE60', platform:'#E67E22',
    project:'#E74C3C', decision:'#F39C12', concept:'#1ABC9C', skill:'#3498DB',
    network:'#2ECC71', credential:'#C0392B', org:'#8E44AD', service:'#16A085',
    runtime:'#D35400', agent:'#7F8C8D', entity:'#95A5A6'
  };
  const container = document.getElementById('legend-items');
  for (const t of types) {
    const div = document.createElement('div');
    div.className = 'leg-item';
    div.innerHTML = \`<div class="leg-dot" style="background:\${colors[t]||'#95A5A6'}"></div>\${t}\`;
    container.appendChild(div);
  }
}
buildLegend();

// ── Stats ──
document.getElementById('stats-label').textContent =
  \`\${DATA.meta.entityCount} entities · \${DATA.meta.edgeCount} edges · depth:\${DATA.meta.maxDepth}\`;
</script>
</body>
</html>`;

writeFileSync(outputPath, html);
console.log(`✅ Graph visualization written to: ${outputPath}`);
console.log(`   Nodes: ${nodes.length} | Edges: ${edges.length} | Parent links: ${graphData.parentEdges.length}`);
