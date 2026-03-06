#!/usr/bin/env node
/**
 * MindGraph Extraction Script
 *
 * Reads a text/memory file + SCHEMA.md, calls LLM to extract structured nodes/edges.
 * If the file exceeds the SUMMARIZE_THRESHOLD, it first summarizes via a Flash call,
 * then extracts from the summary. This handles large session transcripts gracefully.
 *
 * Usage:
 *   node skills/mindgraph/extract.js <file_path> [--model <model>] [--output <path>]
 *
 * Model defaults:
 *   Files < 20KB  → google/gemini-3-flash-preview  (fast, cheap)
 *   Files >= 20KB → google/gemini-3-pro-preview    (larger output capacity)
 *   Override with --model <model>
 *
 * Auto-summarize:
 *   Files > 40KB are summarized via Flash first, then extracted from the summary.
 *   Override threshold with --summarize-threshold <bytes>
 */

'use strict';

const fs     = require('fs');
const path   = require('path');
const crypto = require('crypto');

// ─── Config ───────────────────────────────────────────────────────────────────

const WORKSPACE          = '/home/node/.openclaw/workspace';
const SCHEMA_PATH        = path.join(WORKSPACE, 'skills/mindgraph/SCHEMA.md');
const EXTRACTED_DIR      = path.join(WORKSPACE, 'skills/mindgraph/extracted');
const OC_CONFIG          = path.join(process.env.HOME, '.openclaw/openclaw.json');

const LARGE_FILE_THRESHOLD  = 20 * 1024;  // 20 KB  → switch to Pro model
const SUMMARIZE_THRESHOLD   = 40 * 1024;  // 40 KB  → summarize first, then extract

const MODELS = {
  flash: 'google/gemini-3-flash-preview',
  pro:   'google/gemini-3-pro-preview',
};

// ─── Provider config ──────────────────────────────────────────────────────────

function loadConfig() {
  const c = JSON.parse(fs.readFileSync(OC_CONFIG, 'utf8'));
  const providers = c.models?.providers || {};
  const providerMap = {};

  if (providers.google) {
    providerMap.google = {
      apiKey:  c.env?.GEMINI_API_KEY || providers.google.apiKey,
      baseUrl: (providers.google.baseUrl || 'https://generativelanguage.googleapis.com/v1beta') + '/openai',
    };
  }
  if (providers.moonshot) {
    providerMap.moonshot = {
      apiKey:  c.env?.MOONSHOT_API_KEY || providers.moonshot.apiKey || process.env.MOONSHOT_API_KEY,
      baseUrl: providers.moonshot.baseUrl || 'https://api.moonshot.cn/v1',
    };
  }
  if (providers.anthropic) {
    providerMap.anthropic = {
      apiKey:  providers.anthropic.apiKey || c.env?.ANTHROPIC_API_KEY,
      baseUrl: (providers.anthropic.baseUrl || 'https://api.anthropic.com') + '/v1',
    };
  }
  if (!providerMap.google) {
    providerMap.google = {
      apiKey:  c.env?.GEMINI_API_KEY || '',
      baseUrl: 'https://generativelanguage.googleapis.com/v1beta/openai',
    };
  }
  return { providers: providerMap };
}

// ─── LLM call (returns parsed JSON) ──────────────────────────────────────────

