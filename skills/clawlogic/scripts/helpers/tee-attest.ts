/**
 * Generate a fresh TEE attestation quote from the Phala CVM environment.
 *
 * Usage: npx tsx tee-attest.ts [custom-data]
 *
 * Arguments:
 *   custom-data  - Optional hex string to include as user data in the quote.
 *                  Defaults to the agent's public address.
 *
 * Output (stdout): JSON with { success, inTee, quote, publicKey, deriveKey }
 *
 * This script requires the @phala/dstack-sdk package and must be run inside
 * a Phala CVM (Intel TDX) to produce a real attestation. Outside a TEE,
 * it returns { success: true, inTee: false }.
 */

import { outputSuccess, outputError, createClient } from './setup.js';

async function main(): Promise<void> {
  const customData = process.argv[2] || undefined;

  // Attempt to load dstack SDK (only available inside Phala CVM)
  let TappdClient: any;
  try {
    const dstack = await import('@phala/dstack-sdk');
    TappdClient = dstack.TappdClient;
  } catch {
    // Not in TEE — return gracefully
    outputSuccess({
      inTee: false,
      quote: null,
      publicKey: null,
      message: 'Not running inside a TEE. Deploy to Phala CVM for real attestation.',
    });
    return;
  }

  try {
    const endpoint = process.env.DSTACK_SIMULATOR_ENDPOINT || undefined;
    const client = new TappdClient(endpoint);

    // Derive a deterministic key from TEE hardware
    const deriveResult = await client.deriveKey('/clawlogic/agent/v1');
    const publicKey = '0x' + Buffer.from(deriveResult.asUint8Array(64)).toString('hex');

    // Use custom data or the derived public key as quote user data
    const userData = customData || publicKey;

    // Generate TDX attestation quote
    const quoteResult = await client.tdxQuote(userData);
    const quote = '0x' + Buffer.from(quoteResult.quote).toString('hex');

    // Get agent address for reference
    let agentAddress: string | null = null;
    try {
      const sdkClient = createClient();
      agentAddress = sdkClient.getAddress() ?? null;
    } catch {
      // No private key available — that's fine
    }

    outputSuccess({
      inTee: true,
      quote,
      quoteLength: (quote.length - 2) / 2,
      publicKey,
      agentAddress,
      userData,
      message: 'TEE attestation generated successfully. Submit this quote on-chain for verification.',
    });
  } catch (error) {
    outputError(error);
  }
}

main().catch(outputError);
