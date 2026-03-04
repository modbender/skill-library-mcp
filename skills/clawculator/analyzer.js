'use strict';

const fs   = require('fs');
const path = require('path');
const os   = require('os');

// ── Model pricing (per million tokens, input/output) ─────────────
const MODEL_PRICING = {
  'claude-opus-4-6':              { input: 5.00,  output: 25.00, label: 'Claude Opus 4.6' },
  'claude-opus-4-5':              { input: 5.00,  output: 25.00, label: 'Claude Opus 4.5' },
  'claude-sonnet-4-5-20250929':   { input: 3.00,  output: 15.00, label: 'Claude Sonnet 4.5' },
  'claude-sonnet-4-6':            { input: 3.00,  output: 15.00, label: 'Claude Sonnet 4.6' },
  'claude-haiku-4-5-20251001':    { input: 0.80,  output: 4.00,  label: 'Claude Haiku 4.5' },
  'claude-haiku-4-5':             { input: 0.80,  output: 4.00,  label: 'Claude Haiku 4.5' },
  'claude-3-5-sonnet-20241022':   { input: 3.00,  output: 15.00, label: 'Claude 3.5 Sonnet' },
  'claude-3-5-haiku-20241022':    { input: 0.80,  output: 4.00,  label: 'Claude 3.5 Haiku' },
  'claude-3-opus-20240229':       { input: 15.00, output: 75.00, label: 'Claude 3 Opus' },
  'gpt-4o':                       { input: 2.50,  output: 10.00, label: 'GPT-4o' },
  'gpt-4o-mini':                  { input: 0.15,  output: 0.60,  label: 'GPT-4o Mini' },
  'gpt-4-turbo':                  { input: 10.00, output: 30.00, label: 'GPT-4 Turbo' },
  'gpt-5.2':                      { input: 10.00, output: 40.00, label: 'GPT-5.2' },
  'gpt-5-mini':                   { input: 0.40,  output: 1.60,  label: 'GPT-5 Mini' },
  'gpt-5.3-codex':                { input: 0,     output: 0,     label: 'Codex (subscription)', subscription: true },
  'gemini-1.5-pro':               { input: 1.25,  output: 5.00,  label: 'Gemini 1.5 Pro' },
  'gemini-1.5-flash':             { input: 0.075, output: 0.30,  label: 'Gemini 1.5 Flash' },
  'gemini-2.0-flash':             { input: 0.10,  output: 0.40,  label: 'Gemini 2.0 Flash' },
  'gemini-2.5-flash':             { input: 0.15,  output: 0.60,  label: 'Gemini 2.5 Flash' },
  'gemini-2.5-pro':               { input: 1.25,  output: 10.00, label: 'Gemini 2.5 Pro' },
};

// OpenRouter adds ~8-10% markup on top of provider pricing
const OPENROUTER_MARKUP = 0.10;

