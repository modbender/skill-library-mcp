/**
 * Register the agent on-chain via AgentRegistry.registerAgent().
 *
 * Usage: npx tsx register-agent.ts <name> [attestation]
 *
 * Arguments:
 *   name         - Human-readable agent name (e.g. "AlphaTrader"). Required.
 *   attestation  - TEE attestation bytes, hex-encoded (e.g. "0xdead"). Optional, defaults to "0x".
 *
 * Output (stdout): JSON with success, txHash, and agent address.
 */

import { createClient, outputSuccess, outputError } from './setup.js';

async function main(): Promise<void> {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    console.error(JSON.stringify({
      success: false,
      error: 'Usage: register-agent.ts <name> [attestation]',
    }));
    process.exit(1);
  }

  const name = args[0];
  const attestation = (args[1] ?? '0x') as `0x${string}`;

  const client = createClient();
  const address = client.getAddress()!;

  // Check if already registered
  const alreadyRegistered = await client.isAgent(address);
  if (alreadyRegistered) {
    outputSuccess({
      txHash: null,
      address,
      name,
      message: 'Agent is already registered.',
      alreadyRegistered: true,
    });
    return;
  }

  const txHash = await client.registerAgent(name, attestation);

  outputSuccess({
    txHash,
    address,
    name,
    attestation,
    alreadyRegistered: false,
  });
}

main().catch(outputError);
