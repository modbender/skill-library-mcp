#!/usr/bin/env node
/**
 * Check P&L for all positions and execute sells based on thresholds.
 * Uses nad.fun quote contract getAmountOut(token, balanceWei, false).
 * On revert, falls back to Agent API market price.
 * Reads entry price from positions_report.json (set by buy-token.js). Path: POSITIONS_REPORT_PATH or $HOME/nadfunagent.
 * Sells automatically if P&L >= +5% (take profit) or <= -10% (stop loss).
 * Run: node check-pnl.js [--auto-sell] [--dry-run]
 * Requires: MONAD_PRIVATE_KEY, MONAD_RPC_URL in env or .env (NADFUN_ENV_PATH or $HOME/nadfunagent/.env)
 */
const path = require('path');
const os = require('os');
const fs = require('fs').promises;
const defaultDataDir = path.join(os.homedir(), 'nadfunagent');
const { execSync } = require('child_process');
const { createPublicClient, http, erc20Abi } = require('viem');
const { privateKeyToAccount } = require('viem/accounts');
const { monadMainnet } = require('./monad-chains');

const NADFUN_QUOTE_CONTRACT = '0x7e78A8DE94f21804F7a17F4E8BF9EC2c872187ea'; // nad.fun on-chain quote (LENS)
const API_URL = 'https://api.nadapp.net';
const TAKE_PROFIT_PERCENT = 5;  // +5% take profit
const STOP_LOSS_PERCENT = -10;  // -10% stop loss

