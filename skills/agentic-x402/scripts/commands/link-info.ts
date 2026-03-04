#!/usr/bin/env npx tsx
// Get info about a payment link

import { parseArgs, formatUsd, formatError, truncateAddress } from '../core/utils.js';
import { getConfig } from '../core/config.js';

interface LinkDetails {
  success: boolean;
  details?: {
    name: string;
    description?: string;
    amount: string;
    routerAddress: string;
    chainId: number;
    chainName: string;
    tokenAddress: string;
    hasGatedContent: boolean;
  };
  error?: string;
}

async function main() {
  const { positional, flags } = parseArgs(process.argv.slice(2));

  if (positional.length === 0 || flags.help || flags.h) {
    console.log(`
x402 link-info - Get info about a payment link

Usage: x402 link-info <router-address> [options]

Arguments:
  router-address   The router contract address or full URL

Options:
  --json       Output as JSON
  -h, --help   Show this help

Examples:
  x402 link-info 0x1234...5678
  x402 link-info https://21.cash/pay/0x1234...5678
`);
    process.exit(0);
  }

  const config = getConfig();

  if (!config.x402LinksApiUrl) {
    console.error('Error: X402_LINKS_API_URL environment variable is required');
    process.exit(1);
  }

  const jsonOutput = flags.json === true;

  // Extract router address from input (could be URL or raw address)
  let routerAddress = positional[0];

  // If it's a URL, extract the router address from the path
  if (routerAddress.startsWith('http')) {
    try {
      const url = new URL(routerAddress);
      const pathParts = url.pathname.split('/');
      routerAddress = pathParts[pathParts.length - 1];
    } catch {
      console.error('Error: Invalid URL provided');
      process.exit(1);
    }
  }

  // Validate it looks like an address
  if (!routerAddress.startsWith('0x') || routerAddress.length !== 42) {
    console.error('Error: Invalid router address. Must be a 0x-prefixed 40-character hex string.');
    process.exit(1);
  }

  try {
    const apiUrl = `${config.x402LinksApiUrl}/api/links/${routerAddress}/details`;

    const response = await fetch(apiUrl);
    const data: LinkDetails = await response.json();

    if (!response.ok || !data.success) {
      if (jsonOutput) {
        console.log(JSON.stringify({ success: false, error: data.error || 'Link not found' }));
      } else {
        console.error('Error:', data.error || 'Link not found');
      }
      process.exit(1);
    }

    if (jsonOutput) {
      console.log(JSON.stringify(data));
      return;
    }

    const details = data.details!;

    console.log('Payment Link Details');
    console.log('====================');
    console.log('');
    console.log(`Name: ${details.name}`);

    if (details.description) {
      console.log(`Description: ${details.description}`);
    }

    console.log('');
    console.log(`Price: ${formatUsd(parseFloat(details.amount))}`);
    console.log(`Router: ${details.routerAddress}`);
    console.log(`Chain: ${details.chainName} (${details.chainId})`);
    console.log(`Token: ${truncateAddress(details.tokenAddress)}`);
    console.log(`Has Content: ${details.hasGatedContent ? 'Yes' : 'No'}`);

    console.log('');
    console.log('Payment URL:');
    console.log(`${config.x402LinksApiUrl}/pay/${details.routerAddress}`);

  } catch (error) {
    if (jsonOutput) {
      console.log(JSON.stringify({
        success: false,
        error: formatError(error),
      }));
    } else {
      console.error('Error:', formatError(error));
    }
    process.exit(1);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
