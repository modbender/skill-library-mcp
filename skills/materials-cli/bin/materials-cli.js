#!/usr/bin/env node

import { spawn } from 'child_process';
import { createRequire } from 'module';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const require = createRequire(import.meta.url);

const cliPath = join(__dirname, '../dist/index.js');

// Use tsx loader so dependencies that ship .ts (e.g. declare-render) are transpiled
let tsxLoader;
try {
  tsxLoader = require.resolve('tsx');
} catch {
  tsxLoader = null;
}
const exec = process.execPath;
const args = tsxLoader ? ['--import', tsxLoader, cliPath, ...process.argv.slice(2)] : [cliPath, ...process.argv.slice(2)];

const child = spawn(exec, args, {
  stdio: 'inherit',
  shell: process.platform === 'win32'
});

child.on('exit', (code) => {
  process.exit(code || 0);
});
