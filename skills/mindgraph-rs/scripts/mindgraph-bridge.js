/**
 * mindgraph-bridge.js
 * Memory bridge between OpenClaw sessions and mindgraph-server.
 *
 * Updated to utilize the 18 Cognitive Layer Tools API exclusively.
 */

'use strict';

const mg = require('./mindgraph-client.js');

// ─── FTS query sanitiser ──────────────────────────────────────────────────────

function sanitizeFtsQuery(q) {
  return q.replace(/[{}()\[\]^~*?:\\\/]/g, ' ').replace(/\s+/g, ' ').trim();
}

/**
 * Format context results as structured markdown for injection into prompts.
 */
function formatContext(contextData) {
  const { nodes, sections } = contextData;
  const lines = [];

  const nodeMap = new Map();
  if (nodes instanceof Map) {
    for (const [uid, node] of nodes) nodeMap.set(uid, node);
  } else if (Array.isArray(nodes)) {
    for (const node of nodes) nodeMap.set(node.uid, node);
  } else if (nodes && typeof nodes === 'object') {
    for (const uid in nodes) nodeMap.set(uid, nodes[uid]);
  }

  function renderNode(node, source) {
    let line = `- **${node.label}** (${node.node_type}`;
    if (node.props?.status) line += `, status: ${node.props.status}`;
    line += `): ${node.summary || node.props?.content || node.props?.description || ''}`;
    
    if (node._inboundEdges?.length > 0) {
      const edges = node._inboundEdges.map(e => `${e.from} --[${e.type}]-->`).join(', ');
      line += ` [Ref: ${edges}]`;
    }
    return line;
  }

  if (sections.goals?.length > 0) {
    lines.push('### Active Goals');
    sections.goals.forEach(uid => {
      const node = nodeMap.get(uid);
      if (node) lines.push(renderNode(node, 'goals'));
    });
    lines.push('');
  }

  if (sections.constraints?.length > 0) {
    lines.push('### Active Constraints');
    sections.constraints.forEach(uid => {
      const node = nodeMap.get(uid);
      if (node) lines.push(renderNode(node, 'constraints'));
    });
    lines.push('');
  }

  if (sections.primary?.length > 0) {
    lines.push('### Primary Context');
    sections.primary.forEach(uid => {
      const node = nodeMap.get(uid);
      if (node) lines.push(renderNode(node, 'primary'));
    });
    lines.push('');
  }

  if (sections.related?.length > 0) {
    lines.push('### Related Knowledge');
    sections.related.forEach(uid => {
      const node = nodeMap.get(uid);
      if (node) lines.push(renderNode(node, 'related'));
    });
    lines.push('');
  }

  const count = nodeMap.size;
  lines.push(`_Injected by mindgraph-context hook — ${count} nodes_\n`);

  return lines.join('\n');
}

// ─── Session Management ───────────────────────────────────────────────────────

async function openSession(label, { focus = '', agentId } = {}) {
  const node = await mg.sessionOp({ action: 'open', label, focus, agent_id: agentId });
  return node.uid;
}

async function closeSession(sessionUid, summaryText, { agentId } = {}) {
  const result = await mg.sessionOp({ 
    action: 'close', 
    session_uid: sessionUid, 
    trace_content: summaryText,
    agent_id: agentId 
  });
  return result.summary_uid;
}

// ─── Batch Writing ──────────────────────────────────────────────────────────

