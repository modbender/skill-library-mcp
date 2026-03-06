/**
 * Create a new prediction market via PredictionMarketHook.initializeMarket().
 *
 * Usage: npx tsx create-market.ts <outcome1> <outcome2> <description> [reward] [bond] [initialLiquidityWei]
 *
 * Arguments:
 *   outcome1     - Label for outcome 1 (e.g. "yes"). Required.
 *   outcome2     - Label for outcome 2 (e.g. "no"). Required.
 *   description  - Human-readable market question. Required.
 *   reward       - Bond currency reward for asserter, in wei. Optional, defaults to "0".
 *   bond         - Minimum bond for assertion, in wei. Optional, defaults to "0".
 *   initialLiquidityWei - ETH value (wei) to seed CPMM on creation. Optional, defaults to "0".
 *
 * Output (stdout): JSON with success, txHash, and market creation details.
 */

import { createClient, outputSuccess, outputError } from './setup.js';

async function main(): Promise<void> {
  const args = process.argv.slice(2);

  if (args.length < 3) {
    console.error(JSON.stringify({
      success: false,
      error:
        'Usage: create-market.ts <outcome1> <outcome2> <description> [reward] [bond] [initialLiquidityWei]',
    }));
    process.exit(1);
  }

  const outcome1 = args[0];
  const outcome2 = args[1];
  const description = args[2];
  const reward = BigInt(args[3] ?? '0');
  const requiredBond = BigInt(args[4] ?? '0');
  const initialLiquidityWei = BigInt(args[5] ?? '0');

  const client = createClient();

  const txHash = await client.initializeMarket(
    outcome1,
    outcome2,
    description,
    reward,
    requiredBond,
    initialLiquidityWei,
  );

  // Fetch market IDs to find the newly created one
  const marketIds = await client.getMarketIds();
  const latestMarketId = marketIds.length > 0 ? marketIds[marketIds.length - 1] : null;

  outputSuccess({
    txHash,
    marketId: latestMarketId,
    outcome1,
    outcome2,
    description,
    reward: reward.toString(),
    requiredBond: requiredBond.toString(),
    initialLiquidityWei: initialLiquidityWei.toString(),
    totalMarkets: marketIds.length,
  });
}

main().catch(outputError);
