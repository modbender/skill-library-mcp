#!/usr/bin/env node

// Security: This script uses only Node.js built-in 'fs' and 'path' modules.
// No network access, no external dependencies, no eval/Function, no child_process.
// All input is read from stdin as JSON to prevent shell injection.

const fs = require('fs');
const path = require('path');

// Storage directory: use TOPOLOGY_TREES_DIR env var, or default to {baseDir}/trees/
const TREES_DIR = process.env.TOPOLOGY_TREES_DIR || path.join(__dirname, '..', 'trees');
const CONCEPT_INDEX_PATH = path.join(TREES_DIR, 'concepts.json');

// Ensure storage directory exists
if (!fs.existsSync(TREES_DIR)) {
  fs.mkdirSync(TREES_DIR, { recursive: true });
}

// --- Concept Index ---

function loadConceptIndex() {
  if (!fs.existsSync(CONCEPT_INDEX_PATH)) {
    return { version: '1', updated: new Date().toISOString(), concepts: {} };
  }
  try {
    return JSON.parse(fs.readFileSync(CONCEPT_INDEX_PATH, 'utf8'));
  } catch (e) {
    return { version: '1', updated: new Date().toISOString(), concepts: {} };
  }
}

function saveConceptIndex(index) {
  index.updated = new Date().toISOString();
  fs.writeFileSync(CONCEPT_INDEX_PATH, JSON.stringify(index, null, 2));
}

// Update concept index entries for a single tree (incremental)
function updateConceptIndexForTree(treeFile, tree) {
  const index = loadConceptIndex();
  const filename = path.basename(treeFile);

  // Remove all existing entries for this tree
  for (const [concept, data] of Object.entries(index.concepts)) {
    data.nodes = data.nodes.filter(n => n.tree !== filename);
    data.tree_count = new Set(data.nodes.map(n => n.tree)).size;
    data.active_count = data.nodes.filter(n => n.status === 'active').length;
    data.dead_count = data.nodes.filter(n => n.status === 'dead').length;
  }

  // Remove empty concepts
  for (const concept of Object.keys(index.concepts)) {
    if (index.concepts[concept].nodes.length === 0) {
      delete index.concepts[concept];
    }
  }

  // Add current entries from this tree
  for (const node of Object.values(tree.nodes)) {
    for (const concept of (node.concepts || [])) {
      const key = concept.toLowerCase();
      if (!index.concepts[key]) {
        index.concepts[key] = { nodes: [], tree_count: 0, active_count: 0, dead_count: 0 };
      }
      index.concepts[key].nodes.push({
        tree: filename,
        node_id: node.id,
        status: node.status,
        summary: node.summary
      });
    }
  }

  // Recalculate counts
  for (const data of Object.values(index.concepts)) {
    data.tree_count = new Set(data.nodes.map(n => n.tree)).size;
    data.active_count = data.nodes.filter(n => n.status === 'active').length;
    data.dead_count = data.nodes.filter(n => n.status === 'dead').length;
  }

  saveConceptIndex(index);
  return index;
}

// Full rebuild from all trees
function rebuildConceptIndex() {
  const index = { version: '1', updated: new Date().toISOString(), concepts: {} };
  const allTrees = getAllTrees();

  for (const { file, tree } of allTrees) {
    for (const node of Object.values(tree.nodes)) {
      for (const concept of (node.concepts || [])) {
        const key = concept.toLowerCase();
        if (!index.concepts[key]) {
          index.concepts[key] = { nodes: [], tree_count: 0, active_count: 0, dead_count: 0 };
        }
        index.concepts[key].nodes.push({
          tree: file,
          node_id: node.id,
          status: node.status,
          summary: node.summary
        });
      }
    }
  }

  // Calculate counts
  for (const data of Object.values(index.concepts)) {
    data.tree_count = new Set(data.nodes.map(n => n.tree)).size;
    data.active_count = data.nodes.filter(n => n.status === 'active').length;
    data.dead_count = data.nodes.filter(n => n.status === 'dead').length;
  }

  saveConceptIndex(index);
  return index;
}

// Update weight on nodes based on cross-tree concept spread
function updateWeights(tree, index) {
  let changed = false;
  for (const node of Object.values(tree.nodes)) {
    for (const concept of (node.concepts || [])) {
      const key = concept.toLowerCase();
      const entry = index.concepts[key];
      if (entry && entry.tree_count > 1) {
        if (node.weight !== entry.tree_count) {
          node.weight = entry.tree_count;
          changed = true;
        }
      }
    }
  }
  return changed;
}

