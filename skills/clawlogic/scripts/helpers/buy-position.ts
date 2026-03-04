/**
 * Buy a position by minting outcome tokens with ETH collateral.
 *
 * Usage: npx tsx buy-position.ts <market-id> <eth-amount>
 *
 * Arguments:
 *   market-id   - The bytes32 market identifier (hex string). Required.
 *   eth-amount  - Amount of ETH to deposit as collateral (e.g. "0.1"). Required.
 *
 * This mints BOTH outcome1 and outcome2 tokens in equal amounts.
 * The agent receives both sides and can hold the side they believe in
 * (optionally selling the other on the V4 pool).
 *
 * Output (stdout): JSON with success, txHash, and updated token balances.
 */

import { parseEther, formatEther } from 'viem';
import { createClient, outputSuccess, outputError } from './setup.js';

async function main(): Promise<void> {
  const args = process.argv.slice(2);

  if (args.length < 2) {
    console.error(JSON.stringify({
      success: false,
      error: 'Usage: buy-position.ts <market-id> <eth-amount>',
    }));
    process.exit(1);
  }

  const marketId = args[0] as `0x${string}`;
  const ethAmount = args[1];

  // Parse ETH amount
  let weiAmount: bigint;
  try {
    weiAmount = parseEther(ethAmount);
  } catch {
    console.error(JSON.stringify({
      success: false,
      error: `Invalid ETH amount: "${ethAmount}". Use a decimal number like "0.1".`,
    }));
    process.exit(1);
  }

  if (weiAmount <= 0n) {
    console.error(JSON.stringify({
      success: false,
      error: 'ETH amount must be greater than zero.',
    }));
    process.exit(1);
  }

  const client = createClient();
  const agentAddress = client.getAddress()!;

  // Mint outcome tokens
  const txHash = await client.mintOutcomeTokens(marketId, weiAmount);

  // Fetch updated balances
  const positions = await client.getPositions(marketId, agentAddress);
  const market = await client.getMarket(marketId);

  outputSuccess({
    txHash,
    marketId,
    ethDeposited: ethAmount,
    ethDepositedWei: weiAmount.toString(),
    balances: {
      outcome1: {
        token: market.outcome1,
        address: market.outcome1Token,
        balance: positions.outcome1Balance.toString(),
        balanceFormatted: formatEther(positions.outcome1Balance),
      },
      outcome2: {
        token: market.outcome2,
        address: market.outcome2Token,
        balance: positions.outcome2Balance.toString(),
        balanceFormatted: formatEther(positions.outcome2Balance),
      },
    },
    totalCollateral: market.totalCollateral.toString(),
    totalCollateralEth: formatEther(market.totalCollateral),
  });
}

main().catch(outputError);
