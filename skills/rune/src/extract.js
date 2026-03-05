import fs from 'node:fs';
import crypto from 'node:crypto';
import { UserError } from './errors.js';

const VALID_SCOPES = new Set(['global', 'project', 'conversation']);
const VALID_TIERS = new Set(['working', 'long-term']);
const VALID_SOURCE_TYPES = new Set(['manual', 'inferred', 'user_said', 'tool_output']);
const VALID_CATEGORIES = new Set(['person', 'project', 'preference', 'decision', 'lesson', 'environment', 'tool', 'task']);
const MAX_WORDS_PER_CHUNK = 300;
const OLLAMA_TIMEOUT_MS = 60_000;
const OPENAI_TIMEOUT_MS = 60_000;
const ANTHROPIC_TIMEOUT_MS = 60_000;
const DEFAULT_OPENAI_MODEL = 'gpt-4.1-mini';
const DEFAULT_ANTHROPIC_MODEL = 'claude-sonnet-4-20250514';
const OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions';
const ANTHROPIC_API_URL = 'https://api.anthropic.com/v1/messages';

function buildCompactPrompt(content) {
  return [
    'Extract key facts from this document as JSON. Return ONLY valid JSON.',
    '',
    '{"facts":[{"category":"person|project|preference|decision|lesson|environment|tool","key":"entity.attribute","value":"short fact","scope":"global|project","tier":"long-term","source_type":"user_said|inferred","confidence":0.95}],"session_summary":{"decisions":[],"topics":[]}}',
    '',
    'Rules: entity-specific keys (cory.son not person.son), one fact per attribute, max 15 facts, values under 15 words, skip noise.',
    '',
    'Document:',
    content
  ].join('\n');
}

function buildPrompt(content) {
  return [
    'You are a fact extraction system. Read the document (conversation transcript, notes, or log) and extract structured facts as JSON.',
    '',
    'Output format (JSON only, no explanation):',
    '{',
    '  "facts": [',
    '    {',
    '      "category": "person|project|preference|decision|lesson|environment|tool|task",',
    '      "key": "entity.attribute (e.g. alex.employer, cad-wiki.editor, deploy.cadence)",',
    '      "value": "concise fact string",',
    '      "scope": "global|project",',
    '      "tier": "long-term|working",',
    '      "source_type": "user_said|inferred|tool_output",',
    '      "confidence": 0.5-1.0,',
    '      "ttl": null',
    '    }',
    '  ],',
    '  "session_summary": {',
    '    "decisions": [],',
    '    "open_questions": [],',
    '    "action_items": [],',
    '    "topics": []',
    '  }',
    '}',
    '',
    'KEY RULES:',
    '- Keys MUST be entity-specific: "alex.name" NOT "person.name", "cory.son" NOT "person.son"',
    '- ONE FACT PER ATTRIBUTE. Split compound facts: "backend is Go, frontend is Svelte" = 2 separate facts',
    '- Extract ALL facts: names, emails, employers, roles, tools, frameworks, decisions, relationships, URLs, ports',
    '- When user contradicts themselves, use the LATEST value only. Do NOT include superseded values.',
    '- tier=long-term for durable facts (preferences, names, relationships, tools). ttl must be null.',
    '- tier=working ONLY for active tasks/builds that will expire. Set ttl like "24h" or "7d".',
    '- confidence: 0.95=user explicitly stated verbatim, 0.8=clearly implied, 0.6=inferred/ambiguous',
    '- source_type=user_said when user explicitly states it, inferred when you deduce it',
    '- Ignore noise: greetings, jokes, off-topic chat, brb messages are NOT facts',
    '- Works on conversations (User:/Assistant:), bullet-point notes, logs, and markdown docs',
    '- For notes/logs: extract decisions, tools used, people mentioned, lessons learned, project details',
    '- Keep values SHORT (under 15 words). Capture the fact, not the full sentence.',
    '- MAX 15 facts per document. Prioritize: people, decisions, lessons, tools. Skip status updates and timestamps.',
    '- Return ONLY valid JSON. No markdown, no explanation, no preamble.',
    '',
    'Document:',
    content
  ].join('\n');
}

function normalizeOllamaResponse(text) {
  // Strip <think>...</think> reasoning blocks from models like qwen3
  let cleaned = text.replace(/<think>[\s\S]*?<\/think>/gi, '');
  // Also strip unclosed <think> blocks (model started thinking but didn't close)
  cleaned = cleaned.replace(/<think>[\s\S]*/gi, '');
  const trimmed = cleaned.trim();
  const fenceMatch = trimmed.match(/```(?:json)?\s*([\s\S]*?)\s*```/i);
  return fenceMatch ? fenceMatch[1].trim() : trimmed;
}

