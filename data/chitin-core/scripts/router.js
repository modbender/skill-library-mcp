#!/usr/bin/env node
/**
 * ModelRouter 9001 — Definitive model routing for OpenClaw agents.
 * Perfect fallback + cost-effective routing in one skill.
 * 
 * Usage:
 *   node router.js route "task description"
 *   node router.js fail "provider/model" "error message"
 *   node router.js health
 *   node router.js costs
 *   node router.js validate
 */

const fs = require('fs');
const path = require('path');

// Paths
const SKILL_DIR = path.dirname(__dirname);
const CONFIG_PATH = path.join(SKILL_DIR, 'config.json');
const OC_CONFIG_PATH = path.join(process.env.HOME, '.openclaw', 'openclaw.json');
const STATE_PATH = path.join(process.env.HOME, '.openclaw', 'workspace', 'memory', 'modelrouter-state.json');

// --- Config Loading ---

function loadConfig() {
  try {
    return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  } catch (e) {
    console.error(JSON.stringify({ error: 'config_load_failed', detail: e.message }));
    process.exit(1);
  }
}

function loadState() {
  try {
    if (fs.existsSync(STATE_PATH)) {
      return JSON.parse(fs.readFileSync(STATE_PATH, 'utf8'));
    }
  } catch (e) { /* corrupt state, reset */ }
  return { cooldowns: {}, costs: {}, stats: { totalRouted: 0, byTier: {} } };
}

function saveState(state) {
  const dir = path.dirname(STATE_PATH);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(STATE_PATH, JSON.stringify(state, null, 2));
}

function getAvailableProviders() {
  try {
    const oc = JSON.parse(fs.readFileSync(OC_CONFIG_PATH, 'utf8'));
    const providers = oc?.models?.providers || {};
    const available = new Set();
    for (const [provName, provConfig] of Object.entries(providers)) {
      const models = provConfig.models || [];
      for (const m of models) {
        const id = typeof m === 'string' ? m : m.id;
        available.add(`${provName}/${id}`);
      }
    }
    return available;
  } catch (e) {
    return new Set();
  }
}

// --- Task Classifier ---

const SCORING_DIMENSIONS = {
  codeSignals: {
    keywords: ['code', 'function', 'debug', 'implement', 'refactor', 'api', 'endpoint',
               'react', 'typescript', 'javascript', 'python', 'rust', 'sql', 'css',
               'component', 'module', 'class', 'interface', 'compile', 'lint', 'test',
               'git', 'commit', 'merge', 'deploy', 'docker', 'kubernetes', 'ci/cd',
               'regex', 'parse', 'serialize', 'algorithm', 'data structure'],
    weight: 1.2,
    direction: 1
  },
  reasoningSignals: {
    keywords: ['prove', 'derive', 'theorem', 'analyze', 'step by step', 'reason',
               'evaluate', 'compare', 'trade-off', 'tradeoff', 'architecture',
               'design', 'strategy', 'optimize', 'complex', 'nuanced', 'subtle'],
    weight: 1.5,
    direction: 1
  },
  simpleSignals: {
    keywords: ['hello', 'hi ', 'thanks', 'thank you', 'quick question', 'what time',
               'weather', 'how are you', 'good morning', 'good night',
               'yes', ' ok', 'sure', 'got it', 'cool', 'nice'],
    weight: 1.0,
    direction: -1  // pushes toward LIGHT
  },
  agenticSignals: {
    keywords: ['execute', 'run', 'build', 'create', 'set up', 'configure',
               'install', 'migrate', 'automate', 'orchestrate', 'pipeline',
               'workflow', 'spawn', 'sub-agent', 'subagent'],
    weight: 1.3,
    direction: 1
  },
  constraintSignals: {
    keywords: ['must', 'required', 'constraint', 'exactly', 'strict', 'production',
               'security', 'audit', 'compliance', 'enterprise', 'scale'],
    weight: 0.8,
    direction: 1
  },
  creativeSignals: {
    keywords: ['write', 'story', 'poem', 'creative', 'narrative', 'blog',
               'article', 'essay', 'fiction', 'character'],
    weight: 0.9,
    direction: 0.5  // medium, not heavy
  },
  domainSignals: {
    keywords: ['medical', 'legal', 'financial', 'scientific', 'cryptographic',
               'blockchain', 'quantum', 'genomic', 'pharmaceutical'],
    weight: 1.4,
    direction: 1
  }
};

