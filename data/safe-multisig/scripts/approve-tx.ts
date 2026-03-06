#!/usr/bin/env npx tsx
/**
 * Add an off-chain confirmation for a pending Safe tx.
 */
import SafePkg from '@safe-global/protocol-kit';
import SafeApiKitPkg from '@safe-global/api-kit';

// Handle ESM/CJS interop: Safe SDK default exports may be wrapped
const Safe = (SafePkg as any).default ?? SafePkg;
const SafeApiKit = (SafeApiKitPkg as any).default ?? SafeApiKitPkg;

import {
  addCommonOptions, createCommand, requirePrivateKey,
  resolveTxServiceUrl, resolveChainId, resolveRpcUrl,
  validateAddress, validateApiKey, validateTxHash, type TxHashOptions
} from './safe_lib.js';

const program = addCommonOptions(
  createCommand('approve-tx', 'Add an off-chain confirmation for a Safe tx hash')
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
  const pk = requirePrivateKey();

  // FIX SM-005 / SH-05: Use resolveRpcUrl instead of hardcoded Base fallback
  const provider = resolveRpcUrl(opts);

  const safeSdk = await Safe.init({
    provider,
    signer: pk,
    safeAddress: opts.safe!
  });

  const senderAddress = await safeSdk.getSafeProvider().getSignerAddress();

  // Sign the tx hash
  const sig = await safeSdk.signHash(opts.safeTxHash!);

  const apiKitConfig: { chainId: bigint; txServiceUrl: string; apiKey?: string } = {
    chainId,
    txServiceUrl
  };
  if (opts.apiKey) apiKitConfig.apiKey = opts.apiKey;
  const apiKit = new SafeApiKit(apiKitConfig);

  await apiKit.confirmTransaction(opts.safeTxHash!, sig.data);

  process.stdout.write(JSON.stringify({
    ok: true,
    safe: opts.safe,
    safeTxHash: opts.safeTxHash,
    sender: senderAddress
  }, null, 2) + '\n');

} catch (err: unknown) {
  const message = err instanceof Error ? err.message : String(err);
  process.stderr.write(JSON.stringify({ ok: false, error: message }) + '\n');
  process.exit(1);
}
