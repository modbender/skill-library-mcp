#!/usr/bin/env npx tsx
// Pay for an x402-gated resource

import { getClient } from '../core/client.js';
import { parseArgs, formatUsd, isValidUrl, formatError, truncateAddress } from '../core/utils.js';

async function main() {
  const { positional, flags } = parseArgs(process.argv.slice(2));

  if (positional.length === 0 || flags.help || flags.h) {
    console.log(`
x402 pay - Pay for an x402-gated resource

Usage: x402 pay <url> [options]

Arguments:
  url          The URL of the x402-gated resource

Options:
  --method     HTTP method (default: GET)
  --body       Request body (for POST/PUT)
  --header     Add header (can be used multiple times)
  --max        Maximum payment in USD (default: from config)
  --dry-run    Show payment details without paying
  -h, --help   Show this help

Examples:
  x402 pay https://api.example.com/data
  x402 pay https://api.example.com/submit --method POST --body '{"data":"value"}'
  x402 pay https://api.example.com/data --max 5
  x402 pay https://api.example.com/data --dry-run
`);
    process.exit(0);
  }

  const url = positional[0];

  if (!isValidUrl(url)) {
    console.error('Error: Invalid URL provided');
    process.exit(1);
  }

  const method = (flags.method as string) || 'GET';
  const body = flags.body as string | undefined;
  const maxPayment = flags.max ? parseFloat(flags.max as string) : undefined;
  const dryRun = flags['dry-run'] === true;

  const client = getClient();

  console.log(`Fetching: ${url}`);
  console.log(`Method: ${method}`);
  console.log(`Wallet: ${truncateAddress(client.account.address)}`);
  const networkName = client.config.chainId === 8453 ? 'Base mainnet' : 'Base Sepolia';
  console.log(`Network: ${networkName} (chain ${client.config.chainId})`);
  console.log('');

  try {
    // First, make initial request to see if payment is required
    const initialResponse = await fetch(url, {
      method,
      body: body ? body : undefined,
      headers: {
        'Accept': 'application/json',
        ...(body ? { 'Content-Type': 'application/json' } : {}),
      },
    });

    if (initialResponse.status !== 402) {
      // No payment required - just return the response
      console.log('No payment required for this resource.');
      console.log(`Status: ${initialResponse.status}`);

      if (initialResponse.ok) {
        const contentType = initialResponse.headers.get('content-type');
        if (contentType?.includes('application/json')) {
          const data = await initialResponse.json();
          console.log('\nResponse:');
          console.log(JSON.stringify(data, null, 2));
        } else {
          const text = await initialResponse.text();
          console.log('\nResponse:');
          console.log(text);
        }
      }
      return;
    }

    // Extract payment requirements from 402 response
    const paymentRequired = initialResponse.headers.get('x-payment');
    let paymentInfo: any = null;

    if (paymentRequired) {
      try {
        paymentInfo = JSON.parse(Buffer.from(paymentRequired, 'base64').toString());
      } catch {
        // Try parsing body instead
        try {
          paymentInfo = await initialResponse.json();
        } catch {
          console.error('Could not parse payment requirements');
          process.exit(1);
        }
      }
    } else {
      // Try getting from response body
      try {
        paymentInfo = await initialResponse.json();
      } catch {
        console.error('No payment information found in 402 response');
        process.exit(1);
      }
    }

    console.log('Payment Required:');

    if (paymentInfo.accepts) {
      for (const accept of paymentInfo.accepts) {
        console.log(`  Scheme: ${accept.scheme}`);
        console.log(`  Price: ${accept.price || formatUsd(accept.maxAmountRequired || '0')}`);
        console.log(`  Network: ${accept.network}`);
        console.log(`  Pay To: ${truncateAddress(accept.payTo)}`);
        console.log('');
      }
    }

    // Check max payment limit
    const effectiveMax = maxPayment ?? client.config.maxPaymentUsd;
    const priceStr = paymentInfo.accepts?.[0]?.price || paymentInfo.accepts?.[0]?.maxAmountRequired;
    const priceNum = parseFloat(String(priceStr).replace(/[$,]/g, ''));

    if (priceNum > effectiveMax) {
      console.error(`Payment of ${formatUsd(priceNum)} exceeds max limit of ${formatUsd(effectiveMax)}`);
      console.error('Use --max to increase the limit if desired.');
      process.exit(1);
    }

    if (dryRun) {
      console.log('Dry run - payment not executed.');
      console.log(`Would pay: ${formatUsd(priceNum)}`);
      return;
    }

    // Make payment request using x402 wrapped fetch
    console.log('Processing payment...');

    const response = await client.fetchWithPayment(url, {
      method,
      body: body ? body : undefined,
      headers: {
        'Accept': 'application/json',
        ...(body ? { 'Content-Type': 'application/json' } : {}),
      },
    });

    if (!response.ok) {
      console.error(`Request failed: ${response.status} ${response.statusText}`);
      const text = await response.text();
      if (text) console.error(text);
      process.exit(1);
    }

    console.log('Payment successful!');

    // Try to get payment receipt from response
    const paymentResponse = response.headers.get('x-payment-response');
    if (paymentResponse) {
      try {
        const receipt = JSON.parse(Buffer.from(paymentResponse, 'base64').toString());
        console.log(`Transaction: ${receipt.transactionHash || receipt.txHash || 'N/A'}`);
      } catch {
        // Ignore parsing errors
      }
    }

    console.log('');

    // Show response
    const contentType = response.headers.get('content-type');
    if (contentType?.includes('application/json')) {
      const data = await response.json();
      console.log('Response:');
      console.log(JSON.stringify(data, null, 2));
    } else {
      const text = await response.text();
      console.log('Response:');
      console.log(text);
    }

  } catch (error) {
    console.error('Error:', formatError(error));
    process.exit(1);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
