#!/usr/bin/env node
/**
 * Fix entry prices for existing positions. Sets entryValueMON = 0.15 MON for positions bought today.
 * Run: node fix-entry-prices.js
 */
const fs = require('fs').promises;
const { createPublicClient, http, erc20Abi } = require('viem');
const { privateKeyToAccount } = require('viem/accounts');
const { monadMainnet } = require('./monad-chains');

const API_URL = 'https://api.nadapp.net';
const path = require('path');
const os = require('os');
const defaultDataDir = path.join(os.homedir(), 'nadfunagent');

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

  console.log('🔧 Fixing entry prices for existing positions...\n');
  console.log('Wallet:', walletAddress);
  console.log('');

  // Get holdings from API
  let holdingsData;
  try {
    const res = await fetch(`${API_URL}/agent/holdings/${walletAddress}?limit=100`, {
      headers: { Accept: 'application/json', 'User-Agent': 'Fix-Entry-Prices/1.0' }
    });
    holdingsData = await res.json();
  } catch (e) {
    console.error('Failed to fetch holdings:', e.message);
    process.exit(1);
  }

  const tokens = Array.isArray(holdingsData.tokens) ? holdingsData.tokens : [];
  
  // Load or create report
  let report = {
    timestamp: new Date().toISOString(),
    wallet: walletAddress,
    cycle: 'fix_entry_prices',
    positionsCount: 0,
    positions: [],
    summary: {}
  };

  try {
    const existing = await fs.readFile(REPORT_PATH, 'utf-8');
    const parsed = JSON.parse(existing);
    if (parsed && Array.isArray(parsed.positions)) {
      report = parsed;
    }
  } catch {
    // Create new
  }

  // Optional: add known entry prices for backfill (address, symbol, entryValue in MON)
  const knownPositions = [
    // Example: { address: '0x...', symbol: 'TOKEN', entryValue: 0.15 },
  ];

  console.log('Setting entry prices:\n');

  for (const holding of tokens) {
    const tokenAddress = holding.token_info?.token_id;
    if (!tokenAddress) continue;

    const balance = await publicClient.readContract({
      address: tokenAddress,
      abi: erc20Abi,
      functionName: 'balanceOf',
      args: [walletAddress]
    });

    if (balance === 0n) continue;

    const symbol = holding.token_info?.symbol || 'UNKNOWN';
    
    // Find if we know the entry price
    const known = knownPositions.find(p => 
      p.address.toLowerCase() === tokenAddress.toLowerCase() || p.symbol === symbol
    );
    
    const entryValueMON = known?.entryValue || 0.15; // Default 0.15 if not known

    const existingIdx = report.positions.findIndex(p =>
      (p.address || '').toLowerCase() === tokenAddress.toLowerCase()
    );

    const position = existingIdx >= 0 ? report.positions[existingIdx] : {
      address: tokenAddress,
      symbol: symbol,
      name: holding.token_info?.name || '',
      balance: Number(balance) / 1e18,
      balanceOnChain: Number(balance) / 1e18,
      currentValueMON: 0,
      entryValueMON: entryValueMON,
      pnlPercent: 0,
      dataSource: 'fix_entry_prices',
      updatedAt: new Date().toISOString()
    };

    // Update entry price
    position.entryValueMON = entryValueMON;
    position.address = tokenAddress;
    position.symbol = symbol;
    position.updatedAt = new Date().toISOString();

    if (existingIdx >= 0) {
      report.positions[existingIdx] = position;
    } else {
      report.positions.push(position);
    }

    console.log(`✅ ${symbol} (${tokenAddress}): entryValueMON = ${entryValueMON} MON`);
  }

  report.timestamp = new Date().toISOString();
  report.wallet = walletAddress;
  report.positionsCount = report.positions.length;

  // Ensure directory exists
  const dir = require('path').dirname(reportPath);
  try {
    await fs.mkdir(dir, { recursive: true });
  } catch {
    // Directory might already exist
  }

  await fs.writeFile(reportPath, JSON.stringify(report, null, 2), 'utf-8');
  console.log(`\n✅ Entry prices fixed! Saved to ${reportPath}`);
  console.log(`   Total positions: ${report.positions.length}`);
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