// ── Deterministic fix recommendations ────────────────────────────
const FIXES = {
  HEARTBEAT_PAID_MODEL: {
    fix: 'Set heartbeat.model to a free local Ollama model',
    command: 'ollama pull qwen2.5:0.5b  →  set heartbeat.model = "ollama/qwen2.5:0.5b"',
  },
  HEARTBEAT_TARGET: {
    fix: 'Set heartbeat.target to "none" (required since v2026.2.24)',
    command: 'openclaw config set agents.defaults.heartbeat.target none',
  },
  WHATSAPP_GROUPS_OPEN: {
    fix: 'Set whatsapp.groups to {} to block all groups from auto-processing',
    command: 'openclaw config set channels.whatsapp.groups \'{}\'',
  },
  WHATSAPP_GROUPS_ACTIVE: {
    fix: 'Review each active WhatsApp group — every message costs tokens on your primary model',
    command: 'Remove group IDs from channels.whatsapp.groups to stop processing them',
  },
  TELEGRAM_OPEN: {
    fix: 'Telegram dmPolicy is "open" — anyone can find and message your bot, running up your bill',
    command: 'openclaw config set channels.telegram.dmPolicy allowlist',
  },
  DISCORD_OPEN: {
    fix: 'Discord DM policy is "open" — restrict to allowlist to prevent unknown users billing you',
    command: 'openclaw config set channels.discord.dm.policy allowlist',
  },
  SIGNAL_OPEN: {
    fix: 'Signal has no allowlist — anyone who has your number can message your agent',
    command: 'Add allowFrom list to channels.signal config',
  },
  HOOK_PAID_MODEL: (name) => ({
    fix: `Switch hook "${name}" to Haiku — 80% cheaper than Sonnet for simple tasks`,
    command: `openclaw config set hooks.${name}.model claude-haiku-4-5-20251001`,
  }),
  SKILL_POLLING: (name) => ({
    fix: `Skill "${name}" is polling on a paid model — switch to Ollama or increase interval`,
    command: `Set skills.${name}.model = "ollama/qwen2.5:0.5b" in openclaw.json`,
  }),
  CRON_PAID_MODEL: (name, interval) => ({
    fix: `Cron job "${name}" running every ${interval} on a paid model`,
    command: `Add model: "ollama/qwen2.5:0.5b" to cron job "${name}" config, or increase interval`,
  }),
  MAX_CONCURRENT: {
    fix: 'Reduce maxConcurrent to 2 — high concurrency multiplies cost spikes',
    command: 'openclaw config set agents.defaults.subagents.maxConcurrent 2',
  },
  ORPHANED_SESSIONS: {
    fix: 'Delete sessions.json to clear orphaned sessions — they auto-rebuild on next use',
    command: 'rm ~/.openclaw/agents/main/sessions/sessions.json',
  },
  LARGE_SESSIONS: {
    fix: 'Reduce root-level .md files in your workspace to shrink session context size',
    command: 'Move inactive files to ~/clawd/archive/ and ~/clawd/projects/',
  },
  WORKSPACE_BLOAT: {
    fix: 'Move inactive files to /archive/ and /projects/ subdirectories',
    command: 'mkdir -p ~/clawd/archive ~/clawd/projects  # then move unused .md files',
  },
  MEMORY_FLUSH_PAID: {
    fix: 'memoryFlush inherits your primary model — consider routing compaction to Haiku',
    command: 'Check openclaw.json for memoryFlush.model support in your version',
  },
  CONTEXT_PRUNING_MISSING: {
    fix: 'Add contextPruning to prevent unbounded session growth — each message re-sends full history',
    command: 'openclaw config set agents.defaults.session.contextPruning.mode sliding',
  },
  FALLBACK_EXPENSIVE: (model, position) => ({
    fix: `Fallback position ${position} is an expensive model (${model}) — silent cost escalation on rate limits`,
    command: `Replace ${model} in fallbacks array with a cheaper model like claude-haiku-4-5-20251001`,
  }),
  OPENROUTER_MARKUP: {
    fix: 'OpenRouter adds ~10% markup over direct provider pricing — use direct API keys where possible',
    command: 'Replace openrouter/* model refs with direct anthropic/* or openai/* equivalents',
  },
  IMAGE_DIMENSION: {
    fix: 'Lower imageMaxDimensionPx to reduce vision token costs — default 1200px is expensive',
    command: 'openclaw config set agents.defaults.imageMaxDimensionPx 800',
  },
  MULTI_AGENT_PAID: (agentId) => ({
    fix: `Agent "${agentId}" has its own expensive model config — each agent bills independently`,
    command: `Review agents.list[${agentId}].model config and apply same cost rules as primary agent`,
  }),
};

