#!/usr/bin/env node
/**
 * Check Reputation CLI
 * Check human reputation via Ethos Network, Talent Protocol, and Farcaster
 */

import { checkReputation, getSummary, formatHuman } from './lib/basecred.mjs';

// Parse arguments
const args = process.argv.slice(2);
const address = args.find(arg => arg.startsWith('0x'));
const flags = {
  summary: args.includes('--summary'),
  full: args.includes('--full'),
  json: args.includes('--json') || (!args.includes('--human')),
  human: args.includes('--human'),
  help: args.includes('--help') || args.includes('-h'),
};

// Show help
if (flags.help || !address) {
  console.log(`
📊 BaseCred SDK - Reputation Check

USAGE:
  node check-reputation.mjs <ethereum_address> [options]

OPTIONS:
  --summary     Return summary format only (default)
  --full        Return complete unified profile
  --json        JSON output (default)
  --human       Human-readable format
  --help, -h    Show this help

EXAMPLES:
  # Check vitalik.eth reputation
  node check-reputation.mjs 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045

  # Get full profile in JSON
  node check-reputation.mjs 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 --full

  # Human-readable summary
  node check-reputation.mjs 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 --human

ENVIRONMENT VARIABLES:
  TALENT_API_KEY    - Talent Protocol API key (optional, enables builder/creator scores)
  NEYNAR_API_KEY    - Neynar API key (optional, enables Farcaster quality scores)

NOTE:
  Ethos Network does not require an API key.
  Get Talent Protocol key: https://talentprotocol.com
  Get Neynar key: https://neynar.com
`);
  process.exit(flags.help ? 0 : 1);
}

// Execute
(async () => {
  try {
    // Fetch reputation
    const result = await checkReputation(address, { skipWarnings: flags.json });

    // Handle errors
    if (result.error) {
      if (flags.json) {
        console.log(JSON.stringify(result, null, 2));
      } else {
        console.error(`❌ Error: ${result.message}`);
      }
      process.exit(1);
    }

    // Determine output format
    let output;
    if (flags.full) {
      output = result.profile; // Full profile (unwrap from result)
    } else {
      output = getSummary(result); // Summary (default)
    }

    // Output
    if (flags.human) {
      console.log(formatHuman(output));
    } else {
      console.log(JSON.stringify(output, null, 2));
    }

    process.exit(0);

  } catch (error) {
    console.error('❌ Unexpected error:', error.message);
    process.exit(1);
  }
})();
