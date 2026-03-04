/**
 * Settle a resolved market and redeem winning tokens for ETH.
 *
 * Usage: npx tsx settle-market.ts <market-id>
 *
 * Arguments:
 *   market-id  - The bytes32 market identifier (hex string). Required.
 *
 * The market must be resolved before settlement. Burns the agent's winning
 * outcome tokens and transfers proportional ETH collateral.
 *
 * Output (stdout): JSON with success, txHash, and payout details.
 */

import { formatEther } from 'viem';
import { createClient, outputSuccess, outputError } from './setup.js';

async function main(): Promise<void> {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    console.error(JSON.stringify({
      success: false,
      error: 'Usage: settle-market.ts <market-id>',
    }));
    process.exit(1);
  }

  const marketId = args[0] as `0x${string}`;
  const client = createClient();
  const agentAddress = client.getAddress()!;

  // Fetch market state
  const market = await client.getMarket(marketId);

  if (!market.resolved) {
    console.error(JSON.stringify({
      success: false,
      error: 'Market is not yet resolved. Wait for the assertion liveness window to pass and the market to be resolved.',
    }));
    process.exit(1);
  }

  // Get balances before settlement
  const positionsBefore = await client.getPositions(marketId, agentAddress);
  const balanceBefore = await client.getBalance();

  // Settle
  const txHash = await client.settleOutcomeTokens(marketId);

  // Get balances after settlement
  const positionsAfter = await client.getPositions(marketId, agentAddress);
  const balanceAfter = await client.getBalance();

  const ethPayout = balanceAfter - balanceBefore;

  outputSuccess({
    txHash,
    marketId,
    description: market.description,
    resolvedOutcome: market.assertedOutcomeId,
    balancesBefore: {
      outcome1: positionsBefore.outcome1Balance.toString(),
      outcome2: positionsBefore.outcome2Balance.toString(),
    },
    balancesAfter: {
      outcome1: positionsAfter.outcome1Balance.toString(),
      outcome2: positionsAfter.outcome2Balance.toString(),
    },
    estimatedEthPayout: formatEther(ethPayout > 0n ? ethPayout : 0n),
    message: ethPayout > 0n
      ? `Settlement complete. Received approximately ${formatEther(ethPayout)} ETH.`
      : 'Settlement complete. No ETH received (may have held losing tokens, or gas cost exceeded payout).',
  });
}

main().catch(outputError);
