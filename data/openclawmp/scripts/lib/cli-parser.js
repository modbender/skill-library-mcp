// ============================================================================
// cli-parser.js — Lightweight argument parser (no dependencies)
//
// Parses: command, positional args, and --flag / --key=value / --key value
// ============================================================================

'use strict';

/**
 * Parse process.argv-style arguments
 * @param {string[]} argv - Arguments (without node and script path)
 * @returns {{ command: string|null, args: string[], flags: object }}
 */
function parseArgs(argv) {
  const flags = {};
  const positional = [];

  let i = 0;
  while (i < argv.length) {
    const arg = argv[i];

    if (arg === '--') {
      // Everything after -- is positional
      positional.push(...argv.slice(i + 1));
      break;
    }

    if (arg.startsWith('--')) {
      const eqIndex = arg.indexOf('=');
      if (eqIndex !== -1) {
        // --key=value
        const key = arg.slice(2, eqIndex);
        flags[key] = arg.slice(eqIndex + 1);
      } else {
        const key = arg.slice(2);
        // Check if next arg is a value (not a flag)
        if (i + 1 < argv.length && !argv[i + 1].startsWith('-')) {
          flags[key] = argv[i + 1];
          i++;
        } else {
          flags[key] = true;
        }
      }
    } else if (arg.startsWith('-') && arg.length === 2) {
      // Short flag: -h, -v, etc.
      const key = arg.slice(1);
      flags[key] = true;
    } else {
      positional.push(arg);
    }

    i++;
  }

  const command = positional[0] || null;
  const args = positional.slice(1);

  return { command, args, flags };
}

module.exports = { parseArgs };
