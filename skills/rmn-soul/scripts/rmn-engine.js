/**
 * RMN Soul — Recursive Memory Network Engine v2.0
 * 
 * Improved from v0.1: better layer assignment, auto-compression,
 * semantic similarity, and sponsor wallet support.
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

class RecursiveMemoryNetwork {
  constructor(dbPath) {
    this.dbPath = dbPath;
    this.nodes = new Map();
    this.load();
  }

  load() {
    try {
      const data = JSON.parse(fs.readFileSync(this.dbPath, 'utf-8'));
      for (const node of data.nodes || []) this.nodes.set(node.id, node);
    } catch { /* fresh start */ }
  }

  save() {
    const data = { version: '2.0.0', savedAt: new Date().toISOString(), nodes: Array.from(this.nodes.values()) };
    fs.mkdirSync(path.dirname(this.dbPath), { recursive: true });
    fs.writeFileSync(this.dbPath, JSON.stringify(data, null, 2));
  }

  // Inscribe a new memory node
  inscribe(content, tags = '', layer = null) {
    if (!content || !content.trim()) return null;
    const id = `mem_${Date.now()}_${crypto.randomBytes(3).toString('hex')}`;
    const hash = crypto.createHash('sha256').update(content).digest('hex').slice(0, 16);
    
    // Auto-detect layer if not specified
    if (layer === null) layer = this._detectLayer(content, tags);
    
    const node = {
      id, hash, content: content.trim(),
      layer: Math.max(0, Math.min(4, layer)),
      tags: tags ? tags.split(',').map(t => t.trim()).filter(Boolean) : [],
      refs: [], weight: 1.0,
      createdAt: Date.now(), accessedAt: Date.now(), accessCount: 1,
    };
    
    // Auto-link to related nodes
    this._autoLink(node);
    this.nodes.set(id, node);
    this.save();
    return node;
  }

  // Intelligent layer detection
  _detectLayer(content, tags) {
    const lower = content.toLowerCase();
    const tagStr = tags.toLowerCase();
    
    // Identity markers
    if (tagStr.includes('identity') || tagStr.includes('soul') || tagStr.includes('core') ||
        /^(我是|i am|my name|核心|原则|价值观|mission|purpose)/i.test(lower)) return 4;
    
    // Semantic markers (knowledge, lessons, rules)
    if (tagStr.includes('lesson') || tagStr.includes('rule') || tagStr.includes('knowledge') ||
        /^(教训|规则|注意|记住|always|never|important|关键)/i.test(lower) ||
        /(因为|所以|应该|不要|must|should|avoid)/i.test(lower)) return 3;
    
    // Episodic markers (events, summaries)
    if (tagStr.includes('event') || tagStr.includes('milestone') || tagStr.includes('summary') ||
        /^\d{4}[-/]\d{2}/.test(lower) || /(完成|deployed|launched|finished|发布)/i.test(lower)) return 2;
    
    // Working markers (tasks, current)
    if (tagStr.includes('task') || tagStr.includes('todo') || tagStr.includes('wip') ||
        /(正在|当前|todo|in progress|working on)/i.test(lower)) return 1;
    
    // Default: working memory
    return 1;
  }

  // Auto-link to semantically related nodes
  _autoLink(newNode) {
    const newWords = new Set(newNode.content.toLowerCase().split(/\s+/));
    const newTags = new Set(newNode.tags);
    
    for (const [id, node] of this.nodes) {
      if (id === newNode.id) continue;
      
      // Tag overlap
      const tagOverlap = node.tags.filter(t => newTags.has(t)).length;
      if (tagOverlap >= 2) {
        newNode.refs.push(id);
        continue;
      }
      
      // Word overlap (simple similarity)
      const nodeWords = new Set(node.content.toLowerCase().split(/\s+/));
      const overlap = [...newWords].filter(w => nodeWords.has(w) && w.length > 3).length;
      if (overlap >= 5) {
        newNode.refs.push(id);
      }
    }
    
    // Limit refs
    newNode.refs = newNode.refs.slice(0, 10);
  }

  // Recall by keyword search
  recall(query, limit = 5) {
    const queryWords = new Set(query.toLowerCase().split(/\s+/));
    const scored = [];
    
    for (const node of this.nodes.values()) {
      let score = 0;
      const content = node.content.toLowerCase();
      
      for (const word of queryWords) {
        if (content.includes(word)) score += 2;
        if (node.tags.some(t => t.includes(word))) score += 3;
      }
      
      // Boost by weight and layer
      score *= node.weight * (1 + node.layer * 0.2);
      
      if (score > 0) {
        // LTP: access strengthens
        node.accessedAt = Date.now();
        node.accessCount++;
        node.weight = Math.min(2.0, node.weight + 0.05);
        scored.push({ node, score });
      }
    }
    
    scored.sort((a, b) => b.score - a.score);
    if (scored.length > 0) this.save();
    return scored.slice(0, limit).map(s => s.node);
  }

  // Expand: follow refs recursively
  expand(nodeId, depth = 2) {
    const visited = new Set();
    const result = [];
    
    const walk = (id, d) => {
      if (d > depth || visited.has(id)) return;
      visited.add(id);
      const node = this.nodes.get(id);
      if (!node) return;
      result.push({ ...node, depth: d });
      for (const ref of node.refs) walk(ref, d + 1);
    };
    
    walk(nodeId, 0);
    return result;
  }

  // Decay tick: reduce weights, prune dead nodes
  decayTick() {
    const decayRates = [0.02, 0.01, 0.005, 0.001, 0]; // sensory → identity
    let pruned = 0;
    
    for (const [id, node] of this.nodes) {
      const rate = decayRates[node.layer] || 0.01;
      node.weight = Math.max(0, node.weight - rate);
      
      // Prune if weight too low (never prune identity)
      if (node.weight <= 0.05 && node.layer < 4) {
        this.nodes.delete(id);
        pruned++;
      }
    }
    
    this.save();
    return { pruned, remaining: this.nodes.size };
  }

  // Auto-compress: merge similar nodes in same layer
  compress(layer = 2) {
    const layerNodes = Array.from(this.nodes.values())
      .filter(n => n.layer === layer)
      .sort((a, b) => a.createdAt - b.createdAt);
    
    if (layerNodes.length < 5) return null;
    
    // Group by tag similarity
    const groups = [];
    const used = new Set();
    
    for (const node of layerNodes) {
      if (used.has(node.id)) continue;
      const group = [node];
      used.add(node.id);
      
      for (const other of layerNodes) {
        if (used.has(other.id)) continue;
        const tagOverlap = node.tags.filter(t => other.tags.includes(t)).length;
        if (tagOverlap >= 1) {
          group.push(other);
          used.add(other.id);
        }
      }
      
      if (group.length >= 2) groups.push(group);
    }
    
    // Compress each group into a summary node
    const compressed = [];
    for (const group of groups) {
      const allContent = group.map(n => n.content).join(' | ');
      const allTags = [...new Set(group.flatMap(n => n.tags))];
      const allRefs = [...new Set(group.flatMap(n => n.refs))];
      const summary = `[Compressed ${group.length} nodes] ${allContent.slice(0, 500)}`;
      
      // Remove old nodes
      for (const n of group) this.nodes.delete(n.id);
      
      // Create compressed node at higher layer
      const newNode = this.inscribe(summary, allTags.join(','), Math.min(4, layer + 1));
      if (newNode) {
        newNode.refs = allRefs.slice(0, 10);
        compressed.push(newNode);
      }
    }
    
    this.save();
    return { compressed: compressed.length, removed: groups.reduce((s, g) => s + g.length, 0) };
  }

  // Stats
  stats() {
    const layers = { sensory: 0, working: 0, episodic: 0, semantic: 0, identity: 0 };
    const layerNames = ['sensory', 'working', 'episodic', 'semantic', 'identity'];
    let totalWeight = 0, totalConnections = 0;
    const tags = new Set();
    
    for (const node of this.nodes.values()) {
      layers[layerNames[node.layer] || 'working']++;
      totalWeight += node.weight;
      totalConnections += node.refs.length;
      node.tags.forEach(t => tags.add(t));
    }
    
    return {
      totalNodes: this.nodes.size,
      layers,
      avgWeight: this.nodes.size ? (totalWeight / this.nodes.size).toFixed(3) : '0',
      totalConnections,
      tags: tags.size,
    };
  }

  // Export for visualization
  exportGraph() {
    const nodes = [], edges = [];
    const layerNames = ['sensory', 'working', 'episodic', 'semantic', 'identity'];
    
    for (const node of this.nodes.values()) {
      nodes.push({
        id: node.id,
        label: node.content.slice(0, 60),
        layer: node.layer,
        layerName: layerNames[node.layer],
        weight: node.weight,
        tags: node.tags,
        createdAt: node.createdAt,
      });
      for (const ref of node.refs) {
        if (this.nodes.has(ref)) {
          edges.push({ source: node.id, target: ref });
        }
      }
    }
    
    return { nodes, edges };
  }
}

