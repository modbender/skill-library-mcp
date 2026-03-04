import { daemon } from '../lib/daemon-client.js';
import { buildETHTransfer, buildUSDCTransfer } from '../lib/intent-builder.js';
import { resolveENS } from '../lib/ens.js';
import { formatDaemonError } from '../lib/format.js';
import { validateChainId } from '../lib/constants.js';

/**
 * Send ETH or ERC-20 tokens.
 * Usage: node scripts/send.js <to> <amount> [token] [chainId] [approvalCode]
 *   to: recipient address or ENS name
 *   amount: amount to send (in human units, e.g., "0.1" ETH or "100" USDC)
 *   token: "ETH" (default) or "USDC"
 *   chainId: 1 or 8453 (optional, uses daemon's home chain)
 *   approvalCode: 8-digit code from notification (if re-submitting after 202)
 */
async function main() {
  const [, , to, amount, token = 'ETH', chainIdStr, approvalCode] = process.argv;

  if (!to || !amount) {
    console.error('Usage: send <to> <amount> [token] [chainId] [approvalCode]');
    process.exit(1);
  }

  // Resolve ENS if needed
  let recipient = to;
  if (to.endsWith('.eth')) {
    const { address: resolved, error } = await resolveENS(to);
    if (!resolved) {
      console.error(error || `Could not resolve ENS name: ${to}`);
      process.exit(1);
    }
    recipient = resolved;
    console.log(`Resolved ${to} -> ${recipient}`);
  }

  const chainId = chainIdStr ? parseInt(chainIdStr, 10) : 8453;

  // Build intent
  let intent;
  if (token.toUpperCase() === 'ETH') {
    const amountWei = BigInt(Math.round(parseFloat(amount) * 1e18));
    intent = buildETHTransfer(recipient, amountWei, chainId);
  } else if (token.toUpperCase() === 'USDC') {
    validateChainId(chainId);
    intent = buildUSDCTransfer(chainId, recipient, parseFloat(amount));
  } else {
    console.error(`Unsupported token: ${token}. Use ETH or USDC.`);
    process.exit(1);
  }

  // Attach approval code if re-submitting after a 202
  if (approvalCode) {
    intent.approvalCode = approvalCode;
  }

  // Send to daemon
  try {
    const response = await daemon.sign(intent);

    if (response.status === 200) {
      console.log(`Transaction submitted: ${response.data.userOpHash}`);
      console.log(`Chain: ${response.data.chainId}`);
    } else if (response.status === 202) {
      console.log(`Approval required: ${response.data.reason}`);
      console.log(`Summary: ${response.data.summary}`);
      console.log(`Expires in: ${response.data.expiresIn}s`);
      console.log(`\nTo approve, re-run with the 8-digit code from your notification:`);
      console.log(`  send ${to} ${amount} ${token} ${chainId} <approvalCode>`);
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
