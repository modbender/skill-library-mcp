#!/usr/bin/env npx ts-node
/**
 * Browse OpenSoul community
 * 
 * Usage:
 *   npx ts-node browse.ts                    # List recent souls
 *   npx ts-node browse.ts "research"         # Search by keyword
 *   npx ts-node browse.ts --json             # Output as JSON
 *   npx ts-node browse.ts --sort popular     # Sort by views
 */

import { soulUrl } from './constants';

const API_URL = process.env.OPENSOUL_API || 'https://vztykbphiyumogausvhz.supabase.co/functions/v1';

interface Soul {
  id: string;
  title: string;
  tagline: string | null;
  use_cases: string[];
  agent_type: string | null;
  view_count: number;
  copy_count: number;
  remix_count: number;
  author?: { handle: string; name: string };
}

async function main() {
  const args = process.argv.slice(2);
  
  // Parse args
  let query = '';
  let format = 'text';
  let sort = 'recent';
  let limit = 10;
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--json') format = 'json';
    else if (args[i] === '--sort' && args[i + 1]) sort = args[++i];
    else if (args[i] === '--limit' && args[i + 1]) limit = parseInt(args[++i]);
    else if (!args[i].startsWith('--')) query = args[i];
  }
  
  // Build URL
  const params = new URLSearchParams();
  if (query) params.set('q', query);
  params.set('sort', sort);
  params.set('limit', limit.toString());
  
  const res = await fetch(`${API_URL}/souls-api?${params}`);
  const data = await res.json() as { souls?: Soul[]; total?: number; has_more?: boolean; message?: string };
  
  if (!res.ok) {
    console.error('Error:', data.message);
    process.exit(1);
  }
  
  if (format === 'json') {
    console.log(JSON.stringify(data, null, 2));
    return;
  }
  
  // Text format
  const souls: Soul[] = data.souls || [];
  
  if (souls.length === 0) {
    console.log('\nNo souls found.');
    if (query) console.log(`Try a different search term than "${query}"`);
    console.log('');
    return;
  }
  
  const total = data.total || 0;
  console.log(`\n🎭 Found ${total} soul${total !== 1 ? 's' : ''}${query ? ` matching "${query}"` : ''}:\n`);
  
  for (const soul of souls) {
    console.log(`  ${soul.title}`);
    if (soul.tagline) console.log(`  "${soul.tagline}"`);
    console.log(`  @${soul.author?.handle || 'unknown'} · ${soul.use_cases.slice(0, 3).join(', ') || 'general'}`);
    console.log(`  👁 ${soul.view_count}  📋 ${soul.copy_count}  🔀 ${soul.remix_count}`);
    console.log(`  → ${soulUrl(soul.id)}`);
    console.log('');
  }
  
  if (data.has_more) {
    console.log(`  ... and ${total - souls.length} more. Use --limit to see more.\n`);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
