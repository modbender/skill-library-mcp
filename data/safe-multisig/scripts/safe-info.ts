#!/usr/bin/env npx tsx
/**
 * Fetch Safe info (owners/threshold/nonce) from the Transaction Service REST API.
 * Uses plain HTTP — no SDK needed for read-only queries.
 */
import { addCommonOptions, createCommand, fetchJson, resolveTxServiceUrl, validateAddress, validateApiKey, type SafeOptions } from './safe_lib.js';

const program = addCommonOptions(
  createCommand('safe-info', 'Fetch Safe info (owners/threshold/nonce) from Transaction Service')
)
  .requiredOption('--safe <address>', 'Safe address')
  .parse();

const opts = program.opts() as SafeOptions;

try {
  if (opts.safe) validateAddress(opts.safe, 'safe');
  validateApiKey(opts);
  const baseUrl = resolveTxServiceUrl(opts);
  // Direct HTTP scripts use /v1/ on the resolved URL
  const url = `${baseUrl}/v1/safes/${opts.safe}/`;

  const data = await fetchJson(url);
  process.stdout.write(JSON.stringify(data, null, 2) + '\n');
} catch (err: unknown) {
  const message = err instanceof Error ? err.message : String(err);
  process.stderr.write(JSON.stringify({ ok: false, error: message }) + '\n');
  process.exit(1);
}
