#!/usr/bin/env npx tsx
// Check wallet balances

import { getClient, getWalletAddress, getUsdcBalance, getEthBalance } from '../core/client.js';
import { parseArgs, formatCrypto, truncateAddress } from '../core/utils.js';

async function main() {
  const { flags } = parseArgs(process.argv.slice(2));

  if (flags.help || flags.h) {
    console.log(`
x402 balance - Check wallet balances

Usage: x402 balance [options]

Options:
  --json       Output as JSON
  --full       Show full addresses
  -h, --help   Show this help

Shows:
  - Wallet address
  - USDC balance (for payments)
  - ETH balance (for gas)
`);
    process.exit(0);
  }

  const jsonOutput = flags.json === true;
  const fullAddress = flags.full === true;

  try {
    const client = getClient();
    const address = getWalletAddress();

    const [usdc, eth] = await Promise.all([
      getUsdcBalance(),
      getEthBalance(),
    ]);

    if (jsonOutput) {
      console.log(JSON.stringify({
        address,
        network: client.config.network,
        chainId: client.config.chainId,
        balances: {
          usdc: {
            raw: usdc.raw.toString(),
            formatted: usdc.formatted,
          },
          eth: {
            raw: eth.raw.toString(),
            formatted: eth.formatted,
          },
        },
      }));
      return;
    }

    console.log('x402 Wallet Balance');
    console.log('===================');
    console.log('');
    console.log(`Address: ${address}`);
    const networkName = client.config.chainId === 8453 ? 'Base mainnet' : 'Base Sepolia';
    console.log(`Network: ${networkName} (chain ${client.config.chainId})`);
    console.log('');
    console.log('Balances:');
    console.log(`  USDC: ${formatCrypto(usdc.formatted, 'USDC', 2)}`);
    console.log(`  ETH:  ${formatCrypto(eth.formatted, 'ETH', 6)}`);

    // Warnings
    const usdcNum = parseFloat(usdc.formatted);

    if (usdcNum < 1) {
      console.log('');
      console.log('Warning: Low USDC balance. Fund your wallet to make payments.');
    }

  } catch (error) {
    if (jsonOutput) {
      console.log(JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
      }));
    } else {
      console.error('Error:', error instanceof Error ? error.message : String(error));
    }
    process.exit(1);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
