/**
 * index.js — Funky Fund Flamingo Entrypoint
 *
 * Responsibilities:
 * - Parse CLI arguments
 * - Resolve execution mode (single run vs relay loop)
 * - Invoke evolve.run()
 * - Fail loudly when the cycle breaks
 *
 * This file is orchestration only.
 * Mutation intelligence lives in evolve.js.
 */

'use strict';

const evolve = require('./evolve');

// -----------------------------------------------------------------------------
// CLI Parsing
// -----------------------------------------------------------------------------

function parseArgs(argv) {
  const args = argv.slice(2);

  return {
    command: args[0] || 'run',
    isLoop: args.includes('--loop') || args.includes('--funky-fund-flamingo'),
    isHelp: args.includes('--help') || args.includes('-h')
  };
}

// -----------------------------------------------------------------------------
// Execution Helpers
// -----------------------------------------------------------------------------

async function runEvolution({ isLoop }) {
  console.log('🚀 Starting Funky Fund Flamingo…');

  if (isLoop) {
    console.log('🦩 FUNKY FUND FLAMINGO MODE ACTIVATED');
    console.log('• Slow, local-only continuous improvement mode');
    console.log('• Next cycle should be rerun locally after the pacing interval\n');
  }

  try {
    await evolve.run();
  } catch (err) {
    console.error('\n❌ Evolution cycle failed.');
    console.error(err?.stack || err?.message || err);
    process.exit(1);
  }
}

function printUsage() {
  console.log(`
🧬 Funky Fund Flamingo

Usage:
  node index.js run
  node index.js /evolve
  node index.js --loop
  node index.js run --funky-fund-flamingo

Options:
  --loop, --funky-fund-flamingo   Enable continuous relay-based evolution
  --help, -h         Show this help message

Notes:
- In Funky Fund Flamingo mode, this process runs ONCE.
- The next cycle should be manually or locally rerun.
- This prevents runaway recursion or cron dependency.
`);
}

function printStarBeggar() {
  console.log('\n\x1b[33m%s\x1b[0m', '=======================================================');
  console.log('\x1b[33m%s\x1b[0m', '✨  Loving Funky Fund Flamingo? Give it a Star!  ✨');
  console.log('\x1b[36m%s\x1b[0m', '👉  https://github.com/IceMasterT/funky-fund-flamingo');
  console.log('\x1b[33m%s\x1b[0m', '=======================================================\n');
}

// -----------------------------------------------------------------------------
// Main
// -----------------------------------------------------------------------------

async function main() {
  const { command, isLoop, isHelp } = parseArgs(process.argv);

  if (isHelp) {
    printUsage();
    return;
  }

  // Normalize accepted commands
  const validCommands = new Set(['run', '/evolve']);

  if (!validCommands.has(command) && !isLoop) {
    printUsage();
    process.exit(1);
  }

  await runEvolution({ isLoop });

  // Cosmetic footer (non-functional, safe to remove)
  printStarBeggar();
}

// -----------------------------------------------------------------------------
// Entrypoint Guard
// -----------------------------------------------------------------------------

if (require.main === module) {
  main().catch(err => {
    console.error('❌ Unhandled fatal error.');
    console.error(err?.stack || err);
    process.exit(1);
  });
}
