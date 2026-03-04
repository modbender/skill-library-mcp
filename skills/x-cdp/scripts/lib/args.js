/**
 * Shared CLI argument parser for X CDP scripts.
 * Supports flags (--key value), boolean flags (--dry-run), and positional args.
 */

const fs = require('fs');

/**
 * Parse CLI arguments with validation.
 * @param {string[]} argv - process.argv
 * @param {Object} spec - { positional: ['name1','name2'], flags: { flag: type }, defaults: {} }
 *   type: 'string' | 'number' | 'boolean' | 'file' | 'string[]'
 * @returns {Object} parsed args
 */
function parseArgs(argv, spec) {
  const args = { ...spec.defaults };
  const positionalNames = spec.positional || [];
  let positionalIdx = 0;
  let i = 2;

  while (i < argv.length) {
    const arg = argv[i];

    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      const flagType = spec.flags?.[key];

      if (flagType === 'boolean') {
        args[key] = true;
        i++;
        continue;
      }

      if (!flagType) {
        console.error(`Unknown flag: --${key}`);
        i++;
        continue;
      }

      const value = argv[i + 1];
      if (value === undefined) {
        console.error(`Missing value for --${key}`);
        i++;
        continue;
      }

      switch (flagType) {
        case 'number': {
          const num = parseInt(value, 10);
          if (isNaN(num) || num <= 0) {
            console.error(`Invalid number for --${key}: ${value}`);
            process.exit(1);
          }
          args[key] = num;
          break;
        }
        case 'file': {
          if (!fs.existsSync(value)) {
            console.error(`File not found: ${value}`);
            process.exit(1);
          }
          args[key] = value;
          break;
        }
        case 'string[]': {
          if (!args[key]) args[key] = [];
          args[key].push(value);
          break;
        }
        default:
          args[key] = value;
      }
      i += 2;
      continue;
    }

    // Positional argument
    if (positionalIdx < positionalNames.length) {
      args[positionalNames[positionalIdx]] = arg;
      positionalIdx++;
    }
    i++;
  }

  return args;
}

module.exports = { parseArgs };
