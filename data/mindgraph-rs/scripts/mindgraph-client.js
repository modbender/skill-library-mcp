/**
 * mindgraph-client.js
 * Node.js client for mindgraph-server.
 * Implements the Extended API Endpoint Specification (18 Cognitive Layer Tools).
 */

const fs = require('fs');
const path = require('path');

// ─── Config ──────────────────────────────────────────────────────────────────

function loadConfig() {
  const configPath = path.join(process.env.HOME, '.openclaw', 'mindgraph.json');
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const mg = config;
  return {
    baseUrl: `http://${mg.bind || '127.0.0.1'}:${mg.port || 18790}`,
    token: mg.token || '',
    defaultAgent: mg.default_agent || 'jaadu',
  };
}

const CONFIG = loadConfig();

// ─── HTTP helper ─────────────────────────────────────────────────────────────

async function request(method, path, body = null) {
  const { default: fetch } = await import('node-fetch').catch(() => {
    return { default: globalThis.fetch };
  });

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${CONFIG.token}`,
  };

  const opts = { method, headers };
  if (body !== null) opts.body = JSON.stringify(body);

  const res = await fetch(`${CONFIG.baseUrl}${path}`, opts);
  const text = await res.text();

  if (!res.ok) {
    let errBody = text;
    try { errBody = JSON.parse(text); } catch {}
    const msg = errBody.message || errBody.error || text;
    const error = new Error(`mindgraph ${method} ${path} → ${res.status}: ${msg}`);
    error.status = res.status;
    error.details = errBody;
    throw error;
  }

  if (!text || text === 'null') return null;
  try { return JSON.parse(text); } catch { return text; }
}

/**
 * Sanitise a node label for CozoDB FTS indexing.
 */
function sanitizeLabel(label) {
  if (!label || typeof label !== 'string') return label;
  return label
    .replace(/'/g, "'")
    .replace(/'/g, "'")
    .replace(/[:\\\/]/g, ' ')
    .replace(/\+/g, 'and')
    .replace(/\^/g, '')
    .replace(/~/g, '')
    .replace(/\*/g, '')
    .replace(/\?/g, '')
    .replace(/\s{2,}/g, ' ')
    .trim();
}

// ─── 1. Reality Layer (Ingest) ────────────────────────────────────────────────

async function ingest(label, content, action = 'observation', opts = {}) {
  return request('POST', '/reality/ingest', {
    action, // 'source', 'snippet', 'observation'
    label: sanitizeLabel(label),
    content,
    source_uid: opts.sourceUid,
    medium: opts.medium,
    url: opts.url,
    timestamp: opts.timestamp,
    confidence: opts.confidence,
    salience: opts.salience,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 2. Reality Layer (Entity) ────────────────────────────────────────────────

async function manageEntity(opts = {}) {
  return request('POST', '/reality/entity', {
    action: opts.action, // 'create', 'alias', 'resolve', 'fuzzy_resolve', 'merge'
    label: opts.label ? sanitizeLabel(opts.label) : undefined,
    entity_type: opts.entityType,
    text: opts.text,
    canonical_uid: opts.canonicalUid,
    alias_score: opts.aliasScore,
    keep_uid: opts.keepUid,
    merge_uid: opts.mergeUid,
    limit: opts.limit,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 3. Epistemic Layer (Argument) ───────────────────────────────────────────

async function addArgument(opts = {}) {
  return request('POST', '/epistemic/argument', {
    claim: opts.claim ? { ...opts.claim, label: sanitizeLabel(opts.claim.label) } : undefined,
    evidence: opts.evidence,
    warrant: opts.warrant ? { ...opts.warrant, principle: opts.warrant.principle || opts.warrant.explanation } : undefined,
    argument: opts.argument,
    refutes_uid: opts.refutesUid,
    extends_uid: opts.extendsUid,
    source_uids: opts.sourceUids,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 4. Epistemic Layer (Inquiry) ────────────────────────────────────────────

async function addInquiry(label, content, action, opts = {}) {
  return request('POST', '/epistemic/inquiry', {
    action, // 'hypothesis', 'theory', 'paradigm', 'anomaly', 'assumption', 'question', 'open_question'
    label: sanitizeLabel(label),
    content,
    status: opts.status,
    anomalous_to_uid: opts.anomalousToUid,
    assumes_uid: opts.assumesUid,
    tests_uid: opts.testsUid,
    addresses_uid: opts.addressesUid,
    confidence: opts.confidence,
    salience: opts.salience,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 5. Epistemic Layer (Structure) ──────────────────────────────────────────

async function addStructure(label, content, action, opts = {}) {
  return request('POST', '/epistemic/structure', {
    action, // 'concept', 'pattern', 'mechanism', 'model', 'analogy', 'theorem', 'equation'
    label: sanitizeLabel(label),
    content,
    summary: opts.summary,
    analogous_to_uid: opts.analogousToUid,
    transfers_to_uid: opts.transfersToUid,
    evaluates_uid: opts.evaluatesUid,
    outperforms_uid: opts.outperformsUid,
    chain_steps: opts.chainSteps,
    derived_from_uid: opts.derivedFromUid,
    proven_by_uid: opts.provenByUid,
    confidence: opts.confidence,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 6. Intent Layer (Commitment) ────────────────────────────────────────────

async function addCommitment(label, description, action, opts = {}) {
  return request('POST', '/intent/commitment', {
    action, // 'goal', 'project', 'milestone'
    label: sanitizeLabel(label),
    description,
    priority: opts.priority,
    status: opts.status,
    parent_uid: opts.parentUid,
    due_date: opts.dueDate,
    motivated_by_uid: opts.motivatedByUid,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 7. Intent Layer (Deliberation) ──────────────────────────────────────────

async function deliberate(opts = {}) {
  return request('POST', '/intent/deliberation', {
    action: opts.action, // 'open_decision', 'add_option', 'add_constraint', 'resolve'
    label: opts.label ? sanitizeLabel(opts.label) : undefined,
    description: opts.description,
    decision_uid: opts.decisionUid,
    chosen_option_uid: opts.chosenOptionUid,
    resolution_rationale: opts.resolutionRationale,
    constraint_type: opts.constraintType,
    blocks_uid: opts.blocksUid,
    informs_uid: opts.informsUid,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 8. Action Layer (Procedure) ─────────────────────────────────────────────

async function procedure(opts = {}) {
  return request('POST', '/action/procedure', {
    action: opts.action, // 'create_flow', 'add_step', 'add_affordance', 'add_control'
    label: opts.label ? sanitizeLabel(opts.label) : undefined,
    description: opts.description,
    flow_uid: opts.flowUid,
    step_order: opts.stepOrder,
    previous_step_uid: opts.previousStepUid,
    affordance_type: opts.affordanceType,
    control_type: opts.controlType,
    uses_affordance_uids: opts.usesAffordanceUids,
    goal_uid: opts.goalUid,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 9. Action Layer (Risk) ──────────────────────────────────────────────────

async function risk(opts = {}) {
  return request('POST', '/action/risk', {
    action: opts.action, // 'assess', 'get_assessments'
    label: opts.label ? sanitizeLabel(opts.label) : undefined,
    description: opts.description,
    assessed_uid: opts.assessedUid,
    severity: opts.severity,
    likelihood: opts.likelihood,
    mitigations: opts.mitigations,
    residual_risk: opts.residualRisk,
    filter_uid: opts.filterUid,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 10. Memory Layer (Session) ───────────────────────────────────────────────

async function sessionOp(opts = {}) {
  return request('POST', '/memory/session', {
    action: opts.action, // 'open', 'trace', 'close'
    label: opts.label ? sanitizeLabel(opts.label) : undefined,
    focus: opts.focus,
    session_uid: opts.sessionUid,
    trace_content: opts.traceContent,
    trace_type: opts.traceType,
    relevant_node_uids: opts.relevantNodeUids,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 11. Memory Layer (Distill) ───────────────────────────────────────────────

async function distill(label, content, opts = {}) {
  return request('POST', '/memory/distill', {
    label: sanitizeLabel(label),
    content,
    session_uid: opts.sessionUid,
    summarizes_uids: opts.summarizesUids,
    importance: opts.importance,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 12. Memory Layer (Config) ───────────────────────────────────────────────

async function memoryConfig(opts = {}) {
  return request('POST', '/memory/config', {
    action: opts.action, // 'set_preference', 'set_policy', 'get_preferences', 'get_policies'
    type: opts.type,
    label: opts.label ? sanitizeLabel(opts.label) : undefined,
    key: opts.key,
    value: opts.value,
    policy_content: opts.policyContent,
    applies_to_layers: opts.appliesToLayers,
    decay_half_life: opts.decayHalfLife,
    privacy_default: opts.privacyDefault,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 13. Agent Layer (Plan) ──────────────────────────────────────────────────

async function plan(opts = {}) {
  return request('POST', '/agent/plan', {
    action: opts.action, // 'create_task', 'create_plan', 'add_step', 'update_status', 'get_plan'
    label: opts.label ? sanitizeLabel(opts.label) : undefined,
    description: opts.description,
    goal_uid: opts.goalUid,
    task_uid: opts.taskUid,
    plan_uid: opts.planUid,
    step_order: opts.stepOrder,
    depends_on_uids: opts.dependsOnUids,
    target_uid: opts.targetUid,
    status: opts.status,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 14. Agent Layer (Governance) ────────────────────────────────────────────

async function governance(opts = {}) {
  return request('POST', '/agent/governance', {
    action: opts.action, // 'create_policy', 'set_budget', 'request_approval', 'resolve_approval'
    label: opts.label ? sanitizeLabel(opts.label) : undefined,
    policy_content: opts.policyContent,
    policy_scope: opts.policyScope,
    budget_type: opts.budgetType,
    budget_limit: opts.budgetLimit,
    governed_uid: opts.governedUid,
    approval_request: opts.approvalRequest,
    approval_uid: opts.approvalUid,
    approved: opts.approved,
    resolution_note: opts.resolutionNote,
    requires_plan_uid: opts.requiresPlanUid,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 15. Agent Layer (Execution) ─────────────────────────────────────────────

async function execution(opts = {}) {
  return request('POST', '/agent/execution', {
    action: opts.action, // 'start', 'complete', 'fail', 'register_agent'
    label: opts.label ? sanitizeLabel(opts.label) : undefined,
    plan_uid: opts.planUid,
    executor_uid: opts.executorUid,
    execution_uid: opts.executionUid,
    outcome: opts.outcome,
    produces_node_uid: opts.producesNodeUid,
    error_description: opts.errorDescription,
    agent_name: opts.agentName,
    agent_role: opts.agentRole,
    filter_plan_uid: opts.filterPlanUid,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 16. Connective Tissue (Retrieve) ────────────────────────────────────────

async function embedText(text) {
  // Embed query text client-side via OpenAI — server has no HTTP client
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error('OPENAI_API_KEY not set — cannot embed query for semantic search');
  const https = require('https');
  const body = JSON.stringify({ input: text, model: 'text-embedding-3-small' });
  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: 'api.openai.com',
      path: '/v1/embeddings',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
      },
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (parsed.error) return reject(new Error(parsed.error.message));
          resolve(parsed.data[0].embedding);
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

async function retrieve(mode, opts = {}) {
  // Semantic mode: embed query client-side, then POST /embeddings/search
  if (mode === 'semantic') {
    if (!opts.query) throw new Error('retrieve("semantic") requires opts.query');
    const vector = await embedText(opts.query);
    const results = await request('POST', '/embeddings/search', {
      query: vector,              // server field name is 'query', not 'vector'
      k: opts.k || opts.limit || 10,
    });
    // Normalize: server returns [{node, score}], flatten to [{...nodeFields, score}]
    if (Array.isArray(results)) {
      return results.map(r => ({ ...r.node, score: r.score }));
    }
    return results;
  }

  return request('POST', '/retrieve', {
    action: mode,   // server expects 'action', not 'mode'
    query: opts.query,
    k: opts.k,
    threshold: opts.threshold,
    layer: opts.layer,
    node_types: opts.nodeTypes,
    confidence_min: opts.confidenceMin,
    salience_min: opts.salienceMin,
    limit: opts.limit,
    offset: opts.offset,
  });
}

// ─── 17. Connective Tissue (Traverse) ────────────────────────────────────────

async function traverse(mode, startUid, opts = {}) {
  return request('POST', '/traverse', {
    mode,
    start_uid: startUid,
    end_uid: opts.endUid,
    max_depth: opts.maxDepth,
    direction: opts.direction,
    edge_types: opts.edgeTypes,
    weight_threshold: opts.weightThreshold,
    include_tombstoned: opts.includeTombstoned,
  });
}

// ─── 18. Connective Tissue (Evolve) ──────────────────────────────────────────

async function evolve(action, uid, opts = {}) {
  return request('POST', '/evolve', {
    action, // 'update', 'tombstone', 'restore', 'decay', 'history', 'snapshot'
    uid,
    label: opts.label ? sanitizeLabel(opts.label) : undefined,
    summary: opts.summary,
    confidence: opts.confidence,
    salience: opts.salience,
    props_patch: opts.propsPatch,
    reason: opts.reason,
    cascade: opts.cascade,
    half_life_secs: opts.halfLifeSecs,
    min_salience: opts.minSalience,
    min_age_secs: opts.minAgeSecs,
    version: opts.version,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── Low-level CRUD (Backward Compatibility) ───────────────────────────────

async function addNode(label, props, opts = {}) {
  return request('POST', '/node', {
    label: sanitizeLabel(label),
    props,
    confidence: opts.confidence,
    salience: opts.salience,
    summary: opts.summary,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

async function getNode(uid) {
  return request('GET', `/node/${uid}`);
}

async function updateNode(uid, updates, opts = {}) {
  return request('PATCH', `/node/${uid}`, {
    ...updates,
    agent_id: opts.agentId || CONFIG.defaultAgent,
    reason: opts.reason || 'updated via client',
  });
}

async function deleteNode(uid, opts = {}) {
  const params = new URLSearchParams({
    reason: opts.reason || 'deleted via client',
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
  return request('DELETE', `/node/${uid}?${params}`);
}

async function link(fromUid, toUid, edgeType, opts = {}) {
  return request('POST', '/link', {
    from_uid: fromUid,
    to_uid: toUid,
    edge_type: edgeType,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

async function getEdges(fromUid, opts = {}) {
  const params = new URLSearchParams({ from_uid: fromUid });
  if (opts.edgeType) params.set('edge_type', opts.edgeType);
  const result = await request('GET', `/edges?${params}`);
  return Array.isArray(result) ? result : (result?.items ?? result ?? []);
}

async function edgesTo(uid, edgeType) {
  const params = new URLSearchParams({ to_uid: uid });
  if (edgeType) params.set('edge_type', edgeType);
  const result = await request('GET', `/edges?${params}`);
  return Array.isArray(result) ? result : (result?.items ?? result ?? []);
}

async function edgeBetween(fromUid, toUid, edgeType) {
  // Returns the edge if one exists between fromUid → toUid, else null
  const params = new URLSearchParams({ from_uid: fromUid, to_uid: toUid });
  if (edgeType) params.set('edge_type', edgeType);
  const result = await request('GET', `/edges?${params}`);
  const arr = Array.isArray(result) ? result : (result?.items ?? []);
  return arr.length > 0 ? arr[0] : null;
}

async function openDecisions(opts = {}) {
  // Retrieve Decision nodes with status = 'open'
  const result = await getNodes({ nodeType: 'Decision', limit: opts.limit ?? 100, offset: opts.offset ?? 0 });
  const items = Array.isArray(result) ? result : (result?.items ?? []);
  return items.filter(n => {
    const status = n.props?.status ?? n.props?.decision_status;
    return !status || status === 'open';
  });
}

async function stats() {
  return request('GET', '/stats');
}

async function health() {
  return request('GET', '/health');
}

async function search(query, opts = {}) {
  return request('POST', '/search', {
    query: sanitizeLabel(query),
    node_type: opts.nodeType,
    layer: opts.layer,
    limit: opts.limit,
    min_score: opts.minScore,
  });
}

async function getNodes(opts = {}) {
  const params = new URLSearchParams();
  if (opts.layer) params.set('layer', opts.layer);
  if (opts.nodeType) params.set('node_type', opts.nodeType);
  if (opts.labelContains) params.set('label_contains', opts.labelContains);
  if (opts.agent) params.set('agent', opts.agent);
  params.set('limit', opts.limit || 100);
  params.set('offset', opts.offset || 0);
  return request('GET', `/nodes?${params}`);
}

// ─── Exports ──────────────────────────────────────────────────────────────────

module.exports = {
  health,
  stats,
  search,
  getNodes,
  // 1. Reality
  ingest,
  // 2. Entity
  manageEntity,
  // 3. Argument
  addArgument,
  // 4. Inquiry
  addInquiry,
  // 5. Structure
  addStructure,
  // 6. Commitment
  addCommitment,
  // 7. Deliberation
  deliberate,
  // 8. Procedure
  procedure,
  // 9. Risk
  risk,
  // 10. Session
  sessionOp,
  // 11. Distill
  distill,
  // 12. Config
  memoryConfig,
  // 13. Plan
  plan,
  // 14. Governance
  governance,
  // 15. Execution
  execution,
  // 16. Retrieve
  retrieve,
  // 17. Traverse
  traverse,
  // 18. Evolve
  evolve,
  // Low-level & Compat
  addNode,
  getNode,
  updateNode,
  deleteNode,
  link,
  getEdges,
  edgesTo,
  edgeBetween,
  openDecisions,
  sanitizeLabel,
};
