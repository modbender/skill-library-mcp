#!/usr/bin/env npx tsx
// x402 CLI - Agent skill for x402 payments

import { spawn } from 'child_process';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const scriptsDir = resolve(__dirname, '../scripts');

interface Command {
  script: string;
  description: string;
  category: 'setup' | 'info' | 'payments' | 'links';
}

const commands: Record<string, Command> = {
  // Setup commands
  setup: {
    script: 'commands/setup.ts',
    description: 'Create or configure your x402 wallet',
    category: 'setup',
  },

  // Info commands
  balance: {
    script: 'commands/balance.ts',
    description: 'Check wallet USDC and ETH balances',
    category: 'info',
  },

  // Payment commands
  pay: {
    script: 'commands/pay.ts',
    description: 'Pay for an x402-gated resource',
    category: 'payments',
  },
  fetch: {
    script: 'commands/fetch-paid.ts',
    description: 'Fetch URL with automatic x402 payment',
    category: 'payments',
  },

  // Link commands (21cash integration)
  'create-link': {
    script: 'commands/create-link.ts',
    description: 'Create a payment link to sell content',
    category: 'links',
  },
  'link-info': {
    script: 'commands/link-info.ts',
    description: 'Get info about a payment link',
    category: 'links',
  },
  routers: {
    script: 'commands/routers.ts',
    description: 'List routers where your wallet is a beneficiary',
    category: 'links',
  },
  distribute: {
    script: 'commands/distribute.ts',
    description: 'Distribute USDC from a PaymentRouter',
    category: 'links',
  },
};

function showHelp() {
  console.log(`
x402 - Agent skill for x402 payments

Usage: x402 <command> [arguments]

Setup:
  setup               Create or configure your x402 wallet

Info Commands:
  balance             Check wallet USDC and ETH balances

Payment Commands:
  pay <url>           Pay for an x402-gated resource
  fetch <url>         Fetch URL with automatic x402 payment

Link Commands (21cash integration):
  create-link         Create a payment link to sell content
  link-info <addr>    Get info about a payment link
  routers             List routers where your wallet is a beneficiary
  distribute <addr>   Distribute USDC from a PaymentRouter

Options:
  -h, --help          Show this help
  -v, --version       Show version

Getting Started:
  1. Run "x402 setup" to create a new wallet
  2. Fund your wallet with USDC on Base
  3. Run "x402 balance" to verify
  4. Use "x402 pay <url>" to pay for resources

For command-specific help: x402 <command> --help
`);
}

function showVersion() {
  console.log('agentic-x402 v0.2.1');
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === '-h' || args[0] === '--help' || args[0] === 'help') {
    showHelp();
    process.exit(0);
  }

  if (args[0] === '-v' || args[0] === '--version' || args[0] === 'version') {
    showVersion();
    process.exit(0);
  }

  const commandName = args[0];
  const command = commands[commandName];

  if (!command) {
    console.error(`Unknown command: ${commandName}`);
    console.error('Run "x402 --help" for available commands.');
    process.exit(1);
  }

  const scriptPath = resolve(scriptsDir, command.script);
  const commandArgs = args.slice(1);

  // Run the script with tsx
  const child = spawn('npx', ['tsx', scriptPath, ...commandArgs], {
    stdio: 'inherit',
    env: {
      ...process.env,
      X402_CWD: process.cwd(),
    },
  });

  child.on('close', (code) => {
    process.exit(code ?? 0);
  });

  child.on('error', (err) => {
    console.error('Failed to run command:', err.message);
    process.exit(1);
  });
}

main();
