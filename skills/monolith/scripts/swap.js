import { daemon } from '../lib/daemon-client.js';
import { buildSwapIntent, getUSDCAddress } from '../lib/intent-builder.js';
import { formatDaemonError } from '../lib/format.js';
import { validateChainId } from '../lib/constants.js';

/**
 * Swap ETH for tokens via Uniswap Universal Router.
 * Uses Uniswap Routing API when available; falls back to on-chain V3 fee-tier probing.
 *
 * Usage: node scripts/swap.js <amountETH> [tokenOut] [chainId] [approvalCode]
 *   amountETH: amount of ETH to swap (e.g., "0.1")
 *   tokenOut: "USDC" (default) or a token address
 *   chainId: 1 or 8453 (default: 8453)
 *   approvalCode: 8-digit code from notification (if re-submitting after 202)
 */
async function main() {
  const [, , amountETH, tokenOut = 'USDC', chainIdStr, approvalCode] = process.argv;

  if (!amountETH) {
    console.error('Usage: swap <amountETH> [tokenOut] [chainId] [approvalCode]');
    process.exit(1);
  }

  const chainId = chainIdStr ? parseInt(chainIdStr, 10) : 8453;
  validateChainId(chainId);
  const amountWei = BigInt(Math.round(parseFloat(amountETH) * 1e18));

  console.log(`Quoting ${amountETH} ETH -> ${tokenOut} on chain ${chainId}...`);

  // Default 0.5% slippage (50 bps) — daemon will verify this is within profile limits
  const maxSlippageBps = 50;
  let intent;
  try {
    intent = await buildSwapIntent(chainId, amountWei, tokenOut, maxSlippageBps);
  } catch (err) {
    console.error(`Failed to build swap intent: ${err.message}`);
    process.exit(1);
  }

  // Display quote from whichever source succeeded
  if (intent.quotedAmountOut) {
    const decimals = tokenOut.toUpperCase() === 'USDC' ? 6 : 18;
    const humanAmount = Number(intent.quotedAmountOut) / 10 ** decimals;
    console.log(`Quote: ~${humanAmount.toFixed(decimals === 6 ? 2 : 6)} ${tokenOut} (via ${intent.source})`);
  }

  // Strip non-intent fields before sending to daemon (BigInt can't be serialized)
  const { quotedAmountOut, source, ...daemonIntent } = intent;

  // Attach approval code if re-submitting after a 202
  if (approvalCode) {
    daemonIntent.approvalCode = approvalCode;
  }

  console.log(`Swap intent: ${amountETH} ETH -> ${tokenOut} (max slippage: ${maxSlippageBps / 100}%)`);

  try {
    const response = await daemon.sign(daemonIntent);

    if (response.status === 200) {
      console.log(`Transaction submitted: ${response.data.userOpHash}`);
    } else if (response.status === 202) {
      console.log(`Approval required: ${response.data.reason}`);
      console.log(`Summary: ${response.data.summary}`);
      console.log(`Expires in: ${response.data.expiresIn}s`);
      console.log(`\nTo approve, re-run with the 8-digit code from your notification:`);
      console.log(`  swap ${amountETH} ${tokenOut} ${chainId} <approvalCode>`);
    } else {
      console.error(formatDaemonError(response));
      process.exit(1);
    }
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }
}

main();
