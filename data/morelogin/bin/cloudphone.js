#!/usr/bin/env node
const { spawn } = require('child_process');
const path = require('path');

function main() {
  const script = path.join(__dirname, 'morelogin.js');
  const incoming = process.argv.slice(2);
  const args = ['cloudphone', ...(incoming.length > 0 ? incoming : ['help'])];
  const child = spawn(process.execPath, [script, ...args], {
    stdio: 'inherit',
  });

  child.on('exit', (code) => {
    process.exit(code || 0);
  });
}

main();