// Merkle Tree computation
function sha256(data) {
  return crypto.createHash('sha256').update(data).digest('hex');
}

function merkleRoot(hashes) {
  if (hashes.length === 0) return sha256('empty');
  if (hashes.length === 1) return hashes[0];
  const next = [];
  for (let i = 0; i < hashes.length; i += 2) {
    const left = hashes[i];
    const right = i + 1 < hashes.length ? hashes[i + 1] : left;
    next.push(sha256(left + right));
  }
  return merkleRoot(next);
}

function computeMemoryMerkle(rmn) {
  const layerNames = ['sensory', 'working', 'episodic', 'semantic', 'identity'];
  const layerRoots = {};
  
  for (let layer = 0; layer < 5; layer++) {
    const nodes = Array.from(rmn.nodes.values())
      .filter(n => n.layer === layer)
      .sort((a, b) => a.createdAt - b.createdAt);
    const hashes = nodes.map(n => sha256(JSON.stringify({ content: n.content, refs: n.refs, layer: n.layer, tags: n.tags })));
    layerRoots[layerNames[layer]] = merkleRoot(hashes);
  }
  
  const memoryRoot = merkleRoot(layerNames.map(name => layerRoots[name]));
  const soulHash = layerRoots.identity;
  
  return { memoryRoot, soulHash, layerRoots, version: Date.now(), timestamp: new Date().toISOString() };
}

module.exports = { RecursiveMemoryNetwork, computeMemoryMerkle, merkleRoot, sha256 };
