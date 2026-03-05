#!/usr/bin/env node
// ============================================================================
// 🐟 OpenClaw Marketplace CLI (openclawmp)
//
// Pure Node.js rewrite of seafood-market.sh
// Zero external runtime dependencies
// ============================================================================

'use strict';

const path = require('path');
const libDir = path.join(__dirname, '..', 'lib');
const { parseArgs } = require(path.join(libDir, 'cli-parser.js'));
const { printHelp } = require(path.join(libDir, 'help.js'));

// Command handlers (lazy-loaded)
const cmdDir = path.join(libDir, 'commands');
const commands = {
  install:          () => require(path.join(cmdDir, 'install.js')),
  uninstall:        () => require(path.join(cmdDir, 'uninstall.js')),
  search:           () => require(path.join(cmdDir, 'search.js')),
  list:             () => require(path.join(cmdDir, 'list.js')),
  info:             () => require(path.join(cmdDir, 'info.js')),
  publish:          () => require(path.join(cmdDir, 'publish.js')),
  login:            () => require(path.join(cmdDir, 'login.js')),
  authorize:        () => require(path.join(cmdDir, 'login.js')),  // alias
  whoami:           () => require(path.join(cmdDir, 'whoami.js')),
  star:             () => ({ run: (a, f) => require(path.join(cmdDir, 'star.js')).runStar(a, f) }),
  unstar:           () => ({ run: (a, f) => require(path.join(cmdDir, 'star.js')).runUnstar(a, f) }),
  comment:          () => ({ run: (a, f) => require(path.join(cmdDir, 'comment.js')).runComment(a, f) }),
  comments:         () => ({ run: (a, f) => require(path.join(cmdDir, 'comment.js')).runComments(a, f) }),
  issue:            () => ({ run: (a, f) => require(path.join(cmdDir, 'issue.js')).runIssue(a, f) }),
  issues:           () => ({ run: (a, f) => require(path.join(cmdDir, 'issue.js')).runIssues(a, f) }),
  'delete-account': () => require(path.join(cmdDir, 'delete-account.js')),
  unbind:           () => require(path.join(cmdDir, 'unbind.js')),
  help:             () => ({ run: () => printHelp() }),
};

async function main() {
  const { command, args, flags } = parseArgs(process.argv.slice(2));

  // Handle version flag
  if (flags.version || flags.v) {
    const pkg = require(path.join(__dirname, '..', 'package.json'));
    console.log(pkg.version);
    process.exit(0);
  }

  // Handle help flag or no command
  if (flags.help || flags.h || command === 'help' || !command) {
    printHelp();
    process.exit(0);
  }

  // Resolve command
  const loader = commands[command];
  if (!loader) {
    const ui = require(path.join(libDir, 'ui.js'));
    ui.err(`Unknown command: ${command}`);
    console.log('');
    printHelp();
    process.exit(1);
  }

  // Override API base if --api flag or env var provided
  if (flags.api || process.env.OPENCLAWMP_API) {
    const config = require(path.join(libDir, 'config.js'));
    config.setApiBase(flags.api || process.env.OPENCLAWMP_API);
  }

  try {
    const mod = loader();
    await mod.run(args, flags);
  } catch (e) {
    const ui = require(path.join(libDir, 'ui.js'));
    if (e.code === 'ENOTFOUND' || e.code === 'ECONNREFUSED') {
      ui.err(`Cannot reach API server. Check your connection or use --api to set a custom endpoint.`);
    } else {
      ui.err(e.message || String(e));
    }
    process.exit(1);
  }
}

main();