// ── Helpers ───────────────────────────────────────────────────────
function readJSON(filePath) {
  try {
    if (!fs.existsSync(filePath)) return null;
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch { return null; }
}

function resolveModel(modelStr) {
  if (!modelStr) return null;
  // Strip provider prefix for lookup (anthropic/claude-sonnet → claude-sonnet)
  const stripped = modelStr.toLowerCase().replace(/^(anthropic|openai|google|openrouter\/[^/]+)\//, '');
  if (MODEL_PRICING[stripped]) return stripped;
  for (const key of Object.keys(MODEL_PRICING)) {
    if (stripped.includes(key) || key.includes(stripped)) return key;
  }
  return isLocalModel(modelStr) ? 'ollama' : null;
}

function isLocalModel(modelStr) {
  if (!modelStr) return false;
  const lower = modelStr.toLowerCase();
  return lower.startsWith('ollama/') || lower === 'ollama' ||
    ['qwen', 'llama', 'mistral', 'phi', 'gemma', 'deepseek', 'kimi'].some(m => lower.includes(m));
}

function isHaikuTier(modelStr) {
  if (!modelStr) return false;
  const lower = modelStr.toLowerCase();
  return lower.includes('haiku');
}

function isAcceptableForHooks(modelStr) {
  return isLocalModel(modelStr) || isHaikuTier(modelStr);
}

function isOpenRouter(modelStr) {
  return modelStr?.toLowerCase().startsWith('openrouter/');
}

function costPerCall(modelKey, inputTok = 1000, outputTok = 500) {
  if (!modelKey || modelKey === 'ollama') return 0;
  const p = MODEL_PRICING[modelKey];
  if (!p || p.subscription) return 0;
  return (inputTok / 1e6) * p.input + (outputTok / 1e6) * p.output;
}

function modelTier(modelKey) {
  if (!modelKey || modelKey === 'ollama') return 'free';
  const p = MODEL_PRICING[modelKey];
  if (!p) return 'unknown';
  if (p.input >= 5)  return 'expensive';
  if (p.input >= 1)  return 'medium';
  if (p.input >= 0.5) return 'cheap';
  return 'very-cheap';
}

// ── Rule: Analyze a single agent config block ─────────────────────
function analyzeAgentBlock(agentCfg, primaryModel, agentId = 'main') {
  const findings = [];
  const prefix = agentId === 'main' ? '' : `[Agent: ${agentId}] `;

  // ── Heartbeat ──────────────────────────────────────────────────
  const hb = agentCfg.heartbeat;
  if (hb) {
    const hbModel    = hb.model || primaryModel;
    const hbKey      = resolveModel(hbModel);
    const hbInterval = typeof hb.interval === 'number' ? hb.interval :
                       typeof hb.every === 'string' ? parseInterval(hb.every) : 60;
    const hbPerDay   = Math.floor(86400 / Math.max(hbInterval, 1));

    if (!isLocalModel(hbModel)) {
      const daily   = costPerCall(hbKey, 500, 100) * hbPerDay;
      const monthly = daily * 30;
      findings.push({
        severity: 'critical', source: 'heartbeat',
        message: `${prefix}Heartbeat running on paid model: ${hbModel || 'primary'}`,
        detail: `${hbPerDay} pings/day · $${daily.toFixed(4)}/day`,
        monthlyCost: monthly,
        ...FIXES.HEARTBEAT_PAID_MODEL,
      });
    } else {
      findings.push({
        severity: 'info', source: 'heartbeat',
        message: `${prefix}Heartbeat using local model (${hbModel}) ✓`,
        detail: `${hbPerDay} pings/day · $0.00 cost`, monthlyCost: 0,
      });
    }

    if (hb.target && hb.target !== 'none') {
      findings.push({
        severity: 'high', source: 'heartbeat',
        message: `${prefix}Heartbeat target is "${hb.target}" — must be "none" (v2026.2.24+)`,
        detail: 'Non-"none" targets silently trigger paid model sessions',
        ...FIXES.HEARTBEAT_TARGET,
      });
    }
  }

  // ── Fallback chain ─────────────────────────────────────────────
  const fallbacks = agentCfg.model?.fallbacks || agentCfg.models?.fallbacks || [];
  if (fallbacks.length > 0) {
    fallbacks.forEach((fb, i) => {
      const fbKey  = resolveModel(fb);
      const tier   = modelTier(fbKey);
      const isOR   = isOpenRouter(fb);
      if (tier === 'expensive' || tier === 'medium') {
        const monthly = costPerCall(fbKey, 2000, 500) * 50 * 30;
        findings.push({
          severity: tier === 'expensive' ? 'high' : 'medium',
          source: 'fallbacks',
          message: `${prefix}Fallback #${i + 1} is expensive (${fb}) — silent cost spike on rate limits`,
          detail: `If primary hits rate limit, falls back to ${fb} at ~$${monthly.toFixed(2)}/month equivalent`,
          monthlyCost: 0, // only triggered on rate limit, not always-on
          ...FIXES.FALLBACK_EXPENSIVE(fb, i + 1),
        });
      }
      if (isOR) {
        findings.push({
          severity: 'medium', source: 'fallbacks',
          message: `${prefix}Fallback uses OpenRouter (${fb}) — adds ~10% markup over direct pricing`,
          detail: 'OpenRouter routes through their infrastructure and charges a markup',
          ...FIXES.OPENROUTER_MARKUP,
        });
      }
    });
  }

  // ── contextPruning ─────────────────────────────────────────────
  const pruning = agentCfg.session?.contextPruning || agentCfg.contextPruning;
  if (!pruning || pruning.mode === 'none') {
    findings.push({
      severity: 'medium', source: 'context',
      message: `${prefix}contextPruning is not set — sessions grow unbounded`,
      detail: 'Every message re-sends full conversation history as input tokens. A 30-message chat can cost 5-10x a fresh session.',
      ...FIXES.CONTEXT_PRUNING_MISSING,
    });
  } else {
    findings.push({
      severity: 'info', source: 'context',
      message: `${prefix}contextPruning mode: "${pruning.mode}" ✓`, monthlyCost: 0,
    });
  }

  // ── Image dimension ────────────────────────────────────────────
  const imgDim = agentCfg.imageMaxDimensionPx ?? agentCfg.media?.imageMaxDimensionPx;
  if (imgDim === undefined || imgDim === null || imgDim > 800) {
    const dimVal = imgDim ?? 1200;
    findings.push({
      severity: 'medium', source: 'vision',
      message: `${prefix}imageMaxDimensionPx is ${dimVal} — high-res vision tokens are expensive`,
      detail: 'Each screenshot at 1200px can cost 1000-3000 extra tokens. Reduce to 800px or lower.',
      ...FIXES.IMAGE_DIMENSION,
    });
  }

  return findings;
}

// ── Parse human interval strings like "30m", "2h", "1d" ──────────
function parseInterval(str) {
  if (!str) return 60;
  const match = str.match(/^(\d+)(s|m|h|d)$/);
  if (!match) return 60;
  const val = parseInt(match[1]);
  return { s: val, m: val * 60, h: val * 3600, d: val * 86400 }[match[2]] || 60;
}

// ── Config analysis ───────────────────────────────────────────────
function analyzeConfig(configPath) {
  const findings = [];
  const config = readJSON(configPath);

  if (!config) {
    return {
      exists: false,
      findings: [{ severity: 'info', source: 'config', message: `openclaw.json not found at ${configPath}`, detail: 'Skipping config analysis — run from a machine with OpenClaw installed' }],
      config: null, primaryModel: null,
    };
  }

  const agentDefaults = config.agents?.defaults || config.agent || {};
  const primaryModel  = agentDefaults.model?.primary || agentDefaults.model || config.model || null;
  const primaryKey    = resolveModel(primaryModel);

  // ── Primary model OpenRouter check ────────────────────────────
  if (primaryModel && isOpenRouter(primaryModel)) {
    findings.push({
      severity: 'medium', source: 'primary_model',
      message: `Primary model is routed via OpenRouter (${primaryModel})`,
      detail: 'OpenRouter adds ~10% markup. Direct provider access is cheaper.',
      ...FIXES.OPENROUTER_MARKUP,
    });
  }

  // ── Analyze main agent block ───────────────────────────────────
  findings.push(...analyzeAgentBlock(agentDefaults, primaryModel, 'main'));

  // ── Multi-agent scanning ───────────────────────────────────────
  const agentList = config.agents?.list || [];
  for (const agent of agentList) {
    if (!agent.id || agent.id === 'main') continue;
    const agentModel = agent.model?.primary || agent.model || primaryModel;
    const agentKey   = resolveModel(agentModel);

    // Flag expensive per-agent model overrides
    if (agentModel && !isLocalModel(agentModel) && agentKey) {
      const tier = modelTier(agentKey);
      if (tier === 'expensive' || tier === 'medium') {
        const monthly = costPerCall(agentKey, 2000, 500) * 30 * 30;
        findings.push({
          severity: tier === 'expensive' ? 'high' : 'medium',
          source: 'multi_agent',
          message: `Agent "${agent.id}" using expensive model: ${agentModel}`,
          detail: `Each agent has its own sessions, heartbeat, and hooks — all bill independently`,
          monthlyCost: monthly,
          ...FIXES.MULTI_AGENT_PAID(agent.id),
        });
      }
    }

    // Run full rule engine on each agent's own config
    const agentBlock = { ...agentDefaults, ...agent };
    const agentFindings = analyzeAgentBlock(agentBlock, agentModel, agent.id)
      .filter(f => f.severity !== 'info'); // only surface issues for secondary agents
    findings.push(...agentFindings);
  }

  // ── Hooks ──────────────────────────────────────────────────────
  const hooks = config.hooks?.internal?.entries || config.hooks || {};
  const hookNames = Object.keys(hooks).filter(k => k !== 'enabled' && k !== 'token' && k !== 'path');
  let hookIssues = 0;

  let haikuHooks = 0;
  for (const name of hookNames) {
    const hook = typeof hooks[name] === 'object' ? hooks[name] : {};
    if (hook.enabled === false) continue;
    const hookModel = hook.model || primaryModel;
    if (isLocalModel(hookModel)) {
      // local = free, no finding needed
    } else if (isHaikuTier(hookModel) && resolveModel(hookModel)) {
      const monthly = costPerCall(resolveModel(hookModel), 1000, 200) * 50 * 30;
      haikuHooks++;
      findings.push({
        severity: 'low', source: 'hooks',
        message: `Hook "${name}" on Haiku — minimal cost, good choice`,
        detail: `~50 fires/day estimated · $${monthly.toFixed(2)}/month`,
        monthlyCost: monthly,
      });
    } else if (resolveModel(hookModel)) {
      const monthly = costPerCall(resolveModel(hookModel), 1000, 200) * 50 * 30;
      hookIssues++;
      findings.push({
        severity: 'high', source: 'hooks',
        message: `Hook "${name}" running on ${hookModel} — switch to Haiku or local`,
        detail: `~50 fires/day estimated · $${monthly.toFixed(2)}/month`,
        monthlyCost: monthly,
        ...FIXES.HOOK_PAID_MODEL(name),
      });
    }
  }
  if (hookNames.length > 0 && hookIssues === 0 && haikuHooks === 0) {
    findings.push({ severity: 'info', source: 'hooks', message: `All ${hookNames.length} hooks on local models ✓`, monthlyCost: 0 });
  }

  // ── WhatsApp ───────────────────────────────────────────────────
  const wa     = config.channels?.whatsapp || {};
  const groups = wa.groups;
  if (wa.enabled !== false) {
    if (groups === undefined || groups === null) {
      findings.push({ severity: 'critical', source: 'whatsapp', message: 'WhatsApp groups policy unset — ALL groups auto-joined on primary model', detail: 'Every message from every group you\'re in hits your primary model', ...FIXES.WHATSAPP_GROUPS_OPEN });
    } else if (typeof groups === 'object' && Object.keys(groups).length > 0) {
      findings.push({ severity: 'high', source: 'whatsapp', message: `${Object.keys(groups).length} WhatsApp group(s) actively processing on primary model`, detail: `Group IDs: ${Object.keys(groups).join(', ')}`, ...FIXES.WHATSAPP_GROUPS_ACTIVE });
    } else {
      findings.push({ severity: 'info', source: 'whatsapp', message: 'WhatsApp groups blocked ✓', monthlyCost: 0 });
    }
  }

  // ── Telegram ───────────────────────────────────────────────────
  const tg = config.channels?.telegram || {};
  if (tg.enabled !== false && tg.botToken) {
    const policy = tg.dmPolicy || tg.dm?.policy || 'pairing';
    if (policy === 'open') {
      findings.push({ severity: 'critical', source: 'telegram', message: 'Telegram dmPolicy is "open" — anyone can message your bot and bill you', detail: 'Any Telegram user who finds your bot can trigger paid API calls', ...FIXES.TELEGRAM_OPEN });
    } else {
      findings.push({ severity: 'info', source: 'telegram', message: `Telegram dmPolicy: "${policy}" ✓`, monthlyCost: 0 });
    }
  }

  // ── Discord ────────────────────────────────────────────────────
  const dc = config.channels?.discord || {};
  if (dc.enabled !== false && dc.token) {
    const dcPolicy = dc.dm?.policy || dc.dmPolicy || 'pairing';
    if (dcPolicy === 'open') {
      findings.push({ severity: 'high', source: 'discord', message: 'Discord DM policy is "open" — unknown users can trigger paid API calls', detail: 'Anyone in your server can DM your bot', ...FIXES.DISCORD_OPEN });
    } else {
      findings.push({ severity: 'info', source: 'discord', message: `Discord DM policy: "${dcPolicy}" ✓`, monthlyCost: 0 });
    }
  }

  // ── Signal ─────────────────────────────────────────────────────
  const sig = config.channels?.signal || {};
  if (sig.enabled !== false && sig.phoneNumber) {
    if (!sig.allowFrom || sig.allowFrom.length === 0) {
      findings.push({ severity: 'high', source: 'signal', message: 'Signal has no allowFrom list — anyone with your number can message your agent', detail: 'No sender restriction on Signal channel', ...FIXES.SIGNAL_OPEN });
    }
  }

  // ── Cron jobs ──────────────────────────────────────────────────
  const cronJobs = config.cron?.jobs || config.cron || {};
  if (typeof cronJobs === 'object' && !Array.isArray(cronJobs)) {
    for (const [name, job] of Object.entries(cronJobs)) {
      if (typeof job !== 'object' || job.enabled === false) continue;
      const jobModel   = job.model || primaryModel;
      const jobKey     = resolveModel(jobModel);
      const interval   = job.every ? parseInterval(job.every) : (job.interval || 3600);
      const perDay     = Math.floor(86400 / Math.max(interval, 1));

      if (!isLocalModel(jobModel) && jobKey) {
        const monthly = costPerCall(jobKey, 2000, 500) * perDay * 30;
        findings.push({
          severity: perDay > 24 ? 'critical' : 'high',
          source: 'cron',
          message: `Cron job "${name}" runs ${perDay}x/day on paid model: ${jobModel || 'primary'}`,
          detail: `Interval: ${job.every || interval + 's'} · $${monthly.toFixed(2)}/month estimated`,
          monthlyCost: monthly,
          ...FIXES.CRON_PAID_MODEL(name, job.every || `${interval}s`),
        });
      }
    }
  }

  // ── Skills polling ─────────────────────────────────────────────
  const skills = config.skills?.entries || config.skills || {};
  for (const [name, skill] of Object.entries(skills)) {
    if (typeof skill !== 'object' || skill.enabled === false) continue;
    if (skill.interval || skill.cron || skill.poll) {
      const interval   = typeof skill.interval === 'number' ? skill.interval : 60;
      const perDay     = Math.floor(86400 / interval);
      const skillModel = skill.model || primaryModel;
      const skillKey   = resolveModel(skillModel);
      if (!isLocalModel(skillModel) && skillKey) {
        const monthly = costPerCall(skillKey, 2000, 500) * perDay * 30;
        findings.push({
          severity: 'critical', source: 'skills',
          message: `Skill "${name}" has polling loop on paid model: ${skillModel || 'primary'}`,
          detail: `~${perDay} calls/day · $${monthly.toFixed(2)}/month estimated`,
          monthlyCost: monthly,
          ...FIXES.SKILL_POLLING(name),
        });
      }
    }
  }

  // ── Subagents concurrency ──────────────────────────────────────
  const maxC = agentDefaults.subagents?.maxConcurrent ?? config.subagents?.maxConcurrent ?? null;
  if (maxC !== null && maxC > 2) {
    findings.push({ severity: 'high', source: 'subagents', message: `maxConcurrent = ${maxC} — ${maxC}x cost multiplier during bursts`, detail: `${maxC} paid model calls can fire simultaneously`, ...FIXES.MAX_CONCURRENT });
  } else if (maxC !== null) {
    findings.push({ severity: 'info', source: 'subagents', message: `maxConcurrent = ${maxC} ✓`, monthlyCost: 0 });
  }

  // ── memoryFlush ────────────────────────────────────────────────
  const mfModel = config.memory?.flushModel || config.memoryFlush?.model || primaryModel;
  if (mfModel && !isLocalModel(mfModel)) {
    findings.push({ severity: 'medium', source: 'memory', message: `memoryFlush using paid model: ${mfModel}`, detail: 'Runs on every session compaction — cost scales with context size', ...FIXES.MEMORY_FLUSH_PAID });
  }

  // ── Primary model awareness ────────────────────────────────────
  if (primaryKey && MODEL_PRICING[primaryKey] && !MODEL_PRICING[primaryKey].subscription) {
    const p = MODEL_PRICING[primaryKey];
    const monthly = costPerCall(primaryKey, 2000, 500) * 50 * 30;
    findings.push({
      severity: p.input >= 5 ? 'high' : p.input >= 1 ? 'medium' : 'info',
      source: 'primary_model',
      message: `Primary model: ${p.label} · $${p.input}/$${p.output} per MTok`,
      detail: `Baseline at 50 queries/day: ~$${monthly.toFixed(2)}/month`,
      monthlyCost: monthly,
    });
  }

  return { exists: true, findings, config, primaryModel };
}

// ── Session analysis ──────────────────────────────────────────────
function analyzeSessions(sessionsPath) {
  const findings = [];
  const sessions = readJSON(sessionsPath);

  if (!sessions) return { exists: false, findings: [], sessions: [], totalInputTokens: 0, totalOutputTokens: 0, totalCost: 0, sessionCount: 0 };

  let totalIn = 0, totalOut = 0, totalCost = 0;
  const breakdown = [], orphaned = [], large = [];

  for (const key of Object.keys(sessions)) {
    const s        = sessions[key];
    const model    = s.model || s.primaryModel || null;
    const modelKey = resolveModel(model);
    const inTok    = s.inputTokens  || s.tokensIn  || s.tokens?.input  || 0;
    const outTok   = s.outputTokens || s.tokensOut || s.tokens?.output || 0;
    const cost     = costPerCall(modelKey, inTok, outTok);
    const updatedAt = s.updatedAt || s.lastActive || null;

    totalIn   += inTok;
    totalOut  += outTok;
    totalCost += cost;

    const isOrphaned = key.includes('cron') || key.includes('deleted') ||
      (updatedAt && Date.now() - new Date(updatedAt).getTime() > 48 * 3600 * 1000 && !key.includes('main'));

    if (isOrphaned) orphaned.push({ key, model, tokens: inTok + outTok, cost });
    if (inTok + outTok > 50000) large.push({ key, model, tokens: inTok + outTok });

    const ageMs    = updatedAt ? Date.now() - new Date(updatedAt).getTime() : null;
    const ageDays  = ageMs ? ageMs / (1000 * 3600 * 24) : null;
    const dailyCost = (ageDays && ageDays > 0.01 && cost > 0) ? cost / ageDays : null;

    breakdown.push({ key, model, modelLabel: modelKey ? (MODEL_PRICING[modelKey]?.label || modelKey) : 'unknown', inputTokens: inTok, outputTokens: outTok, cost, updatedAt, ageMs, dailyCost, isOrphaned });
  }

  if (orphaned.length > 0) findings.push({ severity: 'high', source: 'sessions', message: `${orphaned.length} orphaned session(s) — still holding tokens on paid models`, detail: orphaned.map(s => `${s.key}: ${s.tokens.toLocaleString()} tokens ($${s.cost.toFixed(4)})`).join('\n  '), ...FIXES.ORPHANED_SESSIONS });
  if (large.length > 0) findings.push({ severity: 'medium', source: 'sessions', message: `${large.length} session(s) with >50k tokens per conversation`, detail: large.map(s => `${s.key}: ${s.tokens.toLocaleString()} tokens`).join('\n  '), ...FIXES.LARGE_SESSIONS });
  if (Object.keys(sessions).length > 0 && !orphaned.length && !large.length) findings.push({ severity: 'info', source: 'sessions', message: `${Object.keys(sessions).length} session(s) healthy ✓`, detail: `Total tokens: ${(totalIn + totalOut).toLocaleString()}` });

  return { exists: true, findings, sessions: breakdown, totalInputTokens: totalIn, totalOutputTokens: totalOut, totalCost, sessionCount: Object.keys(sessions).length };
}

// ── Workspace analysis ────────────────────────────────────────────
function analyzeWorkspace() {
  const findings = [];
  const workspaceDir = path.join(os.homedir(), 'clawd');
  if (!fs.existsSync(workspaceDir)) return { exists: false, findings: [] };

  try {
    const rootFiles = fs.readdirSync(workspaceDir).filter(f => f.endsWith('.md') || f.endsWith('.txt'));
    const count = rootFiles.length;
    const estimatedTokens = count * 500;
    if (count > 20) {
      findings.push({ severity: 'medium', source: 'workspace', message: `${count} files at workspace root — all loaded into every session context`, detail: `~${estimatedTokens.toLocaleString()} tokens/session from workspace files`, ...FIXES.WORKSPACE_BLOAT });
    } else {
      findings.push({ severity: 'info', source: 'workspace', message: `${count} files at workspace root — lean ✓`, detail: `~${estimatedTokens.toLocaleString()} tokens estimated` });
    }
  } catch { /* not readable */ }

  return { exists: true, findings };
}

// ── Main ──────────────────────────────────────────────────────────
async function runAnalysis({ configPath, sessionsPath, logsDir }) {
  const configResult    = analyzeConfig(configPath);
  const sessionResult   = analyzeSessions(sessionsPath);
  const workspaceResult = analyzeWorkspace();

  const allFindings = [...configResult.findings, ...sessionResult.findings, ...workspaceResult.findings];

  const estimatedMonthlyBleed = allFindings
    .filter(f => f.monthlyCost && f.severity !== 'info')
    .reduce((sum, f) => sum + f.monthlyCost, 0);

  return {
    scannedAt:    new Date().toISOString(),
    configPath,
    sessionsPath,
    primaryModel: configResult.primaryModel,
    findings:     allFindings,
    summary: {
      critical:              allFindings.filter(f => f.severity === 'critical').length,
      high:                  allFindings.filter(f => f.severity === 'high').length,
      medium:                allFindings.filter(f => f.severity === 'medium').length,
      low:                   allFindings.filter(f => f.severity === 'low').length,
      info:                  allFindings.filter(f => f.severity === 'info').length,
      estimatedMonthlyBleed,
      sessionsAnalyzed:      sessionResult.sessionCount,
      totalTokensFound:      (sessionResult.totalInputTokens || 0) + (sessionResult.totalOutputTokens || 0),
    },
    sessions: sessionResult.sessions || [],
    config:   configResult.config,
  };
}

module.exports = { runAnalysis, MODEL_PRICING, resolveModel, costPerCall };
