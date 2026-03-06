#!/usr/bin/env node
// Open Broker CLI - Hyperliquid trading toolkit

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const scriptsDir = path.resolve(__dirname, '../scripts');

const commands: Record<string, { script: string; description: string }> = {
  // Setup
  'setup': { script: 'setup/onboard.ts', description: 'Interactive setup wizard' },
  'onboard': { script: 'setup/onboard.ts', description: 'Interactive setup wizard' },
  'approve-builder': { script: 'setup/approve-builder.ts', description: 'Approve builder fee' },

  // Info
  'account': { script: 'info/account.ts', description: 'View account balance and equity' },
  'positions': { script: 'info/positions.ts', description: 'View open positions' },
  'funding': { script: 'info/funding.ts', description: 'View funding rates' },
  'markets': { script: 'info/markets.ts', description: 'View market data' },
  'all-markets': { script: 'info/all-markets.ts', description: 'View all markets (perps, HIP-3, spot)' },
  'search': { script: 'info/search-markets.ts', description: 'Search for assets across providers' },
  'spot': { script: 'info/spot.ts', description: 'View spot markets and balances' },

  // Operations
  'buy': { script: 'operations/market-order.ts', description: 'Market buy order' },
  'sell': { script: 'operations/market-order.ts', description: 'Market sell order' },
  'market': { script: 'operations/market-order.ts', description: 'Market order' },
  'limit': { script: 'operations/limit-order.ts', description: 'Limit order' },
  'trigger': { script: 'operations/trigger-order.ts', description: 'Trigger order (TP/SL)' },
  'tpsl': { script: 'operations/set-tpsl.ts', description: 'Set TP/SL on position' },
  'cancel': { script: 'operations/cancel.ts', description: 'Cancel orders' },
  'twap': { script: 'operations/twap.ts', description: 'TWAP execution' },
  'scale': { script: 'operations/scale.ts', description: 'Scale in/out orders' },
  'bracket': { script: 'operations/bracket.ts', description: 'Bracket order (entry + TP + SL)' },
  'chase': { script: 'operations/chase.ts', description: 'Chase order with ALO' },

  // Strategies
  'funding-arb': { script: 'strategies/funding-arb.ts', description: 'Funding arbitrage strategy' },
  'grid': { script: 'strategies/grid.ts', description: 'Grid trading strategy' },
  'dca': { script: 'strategies/dca.ts', description: 'DCA strategy' },
  'mm-spread': { script: 'strategies/mm-spread.ts', description: 'Market making (spread)' },
  'mm-maker': { script: 'strategies/mm-maker.ts', description: 'Market making (ALO)' },
};

function printHelp() {
  console.log(`
Open Broker - Hyperliquid Trading CLI

Usage: openbroker <command> [options]

Setup:
  setup                One-command setup (wallet + config + builder approval)

Info Commands:
  account              View account balance, equity, and margin
  positions            View open positions with PnL
  funding              View funding rates (sorted by annualized rate)
  markets              View market data for main perps
  all-markets          View all markets (perps, HIP-3, spot)
  search               Search for assets across all providers
  spot                 View spot markets and balances

Trading Commands:
  buy                  Market buy order
  sell                 Market sell order
  market               Market order (specify --side)
  limit                Limit order
  trigger              Trigger order (stop loss / take profit)
  tpsl                 Set TP/SL on existing position
  cancel               Cancel orders

Advanced Execution:
  twap                 Time-weighted average price execution
  scale                Scale in/out with multiple orders
  bracket              Entry with TP and SL
  chase                Chase price with ALO orders

Strategies:
  funding-arb          Funding rate arbitrage
  grid                 Grid trading
  dca                  Dollar cost averaging
  mm-spread            Market making (spread-based)
  mm-maker             Market making (ALO orders)

Options:
  --help, -h           Show help for a command
  --dry                Preview without executing
  --verbose            Show debug output

Utility:
  approve-builder      Check or retry builder fee approval

Examples:
  openbroker setup                              # First-time setup (does everything)
  openbroker account                            # View account info
  openbroker buy --coin ETH --size 0.1          # Market buy 0.1 ETH
  openbroker limit --coin BTC --side buy --size 0.01 --price 60000
  openbroker search --query GOLD                # Find GOLD across providers
  openbroker tpsl --coin HYPE --tp 40 --sl 30   # Set TP/SL on position

Documentation: https://github.com/aurracloud/open-broker
`);
}

function runScript(scriptPath: string, args: string[]) {
  const fullPath = path.join(scriptsDir, scriptPath);

  // Use tsx to run TypeScript directly
  const child = spawn('npx', ['tsx', fullPath, ...args], {
    stdio: 'inherit',
    cwd: path.resolve(__dirname, '..'),
    env: { ...process.env },
  });

  child.on('error', (err) => {
    if ((err as NodeJS.ErrnoException).code === 'ENOENT') {
      console.error('Error: npx/tsx not found. Please ensure Node.js is installed.');
    } else {
      console.error('Error:', err.message);
    }
    process.exit(1);
  });

  child.on('exit', (code) => {
    process.exit(code ?? 0);
  });
}

function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    printHelp();
    process.exit(0);
  }

  const command = args[0].toLowerCase();
  const commandArgs = args.slice(1);

  // Handle buy/sell shortcuts
  if (command === 'buy') {
    runScript(commands['market'].script, ['--side', 'buy', ...commandArgs]);
    return;
  }
  if (command === 'sell') {
    runScript(commands['market'].script, ['--side', 'sell', ...commandArgs]);
    return;
  }

  // Handle version
  if (command === '--version' || command === '-v') {
    import('../package.json', { with: { type: 'json' } }).then((pkg) => {
      console.log(`openbroker v${pkg.default.version}`);
      process.exit(0);
    });
    return;
  }

  const cmd = commands[command];
  if (!cmd) {
    console.error(`Unknown command: ${command}`);
    console.log('Run "openbroker --help" for usage information.');
    process.exit(1);
  }

  runScript(cmd.script, commandArgs);
}

main();