function findJsonCandidate(text) {
  const normalized = normalizeOllamaResponse(text);
  const starts = [];
  for (let i = 0; i < normalized.length; i += 1) {
    const c = normalized[i];
    if (c === '{' || c === '[') {
      starts.push(i);
    }
  }

  for (const start of starts) {
    for (let end = normalized.length; end > start; end -= 1) {
      const candidate = normalized.slice(start, end).trim();
      if (!candidate) {
        continue;
      }
      try {
        return JSON.parse(candidate);
      } catch {
        // continue scanning
      }
    }
  }

  try {
    return JSON.parse(normalized);
  } catch {
    throw new UserError('Failed to parse Ollama response as JSON');
  }
}

function normalizeSummary(raw) {
  const input = raw && typeof raw === 'object' ? raw : {};
  const toList = (value) => (Array.isArray(value) ? value.filter((v) => typeof v === 'string' && v.trim()).map((v) => v.trim()) : []);
  return {
    decisions: toList(input.decisions),
    open_questions: toList(input.open_questions),
    action_items: toList(input.action_items),
    topics: toList(input.topics)
  };
}

function normalizeFacts(parsed) {
  const out = [];
  for (const item of parsed) {
    if (!item || typeof item !== 'object') {
      continue;
    }

    const categoryRaw = typeof item.category === 'string' ? item.category.trim() : '';
    const keyRaw = typeof item.key === 'string' ? item.key.trim() : '';
    const valueRaw = typeof item.value === 'string' ? item.value.trim() : '';
    const scope = typeof item.scope === 'string' ? item.scope.trim() : 'global';
    const tier = typeof item.tier === 'string' ? item.tier.trim() : 'long-term';
    const sourceType = typeof item.source_type === 'string' ? item.source_type.trim() : 'inferred';
    const confRaw = Number(item.confidence);
    const confidence = Number.isFinite(confRaw) ? Math.max(0, Math.min(1, confRaw)) : 0.8;
    const ttl = item.ttl == null ? null : String(item.ttl).trim();

    if (!categoryRaw || !keyRaw || !valueRaw) {
      continue;
    }
    if (!VALID_CATEGORIES.has(categoryRaw)) {
      continue;
    }
    if (!VALID_SCOPES.has(scope)) {
      continue;
    }
    if (!VALID_TIERS.has(tier)) {
      continue;
    }
    if (!VALID_SOURCE_TYPES.has(sourceType)) {
      continue;
    }
    if (ttl !== null && !ttl) {
      continue;
    }

    out.push({
      category: categoryRaw,
      key: keyRaw,
      value: valueRaw,
      scope,
      tier,
      source_type: sourceType,
      confidence,
      ttl: tier === 'working' ? ttl : null
    });
  }
  return out;
}

async function ollamaHealthCheck(ollamaUrl, timeoutMs = 5000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${ollamaUrl}/api/tags`, { signal: controller.signal });
    return res.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(timer);
  }
}

async function generateOnce(content, { model, ollamaUrl, verbose = false }) {
  // Pre-flight: check Ollama is responsive
  const healthy = await ollamaHealthCheck(ollamaUrl);
  if (!healthy) {
    throw new UserError(`Ollama not responding at ${ollamaUrl}. Is it running? Try: sudo systemctl restart ollama`);
  }

  const wordCount = content.trim().split(/\s+/).length;
  const prompt = wordCount < 1000 ? buildCompactPrompt(content) : buildPrompt(content);

  if (verbose) {
    console.error('--- Extraction Prompt ---');
    console.error(prompt);
  }

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), OLLAMA_TIMEOUT_MS);
  let response;
  try {
    response = await fetch(`${ollamaUrl}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model,
        prompt,
        stream: false,
        think: false,
        options: {
          temperature: 0.3,
          num_predict: 4096,
          num_ctx: 8192
        }
      }),
      signal: controller.signal
    });
  } catch (err) {
    if (err && err.name === 'AbortError') {
      throw new UserError(`Ollama request timed out after ${Math.floor(OLLAMA_TIMEOUT_MS / 1000)}s`);
    }
    throw new UserError(`Failed to reach Ollama at ${ollamaUrl}: ${err.message || String(err)}`);
  } finally {
    clearTimeout(timer);
  }

  if (!response.ok) {
    const errText = await response.text();
    throw new UserError(`Ollama request failed (${response.status}): ${errText}`);
  }

  const payload = await response.json();
  if (!payload.response) {
    throw new UserError('Ollama returned an empty response');
  }

  if (verbose) {
    console.error('--- Extraction Response ---');
    console.error(payload.response);
  }

  const parsed = findJsonCandidate(payload.response);
  let factsRaw = [];
  let summary = normalizeSummary({});

  if (Array.isArray(parsed)) {
    factsRaw = parsed;
  } else if (parsed && typeof parsed === 'object') {
    if (Array.isArray(parsed.facts)) {
      factsRaw = parsed.facts;
    }
    summary = normalizeSummary(parsed.session_summary);
  } else {
    throw new UserError('Ollama response must be a JSON object or array');
  }

  return {
    facts: normalizeFacts(factsRaw),
    session_summary: summary
  };
}

