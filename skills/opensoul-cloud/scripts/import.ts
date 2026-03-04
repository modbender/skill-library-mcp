#!/usr/bin/env npx ts-node
/**
 * Import a soul for inspiration
 * Downloads files to workspace/imported/<soul-id>/
 * 
 * Usage:
 *   npx ts-node import.ts <soul-id>
 *   npx ts-node import.ts fd5aa69a-1fe2-4994-a096-950a5541ced0
 */

import * as fs from 'fs';
import * as path from 'path';
import { soulUrl } from './constants';

const API_URL = process.env.OPENSOUL_API || 'https://vztykbphiyumogausvhz.supabase.co/functions/v1';
const WORKSPACE = process.env.OPENCLAW_WORKSPACE || path.join(process.env.HOME!, '.openclaw/workspace');

interface Soul {
  id: string;
  title: string;
  tagline: string | null;
  description: string | null;
  files: {
    soul_md?: string;
    agents_md?: string;
    tools_md?: string;
    identity_md?: string;
  };
  author?: { handle: string; name: string };
  created_at: string;
}

async function main() {
  const soulId = process.argv[2];
  
  if (!soulId) {
    console.error('\n❌ Usage: npx ts-node import.ts <soul-id>\n');
    console.error('Find soul IDs by browsing: npx ts-node browse.ts\n');
    process.exit(1);
  }
  
  // Fetch soul
  const res = await fetch(`${API_URL}/souls-api/${soulId}`);
  
  if (!res.ok) {
    if (res.status === 404) {
      console.error('\n❌ Soul not found:', soulId);
      console.error('Browse available souls: npx ts-node browse.ts\n');
    } else {
      const error = await res.json() as { message?: string };
      console.error('\n❌ Error:', error.message);
    }
    process.exit(1);
  }
  
  const soul = await res.json() as Soul;
  
  // Create import directory
  const importDir = path.join(WORKSPACE, 'imported', soulId);
  fs.mkdirSync(importDir, { recursive: true });
  
  // Write files
  const written: string[] = [];
  
  if (soul.files?.soul_md) {
    fs.writeFileSync(path.join(importDir, 'SOUL.md'), soul.files.soul_md);
    written.push('SOUL.md');
  }
  if (soul.files?.agents_md) {
    fs.writeFileSync(path.join(importDir, 'AGENTS.md'), soul.files.agents_md);
    written.push('AGENTS.md');
  }
  if (soul.files?.identity_md) {
    fs.writeFileSync(path.join(importDir, 'IDENTITY.md'), soul.files.identity_md);
    written.push('IDENTITY.md');
  }
  // Note: tools_md is intentionally never shared/imported
  
  // Write metadata
  const meta = {
    id: soul.id,
    title: soul.title,
    tagline: soul.tagline,
    description: soul.description,
    author: soul.author?.handle || 'anonymous',
    imported_at: new Date().toISOString(),
    original_created_at: soul.created_at,
    url: soulUrl(soul.id)
  };
  fs.writeFileSync(path.join(importDir, 'META.json'), JSON.stringify(meta, null, 2));
  written.push('META.json');
  
  console.log(`\n✅ Imported "${soul.title}" to:`);
  console.log(`   ${importDir}\n`);
  console.log('Files:');
  for (const f of written) {
    console.log(`  - ${f}`);
  }
  console.log('\n💡 These are for inspiration — read them, learn patterns, adapt to your style.\n');
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