function classifyTask(taskText) {
  const text = taskText.toLowerCase();

  // Check for override tags
  const overrides = { '@light': 'LIGHT', '@medium': 'MEDIUM', '@heavy': 'HEAVY' };
  for (const [tag, tier] of Object.entries(overrides)) {
    if (text.includes(tag)) {
      return { tier, score: 0, confidence: 1.0, override: tag, signals: [] };
    }
  }

  let score = 0;
  const signals = [];

  // Score each dimension
  for (const [dimName, dim] of Object.entries(SCORING_DIMENSIONS)) {
    let dimHits = 0;
    for (const kw of dim.keywords) {
      if (text.includes(kw)) dimHits++;
    }
    if (dimHits > 0) {
      const dimScore = dimHits * dim.weight * dim.direction;
      score += dimScore;
      signals.push(`${dimName}:${dimHits}×${dim.weight}=${dimScore.toFixed(1)}`);
    }
  }

  // Length signal (word count as proxy for complexity)
  const wordCount = text.split(/\s+/).length;
  if (wordCount > 200) {
    score += 1.5;
    signals.push(`length:${wordCount}w=+1.5`);
  } else if (wordCount > 50) {
    score += 0.5;
    signals.push(`length:${wordCount}w=+0.5`);
  } else if (wordCount < 10) {
    score -= 0.5;
    signals.push(`length:${wordCount}w=-0.5`);
  }

  // Determine tier from score
  const config = loadConfig();
  const boundaries = config.boundaries || { lightMedium: 1.0, mediumHeavy: 4.0 };

  let tier;
  if (score < boundaries.lightMedium) tier = 'LIGHT';
  else if (score < boundaries.mediumHeavy) tier = 'MEDIUM';
  else tier = 'HEAVY';

  // Confidence based on distance from boundary
  const distFromNearest = Math.min(
    Math.abs(score - boundaries.lightMedium),
    Math.abs(score - boundaries.mediumHeavy)
  );
  const confidence = Math.min(1.0, 0.5 + distFromNearest * 0.15);

  return { tier, score: Math.round(score * 100) / 100, confidence: Math.round(confidence * 100) / 100, signals };
}

// --- Model Selection ---

function selectModel(tier, config, state, availableProviders) {
  const now = new Date().toISOString();
  const tierModels = config.tiers[tier] || [];

  // Filter: must be in openclaw.json AND not in cooldown
  const candidates = tierModels.filter(m => {
    const fullId = `${m.provider}/${m.model}`;
    // Check if provider/model exists in openclaw config
    if (availableProviders.size > 0 && !availableProviders.has(fullId)) return false;
    // Check cooldown
    const cd = state.cooldowns[fullId];
    if (cd && new Date(cd.until) > new Date(now)) return false;
    return true;
  });

  if (candidates.length > 0) {
    // Sort by input cost (cheapest first)
    candidates.sort((a, b) => a.inputCost - b.inputCost);
    const selected = candidates[0];
    return {
      model: `${selected.provider}/${selected.model}`,
      inputCost: selected.inputCost,
      outputCost: selected.outputCost,
      tier
    };
  }

  return null; // No model available in this tier
}