// Generate a 6-char hex ID. Math.random is sufficient here — IDs only need
// to be unique within a single tree (5-30 nodes), not cryptographically secure.
function genId() {
  return Math.floor(Math.random() * 0xFFFFFF).toString(16).padStart(6, '0');
}

function uniqueId(existingIds) {
  let id;
  do {
    id = genId();
  } while (existingIds.has(id));
  return id;
}

function loadTree(file) {
  const filePath = file.startsWith('/') ? file : path.join(TREES_DIR, file);
  if (!fs.existsSync(filePath)) {
    console.error(`Error: Tree file not found: ${filePath}`);
    process.exit(1);
  }
  return { tree: JSON.parse(fs.readFileSync(filePath, 'utf8')), filePath };
}

function saveTree(filePath, tree) {
  tree.updated = new Date().toISOString();

  // Update concept index, then use it for weights and companion links
  const index = updateConceptIndexForTree(filePath, tree);

  // Update node weights from cross-tree spread
  updateWeights(tree, index);

  fs.writeFileSync(filePath, JSON.stringify(tree, null, 2));
  writeMdCompanion(filePath, tree, index);
}

// Write a .md companion file for semantic search indexing
function writeMdCompanion(jsonPath, tree, index) {
  const mdPath = jsonPath.replace(/\.json$/, '.md');
  const currentFile = path.basename(jsonPath);
  const nodes = Object.values(tree.nodes);
  const active = nodes.filter(n => n.status === 'active');
  const dead = nodes.filter(n => n.status === 'dead');
  const allConcepts = [...new Set(nodes.flatMap(n => n.concepts || []))];

  let md = `# ${tree.topic}\n\n`;
  md += `Updated: ${tree.updated.split('T')[0]} | ${nodes.length} nodes, ${active.length} active, ${dead.length} dead\n\n`;

  // Active branches
  if (active.length > 0) {
    md += `## Active\n`;
    for (const n of active) {
      if (n.type === 'root') continue;
      md += `- ${n.summary}`;
      if (n.reasoning) md += ` — ${n.reasoning}`;
      if (n.weight > 1) md += ` (weight: ${n.weight})`;
      md += `\n`;
    }
    md += `\n`;
  }

  // Dead branches with reasons
  if (dead.length > 0) {
    md += `## Killed\n`;
    for (const n of dead) {
      md += `- ${n.summary}`;
      if (n.killed_by) md += ` — killed: ${n.killed_by}`;
      md += `\n`;
    }
    md += `\n`;
  }

  // Concepts for semantic matching
  if (allConcepts.length > 0) {
    md += `## Concepts\n${allConcepts.join(', ')}\n`;
  }

  // Cross-tree links from concept index
  if (index) {
    const relatedTrees = {}; // filename -> Set of shared concepts
    for (const concept of allConcepts) {
      const key = concept.toLowerCase();
      const entry = index.concepts[key];
      if (!entry) continue;
      for (const ref of entry.nodes) {
        if (ref.tree === currentFile) continue;
        if (!relatedTrees[ref.tree]) relatedTrees[ref.tree] = new Set();
        relatedTrees[ref.tree].add(concept);
      }
    }

    const related = Object.entries(relatedTrees)
      .map(([file, concepts]) => ({ file, concepts: [...concepts], count: concepts.size }))
      .sort((a, b) => b.count - a.count);

    if (related.length > 0) {
      md += `\n## Related trees\n`;
      for (const r of related) {
        const linkName = r.file.replace(/\.json$/, '');
        md += `- [[${linkName}]] — shared: ${r.concepts.join(', ')}\n`;
      }
    }
  }

  fs.writeFileSync(mdPath, md);
}

function slugify(text) {
  return text.toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .substring(0, 40)
    .replace(/-$/, '');
}

function getAllTrees() {
  return fs.readdirSync(TREES_DIR)
    .filter(f => f.endsWith('.json') && f !== 'concepts.json')
    .map(f => {
      try {
        const tree = JSON.parse(fs.readFileSync(path.join(TREES_DIR, f), 'utf8'));
        return { file: f, filePath: path.join(TREES_DIR, f), tree };
      } catch (e) {
        return null;
      }
    })
    .filter(Boolean);
}

// --- Commands ---