async function generateOnceOpenAI(content, { model, verbose = false }) {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new UserError('OPENAI_API_KEY not set. Use --engine ollama or set the env var.');
  }

  const systemPrompt = buildPrompt('').replace(/\nTranscript:\n$/, '').trim();
  const userMessage = content;

  if (verbose) {
    console.error('--- OpenAI Extraction ---');
    console.error(`model: ${model}`);
    console.error(`content length: ${content.length} chars`);
  }

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), OPENAI_TIMEOUT_MS);
  let response;
  try {
    response = await fetch(OPENAI_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userMessage }
        ],
        temperature: 0.2,
        max_tokens: 2048,
        response_format: { type: 'json_object' }
      }),
      signal: controller.signal
    });
  } catch (err) {
    if (err && err.name === 'AbortError') {
      throw new UserError(`OpenAI request timed out after ${Math.floor(OPENAI_TIMEOUT_MS / 1000)}s`);
    }
    throw new UserError(`Failed to reach OpenAI API: ${err.message || String(err)}`);
  } finally {
    clearTimeout(timer);
  }

  if (!response.ok) {
    const errText = await response.text();
    throw new UserError(`OpenAI API error (${response.status}): ${errText}`);
  }

  const payload = await response.json();
  const text = payload.choices?.[0]?.message?.content;
  if (!text) {
    throw new UserError('OpenAI returned an empty response');
  }

  if (verbose) {
    console.error('--- OpenAI Response ---');
    console.error(text);
    const usage = payload.usage;
    if (usage) {
      console.error(`tokens: prompt=${usage.prompt_tokens} completion=${usage.completion_tokens} total=${usage.total_tokens}`);
    }
  }

  const parsed = JSON.parse(text);
  let factsRaw = [];
  let summary = normalizeSummary({});

  if (Array.isArray(parsed)) {
    factsRaw = parsed;
  } else if (parsed && typeof parsed === 'object') {
    if (Array.isArray(parsed.facts)) {
      factsRaw = parsed.facts;
    }
    summary = normalizeSummary(parsed.session_summary);
  } else {
    throw new UserError('OpenAI response must be a JSON object or array');
  }

  return {
    facts: normalizeFacts(factsRaw),
    session_summary: summary
  };
}

async function generateOnceAnthropic(content, { model, verbose = false }) {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    throw new UserError('ANTHROPIC_API_KEY not set. Use --engine ollama or set the env var.');
  }

  const systemPrompt = buildPrompt('').replace(/\nTranscript:\n$/, '').trim();

  if (verbose) {
    console.error('--- Anthropic Extraction ---');
    console.error(`model: ${model}`);
    console.error(`content length: ${content.length} chars`);
  }

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), ANTHROPIC_TIMEOUT_MS);
  let response;
  try {
    response = await fetch(ANTHROPIC_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model,
        max_tokens: 2048,
        temperature: 0.2,
        system: systemPrompt,
        messages: [
          { role: 'user', content: content }
        ]
      }),
      signal: controller.signal
    });
  } catch (err) {
    if (err && err.name === 'AbortError') {
      throw new UserError(`Anthropic request timed out after ${Math.floor(ANTHROPIC_TIMEOUT_MS / 1000)}s`);
    }
    throw new UserError(`Failed to reach Anthropic API: ${err.message || String(err)}`);
  } finally {
    clearTimeout(timer);
  }

  if (!response.ok) {
    const errText = await response.text();
    throw new UserError(`Anthropic API error (${response.status}): ${errText}`);
  }

  const payload = await response.json();
  const textBlock = payload.content?.find(b => b.type === 'text');
  const text = textBlock?.text;
  if (!text) {
    throw new UserError('Anthropic returned an empty response');
  }

  if (verbose) {
    console.error('--- Anthropic Response ---');
    console.error(text);
    console.error(`tokens: input=${payload.usage?.input_tokens} output=${payload.usage?.output_tokens}`);
  }

  const parsed = findJsonCandidate(text);
  let factsRaw = [];
  let summary = normalizeSummary({});

  if (Array.isArray(parsed)) {
    factsRaw = parsed;
  } else if (parsed && typeof parsed === 'object') {
    if (Array.isArray(parsed.facts)) {
      factsRaw = parsed.facts;
    }
    summary = normalizeSummary(parsed.session_summary);
  } else {
    throw new UserError('Anthropic response must be a JSON object or array');
  }

  return {
    facts: normalizeFacts(factsRaw),
    session_summary: summary
  };
}

