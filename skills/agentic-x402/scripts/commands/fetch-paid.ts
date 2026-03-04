#!/usr/bin/env npx tsx
// Fetch a URL with automatic x402 payment handling
// This is a simpler version that just fetches and returns the response

import { getClient } from '../core/client.js';
import { parseArgs, isValidUrl, formatError, truncateAddress } from '../core/utils.js';

async function main() {
  const { positional, flags } = parseArgs(process.argv.slice(2));

  if (positional.length === 0 || flags.help || flags.h) {
    console.log(`
x402 fetch - Fetch URL with automatic x402 payment

Usage: x402 fetch <url> [options]

Arguments:
  url          The URL to fetch

Options:
  --method     HTTP method (default: GET)
  --body       Request body (for POST/PUT)
  --header     Add header as "Key: Value"
  --json       Output as JSON only (for piping)
  --raw        Output raw response body only
  -h, --help   Show this help

Examples:
  x402 fetch https://api.example.com/data
  x402 fetch https://api.example.com/data --json
  x402 fetch https://api.example.com/submit --method POST --body '{"key":"value"}'
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
  const jsonOnly = flags.json === true;
  const rawOnly = flags.raw === true;

  const client = getClient();

  if (!jsonOnly && !rawOnly) {
    console.log(`Fetching: ${url}`);
    console.log(`Wallet: ${truncateAddress(client.account.address)}`);
    console.log('');
  }

  try {
    const headers: Record<string, string> = {
      'Accept': 'application/json',
    };

    if (body) {
      headers['Content-Type'] = 'application/json';
    }

    // Use the x402-wrapped fetch which handles 402 automatically
    const response = await client.fetchWithPayment(url, {
      method,
      body: body ? body : undefined,
      headers: Object.keys(headers).length > 0 ? headers : undefined,
    });

    if (!response.ok) {
      if (!jsonOnly && !rawOnly) {
        console.error(`Request failed: ${response.status} ${response.statusText}`);
      }

      if (jsonOnly) {
        console.log(JSON.stringify({
          success: false,
          status: response.status,
          error: response.statusText,
        }));
      }

      process.exit(1);
    }

    const contentType = response.headers.get('content-type');

    if (rawOnly) {
      // Output raw body
      const text = await response.text();
      process.stdout.write(text);
      return;
    }

    if (contentType?.includes('application/json')) {
      const data = await response.json();

      if (jsonOnly) {
        console.log(JSON.stringify(data));
      } else {
        console.log('Response:');
        console.log(JSON.stringify(data, null, 2));
      }
    } else {
      const text = await response.text();

      if (jsonOnly) {
        console.log(JSON.stringify({ success: true, body: text }));
      } else {
        console.log('Response:');
        console.log(text);
      }
    }

  } catch (error) {
    if (jsonOnly) {
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