function init(args) {
  const topic = args.topic;
  if (!topic) {
    console.error('Error: "topic" is required');
    process.exit(1);
  }

  const date = new Date().toISOString().split('T')[0];
  const slug = slugify(topic);
  const filename = `${date}-${slug}.json`;
  const filePath = path.join(TREES_DIR, filename);

  if (fs.existsSync(filePath)) {
    // Append a short random suffix to avoid filename collision
    const suffix = Math.floor(Math.random() * 0xFFFF).toString(16).padStart(4, '0');
    const altFilename = `${date}-${slug}-${suffix}.json`;
    const altPath = path.join(TREES_DIR, altFilename);
    return initTree(altPath, topic);
  }

  initTree(filePath, topic);
}

function initTree(filePath, topic) {
  const rootId = genId();
  const tree = {
    version: '2',
    topic,
    created: new Date().toISOString(),
    updated: new Date().toISOString(),
    root_id: rootId,
    active_id: rootId,
    nodes: {
      [rootId]: {
        id: rootId,
        parent_id: null,
        type: 'root',
        summary: topic,
        reasoning: 'Root topic of exploration',
        killed_by: null,
        children: [],
        sources: [],
        concepts: [],
        weight: 1,
        timestamp: new Date().toISOString(),
        status: 'active'
      }
    }
  };

  saveTree(filePath, tree);
  console.log(JSON.stringify({ file: filePath, root_id: rootId, topic }));
}

function addNode(args) {
  const { file, parent_id, type, summary, reasoning, concepts } = args;
  if (!file || !parent_id || !type || !summary) {
    console.error('Error: "file", "parent_id", "type", and "summary" are required');
    process.exit(1);
  }

  const { tree, filePath } = loadTree(file);
  const parent = tree.nodes[parent_id];
  if (!parent) {
    console.error(`Error: Parent node not found: ${parent_id}`);
    process.exit(1);
  }

  const existingIds = new Set(Object.keys(tree.nodes));
  const id = uniqueId(existingIds);

  const node = {
    id,
    parent_id,
    type,
    summary,
    reasoning: reasoning || '',
    killed_by: null,
    children: [],
    sources: [],
    concepts: concepts || [],
    weight: 1,
    timestamp: new Date().toISOString(),
    status: 'active'
  };

  tree.nodes[id] = node;
  parent.children.push(id);
  tree.active_id = id;

  saveTree(filePath, tree);
  console.log(JSON.stringify({ id, parent_id, type, summary }));
}

function killBranch(args) {
  const { file, node_id, reason } = args;
  if (!file || !node_id || !reason) {
    console.error('Error: "file", "node_id", and "reason" are required');
    process.exit(1);
  }

  const { tree, filePath } = loadTree(file);
  const node = tree.nodes[node_id];
  if (!node) {
    console.error(`Error: Node not found: ${node_id}`);
    process.exit(1);
  }

  function killRecursive(nid) {
    const n = tree.nodes[nid];
    if (!n) return;
    n.status = 'dead';
    if (!n.killed_by) n.killed_by = reason;
    for (const childId of n.children) {
      killRecursive(childId);
    }
  }

  killRecursive(node_id);

  if (tree.nodes[tree.active_id] && tree.nodes[tree.active_id].status === 'dead') {
    tree.active_id = node.parent_id || tree.root_id;
  }

  saveTree(filePath, tree);
  console.log(JSON.stringify({ killed: node_id, reason, status: 'dead' }));
}

function merge(args) {
  const { file, source_ids, summary, reasoning, concepts } = args;
  if (!file || !source_ids || !summary) {
    console.error('Error: "file", "source_ids", and "summary" are required');
    process.exit(1);
  }

  const { tree, filePath } = loadTree(file);

  for (const sid of source_ids) {
    if (!tree.nodes[sid]) {
      console.error(`Error: Source node not found: ${sid}`);
      process.exit(1);
    }
  }

  const parent_id = tree.active_id;
  const existingIds = new Set(Object.keys(tree.nodes));
  const id = uniqueId(existingIds);

  const node = {
    id,
    parent_id,
    type: 'merge',
    summary,
    reasoning: reasoning || '',
    killed_by: null,
    children: [],
    sources: source_ids,
    concepts: concepts || [],
    weight: 1,
    timestamp: new Date().toISOString(),
    status: 'active'
  };

  tree.nodes[id] = node;
  if (tree.nodes[parent_id]) {
    tree.nodes[parent_id].children.push(id);
  }

  for (const sid of source_ids) {
    tree.nodes[sid].status = 'merged';
  }

  tree.active_id = id;
  saveTree(filePath, tree);
  console.log(JSON.stringify({ id, type: 'merge', sources: source_ids, summary }));
}

