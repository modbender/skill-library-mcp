#!/usr/bin/env npx ts-node
/**
 * Get soul suggestions based on current workspace
 * Reads extracted workspace from stdin, fetches suggestions
 * 
 * Usage:
 *   npx ts-node extract.ts | npx ts-node suggest.ts
 *   npx ts-node suggest.ts --json < workspace.json
 */

import { soulUrl } from './constants';

const API_URL = process.env.OPENSOUL_API || 'https://vztykbphiyumogausvhz.supabase.co/functions/v1';

interface Suggestion {
  soul: {
    id: string;
    title: string;
    tagline: string | null;
    author?: { handle: string; name: string };
  };
  reason: string;
  adds_capabilities: string[];
  adds_use_cases: string[];
  match_score: number;
}

function extractUseCases(data: any): string[] {
  const useCases: string[] = [];
  const agents = (data.agents || '').toLowerCase();
  
  if (agents.includes('calendar')) useCases.push('calendar');
  if (agents.includes('email')) useCases.push('email');
  if (agents.includes('code') || agents.includes('coding')) useCases.push('coding');
  if (agents.includes('memory')) useCases.push('memory');
  if (agents.includes('research')) useCases.push('research');
  if (agents.includes('automation')) useCases.push('automation');
  if (agents.includes('chat') || agents.includes('messaging')) useCases.push('messaging');
  if (agents.includes('heartbeat') || agents.includes('proactive')) useCases.push('proactive-monitoring');
  
  return useCases;
}

async function main() {
  const args = process.argv.slice(2);
  const format = args.includes('--json') ? 'json' : 'text';
  
  // Read from stdin
  const readline = require('readline');
  const rl = readline.createInterface({ input: process.stdin, terminal: false });
  let input = '';
  for await (const line of rl) {
    input += line + '\n';
  }
  
  if (!input.trim()) {
    console.error('\n❌ No input. Pipe your workspace extract:\n');
    console.error('   npx ts-node extract.ts | npx ts-node suggest.ts\n');
    process.exit(1);
  }
  
  let data;
  try {
    data = JSON.parse(input);
  } catch (e) {
    console.error('\n❌ Invalid JSON input\n');
    process.exit(1);
  }
  
  // Build request
  const payload = {
    current_capabilities: data.tools?.toolNames || [],
    current_use_cases: extractUseCases(data),
    current_skills: data.skills?.map((s: any) => s.name) || []
  };
  
  const res = await fetch(`${API_URL}/suggest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  const result = await res.json() as { suggestions?: Suggestion[]; message?: string };
  
  if (!res.ok) {
    console.error('Error:', result.message);
    process.exit(1);
  }
  
  const suggestions: Suggestion[] = result.suggestions || [];
  
  if (format === 'json') {
    console.log(JSON.stringify(result, null, 2));
    return;
  }
  
  if (suggestions.length === 0) {
    console.log('\nNo suggestions found. The community needs more souls!\n');
    console.log('Be the first to share: npx ts-node extract.ts | npx ts-node anonymize.ts | npx ts-node summarize.ts | npx ts-node upload.ts\n');
    return;
  }
  
  console.log('\n💡 Suggestions for your workspace:\n');
  
  for (const s of suggestions) {
    console.log(`  ${s.soul.title}`);
    console.log(`  "${s.reason}"`);
    if (s.adds_capabilities.length > 0) {
      console.log(`  Adds: ${s.adds_capabilities.join(', ')}`);
    }
    console.log(`  → ${soulUrl(s.soul.id)}`);
    console.log('');
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
