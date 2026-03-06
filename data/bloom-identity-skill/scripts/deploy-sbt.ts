#!/usr/bin/env ts-node
/**
 * Deploy BloomTasteCard SBT contract to Base Sepolia (or mainnet).
 *
 * Usage:
 *   npx ts-node scripts/deploy-sbt.ts
 *
 * Requires:
 *   - WALLET_ENCRYPTION_SECRET in .env (for agent wallet key decryption)
 *   - A user wallet in .wallet-storage/ (run the skill once first)
 *   - OR set DEPLOYER_PRIVATE_KEY directly in .env
 *
 * After deploy, add the printed address to .env as SBT_CONTRACT_ADDRESS.
 */
import 'dotenv/config';
import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import {
  createPublicClient,
  createWalletClient,
  http,
} from 'viem';
import { base, baseSepolia } from 'viem/chains';
import { privateKeyToAccount } from 'viem/accounts';

// ---------------------------------------------------------------------------
// 1. Compile contract with solc (npx solc = solcjs wrapper)
// ---------------------------------------------------------------------------
function compile(): { abi: any[]; bytecode: `0x${string}` } {
  const projectRoot = path.resolve(__dirname, '..');
  const contractPath = path.resolve(projectRoot, 'contracts/BloomTasteCard.sol');
  const outDir = path.resolve(projectRoot, '.solc-output');

  console.log('Compiling BloomTasteCard.sol ...');

  // Clean previous output
  fs.rmSync(outDir, { recursive: true, force: true });
  fs.mkdirSync(outDir, { recursive: true });

  // Compile with solcjs via npx
  execSync(
    `npx solc --bin --abi --optimize --optimize-runs 200 ` +
    `--base-path "${projectRoot}" ` +
    `--include-path "${path.join(projectRoot, 'node_modules')}" ` +
    `-o "${outDir}" ` +
    `"${contractPath}"`,
    { encoding: 'utf-8', maxBuffer: 10 * 1024 * 1024 },
  );

  // Read compiled artifacts (solcjs uses flattened filenames)
  const abiFile = path.join(outDir, 'contracts_BloomTasteCard_sol_BloomTasteCard.abi');
  const binFile = path.join(outDir, 'contracts_BloomTasteCard_sol_BloomTasteCard.bin');

  if (!fs.existsSync(abiFile) || !fs.existsSync(binFile)) {
    throw new Error('Compilation output not found — check solc errors above');
  }

  const abi = JSON.parse(fs.readFileSync(abiFile, 'utf-8'));
  const bin = fs.readFileSync(binFile, 'utf-8').trim();

  if (!bin) {
    throw new Error('Empty bytecode — contract may be abstract');
  }

  console.log('Compilation successful.');
  return { abi, bytecode: `0x${bin}` as `0x${string}` };
}

// ---------------------------------------------------------------------------
// 2. Resolve deployer private key
// ---------------------------------------------------------------------------
async function getDeployerKey(): Promise<`0x${string}`> {
  // Option A: explicit env var
  if (process.env.DEPLOYER_PRIVATE_KEY) {
    const key = process.env.DEPLOYER_PRIVATE_KEY;
    return (key.startsWith('0x') ? key : `0x${key}`) as `0x${string}`;
  }

  // Option B: first user wallet in storage (dev convenience)
  const { walletStorage } = await import('../src/blockchain/wallet-storage');
  const users = await walletStorage.listUsers();
  if (users.length === 0) {
    throw new Error(
      'No deployer key found. Set DEPLOYER_PRIVATE_KEY or run the skill once to create a wallet.',
    );
  }

  const wallet = await walletStorage.getUserWallet(users[0]);
  if (!wallet?.privateKey) {
    throw new Error('Stored wallet has no private key (mock wallet). Set DEPLOYER_PRIVATE_KEY instead.');
  }

  console.log(`Using wallet from user "${users[0]}" as deployer.`);
  return wallet.privateKey;
}

// ---------------------------------------------------------------------------
// 3. Deploy
// ---------------------------------------------------------------------------
async function main() {
  const network = (process.env.NETWORK as string) || 'base-sepolia';
  const chain = network === 'base-mainnet' ? base : baseSepolia;

  console.log(`\nTarget network: ${chain.name} (${chain.id})`);

  const { abi, bytecode } = compile();
  const privateKey = await getDeployerKey();
  const account = privateKeyToAccount(privateKey);

  console.log(`Deployer: ${account.address}`);

  const publicClient = createPublicClient({
    chain,
    transport: http(chain.rpcUrls.default.http[0]),
  });

  const walletClient = createWalletClient({
    account,
    chain,
    transport: http(chain.rpcUrls.default.http[0]),
  });

  console.log('Deploying BloomTasteCard ...');

  const hash = await walletClient.deployContract({
    abi,
    bytecode,
    args: [],
  });

  console.log(`Tx submitted: ${hash}`);
  console.log('Waiting for confirmation ...');

  const receipt = await publicClient.waitForTransactionReceipt({ hash });

  if (!receipt.contractAddress) {
    throw new Error('Deploy failed — no contract address in receipt');
  }

  const explorerBase = network === 'base-mainnet'
    ? 'https://basescan.org'
    : 'https://sepolia.basescan.org';

  console.log('\n========================================');
  console.log(`Contract deployed!`);
  console.log(`  Address : ${receipt.contractAddress}`);
  console.log(`  Tx Hash : ${hash}`);
  console.log(`  Network : ${chain.name}`);
  console.log(`  Explorer: ${explorerBase}/address/${receipt.contractAddress}`);
  console.log('========================================');
  console.log(`\nAdd to .env:`);
  console.log(`  SBT_CONTRACT_ADDRESS=${receipt.contractAddress}`);
}

main().catch(err => {
  console.error('\nDeploy failed:', err.message || err);
  process.exit(1);
});
