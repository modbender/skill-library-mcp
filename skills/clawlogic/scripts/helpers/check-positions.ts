/**
 * Check the agent's positions across one or all markets.
 *
 * Usage: npx tsx check-positions.ts [market-id]
 *
 * Arguments:
 *   market-id  - Optional. If provided, shows positions for that market only.
 *                If omitted, shows positions across ALL markets.
 *
 * Output (stdout): JSON with token balances, market status, and portfolio summary.
 */

import { formatEther } from 'viem';
import { createClient, outputSuccess, outputError } from './setup.js';

interface PositionInfo {
  marketId: string;
  description: string;
  status: string;
  outcome1: {
    label: string;
    token: string;
    balance: string;
    balanceFormatted: string;
  };
  outcome2: {
    label: string;
    token: string;
    balance: string;
    balanceFormatted: string;
  };
  totalCollateral: string;
  totalCollateralEth: string;
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const specificMarketId = args[0] as `0x${string}` | undefined;

  const client = createClient();
  const agentAddress = client.getAddress()!;

  // Get ETH balance
  const ethBalance = await client.getBalance();

  // Get market IDs
  let marketIds: `0x${string}`[];
  if (specificMarketId) {
    marketIds = [specificMarketId];
  } else {
    marketIds = await client.getMarketIds();
  }

  if (marketIds.length === 0) {
    outputSuccess({
      agentAddress,
      ethBalance: formatEther(ethBalance),
      positions: [],
      message: 'No markets found.',
    });
    return;
  }

  // Fetch positions for each market
  const positions: PositionInfo[] = [];

  for (const marketId of marketIds) {
    const market = await client.getMarket(marketId);
    const pos = await client.getPositions(marketId, agentAddress);

    // Skip markets where the agent has no position (unless specifically requested)
    if (!specificMarketId && pos.outcome1Balance === 0n && pos.outcome2Balance === 0n) {
      continue;
    }

    const zeroBytes32 = '0x0000000000000000000000000000000000000000000000000000000000000000';
    const hasAssertion = market.assertedOutcomeId !== zeroBytes32;

    positions.push({
      marketId: market.marketId,
      description: market.description,
      status: market.resolved
        ? 'RESOLVED'
        : hasAssertion
          ? 'ASSERTION_PENDING'
          : 'OPEN',
      outcome1: {
        label: market.outcome1,
        token: market.outcome1Token,
        balance: pos.outcome1Balance.toString(),
        balanceFormatted: formatEther(pos.outcome1Balance),
      },
      outcome2: {
        label: market.outcome2,
        token: market.outcome2Token,
        balance: pos.outcome2Balance.toString(),
        balanceFormatted: formatEther(pos.outcome2Balance),
      },
      totalCollateral: market.totalCollateral.toString(),
      totalCollateralEth: formatEther(market.totalCollateral),
    });
  }

  outputSuccess({
    agentAddress,
    ethBalance: formatEther(ethBalance),
    ethBalanceWei: ethBalance.toString(),
    totalMarketsChecked: marketIds.length,
    positionsFound: positions.length,
    positions,
  });
}

main().catch(outputError);