async function writeBatch(items, { defaultAgentId, sessionUid } = {}) {
  const results = [];

  for (const item of items) {
    const agentId = item.agentId || defaultAgentId;
    let uid = null;
    let upsert = 'created';

    try {
      let node;
      switch (item.type.toLowerCase()) {
        case 'claim':
        case 'observation':
        case 'snippet': {
          node = await mg.ingest(item.label, item.content || '', item.type.toLowerCase(), { 
            confidence: item.confidence, 
            agentId 
          });
          break;
        }
        case 'entity': {
          node = await mg.manageEntity({ 
            action: 'create', 
            label: item.label, 
            entityType: item.entityType || 'Organization',
            agentId 
          });
          break;
        }
        case 'goal':
        case 'project': {
          node = await mg.addCommitment(item.label, item.content || item.label, item.type.toLowerCase(), {
            status: 'active',
            agentId
          });
          break;
        }
        case 'decision': {
          node = await mg.deliberate({
            action: 'open_decision',
            label: item.label,
            description: item.content || '',
            agentId
          });
          // If content provided, resolve it immediately
          if (item.content) {
            node = await mg.deliberate({
              action: 'resolve',
              decisionUid: node.uid,
              resolutionRationale: item.content,
              agentId
            });
          }
          break;
        }
        case 'task': {
          node = await mg.plan({
            action: 'create_task',
            label: item.label,
            description: item.content || '',
            agentId
          });
          break;
        }
        case 'preference': {
          node = await mg.memoryConfig({
            action: 'set_preference',
            label: item.label,
            value: item.content || '',
            agentId
          });
          break;
        }
        default:
          console.error(`Unknown item type: ${item.type}`);
          continue;
      }

      if (node) {
        uid = node.uid;
        upsert = node._upsert || 'created';
        if (sessionUid) {
          await mg.sessionOp({
            action: 'trace',
            session_uid: sessionUid,
            relevant_node_uids: [uid],
            trace_content: `Captured ${item.type}: ${item.label}`,
            agentId
          }).catch(() => {});
        }
      }

      results.push({ label: item.label, uid, type: item.type, upsert });
    } catch (err) {
      console.error(`Failed to write "${item.label}": ${err.message}`);
      results.push({ label: item.label, uid: null, error: err.message });
    }
  }

  return results;
}

// ─── Sub-agent scoping ────────────────────────────────────────────────────────

function subAgentClient(subLabel) {
  const agentId = `jaadu/sub-${subLabel}`;
  const scoped = {};

  // All 18 tools + search/stats
  const tools = [
    'ingest', 'manageEntity', 'addArgument', 'addInquiry', 'addStructure',
    'addCommitment', 'deliberate', 'procedure', 'risk', 'sessionOp',
    'distill', 'memoryConfig', 'plan', 'governance', 'execution',
    'retrieve', 'traverse', 'evolve', 'search', 'stats', 'health', 'getNodes'
  ];

  for (const fn of tools) {
    scoped[fn] = (...args) => {
      // Find or create options object
      let opts = args[args.length - 1];
      if (typeof opts !== 'object' || Array.isArray(opts) || opts === null) {
        opts = {};
        args.push(opts);
      }
      opts.agentId = agentId;
      return mg[fn](...args);
    };
  }

  scoped.agentId = agentId;
  return scoped;
}

// ─── CLI interface ────────────────────────────────────────────────────────────

