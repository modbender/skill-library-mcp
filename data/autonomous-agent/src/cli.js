#!/usr/bin/env node
/**
 * CLI router for cornerstone-autonomous-agent.
 * Enables: npx cornerstone-autonomous-agent <command> [args...]
 * Commands: attest:aptos, attest:evm, and fallback to run-agent (default).
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, '..');

const COMMANDS = {
  'attest:aptos': 'src/attest-aptos-wallet.js',
  'attest:evm': 'src/attest-evm-wallet.js',
  'setup': 'src/setup.js',
  'setup:aptos': 'src/setup-aptos.js',
  'setup:evm:multichain': 'src/setup-evm-multichain.js',
  'addresses': 'src/show-agent-addresses.js',
  'balance': 'src/balance.js',
  'transfer': 'src/transfer.js',
  'contract': 'src/contract.js',
  'swap': 'src/swap.js',
  'agent': 'src/run-agent.js',
  'start': 'src/run-agent.js',
};

function main() {
  const args = process.argv.slice(2);
  const sub = args[0];
  const script = sub && COMMANDS[sub];

  if (script) {
    const scriptPath = join(root, script);
    const rest = args.slice(1);
    const child = spawn(process.execPath, [scriptPath, ...rest], {
      stdio: 'inherit',
      cwd: root,
      env: process.env,
    });
    child.on('exit', (code) => process.exit(code ?? 0));
    return;
  }

  // Default: run the skill demo (backward compatibility: npx cornerstone-autonomous-agent "some message")
  const runAgentPath = join(root, 'src/run-agent.js');
  const child = spawn(process.execPath, [runAgentPath, ...args], {
    stdio: 'inherit',
    cwd: root,
    env: process.env,
  });
  child.on('exit', (code) => process.exit(code ?? 0));
}

main();