function selectWithFallback(tier, config, state, availableProviders) {
  // Try requested tier first
  let result = selectModel(tier, config, state, availableProviders);
  if (result) return result;

  // Escalate: LIGHT → MEDIUM → HEAVY
  const escalation = { LIGHT: ['MEDIUM', 'HEAVY'], MEDIUM: ['HEAVY', 'LIGHT'], HEAVY: ['MEDIUM', 'LIGHT'] };
  for (const fallbackTier of (escalation[tier] || [])) {
    result = selectModel(fallbackTier, config, state, availableProviders);
    if (result) {
      result.fallbackFrom = tier;
      return result;
    }
  }

  // All tiers exhausted — find earliest cooldown expiry
  let earliestRetry = null;
  for (const [, cd] of Object.entries(state.cooldowns)) {
    if (!earliestRetry || new Date(cd.until) < new Date(earliestRetry)) {
      earliestRetry = cd.until;
    }
  }

  return {
    error: 'all_providers_down',
    retryAfter: earliestRetry || new Date(Date.now() + 300000).toISOString(),
    message: 'All configured models are rate-limited or unavailable. Try again later.'
  };
}

// --- Cost Tracking ---

function trackCost(state, model, tier, inputCost, outputCost) {
  const today = new Date().toISOString().slice(0, 10);
  if (!state.costs[today]) {
    state.costs[today] = { total: 0, byTier: {}, byModel: {} };
  }

  // Estimate tokens: rough average per tier
  const avgOutputTokens = { LIGHT: 200, MEDIUM: 800, HEAVY: 2000 };
  const estInputTokens = 500; // rough average
  const estOutputTokens = avgOutputTokens[tier] || 500;
  const cost = (estInputTokens * inputCost + estOutputTokens * outputCost) / 1000000;

  state.costs[today].total = Math.round((state.costs[today].total + cost) * 10000) / 10000;
  state.costs[today].byTier[tier] = Math.round(((state.costs[today].byTier[tier] || 0) + cost) * 10000) / 10000;
  state.costs[today].byModel[model] = Math.round(((state.costs[today].byModel[model] || 0) + cost) * 10000) / 10000;

  // Update stats
  state.stats.totalRouted++;
  state.stats.byTier[tier] = (state.stats.byTier[tier] || 0) + 1;

  return cost;
}

// --- Commands ---

function cmdRoute(taskText) {
  const config = loadConfig();
  const state = loadState();
  const available = getAvailableProviders();
  const classification = classifyTask(taskText);
  const selection = selectWithFallback(classification.tier, config, state, available);

  if (selection.error) {
    console.log(JSON.stringify(selection));
    return;
  }

  const cost = trackCost(state, selection.model, selection.tier, selection.inputCost, selection.outputCost);
  saveState(state);

  console.log(JSON.stringify({
    tier: selection.tier,
    model: selection.model,
    confidence: classification.confidence,
    score: classification.score,
    estimatedCost: Math.round(cost * 10000) / 10000,
    signals: classification.signals,
    ...(selection.fallbackFrom ? { fallbackFrom: selection.fallbackFrom } : {}),
    ...(classification.override ? { override: classification.override } : {})
  }));
}

function cmdFail(model, errorMsg) {
  const state = loadState();
  const now = new Date();
  let cooldownMs = 5 * 60 * 60 * 1000; // 5 hours default

  const errLower = (errorMsg || '').toLowerCase();

  // Parse retry-after from error message
  const retryMatch = errLower.match(/try again in (\d+)m(\d+)?s?/i);
  if (retryMatch) {
    cooldownMs = (parseInt(retryMatch[1]) * 60 + (parseInt(retryMatch[2]) || 0)) * 1000;
  }
  // Google quota → midnight PT
  else if (errLower.includes('resource_exhausted') || errLower.includes('quota')) {
    const midnightPT = new Date();
    midnightPT.setUTCHours(8, 0, 0, 0); // midnight PT = 08:00 UTC
    if (midnightPT <= now) midnightPT.setDate(midnightPT.getDate() + 1);
    cooldownMs = midnightPT - now;
  }
  // Anthropic daily → midnight UTC
  else if (errLower.includes('daily') || errLower.includes('rate limit')) {
    const midnightUTC = new Date();
    midnightUTC.setUTCHours(0, 0, 0, 0);
    midnightUTC.setDate(midnightUTC.getDate() + 1);
    cooldownMs = midnightUTC - now;
  }
  // Auth error → long cooldown (likely permanent until config fix)
  else if (errLower.includes('401') || errLower.includes('403') || errLower.includes('unauthorized')) {
    cooldownMs = 24 * 60 * 60 * 1000; // 24 hours
  }

  const until = new Date(now.getTime() + cooldownMs).toISOString();
  state.cooldowns[model] = {
    until,
    reason: errorMsg || 'unknown',
    hitAt: now.toISOString()
  };

  saveState(state);
  console.log(JSON.stringify({ model, cooldownUntil: until, cooldownMinutes: Math.round(cooldownMs / 60000) }));
}

