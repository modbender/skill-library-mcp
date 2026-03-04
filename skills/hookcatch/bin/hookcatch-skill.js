#!/usr/bin/env node

/**
 * HookCatch Skill Wrapper for OpenClaw
 * 
 * This wrapper provides AI-friendly output formatting and error handling
 * for the HookCatch CLI when used by OpenClaw agents.
 */

const { spawn } = require('child_process');
const path = require('path');

// Check if HOOKCATCH_API_KEY is set
if (!process.env.HOOKCATCH_API_KEY && !process.env.HOOKCATCH_TOKEN) {
  console.error(JSON.stringify({
    error: 'Authentication required',
    message: 'Set HOOKCATCH_API_KEY environment variable. Generate one with: hookcatch token generate',
    action: 'run_command',
    command: 'hookcatch token generate'
  }));
  process.exit(1);
}

// Get command arguments
const args = process.argv.slice(2);

if (args.length === 0) {
  console.log(JSON.stringify({
    name: 'HookCatch',
    version: '1.0.0',
    description: 'Webhook testing and localhost tunneling',
    commands: [
      { name: 'bin create', description: 'Create a new webhook bin' },
      { name: 'bin list', description: 'List your webhook bins' },
      { name: 'bin requests <binId>', description: 'Get captured requests' },
      { name: 'bin update <binId>', description: 'Update bin settings' },
      { name: 'bin delete <binId>', description: 'Delete a bin' },
      { name: 'request <requestId> <binId>', description: 'Show a single request' },
      { name: 'replay <binId> <requestId> <url>', description: 'Replay a request to a target URL' },
      { name: 'tunnel <port>', description: 'Create localhost tunnel' },
      { name: 'tunnel list', description: 'List active tunnels' },
      { name: 'stop <tunnelId>', description: 'Stop an active tunnel' },
      { name: 'token generate', description: 'Generate API token' },
      { name: 'token status', description: 'Check token status' },
      { name: 'token revoke', description: 'Revoke API token' },
      { name: 'status', description: 'Show account details' }
    ],
    usage: 'hookcatch-skill <command> [options]'
  }, null, 2));
  process.exit(0);
}

// Force JSON output where supported (better for AI parsing)
if (args[0] === 'bin' && ['create', 'list', 'requests'].includes(args[1]) && !args.includes('--format')) {
  args.push('--format', 'json');
}

if (args[0] === 'request' && !args.includes('--format')) {
  args.push('--format', 'json');
}

// Execute the actual hookcatch CLI
const hookcatch = spawn('hookcatch', args, {
  stdio: 'inherit',
  env: {
    ...process.env,
    // Map HOOKCATCH_API_KEY to HOOKCATCH_TOKEN for the CLI
    HOOKCATCH_TOKEN: process.env.HOOKCATCH_API_KEY || process.env.HOOKCATCH_TOKEN
  }
});

hookcatch.on('error', (err) => {
  console.error(JSON.stringify({
    error: 'Failed to execute HookCatch CLI',
    message: err.message,
    hint: 'Make sure HookCatch CLI is installed: npm install -g hookcatch'
  }));
  process.exit(1);
});

hookcatch.on('exit', (code) => {
  process.exit(code || 0);
});
