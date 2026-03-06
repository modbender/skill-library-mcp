#!/usr/bin/env npx ts-node
/**
 * Generate intelligent soul summary using local LLM
 * Falls back to simple extraction if Ollama unavailable
 */

import * as readline from 'readline';

const OLLAMA_URL = process.env.OLLAMA_URL || 'http://localhost:11434';
const MODEL = process.env.OLLAMA_MODEL || 'lfm2.5:1.2b';

// ============ LLM SUMMARIZATION ============

const SYSTEM_PROMPT = `You are analyzing an OpenClaw AI assistant's workspace configuration.
Your job is to extract what would be USEFUL for someone else setting up their own assistant.

Focus on:
- Concrete patterns they could copy
- Actual lessons learned (not generic advice)
- Interesting automation (cron jobs, heartbeats)
- Unique approaches worth highlighting

Skip:
- Generic/boilerplate content
- Personal details (already anonymized as [USER], [PROJECT_N])
- Obvious things everyone does`;

const EXTRACTION_PROMPT = `Analyze this workspace and extract a useful summary for sharing.

Return JSON with these fields:
{
  "title": "Agent name or short descriptive title",
  "tagline": "One sentence describing what makes this setup useful",
  "summary": "2-3 sentences explaining the overall approach and philosophy",
  "keyPatterns": ["Pattern 1: explanation", "Pattern 2: explanation", ...],
  "lessonsLearned": ["Specific insight 1", "Specific insight 2", ...],
  "interestingAutomation": ["Cron/heartbeat description with why it's useful", ...],
  "toolsUsed": ["tool1", "tool2", ...]
}

Only include items that would actually help someone else. Quality over quantity.
If a section has nothing interesting, use empty array.

Workspace data:
`;

interface LLMSummary {
  title: string;
  tagline: string;
  summary: string;
  keyPatterns: string[];
  lessonsLearned: string[];
  interestingAutomation: string[];
  toolsUsed: string[];
}

async function checkOllama(): Promise<boolean> {
  try {
    const res = await fetch(`${OLLAMA_URL}/api/tags`, { signal: AbortSignal.timeout(2000) });
    return res.ok;
  } catch {
    return false;
  }
}

async function summarizeWithLLM(data: any): Promise<LLMSummary | null> {
  // Prepare condensed input for LLM (avoid token limits)
  const input = {
    soul: data.soul?.slice(0, 2000),
    agents: data.agents?.slice(0, 3000),
    memory: data.memory?.slice(0, 2000),
    tools: data.tools,
    cronJobs: data.cronJobs,
    skills: data.skills,
  };

  try {
    const res = await fetch(`${OLLAMA_URL}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: MODEL,
        system: SYSTEM_PROMPT,
        prompt: EXTRACTION_PROMPT + JSON.stringify(input, null, 2),
        stream: false,
        options: { temperature: 0.3 },
      }),
    });

    if (!res.ok) return null;
    
    const result = await res.json();
    const text = result.response || '';
    
    // Extract JSON from response
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) return null;
    
    return JSON.parse(jsonMatch[0]) as LLMSummary;
  } catch (err) {
    console.error('LLM error:', err);
    return null;
  }
}

// ============ FALLBACK: Simple extraction ============

function simpleSummary(data: any): LLMSummary {
  // Extract title from identity
  let title = 'OpenClaw Agent';
  if (data.identity) {
    const match = data.identity.match(/\*\*Name:\*\*\s*([A-Za-z0-9_-]+)/);
    if (match && match[1] !== '[USER]') title = match[1];
  }

  // Simple tagline from tools
  const tools = data.tools?.toolNames || [];
  const tagline = tools.length > 0
    ? `Assistant with ${tools.slice(0, 3).join(', ')} integration`
    : 'Personal AI assistant';

  // Cron jobs as automation
  const automation = (data.cronJobs || [])
    .filter((j: any) => j.enabled)
    .map((j: any) => `${j.name}: ${j.description}`);

  return {
    title,
    tagline,
    summary: 'Workspace configuration shared via OpenSoul.',
    keyPatterns: [],
    lessonsLearned: [],
    interestingAutomation: automation,
    toolsUsed: tools,
  };
}

// ============ OUTPUT FORMATTING ============

function formatOutput(summary: LLMSummary, data: any, usedLLM: boolean) {
  return {
    profile: {
      title: summary.title,
      tagline: summary.tagline,
      summary: summary.summary,
      keyPatterns: summary.keyPatterns,
      lessonsLearned: summary.lessonsLearned,
      interestingAutomation: summary.interestingAutomation,
      toolsUsed: summary.toolsUsed,
      // Legacy fields for API compatibility
      useCases: [],
      capabilities: summary.toolsUsed.map(t => `${t} integration`),
      skills: data.skills?.map((s: any) => s.name) || [],
      workflows: summary.keyPatterns,
      tips: summary.lessonsLearned,
      workingStyle: [],
      heartbeatChecks: [],
      cronJobs: (data.cronJobs || []).filter((j: any) => j.enabled).map((j: any) => ({
        name: j.name,
        schedule: j.schedule,
        description: j.description,
      })),
      integrations: summary.toolsUsed,
      persona: { tone: [], style: [], boundaries: [] },
    },
    raw: {
      soul: data.soul,
      agents: data.agents,
      identity: data.identity,
      tools: data.toolsRaw,
      memoryHighlights: null,
    },
    meta: {
      summarizedAt: new Date().toISOString(),
      usedLLM,
      model: usedLLM ? MODEL : null,
    },
  };
}

// ============ EXPORTS (for testing) ============

export { simpleSummary, formatOutput };
export type { LLMSummary };

// ============ MAIN ============

async function main() {
  const rl = readline.createInterface({ input: process.stdin, terminal: false });
  let input = '';
  for await (const line of rl) input += line + '\n';

  const data = JSON.parse(input);
  
  // Try LLM first
  const ollamaAvailable = await checkOllama();
  let summary: LLMSummary;
  let usedLLM = false;

  if (ollamaAvailable) {
    console.error(`Using local LLM (${MODEL})...`);
    const llmResult = await summarizeWithLLM(data);
    if (llmResult) {
      summary = llmResult;
      usedLLM = true;
      console.error('✓ LLM summary generated');
    } else {
      console.error('✗ LLM failed, using simple extraction');
      summary = simpleSummary(data);
    }
  } else {
    console.error('Ollama not available, using simple extraction.');
    console.error('');
    console.error('For richer summaries, install the Liquid Foundation Model (LFM2.5):');
    console.error('  1. Install Ollama: https://ollama.ai');
    console.error('  2. Pull LFM2.5:   ollama pull hf.co/LiquidAI/LFM2.5-1.2B-Instruct');
    console.error('  3. Re-run:         opensoul share');
    console.error('');
    summary = simpleSummary(data);
  }

  console.log(JSON.stringify(formatOutput(summary, data, usedLLM), null, 2));
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