function render(args) {
  const { file } = args;
  if (!file) {
    console.error('Error: "file" is required');
    process.exit(1);
  }

  const { tree } = loadTree(file);
  const output = [];
  const nodes = Object.values(tree.nodes);
  const totalBranches = nodes.length;
  const killed = nodes.filter(n => n.status === 'dead').length;
  const active = nodes.filter(n => n.status === 'active').length;

  function getDepth(nodeId, visited = new Set()) {
    if (visited.has(nodeId)) return 0;
    visited.add(nodeId);
    const n = tree.nodes[nodeId];
    if (!n || !n.parent_id) return 0;
    return 1 + getDepth(n.parent_id, visited);
  }
  const maxDepth = Math.max(...nodes.map(n => getDepth(n.id)));

  function getMarker(node) {
    if (node.id === tree.active_id) return '(*)';
    if (node.type === 'merge') return '[+]';
    if (node.status === 'dead') return '[x]';
    return '[*]';
  }

  function getLabel(node) {
    let label = `${getMarker(node)} ${node.summary}`;
    if (node.status === 'dead' && node.killed_by) {
      label += ` (killed: ${node.killed_by})`;
    }
    if (node.type === 'merge' && node.sources.length > 0) {
      const sourceLabels = node.sources.map(sid => {
        const s = tree.nodes[sid];
        return s ? s.summary.substring(0, 20) : sid;
      });
      label += ` (merged from: ${sourceLabels.join(' + ')})`;
    }
    return label;
  }

  function renderNode(nodeId, prefix, isLast, isRoot) {
    const node = tree.nodes[nodeId];
    if (!node) return;

    if (isRoot) {
      output.push(getLabel(node));
    } else {
      const connector = isLast ? '`-- ' : '|-- ';
      output.push(`${prefix}${connector}${getLabel(node)}`);
    }

    const childPrefix = isRoot ? '' : prefix + (isLast ? '    ' : '|   ');
    const children = node.children || [];
    for (let i = 0; i < children.length; i++) {
      renderNode(children[i], childPrefix, i === children.length - 1, false);
    }
  }

  output.push(`${tree.topic}`);
  output.push('');
  renderNode(tree.root_id, '', true, true);
  output.push('');
  output.push(`${totalBranches} branches explored, ${killed} killed, ${active} active, depth ${maxDepth}`);

  console.log(output.join('\n'));
}

