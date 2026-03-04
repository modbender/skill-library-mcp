#!/usr/bin/env npx ts-node
/**
 * Upload anonymized soul to OpenSoul
 * Reads summarized JSON from stdin, uploads to API
 * 
 * Usage: cat summary.json | npx ts-node upload.ts
 * Or pipe from full pipeline:
 *   npx ts-node extract.ts | npx ts-node anonymize.ts | npx ts-node summarize.ts | npx ts-node upload.ts
 */

import * as fs from 'fs';
import * as path from 'path';
import * as readline from 'readline';

const API_URL = process.env.OPENSOUL_API || 'https://vztykbphiyumogausvhz.supabase.co/functions/v1';
const CREDS_FILE = path.join(process.env.HOME!, '.opensoul/credentials.json');

function inferAgentType(data: any): string {
  const agents = data.raw?.agents?.toLowerCase() || '';
  if (agents.includes('orchestrat')) return 'orchestrator';
  if (agents.includes('specialist') || agents.includes('expert')) return 'specialist';
  if (agents.includes('critic') || agents.includes('review')) return 'critic';
  if (agents.includes('generator') || agents.includes('creat')) return 'generator';
  return 'assistant';
}

async function main() {
  // Check credentials
  if (!fs.existsSync(CREDS_FILE)) {
    console.error('\n❌ Not registered. Run first:');
    console.error('   npx ts-node scripts/register.ts\n');
    process.exit(1);
  }
  
  const creds = JSON.parse(fs.readFileSync(CREDS_FILE, 'utf-8'));
  
  // Read from stdin
  const rl = readline.createInterface({ input: process.stdin, terminal: false });
  let input = '';
  for await (const line of rl) {
    input += line + '\n';
  }
  
  if (!input.trim()) {
    console.error('\n❌ No input received. Pipe summarized JSON to this script.\n');
    console.error('Usage:');
    console.error('  npx ts-node extract.ts | npx ts-node anonymize.ts | npx ts-node summarize.ts | npx ts-node upload.ts\n');
    process.exit(1);
  }
  
  let data;
  try {
    data = JSON.parse(input);
  } catch (e) {
    console.error('\n❌ Invalid JSON input\n');
    process.exit(1);
  }
  
  // Build payload
  const payload = {
    title: data.profile?.title || 'Untitled Soul',
    tagline: data.profile?.tagline || null,
    description: data.profile?.summary || data.profile?.description || null,
    use_cases: data.profile?.useCases || [],
    capabilities: data.profile?.capabilities || [],
    agent_type: data.profile?.agentType || inferAgentType(data),
    skills: data.profile?.skills || [],
    persona: {
      tone: data.profile?.persona?.tone || [],
      style: data.profile?.persona?.style || [],
      boundaries: data.profile?.persona?.boundaries || []
    },
    // v2: Experience fields (now LLM-generated)
    workflows: data.profile?.keyPatterns || data.profile?.workflows || [],
    lessons_learned: data.profile?.lessonsLearned || [],
    tips: data.profile?.tips || [],
    working_style: data.profile?.workingStyle || [],
    heartbeat_checks: data.profile?.interestingAutomation || data.profile?.heartbeatChecks || [],
    integrations: data.profile?.toolsUsed || data.profile?.integrations || [],
    cron_jobs: data.profile?.cronJobs || [],
    // Files
    files: {
      soul_md: data.raw?.soul || null,
      agents_md: data.raw?.agents || null,
      tools_md: data.raw?.tools || null,  // Anonymized TOOLS.md (secrets stripped)
      identity_md: data.raw?.identity || null,
      memory_highlights: data.raw?.memoryHighlights || null,  // v2: anonymized memory snippets
    },
    personal_note: process.env.OPENSOUL_NOTE || null,
    remixed_from: null
  };
  
  // Upload
  const res = await fetch(`${API_URL}/souls-api`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${creds.api_key}`
    },
    body: JSON.stringify(payload)
  });
  
  const result = await res.json() as { message?: string; url?: string; id?: string };
  
  if (!res.ok) {
    console.error('\n❌ Upload failed:', result.message);
    process.exit(1);
  }
  
  console.log('\n✅ Soul shared!');
  console.log(`   ${result.url}`);
  
  // Share on X link
  const xText = encodeURIComponent('Check out my agent soul on OpenSoul');
  const xUrl = encodeURIComponent(result.url || '');
  console.log(`   Share on X: https://x.com/intent/tweet?text=${xText}&url=${xUrl}\n`);
  
  // Hint about LFM2.5 for better summaries
  if (!data.meta?.usedLLM) {
    console.log('💡 Tip: Get better summaries with the Liquid Foundation Model:');
    console.log('   ollama pull hf.co/LiquidAI/LFM2.5-1.2B-Instruct');
    console.log('   opensoul share   # LFM2.5 will be used automatically\n');
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
