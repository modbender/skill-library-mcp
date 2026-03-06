/**
 * Analyze a prediction market -- returns full details for agent decision-making.
 *
 * Usage: npx tsx analyze-market.ts <market-id>
 *
 * Arguments:
 *   market-id  - The bytes32 market identifier (hex string). Required.
 *
 * Output (stdout): JSON with market details, token balances, resolution status,
 *   and contextual information for the agent to reason about.
 */

import { formatEther } from 'viem';
import { createClient, outputSuccess, outputError } from './setup.js';

async function main(): Promise<void> {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    console.error(JSON.stringify({
      success: false,
      error: 'Usage: analyze-market.ts <market-id>',
    }));
    process.exit(1);
  }

  const marketId = args[0] as `0x${string}`;
  const client = createClient();
  const agentAddress = client.getAddress();

  // Fetch market data
  const market = await client.getMarket(marketId);

  // Fetch agent's positions if we have an address
  let agentPositions: { outcome1Balance: string; outcome2Balance: string } | null = null;
  if (agentAddress) {
    const positions = await client.getPositions(marketId, agentAddress);
    agentPositions = {
      outcome1Balance: positions.outcome1Balance.toString(),
      outcome2Balance: positions.outcome2Balance.toString(),
    };
  }

  // Fetch total supply of each outcome token for market context
  const [outcome1Supply, outcome2Supply] = await Promise.all([
    client.getOutcomeTokenTotalSupply(market.outcome1Token),
    client.getOutcomeTokenTotalSupply(market.outcome2Token),
  ]);

  // Compute implied probabilities from supply ratios (basic heuristic)
  const totalSupply = outcome1Supply + outcome2Supply;
  const impliedYesProbability =
    totalSupply > 0n
      ? Number((outcome1Supply * 10000n) / totalSupply) / 100
      : 50.0;

  // Zero assertedOutcomeId means no assertion yet
  const zeroBytes32 = '0x0000000000000000000000000000000000000000000000000000000000000000';
  const hasAssertion = market.assertedOutcomeId !== zeroBytes32;

  outputSuccess({
    market: {
      marketId: market.marketId,
      description: market.description,
      outcome1: market.outcome1,
      outcome2: market.outcome2,
      outcome1Token: market.outcome1Token,
      outcome2Token: market.outcome2Token,
      reward: market.reward.toString(),
      requiredBond: market.requiredBond.toString(),
      resolved: market.resolved,
      assertedOutcomeId: market.assertedOutcomeId,
      hasActiveAssertion: hasAssertion && !market.resolved,
      poolId: market.poolId,
      totalCollateral: market.totalCollateral.toString(),
      totalCollateralEth: formatEther(market.totalCollateral),
    },
    tokenMetrics: {
      outcome1TotalSupply: outcome1Supply.toString(),
      outcome2TotalSupply: outcome2Supply.toString(),
      impliedYesProbability: `${impliedYesProbability.toFixed(2)}%`,
    },
    agentPositions,
    agentAddress: agentAddress ?? null,
    analysis: {
      status: market.resolved
        ? 'RESOLVED'
        : hasAssertion
          ? 'ASSERTION_PENDING'
          : 'OPEN',
      canTrade: !market.resolved,
      canAssert: !market.resolved && !hasAssertion,
      canSettle: market.resolved,
    },
  });
}

main().catch(outputError);