function resolveEngine(engine) {
  if (engine === 'openai' || engine === 'codex') return 'openai';
  if (engine === 'anthropic' || engine === 'claude') return 'anthropic';
  if (engine === 'ollama') return 'ollama';
  if (engine === 'auto' || !engine) {
    // Prefer Anthropic (Max sub, no per-token cost), fall back to OpenAI, then Ollama
    if (process.env.ANTHROPIC_API_KEY) return 'anthropic';
    if (process.env.OPENAI_API_KEY) return 'openai';
    return 'ollama';
  }
  throw new UserError(`Unknown engine "${engine}". Use: anthropic, openai, ollama, or auto`);
}

function chunkContent(content) {
  const words = content.trim().split(/\s+/).filter(Boolean);
  if (words.length <= MAX_WORDS_PER_CHUNK) {
    return [content];
  }

  const chunks = [];
  for (let i = 0; i < words.length; i += MAX_WORDS_PER_CHUNK) {
    chunks.push(words.slice(i, i + MAX_WORDS_PER_CHUNK).join(' '));
  }
  return chunks;
}

function mergeSummaries(summaries) {
  const unique = {
    decisions: new Set(),
    open_questions: new Set(),
    action_items: new Set(),
    topics: new Set()
  };
  for (const summary of summaries) {
    for (const decision of summary.decisions) unique.decisions.add(decision);
    for (const openQuestion of summary.open_questions) unique.open_questions.add(openQuestion);
    for (const actionItem of summary.action_items) unique.action_items.add(actionItem);
    for (const topic of summary.topics) unique.topics.add(topic);
  }

  return {
    decisions: [...unique.decisions],
    open_questions: [...unique.open_questions],
    action_items: [...unique.action_items],
    topics: [...unique.topics]
  };
}

function dedupeExtractedFacts(facts) {
  const map = new Map();
  for (const fact of facts) {
    const k = `${fact.category}::${fact.key}`;
    const prev = map.get(k);
    if (!prev || fact.confidence >= prev.confidence) {
      map.set(k, fact);
    }
  }
  return [...map.values()];
}

function fileHash(content) {
  return crypto.createHash('sha256').update(content).digest('hex').slice(0, 16);
}

export function wasAlreadyExtracted(db, filePath, content) {
  const hash = fileHash(content);
  const row = db.prepare(
    "SELECT id FROM extraction_log WHERE file_path = ? AND file_hash = ? AND status = 'ok'"
  ).get(filePath, hash);
  return Boolean(row);
}

export function logExtraction(db, { filePath, content, engine, model, facts, inserted, updated, skipped, durationMs, status, error }) {
  const hash = fileHash(content);
  db.prepare(`
    INSERT INTO extraction_log (file_path, file_hash, engine, model, facts_extracted, facts_inserted, facts_updated, facts_skipped, duration_ms, status, error, created)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    ON CONFLICT(file_path, file_hash) DO UPDATE SET
      engine = excluded.engine,
      model = excluded.model,
      facts_extracted = excluded.facts_extracted,
      facts_inserted = excluded.facts_inserted,
      facts_updated = excluded.facts_updated,
      facts_skipped = excluded.facts_skipped,
      duration_ms = excluded.duration_ms,
      status = excluded.status,
      error = excluded.error,
      created = excluded.created
  `).run(filePath, hash, engine, model, facts, inserted, updated, skipped, durationMs, status, error ?? null);
}

export async function extractFactsFromFile(filePath, options = {}) {
  if (!fs.existsSync(filePath)) {
    throw new UserError(`File not found: ${filePath}`);
  }
  const content = fs.readFileSync(filePath, 'utf8');
  const chunks = chunkContent(content);
  const engine = resolveEngine(options.engine);

  const allFacts = [];
  const summaries = [];
  for (const chunk of chunks) {
    let extracted;
    if (engine === 'anthropic') {
      const model = options.model || DEFAULT_ANTHROPIC_MODEL;
      extracted = await generateOnceAnthropic(chunk, {
        model,
        verbose: Boolean(options.verbose)
      });
    } else if (engine === 'openai') {
      const model = options.model || DEFAULT_OPENAI_MODEL;
      extracted = await generateOnceOpenAI(chunk, {
        model,
        verbose: Boolean(options.verbose)
      });
    } else {
      const ollamaUrl = process.env.OLLAMA_URL || 'http://localhost:11434';
      const model = options.model || 'qwen3:8b';
      extracted = await generateOnce(chunk, {
        model,
        ollamaUrl,
        verbose: Boolean(options.verbose)
      });
    }
    allFacts.push(...extracted.facts);
    summaries.push(extracted.session_summary);
  }

  return {
    facts: dedupeExtractedFacts(allFacts),
    session_summary: mergeSummaries(summaries),
    chunks: chunks.length,
    engine
  };
}
