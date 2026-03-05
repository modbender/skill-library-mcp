#!/usr/bin/env npx tsx
/**
 * Execute a Safe tx onchain (requires enough confirmations already collected).
 *
 * FIX SM-003: Use SDK's built-in getTransaction → executeTransaction flow
 * instead of manual reconstruction with broken signature objects.
 *
 * FIX PT-004: Verify safeTxHash matches after rebuilding to prevent TOFU attack.
 */
import SafePkg from '@safe-global/protocol-kit';
import SafeApiKitPkg from '@safe-global/api-kit';

const Safe = (SafePkg as any).default ?? SafePkg;
const SafeApiKit = (SafeApiKitPkg as any).default ?? SafeApiKitPkg;

import {
  addCommonOptions, createCommand, requirePrivateKey,
  resolveTxServiceUrl, resolveChainId, resolveRpcUrl,
  validateAddress, validateApiKey, validateTxHash, type TxHashOptions
} from './safe_lib.js';

const program = addCommonOptions(
  createCommand('execute-tx', 'Execute a Safe tx onchain (requires enough confirmations)')
)
  .requiredOption('--safe <address>', 'Safe address')
  .requiredOption('--safe-tx-hash <hash>', 'Safe transaction hash')
  .parse();

const opts = program.opts() as TxHashOptions;

try {
  if (opts.safe) validateAddress(opts.safe, 'safe');
  if (opts.safeTxHash) validateTxHash(opts.safeTxHash, 'safe-tx-hash');
  validateApiKey(opts);

  const txServiceUrl = resolveTxServiceUrl(opts);
  const chainId = resolveChainId(opts);
  const rpcUrl = resolveRpcUrl(opts);
  const pk = requirePrivateKey();

  const safeSdk = await Safe.init({
    provider: rpcUrl,
    signer: pk,
    safeAddress: opts.safe!
  });

  const senderAddress = await safeSdk.getSafeProvider().getSignerAddress();

  // Init api-kit
  const apiKitConfig: { chainId: bigint; txServiceUrl: string; apiKey?: string } = {
    chainId,
    txServiceUrl
  };
  if (opts.apiKey) apiKitConfig.apiKey = opts.apiKey;
  const apiKit = new SafeApiKit(apiKitConfig);

  // FIX SM-003: Fetch tx from API and use SDK's executeTransaction directly.
  // The SDK handles signature reconstruction correctly for all signer types
  // (EOA, contract signers, approved-hash) via toSafeTransactionType().
  const tx = await apiKit.getTransaction(opts.safeTxHash!);

  // FIX PT-004: Verify the transaction data hasn't been tampered with.
  // Rebuild the transaction and verify the hash matches what we requested.
  const safeTransaction = await safeSdk.createTransaction({
    transactions: [{
      to: tx.to,
      data: tx.data ?? '0x',
      value: String(tx.value ?? '0'),
      operation: tx.operation ?? 0
    }],
    options: {
      nonce: typeof tx.nonce === 'string' ? parseInt(tx.nonce, 10) : tx.nonce,
      safeTxGas: String(tx.safeTxGas ?? '0'),
      baseGas: String(tx.baseGas ?? '0'),
      gasPrice: String(tx.gasPrice ?? '0'),
      gasToken: tx.gasToken || '0x0000000000000000000000000000000000000000',
      refundReceiver: tx.refundReceiver || '0x0000000000000000000000000000000000000000'
    }
  });

  const recomputedHash = await safeSdk.getTransactionHash(safeTransaction);
  if (recomputedHash.toLowerCase() !== opts.safeTxHash!.toLowerCase()) {
    throw new Error(
      `safeTxHash mismatch — possible data tampering! ` +
      `Expected: ${opts.safeTxHash}, Got: ${recomputedHash}. ` +
      `The transaction service may have returned modified data.`
    );
  }

  // Execute using the API response directly — SDK handles signatures properly
  const execResponse = await safeSdk.executeTransaction(tx);
  const receipt = await execResponse.transactionResponse?.wait?.();

  process.stdout.write(JSON.stringify({
    ok: true,
    safe: opts.safe,
    safeTxHash: opts.safeTxHash,
    executor: senderAddress,
    txHash: receipt?.hash || execResponse.hash
  }, null, 2) + '\n');

} catch (err: unknown) {
  const message = err instanceof Error ? err.message : String(err);
  process.stderr.write(JSON.stringify({ ok: false, error: message }) + '\n');
  process.exit(1);
}