async function cli() {
  const [,, cmd, ...args] = process.argv;

  switch (cmd) {

    case 'context': {
      const opts = { mode: 'context' };
      for (let i = 0; i < args.length; i++) {
        if (args[i] === '--query') opts.query = args[++i];
        else if (args[i] === '--limit') opts.limit = parseInt(args[++i]);
        else if (args[i] === '--layer') opts.layer = args[++i];
        else if (args[i] === '--type') opts.nodeTypes = [args[++i]];
        else if (args[i] === '--no-goals') opts.noGoals = true; // handled by mode logic if implemented
        else if (!opts.query) opts.query = args[i];
      }
      
      const contextData = await mg.retrieve('context', opts);
      console.log(formatContext(contextData));
      if (!contextData || contextData.totalCount === 0) console.log('(no context found)');
      break;
    }

    case 'write-fact':
    case 'write-claim': {
      const label = args[0];
      const content = args[1] || '';
      const conf = args.includes('--confidence') ? parseFloat(args[args.indexOf('--confidence') + 1]) : 0.8;
      if (!label) { console.error('Usage: write-fact <label> [content] [--confidence N]'); process.exit(1); }
      const node = await mg.ingest(label, content, 'claim', { confidence: conf });
      console.log(JSON.stringify({ uid: node.uid, label: node.label, upsert: node._upsert }));
      break;
    }

    case 'write-decision': {
      const label = args[0];
      const rationale = args[1] || '';
      if (!label) { console.error('Usage: write-decision <label> <rationale>'); process.exit(1); }
      const node = await mg.deliberate({ 
        action: 'open_decision',
        label,
        description: rationale
      });
      // Resolve immediately
      const resolved = await mg.deliberate({
        action: 'resolve',
        decisionUid: node.uid,
        resolutionRationale: rationale || label
      });
      console.log(JSON.stringify({ uid: resolved.uid, label: resolved.label, upsert: resolved._upsert }));
      break;
    }

    case 'write-entity': {
      const label = args[0];
      const entityType = args[1] || 'Organization';
      if (!label) { console.error('Usage: write-entity <label> <entity_type>'); process.exit(1); }
      const node = await mg.manageEntity({ action: 'create', label, entityType });
      console.log(JSON.stringify({ uid: node.uid, label: node.label, upsert: node._upsert }));
      break;
    }

    case 'write-session': {
      const label = args[0] || `Session ${new Date().toISOString()}`;
      const focus = args[1] || '';
      if (!label) { console.error('Usage: write-session <label> [focus]'); process.exit(1); }
      const node = await mg.sessionOp({ action: 'open', label, focus });
      console.log(JSON.stringify({ uid: node.uid, label: node.label }));
      break;
    }

    case 'write-batch': {
      let data;
      if (args[0] && args[0] !== '-') {
        data = JSON.parse(require('fs').readFileSync(args[0], 'utf8'));
      } else {
        const chunks = [];
        for await (const chunk of process.stdin) chunks.push(chunk);
        data = JSON.parse(chunks.join(''));
      }
      const { items, sessionUid, agentId } = data;
      const results = await writeBatch(items, { defaultAgentId: agentId, sessionUid });
      console.log(JSON.stringify(results, null, 2));
      break;
    }

    case 'search': {
      const query = args.join(' ');
      if (!query) { console.error('Usage: search <query>'); process.exit(1); }
      const results = await mg.search(sanitizeFtsQuery(query), { limit: 10 });
      if (!results || !results.length) { console.log('No results.'); break; }
      for (const r of results) {
        const node = r.node || r;
        console.log(`[${node.node_type}] ${node.label} (score: ${(r.score||0).toFixed(2)})`);
        if (node.summary) console.log(`  ${node.summary.slice(0, 120)}`);
        else if (node.props?.content) console.log(`  ${node.props.content.slice(0, 120)}`);
      }
      break;
    }

    case 'stats': {
      const s = await mg.stats();
      console.log(JSON.stringify(s, null, 2));
      break;
    }

    case 'health': {
      const h = await mg.health();
      console.log(h);
      break;
    }

    default: {
      console.log(`mindgraph-bridge — memory bridge for OpenClaw

Commands:
  context [--query "..."] [--limit N] [--layer X] [--type X]
    Pull enriched context from the graph using the cognitive retrieve tool

  write-fact <label> [content] [--confidence N]
    Capture a fact/claim using the ingest tool

  write-decision <label> [content]
    Capture a decision using the deliberation tool

  write-entity <label> <entity_type>
    Capture an entity using the manageEntity tool

  write-session <label> [focus]
    Start a session using the sessionOp tool

  write-batch <file.json | ->
    Bulk write from JSON: { items: [...], sessionUid?, agentId? }

  search <query>
    Search using the search tool

  stats
    Show graph statistics

  health
    Check server health
`);
      break;
    }
  }
}

// ─── Exports ──────────────────────────────────────────────────────────────────

module.exports = {
  openSession,
  closeSession,
  writeBatch,
  subAgentClient,
  mg,
};

if (require.main === module) {
  cli().catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
  });
}
