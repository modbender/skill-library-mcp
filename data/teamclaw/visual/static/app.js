/**
 * Visual Agent Orchestration System - Core Application Logic
 * Handles canvas node management, drag & drop, connections, grouping,
 * and YAML generation.
 */

// ── Application State ──
const state = {
    experts: [],          // Available expert pool
    nodes: [],            // Canvas nodes: { id, name, tag, emoji, x, y, type, temperature, author, content }
    edges: [],            // Directed edges: { id, source, target }
    groups: [],           // Group zones: { id, name, type, x, y, w, h, nodeIds }
    selectedNodes: new Set(),
    nextNodeId: 1,
    nextEdgeId: 1,
    nextGroupId: 1,
    settings: {
        repeat: true,
        max_rounds: 5,
        use_bot_session: false,
        cluster_threshold: 150,
    },
    // Interaction state
    dragging: null,       // { nodeId, offsetX, offsetY } | { type: 'canvas', startX, startY }
    connecting: null,     // { sourceId, startX, startY }
    selecting: null,      // { startX, startY }
    contextMenu: null,
    panOffset: { x: 0, y: 0 },
};

// ── Initialization ──
document.addEventListener('DOMContentLoaded', async () => {
    await loadExperts();
    renderSidebar();
    setupCanvasEvents();
    setupTopBarEvents();
    setupSettingsEvents();
    updateYamlOutput();
});

async function loadExperts() {
    try {
        const resp = await fetch('/api/experts');
        state.experts = await resp.json();
    } catch (e) {
        console.error('Failed to load experts:', e);
    }
}

// ── Sidebar Rendering ──
function renderSidebar() {
    const list = document.getElementById('expert-list');
    list.innerHTML = '';

    state.experts.forEach(expert => {
        const card = document.createElement('div');
        card.className = 'expert-card';
        card.draggable = true;
        card.dataset.tag = expert.tag;
        card.innerHTML = `
            <span class="emoji">${expert.emoji}</span>
            <div class="info">
                <div class="name">${expert.name}</div>
                <div class="tag">${expert.tag}</div>
            </div>
            <span class="temp">${expert.temperature}</span>
        `;
        card.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('application/json', JSON.stringify({
                type: 'expert',
                ...expert
            }));
            e.dataTransfer.effectAllowed = 'copy';
        });
        // Double-click to quick-add to canvas center
        card.addEventListener('dblclick', () => {
            addNodeToCenter({ type: 'expert', ...expert });
        });
        list.appendChild(card);
    });
}

// ── Canvas Node Management ──
function addNodeToCanvas(data, x, y) {
    const id = 'n' + state.nextNodeId++;
    const node = {
        id,
        name: data.name,
        tag: data.tag || 'custom',
        emoji: data.emoji || '⭐',
        x: Math.round(x),
        y: Math.round(y),
        type: data.type || 'expert',
        temperature: data.temperature || 0.5,
        author: data.author || '主持人',
        content: data.content || '',
    };
    state.nodes.push(node);
    renderNode(node);
    updateYamlOutput();
    updateStatusBar();
    return node;
}

/**
 * Add a node to the center of the canvas with smart offset to avoid overlapping.
 * Nodes are placed in a spiral pattern around the center.
 */
function addNodeToCenter(data) {
    const area = document.getElementById('canvas-area');
    const areaW = area.offsetWidth;
    const areaH = area.offsetHeight;
    const centerX = areaW / 2 - 60;
    const centerY = areaH / 2 - 20;

    // Smart offset: spiral outward based on existing node count
    const existingCount = state.nodes.length;
    const spiralStep = 80; // pixels between spiral rings
    const angleStep = 137.5 * (Math.PI / 180); // golden angle for nice distribution
    const angle = existingCount * angleStep;
    const radius = spiralStep * Math.sqrt(existingCount) * 0.5;

    const x = centerX + radius * Math.cos(angle);
    const y = centerY + radius * Math.sin(angle);

    return addNodeToCanvas(data, x, y);
}

