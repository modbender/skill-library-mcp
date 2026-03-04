#!/usr/bin/env npx tsx
/**
 * Predict (and optionally deploy) a new Safe multisig wallet.
 * Uses @safe-global/protocol-kit v6 predictedSafe flow.
 */
import { JsonRpcProvider, Wallet } from 'ethers';

import SafePkg from '@safe-global/protocol-kit';
const Safe = (SafePkg as any).default ?? SafePkg;

import {
  addCommonOptions,
  createCommand,
  resolveRpcUrl,
  resolveChainId,
  validateAddress,
  type CommonOptions
} from './safe_lib.js';

interface CreateSafeOptions extends CommonOptions {
  owners?: string;
  threshold?: string;
  saltNonce?: string;
  safeVersion?: string;
  deploy?: boolean;
}

const program = addCommonOptions(
  createCommand('create-safe', 'Predict address (and optionally deploy) a new Safe multisig')
)
  .requiredOption('--owners <addresses>', 'Comma-separated owner addresses')
  .requiredOption('--threshold <n>', 'Confirmation threshold')
  .option('--salt-nonce <nonce>', 'Salt nonce for deterministic address', '0')
  .option('--safe-version <version>', 'Safe contract version', '1.4.1')
  .option('--deploy', 'Send deployment transaction on-chain')
  .parse();

const opts = program.opts() as CreateSafeOptions;

try {
  resolveChainId(opts); // validates chain slug is known — must run FIRST
  const rpcUrl = resolveRpcUrl(opts);

  // Parse and validate owners
  const owners = (opts.owners ?? '').split(',').map(s => s.trim()).filter(Boolean);
  if (owners.length === 0) throw new Error('--owners must contain at least one address');
  for (const owner of owners) validateAddress(owner, 'owner');

  // Parse and validate threshold
  const threshold = parseInt(opts.threshold ?? '0', 10);
  if (!Number.isFinite(threshold) || threshold < 1) {
    throw new Error('--threshold must be a positive integer');
  }
  if (threshold > owners.length) {
    throw new Error(`--threshold (${threshold}) cannot exceed number of owners (${owners.length})`);
  }

  // Safe version
  const safeVersion = (opts.safeVersion ?? '1.4.1') as '1.4.1' | '1.3.0' | '1.2.0' | '1.1.1' | '1.0.0';

  // Init with predictedSafe config
  const safeSdk = await Safe.init({
    provider: rpcUrl,
    signer: opts.deploy ? undefined : undefined,
    ...(opts.deploy
      ? { signer: requirePrivateKeyForDeploy() }
      : {}),
    predictedSafe: {
      safeAccountConfig: { owners, threshold },
      safeDeploymentConfig: {
        saltNonce: opts.saltNonce ?? '0',
        safeVersion
      }
    }
  });

  const predictedAddress = await safeSdk.getAddress();
  const isDeployed = await safeSdk.isSafeDeployed();

  const result: Record<string, unknown> = {
    ok: true,
    predictedAddress,
    isDeployed,
    owners,
    threshold,
    safeVersion,
    saltNonce: opts.saltNonce ?? '0',
    chain: opts.chain ?? null
  };

  if (isDeployed) {
    result.note = 'Safe is already deployed at this address.';
  }

  if (opts.deploy && !isDeployed) {
    const deployTx = await safeSdk.createSafeDeploymentTransaction();
    const provider = new JsonRpcProvider(rpcUrl);
    const pk = requirePrivateKeyForDeploy();
    const wallet = new Wallet(pk, provider);

    const txResponse = await wallet.sendTransaction({
      to: deployTx.to,
      value: BigInt(deployTx.value),
      data: deployTx.data
    });
    const receipt = await txResponse.wait();

    result.deployed = true;
    result.txHash = receipt?.hash ?? txResponse.hash;
  } else if (opts.deploy && isDeployed) {
    result.deployed = false;
    result.note = 'Safe already deployed; skipping deployment.';
  }

  process.stdout.write(JSON.stringify(result, null, 2) + '\n');
} catch (err: unknown) {
  const message = err instanceof Error ? err.message : String(err);
  process.stderr.write(JSON.stringify({ ok: false, error: message }) + '\n');
  process.exit(1);
}

function requirePrivateKeyForDeploy(): string {
  const pk = process.env.SAFE_SIGNER_PRIVATE_KEY;
  if (!pk) throw new Error('Missing SAFE_SIGNER_PRIVATE_KEY env var (required for --deploy)');
  return pk.startsWith('0x') ? pk : `0x${pk}`;
}
