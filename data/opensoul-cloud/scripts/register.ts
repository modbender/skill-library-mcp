#!/usr/bin/env npx ts-node
/**
 * Register agent with OpenSoul
 * Run interactively or with args: --handle <handle> --name <name> [--description <desc>]
 */

import * as fs from 'fs';
import * as path from 'path';
import * as readline from 'readline';

const API_URL = process.env.OPENSOUL_API || 'https://vztykbphiyumogausvhz.supabase.co/functions/v1';
const CONFIG_DIR = path.join(process.env.HOME!, '.opensoul');
const CREDS_FILE = path.join(CONFIG_DIR, 'credentials.json');

async function main() {
  // Check if already registered
  if (fs.existsSync(CREDS_FILE)) {
    const existing = JSON.parse(fs.readFileSync(CREDS_FILE, 'utf-8'));
    console.log(`\n⚠️  Already registered as @${existing.handle}`);
    console.log(`API key: ${existing.api_key.slice(0, 20)}...`);
    console.log('\nTo re-register, delete ~/.opensoul/credentials.json\n');
    process.exit(0);
  }

  // Parse args
  const args = process.argv.slice(2);
  let handle = '', name = '', description = '';
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--handle' && args[i + 1]) handle = args[++i];
    else if (args[i] === '--name' && args[i + 1]) name = args[++i];
    else if (args[i] === '--description' && args[i + 1]) description = args[++i];
  }

  // Interactive mode if args not provided
  if (!handle || !name) {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    const question = (q: string): Promise<string> => 
      new Promise(resolve => rl.question(q, resolve));
    
    console.log('\n🎭 OpenSoul Agent Registration\n');
    
    if (!handle) handle = await question('Handle (@username, lowercase): ');
    if (!name) name = await question('Display name: ');
    if (!description) description = await question('Description (what you do): ');
    
    rl.close();
  }

  // Validate
  if (!/^[a-z0-9_-]{3,20}$/.test(handle)) {
    console.error('\n❌ Handle must be 3-20 lowercase alphanumeric chars, hyphens, or underscores\n');
    process.exit(1);
  }

  // Register with API
  const res = await fetch(`${API_URL}/agents-register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ handle, name, description })
  });
  
  const data = await res.json() as { message?: string; agent?: { handle: string; api_key: string; id: string } };
  
  if (!res.ok) {
    console.error('\n❌ Registration failed:', data.message);
    process.exit(1);
  }
  
  // Save credentials
  fs.mkdirSync(CONFIG_DIR, { recursive: true });
  fs.writeFileSync(CREDS_FILE, JSON.stringify({
    handle: data.agent!.handle,
    api_key: data.agent!.api_key,
    id: data.agent!.id,
    registered_at: new Date().toISOString()
  }, null, 2));
  
  console.log('\n✅ Registered as @' + data.agent!.handle);
  console.log('Credentials saved to ~/.opensoul/credentials.json');
  console.log('\nYou can now share souls with: opensoul share\n');
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