function cmdHealth() {
  const config = loadConfig();
  const state = loadState();
  const available = getAvailableProviders();
  const now = new Date();

  const models = [];
  let healthy = 0, limited = 0, unavailable = 0;

  for (const [tierName, tierModels] of Object.entries(config.tiers)) {
    for (const m of tierModels) {
      const fullId = `${m.provider}/${m.model}`;
      const inConfig = available.size === 0 || available.has(fullId);
      const cd = state.cooldowns[fullId];
      const isLimited = cd && new Date(cd.until) > now;

      let status;
      if (!inConfig) { status = 'not_configured'; unavailable++; }
      else if (isLimited) { status = 'rate_limited'; limited++; }
      else { status = 'healthy'; healthy++; }

      models.push({
        model: fullId,
        tier: tierName,
        status,
        ...(isLimited ? { cooldownUntil: cd.until, reason: cd.reason } : {}),
        cost: `$${m.inputCost}/$${m.outputCost} per 1M tokens`
      });
    }
  }

  console.log(JSON.stringify({ healthy, limited, unavailable, models }, null, 2));
}

function cmdCosts() {
  const state = loadState();
  const today = new Date().toISOString().slice(0, 10);
  const todayCosts = state.costs[today] || { total: 0, byTier: {}, byModel: {} };

  // Calculate week total
  const weekAgo = new Date(Date.now() - 7 * 86400000);
  let weekTotal = 0;
  for (const [date, data] of Object.entries(state.costs)) {
    if (new Date(date) >= weekAgo) weekTotal += data.total;
  }

  console.log(JSON.stringify({
    today: todayCosts.total,
    thisWeek: Math.round(weekTotal * 10000) / 10000,
    todayByTier: todayCosts.byTier,
    todayByModel: todayCosts.byModel,
    totalRouted: state.stats.totalRouted,
    routedByTier: state.stats.byTier
  }, null, 2));
}

function cmdValidate() {
  const config = loadConfig();
  const available = getAvailableProviders();

  if (available.size === 0) {
    console.log(JSON.stringify({ valid: false, error: 'Cannot read openclaw.json', availableModels: 0 }));
    return;
  }

  const allConfigured = [];
  const missing = [];
  const matched = [];

  for (const [tierName, tierModels] of Object.entries(config.tiers)) {
    for (const m of tierModels) {
      const fullId = `${m.provider}/${m.model}`;
      allConfigured.push(fullId);
      if (available.has(fullId)) matched.push(fullId);
      else missing.push({ model: fullId, tier: tierName });
    }
  }

  console.log(JSON.stringify({
    valid: matched.length > 0,
    totalConfigured: allConfigured.length,
    availableModels: matched.length,
    missingModels: missing,
    availableProviders: [...available]
  }, null, 2));
}

// --- Main ---

const [,, command, ...args] = process.argv;

switch (command) {
  case 'route':
    if (!args.length) { console.error('Usage: router.js route "task text"'); process.exit(1); }
    cmdRoute(args.join(' '));
    break;
  case 'fail':
    if (args.length < 2) { console.error('Usage: router.js fail "provider/model" "error"'); process.exit(1); }
    cmdFail(args[0], args.slice(1).join(' '));
    break;
  case 'health':
    cmdHealth();
    break;
  case 'costs':
    cmdCosts();
    break;
  case 'validate':
    cmdValidate();
    break;
  default:
    console.log(JSON.stringify({
      name: 'ModelRouter 9001',
      version: '1.0.0',
      commands: ['route', 'fail', 'health', 'costs', 'validate'],
      usage: 'node router.js <command> [args]'
    }));
}
