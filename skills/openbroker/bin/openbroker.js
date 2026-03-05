#!/usr/bin/env node

// This wrapper runs the TypeScript CLI using tsx
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const packageRoot = path.dirname(__dirname);
const cliPath = path.join(__dirname, 'cli.ts');

// Run the TypeScript CLI with tsx from package's node_modules
const tsxBin = path.join(packageRoot, 'node_modules', '.bin', 'tsx');

const child = spawn(
  tsxBin,
  [cliPath, ...process.argv.slice(2)],
  {
    stdio: 'inherit',
    cwd: packageRoot,
    env: {
      ...process.env,
      // Preserve the original working directory for local .env lookup
      OPENBROKER_CWD: process.cwd(),
      // Suppress Node.js experimental warnings
      NODE_NO_WARNINGS: '1',
    },
  }
);

child.on('error', (err) => {
  // If tsx binary not found, try npx tsx as fallback
  if (err.code === 'ENOENT') {
    const fallback = spawn(
      'npx',
      ['tsx', cliPath, ...process.argv.slice(2)],
      {
        stdio: 'inherit',
        cwd: packageRoot,
        env: {
          ...process.env,
          OPENBROKER_CWD: process.cwd(),
          NODE_NO_WARNINGS: '1',
        },
      }
    );
    fallback.on('exit', (code) => process.exit(code ?? 0));
    fallback.on('error', () => {
      console.error('Error: tsx not found. Try reinstalling openbroker.');
      process.exit(1);
    });
  } else {
    console.error('Error:', err.message);
    process.exit(1);
  }
});

child.on('exit', (code) => {
  process.exit(code ?? 0);
});
