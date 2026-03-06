#!/usr/bin/env node
/**
 * Sell ALL token positions (bonding curve + DEX). Uses Agent API holdings + on-chain balance.
 * Run: node sell-all.js [--slippage 300] [--dry-run]
 * Requires: MONAD_PRIVATE_KEY in .env (NADFUN_ENV_PATH or $HOME/nadfunagent/.env), or NAD_PRIVATE_KEY for sell-token.js
 */
const path = require('path');
const os = require('os');
const fs = require('fs').promises;
const defaultDataDir = path.join(os.homedir(), 'nadfunagent');
const { execSync } = require('child_process');
const { createPublicClient, http, erc20Abi } = require('viem');
const { privateKeyToAccount } = require('viem/accounts');
const { monadMainnet } = require('./monad-chains');

const API_URL = 'https://api.nadapp.net';
const SKILL_DIR = __dirname;

async function loadConfig() {
  const envPath = process.env.NADFUN_ENV_PATH || path.join(defaultDataDir, '.env');
  try {
    const content = await fs.readFile(envPath, 'utf-8');
    const config = {};
    content.split('\n').forEach(line => {
      const m = line.match(/^([^=]+)=(.*)$/);
      if (m) config[m[1].trim()] = m[2].trim();
    });
    return config;
  } catch {
    return {};
  }
}

async function main() {
  const args = process.argv.slice(2);
  const dryRun = args.includes('--dry-run');
  let slippageBps = 300;
  const slippageIdx = args.indexOf('--slippage');
  if (slippageIdx >= 0 && args[slippageIdx + 1]) slippageBps = parseInt(args[slippageIdx + 1], 10) || 300;

  const config = await loadConfig();
  const privateKey = config.MONAD_PRIVATE_KEY || process.env.MONAD_PRIVATE_KEY;
  const rpcUrl = config.MONAD_RPC_URL || process.env.MONAD_RPC_URL || 'https://monad-mainnet.drpc.org';

  if (!privateKey) {
    console.error('Set MONAD_PRIVATE_KEY in', path.join(defaultDataDir, '.env'), 'or NADFUN_ENV_PATH');
    process.exit(1);
  }

  const account = privateKeyToAccount(privateKey);
  const walletAddress = account.address;
  const publicClient = createPublicClient({ chain: monadMainnet, transport: http(rpcUrl) });

  console.log('🔄 Sell ALL tokens');
  console.log('Wallet:', walletAddress);
  if (dryRun) console.log('⚠️  DRY RUN — no sells will be executed\n');

  let holdingsData;
  try {
    const res = await fetch(`${API_URL}/agent/holdings/${walletAddress}?limit=100`, {
      headers: { Accept: 'application/json', 'User-Agent': 'Nadfun-SellAll/1.0' }
    });
    holdingsData = await res.json();
  } catch (e) {
    console.error('Failed to fetch holdings:', e.message);
    process.exit(1);
  }

  const tokens = Array.isArray(holdingsData.tokens) ? holdingsData.tokens : [];
  const toSell = [];
  for (const holding of tokens) {
    const tokenAddress = holding.token_info?.token_id;
    if (!tokenAddress) continue;
    let balanceWei;
    try {
      balanceWei = await publicClient.readContract({
        address: tokenAddress, abi: erc20Abi, functionName: 'balanceOf', args: [walletAddress]
      });
    } catch { continue; }
    if (balanceWei > 0n) toSell.push({ address: tokenAddress, symbol: holding.token_info?.symbol || 'UNKNOWN', balance: balanceWei });
  }

  if (toSell.length === 0) {
    console.log('No token positions to sell.');
    return;
  }

  console.log(`Found ${toSell.length} position(s) to sell:\n`);
  toSell.forEach((p, i) => console.log(`  ${i + 1}. ${p.symbol} (${p.address})`));
  console.log('');

  if (dryRun) {
    console.log('Dry run: would run for each: node sell-token.js --token <addr> --amount all --slippage', slippageBps);
    return;
  }

  const env = { ...process.env, NAD_PRIVATE_KEY: privateKey };
  for (let i = 0; i < toSell.length; i++) {
    const pos = toSell[i];
    console.log(`\n[${i + 1}/${toSell.length}] Selling ${pos.symbol} (${pos.address})...`);
    try {
      execSync(`node sell-token.js --token ${pos.address} --amount all --slippage ${slippageBps}`, { cwd: SKILL_DIR, env, stdio: 'inherit' });
    } catch (e) {
      console.error(`❌ Failed to sell ${pos.symbol}:`, e.message || e);
    }
    if (i < toSell.length - 1) {
      console.log('Waiting 3s before next sell...');
      await new Promise(r => setTimeout(r, 3000));
    }
  }
  console.log('\n✅ Sell-all finished.');
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