const lensAbi = [
  {
    name: 'getAmountOut',
    type: 'function',
    stateMutability: 'view',
    inputs: [
      { name: 'token', type: 'address' },
      { name: 'amountIn', type: 'uint256' },
      { name: 'isBuy', type: 'bool' }
    ],
    outputs: [
      { name: 'router', type: 'address' },
      { name: 'amountOut', type: 'uint256' }
    ]
  }
];

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
  const autoSell = process.argv.includes('--auto-sell');
  const dryRun = process.argv.includes('--dry-run');
  
  const config = await loadConfig();
  const privateKey = config.MONAD_PRIVATE_KEY || process.env.MONAD_PRIVATE_KEY;
  const rpcUrl = config.MONAD_RPC_URL || process.env.MONAD_RPC_URL || 'https://monad-mainnet.drpc.org';

  if (!privateKey) {
    const envPath = process.env.NADFUN_ENV_PATH || path.join(defaultDataDir, '.env');
    console.error(`Set MONAD_PRIVATE_KEY in ${envPath} or MONAD_PRIVATE_KEY env variable`);
    process.exit(1);
  }

  const account = privateKeyToAccount(privateKey);
  const walletAddress = account.address;

  const publicClient = createPublicClient({
    chain: monadMainnet,
    transport: http(rpcUrl)
  });

  console.log('🔍 Checking positions for sell signals...\n');
  console.log('Wallet:', walletAddress);
  console.log('');

  let holdingsData;
  try {
    const res = await fetch(`${API_URL}/agent/holdings/${walletAddress}?limit=100`, {
      headers: { Accept: 'application/json', 'User-Agent': 'Nadfun-CheckPnl/1.0' }
    });
    holdingsData = await res.json();
  } catch (e) {
    console.error('Failed to fetch holdings:', e.message);
    process.exit(1);
  }

  const tokens = Array.isArray(holdingsData.tokens) ? holdingsData.tokens : [];
  if (tokens.length === 0) {
    console.log('No positions reported by API.');
    return;
  }

  let previousReport = null;
  try {
    const reportPath = process.env.POSITIONS_REPORT_PATH || path.join(defaultDataDir, 'positions_report.json');
    const raw = await fs.readFile(reportPath, 'utf-8');
    previousReport = JSON.parse(raw);
  } catch {
    // no previous report
  }

  const positions = [];

  for (const holding of tokens) {
    const tokenAddress = holding.token_info?.token_id;
    if (!tokenAddress) continue;

    let balanceWei;
    try {
      balanceWei = await publicClient.readContract({
        address: tokenAddress,
        abi: erc20Abi,
        functionName: 'balanceOf',
        args: [walletAddress]
      });
    } catch {
      continue;
    }

    if (balanceWei === 0n) continue;

    const symbol = holding.token_info?.symbol || 'UNKNOWN';
    const balanceNum = Number(balanceWei) / 1e18;

    let currentValueMON = 0;
    let dataSource = 'api';

    try {
      const [router, amountOutWei] = await publicClient.readContract({
        address: NADFUN_QUOTE_CONTRACT,
        abi: lensAbi,
        functionName: 'getAmountOut',
        args: [tokenAddress, balanceWei, false]  // nad.fun quote: (token, amountIn, isBuy)
      });
      currentValueMON = Number(amountOutWei) / 1e18;
      dataSource = 'onchain';
    } catch (e) {
      try {
        const mRes = await fetch(`${API_URL}/agent/market/${tokenAddress}`, {
          headers: { Accept: 'application/json' }
        });
        const market = await mRes.json();
        const price = parseFloat(market?.market_info?.price) || 0;
        if (price > 0) {
          currentValueMON = price * balanceNum;
        }
      } catch {
        // skip
      }
    }

    const prev = previousReport?.positions?.find(p =>
      (p.address || '').toLowerCase() === tokenAddress.toLowerCase()
    );
    const entryValueMON = prev?.entryValueMON ?? currentValueMON;
    const pnlPercent = entryValueMON > 0
      ? ((currentValueMON - entryValueMON) / entryValueMON) * 100
      : 0;

    positions.push({
      address: tokenAddress,
      symbol: symbol,
      name: holding.token_info?.name || '',
      balance: balanceNum,
      currentValueMON,
      entryValueMON,
      pnlPercent,
      dataSource
    });

    const pnlStr = pnlPercent >= 0 ? `+${pnlPercent.toFixed(2)}%` : `${pnlPercent.toFixed(2)}%`;
    const shouldSell = pnlPercent >= TAKE_PROFIT_PERCENT || pnlPercent <= STOP_LOSS_PERCENT;
    const reason = pnlPercent >= TAKE_PROFIT_PERCENT ? 'take profit' : pnlPercent <= STOP_LOSS_PERCENT ? 'stop loss' : null;
    const action = shouldSell 
      ? (pnlPercent >= TAKE_PROFIT_PERCENT ? '🟢 SELL (take profit)' : '🔴 SELL (stop loss)')
      : '⚪ HOLD';
    
    console.log(`${symbol}: ${balanceNum.toFixed(2)} tokens | ${currentValueMON.toFixed(4)} MON | Entry: ${entryValueMON.toFixed(4)} MON | P&L ${pnlStr} (${dataSource}) | ${action}`);
    
    // Auto-sell if threshold reached
    if (shouldSell && autoSell && !dryRun) {
      console.log(`   🔄 Executing sell: ${reason}...`);
      try {
        const env = { ...process.env, NAD_PRIVATE_KEY: privateKey };
        execSync(
          `node sell-token.js --token ${tokenAddress} --amount all --slippage 300`,
          { cwd: __dirname, env, stdio: 'inherit' }
        );
        console.log(`   ✅ Sold ${symbol}`);
        await new Promise(r => setTimeout(r, 3000)); // Rate limit
      } catch (e) {
        console.error(`   ❌ Failed to sell ${symbol}:`, e.message || e);
      }
    }
  }

  console.log('');
  const sellCount = positions.filter(p => {
    const pnl = p.entryValueMON > 0 ? ((p.currentValueMON - p.entryValueMON) / p.entryValueMON) * 100 : 0;
    return pnl >= TAKE_PROFIT_PERCENT || pnl <= STOP_LOSS_PERCENT;
  }).length;
  console.log(`✅ Processed ${positions.length} positions. ${sellCount} position(s) meet sell criteria.`);
  if (!autoSell && sellCount > 0) {
    console.log(`   Run with --auto-sell to execute sells automatically.`);
  }
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
