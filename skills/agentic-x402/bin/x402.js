#!/usr/bin/env node
// x402 CLI wrapper - runs the TypeScript CLI via tsx

import { spawn } from 'child_process';
import { dirname, resolve } from 'path';
import { fileURLToPath } from 'url';
import { existsSync } from 'fs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const cliPath = resolve(__dirname, 'cli.ts');

// Find tsx binary
function findTsx() {
  // Check local node_modules first
  const localTsx = resolve(__dirname, '../node_modules/.bin/tsx');
  if (existsSync(localTsx)) {
    return localTsx;
  }

  // Fall back to npx
  return null;
}

const tsxPath = findTsx();

// Suppress experimental warnings
const env = {
  ...process.env,
  NODE_NO_WARNINGS: '1',
  X402_CWD: process.cwd(),
};

let child;

if (tsxPath) {
  // Use local tsx directly
  child = spawn(tsxPath, [cliPath, ...process.argv.slice(2)], {
    stdio: 'inherit',
    env,
  });
} else {
  // Fall back to npx tsx
  child = spawn('npx', ['tsx', cliPath, ...process.argv.slice(2)], {
    stdio: 'inherit',
    env,
  });
}

child.on('close', (code) => {
  process.exit(code ?? 0);
});

child.on('error', (err) => {
  console.error('Failed to start x402 CLI:', err.message);
  console.error('Make sure tsx is installed: npm install -g tsx');
  process.exit(1);
});