async function callLLM(model, config, messages, { maxTokens, raw } = {}) {
  const { default: fetch } = await import('node-fetch')
    .catch(() => ({ default: globalThis.fetch }));

  const providerPrefix = model.includes('/') ? model.split('/')[0] : 'google';
  const provider = config.providers[providerPrefix] || config.providers.google;
  const { apiKey, baseUrl } = provider;
  const cleanModel = model.replace(/^(google|moonshot|anthropic)\//, '');

  const body = {
    model:       cleanModel,
    messages,
    temperature: providerPrefix === 'moonshot' ? 1 : 0.1,
    max_tokens:  maxTokens || (cleanModel.includes('gemini-3-flash') ? 32000 : 16000),
  };

  const response = await fetch(`${baseUrl}/chat/completions`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${apiKey}` },
    body:    JSON.stringify(body),
    timeout: 300000,
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`API error ${response.status}: ${err.slice(0, 400)}`);
  }

  const parsed  = await response.json();
  const msg     = parsed.choices?.[0]?.message;
  const content = msg?.content || msg?.reasoning_content;
  if (!content) throw new Error(`Empty response. Raw: ${JSON.stringify(parsed).slice(0, 300)}`);

  if (raw) return content; // For summarization pass — plain text

  const jsonMatch =
    content.match(/```json\s*([\s\S]*?)\s*```/) ||
    content.match(/```\s*([\s\S]*?)\s*```/)     ||
    [null, content];
  try {
    return JSON.parse(jsonMatch[1].trim());
  } catch (e) {
    throw new Error(`JSON parse failed: ${e.message}\nContent start: ${content.slice(0, 400)}`);
  }
}

// ─── Summarization pass ───────────────────────────────────────────────────────

async function summarize(content, config) {
  console.error(`  → File too large (${Math.round(Buffer.byteLength(content) / 1024)}KB). Summarizing first...`);

  const summary = await callLLM(MODELS.flash, config, [
    {
      role:    'system',
      content: 'You are a knowledge distillation assistant. Summarize the conversation or document below, focusing on: decisions made, tasks agreed, facts stated, constraints identified, goals discussed, and any anomalies or new information worth preserving. Be thorough but concise. Plain text only, no JSON.',
    },
    {
      role:    'user',
      content: `Summarize this for knowledge graph extraction:\n\n${content}`,
    },
  ], { raw: true });

  console.error(`  → Summary: ${Math.round(Buffer.byteLength(summary) / 1024)}KB`);
  return summary;
}

// ─── Known entities for canonical label reuse ─────────────────────────────────

const KNOWN_ENTITIES = `## KNOWN ENTITIES — reuse these EXACT labels when the concept appears

People/Orgs: Shan Rizvi, Thumos, BCG X, Hippocratic AI, ElevenLabs, Hunter.io, Firecrawl
Projects: Thumos Care, 32B Scientific Reasoning Engine, Elys Live, UN Diplomatic Knowledge Graph,
  MCP Neo4j Server, MatSyn, Pencil News, Just Ads, Polymarket Trading System, X Listening System,
  MindGraph Memory System, Job Search Feb 2026
Goals: Income Generation

Use EXACT labels above. Do NOT create variants.`;

// ─── Extraction prompt ────────────────────────────────────────────────────────

function buildPrompt(schema, fileContent) {
  return `You are a knowledge graph extraction agent. Extract structured knowledge from the content below.

## SCHEMA — use ONLY the types defined here
${schema}

${KNOWN_ENTITIES}

## OUTPUT RULES
1. Use the MOST SPECIFIC type the schema provides.
2. Every node MUST have a non-empty \`summary\` field (max 300 chars).
3. Edge \`from\` and \`to\` values are node LABELS (not UIDs).
4. Edge types use SCREAMING_SNAKE_CASE (AUTHORED_BY, CONSTRAINED_BY, MOTIVATED_BY, etc.).
5. Do NOT create DERIVED_FROM or PART_OF edges — the import script handles provenance.
6. RELEVANT_TO is last resort — prefer semantic edges (SUPPORTS, EXTENDS, ADDRESSES, etc.).
7. Output valid JSON only — no markdown, no explanation.
8. Do NOT create Source nodes — file references and session logs have no graph value.
9. LABEL RULES (critical):
   - Labels must be SHORT and NOUN-PHRASE style: max 60 characters.
   - Labels identify the thing, not describe it. "MindGraph Port Decision" not "Decision MindGraph UI Port 8766. Status made. Rationale Fixed at 8766..."
   - All descriptive content goes in \`summary\` or \`props.description\`, never in the label.
   - Labels should be reusable as graph node names — imagine them as Wikipedia article titles.

## OUTPUT FORMAT
{ "nodes": [{ "label": "...", "type": "...", "summary": "...", "props": {} }], "edges": [{ "from": "...", "to": "...", "type": "..." }] }

## CONTENT
${fileContent}`;
}

// ─── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  const args        = process.argv.slice(2);
  const filePathArg = args.find(a => !a.startsWith('--'));

  if (!filePathArg) {
    console.error('Usage: node extract.js <file_path> [--model <model>] [--output <path>] [--summarize-threshold <bytes>]');
    process.exit(1);
  }

  const filePath = path.resolve(filePathArg);
  if (!fs.existsSync(filePath)) {
    console.error(`File not found: ${filePath}`);
    process.exit(1);
  }

  let fileContent    = fs.readFileSync(filePath, 'utf8');
  const fileSize     = Buffer.byteLength(fileContent, 'utf8');
  const fileHash     = crypto.createHash('sha256').update(fileContent).digest('hex').slice(0, 16);
  const config       = loadConfig();
  const schema       = fs.readFileSync(SCHEMA_PATH, 'utf8');

  // ── Summarize threshold (default 40KB, overridable) ──
  const sumThreshIdx   = args.indexOf('--summarize-threshold');
  const sumThreshold   = sumThreshIdx !== -1 ? parseInt(args[sumThreshIdx + 1]) : SUMMARIZE_THRESHOLD;

  // ── Model selection ──
  const modelIdx = args.indexOf('--model');
  const model    = modelIdx !== -1
    ? args[modelIdx + 1]
    : (fileSize >= LARGE_FILE_THRESHOLD ? MODELS.pro : MODELS.flash);

  const outputIdx  = args.indexOf('--output');
  const explicitOut = outputIdx !== -1 ? args[outputIdx + 1] : null;

  console.error(`Extracting [${model}] (${Math.round(fileSize / 1024)}KB): ${path.basename(filePath)}`);

  // ── Stage 1: Summarize if too large ──
  let summarized = false;
  if (fileSize > sumThreshold) {
    fileContent = await summarize(fileContent, config);
    summarized  = true;
  }

  // ── Stage 2: Extract structured nodes ──
  const extracted = await callLLM(model, config, [
    { role: 'system', content: 'You are a knowledge graph extraction agent. Output valid JSON only.' },
    { role: 'user',   content: buildPrompt(schema, fileContent) },
  ]);

  const result = {
    meta: {
      source_path:  filePath,
      extracted_at: new Date().toISOString(),
      model,
      summarized,
      file_hash:    fileHash,
      file_size:    fileSize,
      node_count:   extracted.nodes?.length || 0,
      edge_count:   extracted.edges?.length || 0,
    },
    nodes: extracted.nodes || [],
    edges: extracted.edges || [],
  };

  if (!fs.existsSync(EXTRACTED_DIR)) fs.mkdirSync(EXTRACTED_DIR, { recursive: true });

  const datestamp  = new Date().toISOString().slice(0, 10);
  const outputPath = explicitOut
    || path.join(EXTRACTED_DIR, `${path.basename(filePath)}.${datestamp}.json`);

  fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));
  console.error(`✓ Saved ${result.meta.node_count} nodes, ${result.meta.edge_count} edges → ${outputPath}${summarized ? ' (via summary)' : ''}`);
  process.stdout.write(JSON.stringify(result, null, 2) + '\n');
}

main().catch(e => {
  console.error('FATAL:', e.message);
  process.exit(1);
});