function exportMermaid(args) {
  const { file } = args;
  if (!file) {
    console.error('Error: "file" is required');
    process.exit(1);
  }

  const { tree } = loadTree(file);
  const lines = ['graph TD'];

  function sanitize(text) {
    return text.replace(/"/g, "'").replace(/[[\]]/g, '');
  }

  for (const [id, node] of Object.entries(tree.nodes)) {
    const label = sanitize(node.summary);

    if (node.status === 'dead') {
      lines.push(`  ${id}["x ${label}"]`);
      lines.push(`  style ${id} fill:#ffcccc,stroke:#cc0000`);
    } else if (node.type === 'merge') {
      lines.push(`  ${id}(("+ ${label}"))`);
      lines.push(`  style ${id} fill:#ccffcc,stroke:#00cc00`);
    } else if (node.id === tree.active_id) {
      lines.push(`  ${id}["* ${label}"]`);
      lines.push(`  style ${id} fill:#cce5ff,stroke:#0066cc,stroke-width:3px`);
    } else if (node.type === 'root') {
      lines.push(`  ${id}["${label}"]`);
      lines.push(`  style ${id} fill:#fff3cd,stroke:#cc9900,stroke-width:2px`);
    } else {
      lines.push(`  ${id}["${label}"]`);
    }
  }

  for (const [id, node] of Object.entries(tree.nodes)) {
    if (node.parent_id) {
      if (node.status === 'dead' && node.killed_by) {
        lines.push(`  ${node.parent_id} -- "${sanitize(node.killed_by)}" --> ${id}`);
      } else if (node.type === 'pivot') {
        lines.push(`  ${node.parent_id} -. pivot .-> ${id}`);
      } else {
        lines.push(`  ${node.parent_id} --> ${id}`);
      }
    }
    if (node.type === 'merge' && node.sources.length > 0) {
      for (const sid of node.sources) {
        lines.push(`  ${sid} -. source .-> ${id}`);
      }
    }
  }

  console.log('```mermaid');
  console.log(lines.join('\n'));
  console.log('```');
}

function fork(args) {
  const { file, node_id, summary, reasoning } = args;
  if (!file || !node_id) {
    console.error('Error: "file" and "node_id" are required');
    process.exit(1);
  }

  const { tree, filePath } = loadTree(file);
  const sourceNode = tree.nodes[node_id];
  if (!sourceNode) {
    console.error(`Error: Node not found: ${node_id}`);
    process.exit(1);
  }

  const existingIds = new Set(Object.keys(tree.nodes));
  const id = uniqueId(existingIds);

  const node = {
    id,
    parent_id: node_id,
    type: 'pivot',
    summary: summary || `Fork from: ${sourceNode.summary}`,
    reasoning: reasoning || `Re-exploring from node ${node_id}`,
    killed_by: null,
    children: [],
    sources: [],
    concepts: [],
    weight: 1,
    timestamp: new Date().toISOString(),
    status: 'active'
  };

  tree.nodes[id] = node;
  sourceNode.children.push(id);
  tree.active_id = id;

  saveTree(filePath, tree);
  console.log(JSON.stringify({ id, forked_from: node_id, summary: node.summary }));
}

function list() {
  const allTrees = getAllTrees();
  if (allTrees.length === 0) {
    console.log('No decision trees found.');
    return;
  }

  // Sort by updated date, most recent first
  allTrees.sort((a, b) => (b.tree.updated || '').localeCompare(a.tree.updated || ''));

  const output = [`${allTrees.length} decision trees found in ${TREES_DIR}:`, ''];

  for (const { file, filePath, tree } of allTrees) {
    const nodeCount = Object.keys(tree.nodes).length;
    const deadCount = Object.values(tree.nodes).filter(n => n.status === 'dead').length;
    const activeCount = Object.values(tree.nodes).filter(n => n.status === 'active').length;
    output.push(`  File: ${filePath}`);
    output.push(`  Topic: ${tree.topic}`);
    output.push(`  Nodes: ${nodeCount} (${activeCount} active, ${deadCount} dead)`);
    output.push(`  Updated: ${tree.updated ? tree.updated.split('T')[0] : 'unknown'}`);
    output.push('');
  }

  console.log(output.join('\n'));
}

function stats(args) {
  const { file } = args;
  if (!file) {
    console.error('Error: "file" is required');
    process.exit(1);
  }

  const { tree } = loadTree(file);
  const nodes = Object.values(tree.nodes);
  const total = nodes.length;
  const dead = nodes.filter(n => n.status === 'dead');
  const active = nodes.filter(n => n.status === 'active');
  const merged = nodes.filter(n => n.status === 'merged');
  const proposals = nodes.filter(n => n.type === 'proposal');
  const pivots = nodes.filter(n => n.type === 'pivot');
  const merges = nodes.filter(n => n.type === 'merge');

  function getDepth(nodeId, visited = new Set()) {
    if (visited.has(nodeId)) return 0;
    visited.add(nodeId);
    const node = tree.nodes[nodeId];
    if (!node || !node.parent_id) return 0;
    return 1 + getDepth(node.parent_id, visited);
  }

  const depths = nodes.map(n => getDepth(n.id));
  const maxDepth = Math.max(...depths);
  const avgDepth = (depths.reduce((a, b) => a + b, 0) / depths.length).toFixed(1);

  const killReasons = {};
  for (const n of dead) {
    if (n.killed_by) {
      const reason = n.killed_by.substring(0, 50);
      killReasons[reason] = (killReasons[reason] || 0) + 1;
    }
  }
  const topReasons = Object.entries(killReasons)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  // Collect all concepts
  const conceptCounts = {};
  for (const n of nodes) {
    for (const c of (n.concepts || [])) {
      conceptCounts[c] = (conceptCounts[c] || 0) + 1;
    }
  }
  const topConcepts = Object.entries(conceptCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);

  const output = [
    `Stats: ${tree.topic}`,
    '',
    `  Total nodes:      ${total}`,
    `  Active branches:  ${active.length}`,
    `  Dead branches:    ${dead.length}`,
    `  Merged:           ${merged.length}`,
    `  Kill rate:        ${total > 1 ? ((dead.length / (total - 1)) * 100).toFixed(0) : 0}%`,
    '',
    `  Proposals:        ${proposals.length}`,
    `  Pivots:           ${pivots.length}`,
    `  Merges:           ${merges.length}`,
    '',
    `  Max depth:        ${maxDepth}`,
    `  Avg depth:        ${avgDepth}`,
  ];

  if (topReasons.length > 0) {
    output.push('');
    output.push('  Top rejection reasons:');
    for (const [reason, count] of topReasons) {
      output.push(`    ${count}x  ${reason}`);
    }
  }

  if (topConcepts.length > 0) {
    output.push('');
    output.push('  Top concepts:');
    for (const [concept, count] of topConcepts) {
      output.push(`    ${count}x  ${concept}`);
    }
  }

  console.log(output.join('\n'));
}

function associate(args) {
  const { query } = args;
  if (!query) {
    console.error('Error: "query" is required');
    process.exit(1);
  }

  const allTrees = getAllTrees();
  if (allTrees.length === 0) {
    console.log(JSON.stringify({ match: null, score: 0, message: 'No existing trees' }));
    return;
  }

  const queryTerms = query.toLowerCase().split(/\s+/).filter(t => t.length > 2);

  const scored = allTrees.map(({ file, filePath, tree }) => {
    let score = 0;
    const nodes = Object.values(tree.nodes);

    // Match against topic
    const topicLower = tree.topic.toLowerCase();
    for (const term of queryTerms) {
      if (topicLower.includes(term)) score += 0.3;
    }

    // Match against node summaries and concepts
    for (const node of nodes) {
      const summaryLower = (node.summary || '').toLowerCase();
      const concepts = (node.concepts || []).map(c => c.toLowerCase());

      for (const term of queryTerms) {
        if (summaryLower.includes(term)) score += 0.1;
        if (concepts.includes(term)) score += 0.15;
      }
    }

    // Normalize score to 0-1 range (cap at 1)
    score = Math.min(score / Math.max(queryTerms.length, 1), 1);

    // Recency boost: small bonus for recent trees (max +0.05)
    const daysSinceUpdate = (Date.now() - new Date(tree.updated).getTime()) / (1000 * 60 * 60 * 24);
    if (daysSinceUpdate < 7) score = Math.min(score + 0.03, 1);
    if (daysSinceUpdate < 1) score = Math.min(score + 0.02, 1);

    return { file, filePath, topic: tree.topic, score: parseFloat(score.toFixed(2)), updated: tree.updated };
  });

  scored.sort((a, b) => b.score - a.score);
  const best = scored[0];

  const MATCH_THRESHOLD = 0.4;
  const CANDIDATE_THRESHOLD = 0.25;

  const result = {
    match: best.score >= MATCH_THRESHOLD ? {
      file: best.filePath,
      topic: best.topic,
      updated: best.updated
    } : null,
    score: best.score,
    action: best.score >= MATCH_THRESHOLD ? 'continue' :
            best.score >= CANDIDATE_THRESHOLD ? 'ask_user' : 'new_tree',
    candidates: scored.filter(s => s.score >= CANDIDATE_THRESHOLD).slice(0, 3).map(s => ({
      file: s.filePath,
      topic: s.topic,
      score: s.score
    }))
  };

  console.log(JSON.stringify(result, null, 2));
}

function concept(args) {
  const index = loadConceptIndex();

  // List all concepts sorted by cross-tree spread
  if (args.list) {
    const sorted = Object.entries(index.concepts)
      .sort((a, b) => b[1].tree_count - a[1].tree_count || b[1].nodes.length - a[1].nodes.length);

    if (sorted.length === 0) {
      console.log('No concepts indexed. Run rebuild-index first.');
      return;
    }

    const output = [`${sorted.length} concepts indexed:`, ''];
    for (const [name, data] of sorted) {
      const marker = data.tree_count > 1 ? '*' : ' ';
      output.push(`  ${marker} ${name} — ${data.tree_count} tree${data.tree_count > 1 ? 's' : ''}, ${data.active_count} active, ${data.dead_count} dead`);
    }
    output.push('');
    output.push(`* = cross-tree concept`);
    console.log(output.join('\n'));
    return;
  }

  // Show orphan concepts (only in one tree)
  if (args.orphans) {
    const orphans = Object.entries(index.concepts)
      .filter(([, data]) => data.tree_count === 1)
      .sort((a, b) => b[1].nodes.length - a[1].nodes.length);

    if (orphans.length === 0) {
      console.log('No orphan concepts — all concepts span multiple trees.');
      return;
    }

    const output = [`${orphans.length} orphan concepts (single-tree):`, ''];
    for (const [name, data] of orphans) {
      const tree = data.nodes[0] ? data.nodes[0].tree : 'unknown';
      output.push(`  ${name} — in ${tree} (${data.nodes.length} node${data.nodes.length > 1 ? 's' : ''})`);
    }
    console.log(output.join('\n'));
    return;
  }

  // Lookup a specific concept
  if (args.name) {
    const key = args.name.toLowerCase();
    const entry = index.concepts[key];
    if (!entry) {
      console.log(JSON.stringify({ concept: key, found: false, message: 'Not in index' }));
      return;
    }

    const byTree = {};
    for (const ref of entry.nodes) {
      if (!byTree[ref.tree]) byTree[ref.tree] = [];
      byTree[ref.tree].push(ref);
    }

    const output = [
      `Concept: "${key}"`,
      `  Trees: ${entry.tree_count} | Active: ${entry.active_count} | Dead: ${entry.dead_count}`,
      ''
    ];

    for (const [tree, refs] of Object.entries(byTree)) {
      output.push(`  ${tree}:`);
      for (const ref of refs) {
        const marker = ref.status === 'dead' ? 'x' : ref.status === 'merged' ? '+' : '*';
        output.push(`    ${marker} [${ref.node_id}] ${ref.summary}`);
      }
    }

    console.log(output.join('\n'));
    return;
  }

  console.error('Usage: concept {"name":"trust"} | concept {"list":true} | concept {"orphans":true}');
  process.exit(1);
}

function analyze() {
  // Ensure concept index is current
  const index = rebuildConceptIndex();

  const allTrees = getAllTrees();
  if (allTrees.length === 0) {
    console.log('No trees to analyze.');
    return;
  }

  const treeStats = [];
  for (const { file, tree } of allTrees) {
    const nodes = Object.values(tree.nodes);
    const dead = nodes.filter(n => n.status === 'dead').length;
    const active = nodes.filter(n => n.status === 'active').length;
    const daysSinceUpdate = (Date.now() - new Date(tree.updated).getTime()) / (1000 * 60 * 60 * 24);

    treeStats.push({
      file,
      topic: tree.topic,
      nodeCount: nodes.length,
      dead,
      active,
      daysSinceUpdate: Math.round(daysSinceUpdate),
      recentlyActive: daysSinceUpdate < 7
    });
  }

  const output = ['Topology Analysis', ''];

  // Tree summaries
  output.push('Trees:');
  for (const ts of treeStats) {
    const marker = ts.recentlyActive ? '*' : ' ';
    output.push(`  ${marker} ${ts.topic} (${ts.nodeCount} nodes, ${ts.dead} killed, ${ts.active} active) — ${ts.daysSinceUpdate}d ago`);
  }
  output.push('');

  // Cross-tree concepts
  const crossTreeConcepts = {};
  for (const [concept, data] of Object.entries(index.concepts)) {
    if (data.tree_count > 1) {
      crossTreeConcepts[concept] = data;
    }
  }

  if (Object.keys(crossTreeConcepts).length > 0) {
    output.push('Cross-root concepts:');
    const sorted = Object.entries(crossTreeConcepts).sort((a, b) => b[1].tree_count - a[1].tree_count);
    for (const [concept, data] of sorted) {
      const fate = data.active_count > data.dead_count ? 'mostly survives' :
                   data.dead_count > data.active_count ? 'mostly killed' : 'mixed';
      output.push(`  "${concept}" — ${data.tree_count} trees (${data.active_count} active, ${data.dead_count} dead — ${fate})`);
      for (const ref of data.nodes.slice(0, 3)) {
        const marker = ref.status === 'dead' ? 'x' : '*';
        output.push(`    ${marker} ${ref.tree}: ${ref.summary}`);
      }
    }
    output.push('');
  }

  // Concepts that keep getting killed
  const killedConcepts = Object.entries(index.concepts)
    .filter(([, data]) => data.dead_count >= 2)
    .sort((a, b) => b[1].dead_count - a[1].dead_count);

  if (killedConcepts.length > 0) {
    output.push('Repeatedly killed concepts:');
    for (const [concept, data] of killedConcepts) {
      const deadNodes = data.nodes.filter(n => n.status === 'dead');
      output.push(`  "${concept}" — killed ${deadNodes.length} times`);
      for (const ref of deadNodes.slice(0, 3)) {
        output.push(`    x ${ref.tree}: ${ref.summary}`);
      }
    }
    output.push('');
  }

  // Concepts that keep surviving
  const survivingConcepts = Object.entries(index.concepts)
    .filter(([, data]) => data.active_count >= 2)
    .sort((a, b) => b[1].active_count - a[1].active_count);

  if (survivingConcepts.length > 0) {
    output.push('Persistent concepts:');
    for (const [concept, data] of survivingConcepts) {
      const activeNodes = data.nodes.filter(n => n.status === 'active');
      output.push(`  "${concept}" — active ${activeNodes.length} times`);
      for (const ref of activeNodes.slice(0, 3)) {
        output.push(`    * ${ref.tree}: ${ref.summary}`);
      }
    }
    output.push('');
  }

  // Index health
  const totalConcepts = Object.keys(index.concepts).length;
  const crossCount = Object.keys(crossTreeConcepts).length;
  const orphanCount = totalConcepts - crossCount;
  output.push(`Index: ${totalConcepts} concepts, ${crossCount} cross-tree, ${orphanCount} orphans`);

  // Regenerate all companion .md files with updated links
  for (const { filePath, tree } of allTrees) {
    updateWeights(tree, index);
    fs.writeFileSync(filePath, JSON.stringify(tree, null, 2));
    writeMdCompanion(filePath, tree, index);
  }

  console.log(output.join('\n'));
}

// --- CLI Router ---
// process.exit(1) below is standard CLI error handling for invalid input.

// Commands that require no arguments (never read stdin for these)
const NO_ARG_COMMANDS = new Set(['list', 'analyze', 'rebuild-index']);

// Read args from argv or stdin. Stdin is preferred when input contains
// user-derived content (topics, summaries, queries) to avoid shell injection.
// This is the ONLY input vector — the script never reads environment variables
// for content, never fetches URLs, and never spawns child processes.
function readArgs(command) {
  return new Promise((resolve) => {
    // Commands that take no args — resolve immediately
    if (NO_ARG_COMMANDS.has(command)) {
      resolve({});
      return;
    }

    // If args passed as argv[3], use those
    if (process.argv[3]) {
      try {
        resolve(JSON.parse(process.argv[3]));
      } catch (e) {
        console.error(`Error: Invalid JSON argument: ${e.message}`);
        process.exit(1);
      }
      return;
    }

    // Check if stdin is a TTY (interactive terminal, no piped data)
    if (process.stdin.isTTY) {
      resolve({});
      return;
    }

    // Read piped stdin
    let data = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (chunk) => { data += chunk; });
    process.stdin.on('end', () => {
      if (!data.trim()) {
        resolve({});
        return;
      }
      try {
        resolve(JSON.parse(data));
      } catch (e) {
        console.error(`Error: Invalid JSON on stdin: ${e.message}`);
        process.exit(1);
      }
    });
  });
}

