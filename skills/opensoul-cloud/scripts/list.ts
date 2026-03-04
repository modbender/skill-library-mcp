#!/usr/bin/env tsx
/**
 * List your own souls on OpenSoul
 * 
 * Usage:
 *   opensoul list
 *   opensoul list --json
 */

import * as fs from 'fs';
import * as path from 'path';
import { soulUrl } from './constants';

const API_URL = process.env.OPENSOUL_API || 'https://vztykbphiyumogausvhz.supabase.co/functions/v1';
const CREDS_FILE = path.join(process.env.HOME!, '.opensoul/credentials.json');

interface Soul {
  id: string;
  title: string;
  tagline: string | null;
  created_at: string;
  view_count: number;
  copy_count: number;
  remix_count: number;
}

async function main() {
  const args = process.argv.slice(2);
  const format = args.includes('--json') ? 'json' : 'text';
  
  // Check credentials
  if (!fs.existsSync(CREDS_FILE)) {
    console.error('\n❌ Not registered. Run first:');
    console.error('   opensoul register\n');
    process.exit(1);
  }
  
  const creds = JSON.parse(fs.readFileSync(CREDS_FILE, 'utf-8'));
  
  // Fetch user's souls
  const res = await fetch(`${API_URL}/souls-api?author=${creds.id}`, {
    headers: {
      'Authorization': `Bearer ${creds.api_key}`
    }
  });
  
  const data = await res.json() as { souls?: Soul[]; message?: string };
  
  if (!res.ok) {
    console.error('Error:', data.message);
    process.exit(1);
  }
  
  if (format === 'json') {
    console.log(JSON.stringify(data, null, 2));
    return;
  }
  
  const souls: Soul[] = data.souls || [];
  
  if (souls.length === 0) {
    console.log('\nYou haven\'t shared any souls yet.');
    console.log('Share your first: opensoul share\n');
    return;
  }
  
  console.log(`\n🎭 Your souls (${souls.length}):\n`);
  
  for (const soul of souls) {
    const date = new Date(soul.created_at).toLocaleDateString();
    console.log(`  ${soul.title}`);
    if (soul.tagline) console.log(`  "${soul.tagline}"`);
    console.log(`  Created: ${date} · 👁 ${soul.view_count}  📋 ${soul.copy_count}  🔀 ${soul.remix_count}`);
    console.log(`  ID: ${soul.id}`);
    console.log(`  → ${soulUrl(soul.id)}`);
    console.log('');
  }
  
  console.log('To delete a soul: opensoul delete <id>\n');
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