function renderNode(node) {
    const area = document.getElementById('canvas-area');
    const el = document.createElement('div');
    el.className = 'canvas-node' + (node.type === 'manual' ? ' manual-node' : '');
    el.id = 'node-' + node.id;
    el.style.left = node.x + 'px';
    el.style.top = node.y + 'px';

    el.innerHTML = `
        <span class="node-emoji">${node.emoji}</span>
        <div class="node-info">
            <div class="node-name">${node.name}</div>
            <div class="node-tag">${node.tag}</div>
        </div>
        <div class="node-delete" title="Remove">×</div>
        <div class="port port-in" data-node="${node.id}" data-dir="in"></div>
        <div class="port port-out" data-node="${node.id}" data-dir="out"></div>
    `;

    // Delete button
    el.querySelector('.node-delete').addEventListener('click', (e) => {
        e.stopPropagation();
        removeNode(node.id);
    });

    // Node drag
    el.addEventListener('mousedown', (e) => {
        if (e.target.classList.contains('port')) return;
        if (e.target.classList.contains('node-delete')) return;
        e.stopPropagation();

        // Select logic
        if (!e.shiftKey && !state.selectedNodes.has(node.id)) {
            clearSelection();
        }
        selectNode(node.id);

        state.dragging = {
            nodeId: node.id,
            offsetX: e.clientX - node.x,
            offsetY: e.clientY - node.y,
            multiDrag: state.selectedNodes.size > 1,
            startPositions: {},
        };

        // Store start positions for multi-drag
        if (state.selectedNodes.size > 1) {
            state.selectedNodes.forEach(nid => {
                const n = state.nodes.find(nn => nn.id === nid);
                if (n) state.dragging.startPositions[nid] = { x: n.x, y: n.y };
            });
        }
    });

    // Connection ports
    el.querySelectorAll('.port').forEach(port => {
        port.addEventListener('mousedown', (e) => {
            e.stopPropagation();
            if (port.dataset.dir === 'out') {
                const rect = port.getBoundingClientRect();
                const canvasRect = document.getElementById('canvas-area').getBoundingClientRect();
                state.connecting = {
                    sourceId: node.id,
                    startX: rect.left + 6 - canvasRect.left,
                    startY: rect.top + 6 - canvasRect.top,
                };
            }
        });

        port.addEventListener('mouseup', (e) => {
            e.stopPropagation();
            if (state.connecting && port.dataset.dir === 'in' && port.dataset.node !== state.connecting.sourceId) {
                addEdge(state.connecting.sourceId, node.id);
            }
            state.connecting = null;
            removeTempLine();
        });
    });

    // Double-click to edit (for manual nodes)
    el.addEventListener('dblclick', () => {
        if (node.type === 'manual') {
            showManualEditModal(node);
        }
    });

    area.appendChild(el);
}

function removeNode(nodeId) {
    state.nodes = state.nodes.filter(n => n.id !== nodeId);
    state.edges = state.edges.filter(e => e.source !== nodeId && e.target !== nodeId);
    state.selectedNodes.delete(nodeId);

    // Remove from groups
    state.groups.forEach(g => {
        g.nodeIds = g.nodeIds.filter(id => id !== nodeId);
    });

    const el = document.getElementById('node-' + nodeId);
    if (el) el.remove();

    renderAllEdges();
    updateYamlOutput();
    updateStatusBar();
}

function selectNode(nodeId) {
    state.selectedNodes.add(nodeId);
    const el = document.getElementById('node-' + nodeId);
    if (el) el.classList.add('selected');
}

function clearSelection() {
    state.selectedNodes.forEach(nid => {
        const el = document.getElementById('node-' + nid);
        if (el) el.classList.remove('selected');
    });
    state.selectedNodes.clear();
}

// ── Edge Management ──
function addEdge(sourceId, targetId) {
    // Prevent duplicate
    if (state.edges.some(e => e.source === sourceId && e.target === targetId)) return;
    const id = 'e' + state.nextEdgeId++;
    state.edges.push({ id, source: sourceId, target: targetId });
    renderAllEdges();
    updateYamlOutput();
}

function removeEdge(edgeId) {
    state.edges = state.edges.filter(e => e.id !== edgeId);
    renderAllEdges();
    updateYamlOutput();
}