const command = process.argv[2];

readArgs(command).then((args) => {

switch (command) {
  case 'init': init(args); break;
  case 'add-node': addNode(args); break;
  case 'kill-branch': killBranch(args); break;
  case 'merge': merge(args); break;
  case 'render': render(args); break;
  case 'export': exportMermaid(args); break;
  case 'fork': fork(args); break;
  case 'list': list(); break;
  case 'stats': stats(args); break;
  case 'associate': associate(args); break;
  case 'analyze': analyze(); break;
  case 'concept': concept(args); break;
  case 'rebuild-index': {
    const idx = rebuildConceptIndex();
    const total = Object.keys(idx.concepts).length;
    const cross = Object.values(idx.concepts).filter(d => d.tree_count > 1).length;
    const allTrees = getAllTrees();
    for (const { filePath, tree } of allTrees) {
      updateWeights(tree, idx);
      fs.writeFileSync(filePath, JSON.stringify(tree, null, 2));
      writeMdCompanion(filePath, tree, idx);
    }
    console.log(`Rebuilt concept index: ${total} concepts, ${cross} cross-tree. Updated ${allTrees.length} companion files.`);
    break;
  }
  default:
    console.error('Usage: topology.js <command> [args as JSON]');
    console.error('       echo \'{"key":"value"}\' | topology.js <command>');
    console.error('');
    console.error('Args can be passed as argv[3] or piped via stdin (preferred for user input).');
    console.error('');
    console.error('Commands:');
    console.error('  init            Create a new decision tree');
    console.error('  add-node        Add a node to the tree');
    console.error('  kill-branch     Mark a branch as dead');
    console.error('  merge           Create a merge node from sources');
    console.error('  render          Display ASCII tree');
    console.error('  export          Export as Mermaid diagram');
    console.error('  fork            Branch from any node');
    console.error('  list            Show all saved trees');
    console.error('  stats           Show tree statistics');
    console.error('  associate       Find matching tree for a query');
    console.error('  analyze         Cross-tree concept analysis');
    console.error('  concept         Query the concept index');
    console.error('  rebuild-index   Rebuild concept index from all trees');
    process.exit(1);
}

}); // end readArgs
