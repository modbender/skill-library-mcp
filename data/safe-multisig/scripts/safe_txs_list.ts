#!/usr/bin/env npx tsx
/**
 * List multisig transactions for a Safe. Uses plain HTTP — no SDK needed.
 */
import { addCommonOptions, createCommand, fetchJson, resolveTxServiceUrl, validateAddress, validateApiKey, type ListOptions } from './safe_lib.js';

const program = addCommonOptions(
  createCommand('safe_txs_list', 'List multisig transactions for a Safe (queued + executed)')
)
  .requiredOption('--safe <address>', 'Safe address')
  .option('--limit <n>', 'Page size', '10')
  .option('--offset <n>', 'Offset', '0')
  .option('--executed <true|false>', 'Filter by executed status')
  .parse();

const opts = program.opts() as ListOptions;

try {
  if (opts.safe) validateAddress(opts.safe, 'safe');
  validateApiKey(opts);
  const baseUrl = resolveTxServiceUrl(opts);

  const params = new URLSearchParams({ limit: opts.limit ?? '10', offset: opts.offset ?? '0' });
  if (opts.executed !== undefined) {
    if (opts.executed !== 'true' && opts.executed !== 'false') {
      throw new Error('--executed must be true or false');
    }
    params.set('executed', opts.executed);
  }

  const url = `${baseUrl}/v1/safes/${opts.safe}/multisig-transactions/?${params}`;
  const data = await fetchJson(url);
  process.stdout.write(JSON.stringify(data, null, 2) + '\n');
} catch (err: unknown) {
  const message = err instanceof Error ? err.message : String(err);
  process.stderr.write(JSON.stringify({ ok: false, error: message }) + '\n');
  process.exit(1);
}
