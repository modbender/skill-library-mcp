#!/usr/bin/env node
/**
 * OpenClaw Avatar CLI
 *
 * Usage: openclaw-avatar [options]
 */

import { loadConfig } from './config/index.js';

// Simple CLI - just starts the server
async function main(): Promise<void> {
  const args = process.argv.slice(2);

  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
OpenClaw Avatar - Interactive AI avatar frontend

Usage: openclaw-avatar [options]

Options:
  --help, -h     Show this help message
  --version, -v  Show version number

Configuration:
  - Copy .env.example to .env and add your API keys
  - Optionally copy avatar.config.example.json to avatar.config.json

For more information, see: https://github.com/openclaw/avatar
`);
    process.exit(0);
  }

  if (args.includes('--version') || args.includes('-v')) {
    // Read version from package.json
    const pkg = await import('../package.json', { assert: { type: 'json' } });
    console.log(pkg.default.version);
    process.exit(0);
  }

  // Validate config before starting
  try {
    loadConfig();
  } catch (err) {
    console.error('Configuration error:', (err as Error).message);
    console.error('\nMake sure you have:');
    console.error('  1. Copied .env.example to .env');
    console.error('  2. Added your SIMLI_API_KEY and ELEVENLABS_API_KEY');
    process.exit(1);
  }

  // Import and run the server
  await import('./server.js');
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
