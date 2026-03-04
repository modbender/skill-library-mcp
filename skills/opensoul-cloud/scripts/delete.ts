#!/usr/bin/env tsx
/**
 * Delete a soul from OpenSoul
 * 
 * Usage:
 *   opensoul delete <soul-id>
 *   opensoul delete <soul-id> --force   # Skip confirmation
 */

import * as fs from 'fs';
import * as path from 'path';
import * as readline from 'readline';

const API_URL = process.env.OPENSOUL_API || 'https://vztykbphiyumogausvhz.supabase.co/functions/v1';
const CREDS_FILE = path.join(process.env.HOME!, '.opensoul/credentials.json');

async function confirm(question: string): Promise<boolean> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.toLowerCase() === 'y' || answer.toLowerCase() === 'yes');
    });
  });
}

async function main() {
  const args = process.argv.slice(2);
  
  // Parse args
  const force = args.includes('--force');
  const soulId = args.find(a => !a.startsWith('--'));
  
  if (!soulId) {
    console.error('\n❌ Missing soul ID');
    console.error('Usage: opensoul delete <soul-id>');
    console.error('\nFind your soul IDs with: opensoul list\n');
    process.exit(1);
  }
  
  // Check credentials
  if (!fs.existsSync(CREDS_FILE)) {
    console.error('\n❌ Not registered. Run first:');
    console.error('   opensoul register\n');
    process.exit(1);
  }
  
  const creds = JSON.parse(fs.readFileSync(CREDS_FILE, 'utf-8'));
  
  // Confirm deletion
  if (!force) {
    const confirmed = await confirm(`\n⚠️  Delete soul ${soulId}? This cannot be undone. (y/N) `);
    if (!confirmed) {
      console.log('Cancelled.\n');
      process.exit(0);
    }
  }
  
  // Delete
  const res = await fetch(`${API_URL}/souls-api/${soulId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${creds.api_key}`
    }
  });
  
  const result = await res.json() as { message?: string };
  
  if (!res.ok) {
    console.error('\n❌ Delete failed:', result.message);
    process.exit(1);
  }
  
  console.log('\n✅ Soul deleted.\n');
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
