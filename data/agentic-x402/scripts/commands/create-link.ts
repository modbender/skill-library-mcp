#!/usr/bin/env npx tsx
// Create a payment link via 21cash x402-links-server

import { getClient, getWalletAddress } from '../core/client.js';
import { parseArgs, formatUsd, isValidUrl, formatError, truncateAddress } from '../core/utils.js';
import { getConfig } from '../core/config.js';

interface CreateLinkRequest {
  name: string;
  description?: string;
  price: string;
  creatorAddress: string;
  chainId: number;
  gatedUrl?: string;
  gatedText?: string;
  webhookUrl?: string;
}

interface CreateLinkResponse {
  success: boolean;
  link?: {
    id: string;
    url: string;
    routerAddress: string;
    amount: string;
    tokenAddress: string;
    chainId: number;
    chainName: string;
    hasGatedContent: boolean;
    deployTxHash?: string;
  };
  error?: string;
}

async function main() {
  const { positional, flags } = parseArgs(process.argv.slice(2));

  if (flags.help || flags.h) {
    console.log(`
x402 create-link - Create a payment link

Usage: x402 create-link --name <name> --price <price> [options]

Required:
  --name       Name of the payment link
  --price      Price in USD (e.g., "5.00" or "0.10")

Content (one required):
  --url        URL to gate behind payment
  --text       Text content to gate behind payment

Options:
  --desc       Description of the link
  --webhook    Webhook URL for payment notifications
  --json       Output as JSON
  -h, --help   Show this help

Environment:
  X402_LINKS_API_URL   Base URL of x402-links-server (default: https://21.cash)

Examples:
  x402 create-link --name "Premium Guide" --price 5.00 --url https://mysite.com/guide.pdf
  x402 create-link --name "Secret Message" --price 0.50 --text "The secret is..."
  x402 create-link --name "API Access" --price 1.00 --url https://api.example.com/data --webhook https://mysite.com/webhook
`);
    process.exit(0);
  }

  const config = getConfig();

  const name = flags.name as string;
  const price = flags.price as string;
  const gatedUrl = flags.url as string | undefined;
  const gatedText = flags.text as string | undefined;
  const description = flags.desc as string | undefined;
  const webhookUrl = flags.webhook as string | undefined;
  const jsonOutput = flags.json === true;

  // Validate required fields
  if (!name) {
    console.error('Error: --name is required');
    process.exit(1);
  }

  if (!price) {
    console.error('Error: --price is required');
    process.exit(1);
  }

  if (!gatedUrl && !gatedText) {
    console.error('Error: Either --url or --text is required');
    process.exit(1);
  }

  if (gatedUrl && !isValidUrl(gatedUrl)) {
    console.error('Error: Invalid URL provided for --url');
    process.exit(1);
  }

  if (webhookUrl && !isValidUrl(webhookUrl)) {
    console.error('Error: Invalid URL provided for --webhook');
    process.exit(1);
  }

  try {
    const client = getClient();
    const creatorAddress = getWalletAddress();

    const requestBody: CreateLinkRequest = {
      name,
      price,
      creatorAddress,
      chainId: config.chainId,
    };

    if (description) requestBody.description = description;
    if (gatedUrl) requestBody.gatedUrl = gatedUrl;
    if (gatedText) requestBody.gatedText = gatedText;
    if (webhookUrl) requestBody.webhookUrl = webhookUrl;

    if (!jsonOutput) {
      console.log('Creating payment link...');
      console.log(`  Name: ${name}`);
      console.log(`  Price: ${formatUsd(parseFloat(price))}`);
      console.log(`  Creator: ${truncateAddress(creatorAddress)}`);
      console.log(`  Network: ${config.chainId === 8453 ? 'Base mainnet' : 'Base Sepolia'} (chain ${config.chainId})`);
      console.log('');
    }

    const apiUrl = `${config.x402LinksApiUrl}/api/links/programmatic`;

    const response = await client.fetchWithPayment(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    const data: CreateLinkResponse = await response.json();

    if (!response.ok || !data.success) {
      if (jsonOutput) {
        console.log(JSON.stringify({ success: false, error: data.error || 'Unknown error' }));
      } else {
        console.error('Error creating link:', data.error || 'Unknown error');
      }
      process.exit(1);
    }

    if (jsonOutput) {
      console.log(JSON.stringify(data));
      return;
    }

    console.log('Payment link created!');
    console.log('');
    console.log(`URL: ${data.link!.url}`);
    console.log(`Router: ${truncateAddress(data.link!.routerAddress)}`);
    console.log(`Chain: ${data.link!.chainName}`);

    if (data.link!.deployTxHash) {
      console.log(`Deploy TX: ${truncateAddress(data.link!.deployTxHash)}`);
    }

    console.log('');
    console.log('Share this URL to accept payments:');
    console.log(data.link!.url);

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