function renderAllEdges() {
    const svg = document.getElementById('edge-svg');
    // Keep only the defs and temp-line
    const defs = svg.querySelector('defs');
    svg.innerHTML = '';
    if (defs) svg.appendChild(defs);
    else {
        const newDefs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        newDefs.innerHTML = `
            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="#667eea" />
            </marker>
        `;
        svg.appendChild(newDefs);
    }

    state.edges.forEach(edge => {
        const srcNode = state.nodes.find(n => n.id === edge.source);
        const tgtNode = state.nodes.find(n => n.id === edge.target);
        if (!srcNode || !tgtNode) return;

        const srcEl = document.getElementById('node-' + edge.source);
        const tgtEl = document.getElementById('node-' + edge.target);
        if (!srcEl || !tgtEl) return;

        const x1 = srcNode.x + srcEl.offsetWidth;
        const y1 = srcNode.y + srcEl.offsetHeight / 2;
        const x2 = tgtNode.x;
        const y2 = tgtNode.y + tgtEl.offsetHeight / 2;

        // Bezier curve
        const cpx = (x1 + x2) / 2;
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        line.setAttribute('d', `M${x1},${y1} C${cpx},${y1} ${cpx},${y2} ${x2},${y2}`);
        line.setAttribute('stroke', '#667eea');
        line.setAttribute('stroke-width', '2');
        line.setAttribute('fill', 'none');
        line.setAttribute('marker-end', 'url(#arrowhead)');
        line.setAttribute('data-edge-id', edge.id);
        line.style.cursor = 'pointer';
        line.style.pointerEvents = 'all';

        // Click to delete edge
        line.addEventListener('click', (e) => {
            e.stopPropagation();
            removeEdge(edge.id);
        });

        // Hover effect
        line.addEventListener('mouseenter', () => { line.setAttribute('stroke', '#ff6b6b'); line.setAttribute('stroke-width', '3'); });
        line.addEventListener('mouseleave', () => { line.setAttribute('stroke', '#667eea'); line.setAttribute('stroke-width', '2'); });

        svg.appendChild(line);
    });
}

function removeTempLine() {
    const svg = document.getElementById('edge-svg');
    const temp = svg.querySelector('.temp-line');
    if (temp) temp.remove();
}

function drawTempLine(x1, y1, x2, y2) {
    const svg = document.getElementById('edge-svg');
    removeTempLine();
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.classList.add('temp-line');
    line.setAttribute('x1', x1);
    line.setAttribute('y1', y1);
    line.setAttribute('x2', x2);
    line.setAttribute('y2', y2);
    line.setAttribute('stroke', '#667eea80');
    line.setAttribute('stroke-width', '2');
    line.setAttribute('stroke-dasharray', '5,5');
    svg.appendChild(line);
}

// ── Group Management ──
function createGroup(type, x, y, w, h, nodeIds) {
    const id = 'g' + state.nextGroupId++;
    const labelMap = { parallel: '🔀 Parallel', all: '👥 All Experts', manual: '📝 Manual' };
    const group = {
        id,
        name: labelMap[type] || type,
        type,
        x, y, w, h,
        nodeIds: [...nodeIds],
    };
    state.groups.push(group);
    renderGroup(group);
    updateYamlOutput();
    return group;
}

function renderGroup(group) {
    const area = document.getElementById('canvas-area');
    const el = document.createElement('div');
    el.className = 'group-zone ' + group.type;
    el.id = 'group-' + group.id;
    el.style.left = group.x + 'px';
    el.style.top = group.y + 'px';
    el.style.width = group.w + 'px';
    el.style.height = group.h + 'px';

    el.innerHTML = `
        <span class="group-label">${group.name}</span>
        <div class="group-delete" title="Dissolve group">×</div>
    `;

    el.querySelector('.group-delete').addEventListener('click', (e) => {
        e.stopPropagation();
        removeGroup(group.id);
    });

    area.appendChild(el);
}

function removeGroup(groupId) {
    state.groups = state.groups.filter(g => g.id !== groupId);
    const el = document.getElementById('group-' + groupId);
    if (el) el.remove();
    updateYamlOutput();
}

function updateGroupBounds(group) {
    // Recalculate group bounds from member nodes
    const members = state.nodes.filter(n => group.nodeIds.includes(n.id));
    if (members.length === 0) return;

    const padding = 30;
    const minX = Math.min(...members.map(n => n.x)) - padding;
    const minY = Math.min(...members.map(n => n.y)) - padding;
    const maxX = Math.max(...members.map(n => {
        const el = document.getElementById('node-' + n.id);
        return n.x + (el ? el.offsetWidth : 120);
    })) + padding;
    const maxY = Math.max(...members.map(n => {
        const el = document.getElementById('node-' + n.id);
        return n.y + (el ? el.offsetHeight : 50);
    })) + padding;

    group.x = minX;
    group.y = minY;
    group.w = maxX - minX;
    group.h = maxY - minY;

    const el = document.getElementById('group-' + group.id);
    if (el) {
        el.style.left = group.x + 'px';
        el.style.top = group.y + 'px';
        el.style.width = group.w + 'px';
        el.style.height = group.h + 'px';
    }
}
