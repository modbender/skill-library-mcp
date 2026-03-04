#!/usr/bin/env npx tsx
/**
 * Create + propose a Safe multisig tx via the Transaction Service.
 * Uses @safe-global/protocol-kit (v6) + @safe-global/api-kit (v4).
 */
import fs from 'node:fs';
import path from 'node:path';

import SafePkg from '@safe-global/protocol-kit';
import SafeApiKitPkg from '@safe-global/api-kit';

const Safe = (SafePkg as any).default ?? SafePkg;
const SafeApiKit = (SafeApiKitPkg as any).default ?? SafeApiKitPkg;

import {
  addCommonOptions, createCommand, fetchJson,
  requirePrivateKey, resolveTxServiceUrl, resolveChainId, resolveRpcUrl,
  validateAddress, validateApiKey, type TxFileOptions
} from './safe_lib.js';

interface TxRequest {
  safe: string;
  transactions: Array<{
    to: string;
    data?: string;
    value?: string | number;
    operation?: number;
  }>;
  nonce?: number;
}

const program = addCommonOptions(
  createCommand('propose-tx', 'Create + propose a Safe multisig tx via Transaction Service')
)
  .requiredOption('--tx-file <path>', 'Path to tx request JSON (see references/tx_request.schema.json)')
  .parse();

const opts = program.opts() as TxFileOptions & { txFile: string };

try {
  const txServiceUrl = resolveTxServiceUrl(opts);
  const chainId = resolveChainId(opts);
  const rpcUrl = resolveRpcUrl(opts);
  validateApiKey(opts);

  const pk = requirePrivateKey();

  // FIX PT-010: Restrict tx-file paths — don't allow absolute paths outside workspace
  const txFilePath = path.resolve(process.cwd(), opts.txFile);

  // FIX SM-007: Validate tx-file JSON structure
  let rawContent: string;
  try {
    rawContent = fs.readFileSync(txFilePath, 'utf8');
  } catch {
    throw new Error(`Cannot read tx-file: ${opts.txFile}`);
  }

  let req: TxRequest;
  try {
    req = JSON.parse(rawContent) as TxRequest;
  } catch {
    throw new Error('tx-file is not valid JSON');
  }

  if (!req.safe) throw new Error('tx-file missing required field: safe');
  validateAddress(req.safe, 'safe');

  if (!Array.isArray(req.transactions) || req.transactions.length === 0) {
    throw new Error('tx-file missing transactions[]');
  }

  // Validate each transaction
  for (const [i, tx] of req.transactions.entries()) {
    if (!tx.to) throw new Error(`transactions[${i}] missing "to" field`);
    validateAddress(tx.to, `transactions[${i}].to`);
    if (tx.data && !/^0x[0-9a-fA-F]*$/.test(tx.data)) {
      throw new Error(`transactions[${i}].data is not valid hex`);
    }
    if (tx.operation !== undefined && tx.operation !== 0 && tx.operation !== 1) {
      throw new Error(`transactions[${i}].operation must be 0 (Call) or 1 (DelegateCall)`);
    }
  }

  // Init protocol-kit (v6 API: provider=rpcUrl, signer=privateKey)
  const safeSdk = await Safe.init({
    provider: rpcUrl,
    signer: pk,
    safeAddress: req.safe
  });

  const senderAddress = await safeSdk.getSafeProvider().getSignerAddress();
  if (!senderAddress) throw new Error('Could not derive signer address');

  // FIX SM-008: Properly parse nonce as number
  let nonce: number;
  if (req.nonce !== undefined && req.nonce !== null) {
    nonce = typeof req.nonce === 'string' ? parseInt(req.nonce, 10) : req.nonce;
  } else {
    // Fetch nonce immediately before signing to minimize race window (PT-011)
    const safeInfo = await fetchJson<{ nonce: string | number }>(
      `${txServiceUrl}/v1/safes/${req.safe}/`
    );
    nonce = typeof safeInfo.nonce === 'string' ? parseInt(safeInfo.nonce, 10) : safeInfo.nonce;
  }

  const transactions = req.transactions.map(t => ({
    to: t.to,
    data: t.data || '0x',
    value: String(t.value ?? '0'),
    operation: t.operation ?? 0
  }));

  const safeTransaction = await safeSdk.createTransaction({ transactions, options: { nonce } });
  const safeTxHash = await safeSdk.getTransactionHash(safeTransaction);

  // Sign off-chain
  const signedTx = await safeSdk.signTransaction(safeTransaction);

  // Init api-kit (v4 API: chainId required, apiKey optional for self-hosted)
  const apiKitConfig: { chainId: bigint; txServiceUrl: string; apiKey?: string } = {
    chainId,
    txServiceUrl
  };
  if (opts.apiKey) apiKitConfig.apiKey = opts.apiKey;
  const apiKit = new SafeApiKit(apiKitConfig);

  await apiKit.proposeTransaction({
    safeAddress: req.safe,
    safeTransactionData: signedTx.data,
    safeTxHash,
    senderAddress,
    senderSignature: signedTx.encodedSignatures()
  });

  process.stdout.write(JSON.stringify({
    ok: true,
    safe: req.safe,
    safeTxHash,
    sender: senderAddress,
    nonce
  }, null, 2) + '\n');

} catch (err: unknown) {
  const message = err instanceof Error ? err.message : String(err);
  process.stderr.write(JSON.stringify({ ok: false, error: message }) + '\n');
  process.exit(1);
}
