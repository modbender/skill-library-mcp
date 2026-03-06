/**
 * Assert the outcome of a market via UMA Optimistic Oracle V3.
 *
 * Usage: npx tsx assert-outcome.ts <market-id> <outcome>
 *
 * Arguments:
 *   market-id  - The bytes32 market identifier (hex string). Required.
 *   outcome    - The outcome to assert. Must exactly match outcome1, outcome2,
 *                or "Unresolvable". Required.
 *
 * WARNING: Asserting requires posting a bond. If your assertion is disputed
 * and found to be incorrect, you LOSE the bond. Only assert when confident.
 *
 * Output (stdout): JSON with success, txHash, and assertion details.
 */

import { createClient, outputSuccess, outputError } from './setup.js';

async function main(): Promise<void> {
  const args = process.argv.slice(2);

  if (args.length < 2) {
    console.error(JSON.stringify({
      success: false,
      error: 'Usage: assert-outcome.ts <market-id> <outcome>',
    }));
    process.exit(1);
  }

  const marketId = args[0] as `0x${string}`;
  const assertedOutcome = args[1];

  const client = createClient();

  // Fetch market to validate the outcome
  const market = await client.getMarket(marketId);

  if (market.resolved) {
    console.error(JSON.stringify({
      success: false,
      error: `Market is already resolved. Cannot assert.`,
    }));
    process.exit(1);
  }

  // Validate outcome matches one of the valid options
  const validOutcomes = [market.outcome1, market.outcome2, 'Unresolvable'];
  if (!validOutcomes.includes(assertedOutcome)) {
    console.error(JSON.stringify({
      success: false,
      error: `Invalid outcome "${assertedOutcome}". Must be one of: ${validOutcomes.map(o => `"${o}"`).join(', ')}`,
    }));
    process.exit(1);
  }

  const txHash = await client.assertMarket(marketId, assertedOutcome);

  // Refetch market to get the assertionId
  const updatedMarket = await client.getMarket(marketId);

  outputSuccess({
    txHash,
    marketId,
    assertedOutcome,
    assertedOutcomeId: updatedMarket.assertedOutcomeId,
    description: market.description,
    requiredBond: market.requiredBond.toString(),
    message: `Assertion submitted. Other agents have the liveness window to dispute. If no dispute, the market will resolve to "${assertedOutcome}".`,
  });
}

main().catch(outputError);
