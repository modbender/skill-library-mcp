#!/usr/bin/env node
/**
 * Output current positions (holdings) as JSON for the trading agent.
 * Uses Agent API holdings endpoint.
 * Reads: NADFUNAGENT_DATA_DIR (default $HOME/nadfunagent) for .env; or NADFUN_ENV_PATH for .env path.
 * Usage: node check_positions.js [0xWalletAddress]
 * Output: JSON to stdout with wallet, positions[], source.
 */
const fs = require('fs');
const path = require('path');
const os = require('os');

const DATA_DIR = process.env.NADFUNAGENT_DATA_DIR || path.join(os.homedir(), 'nadfunagent');
const ENV_PATH = process.env.NADFUN_ENV_PATH || path.join(DATA_DIR, '.env');

function loadEnv() {
  const env = {};
  try {
    const content = fs.readFileSync(ENV_PATH, 'utf-8');
    content.split('\n').forEach(line => {
      line = line.trim();
      if (line && !line.startsWith('#') && line.includes('=')) {
        const idx = line.indexOf('=');
        const k = line.slice(0, idx).trim();
        const v = line.slice(idx + 1).trim().replace(/^["']|["']$/g, '');
        env[k] = v;
      }
    });
  } catch {}
  return env;
}

async function main() {
  const env = loadEnv();
  const network = env.MONAD_NETWORK || process.env.MONAD_NETWORK || 'mainnet';
  let wallet = process.argv[2]?.startsWith('0x') ? process.argv[2] : null;
  wallet = wallet || env.MONAD_WALLET || env.WALLET_ADDRESS || process.env.NADFUNAGENT_WALLET;

  if (!wallet || !wallet.startsWith('0x')) {
    console.log(JSON.stringify({
      error: 'Wallet not set. Use: node check_positions.js 0xYourAddress OR set MONAD_WALLET in .env',
      positions: [],
      wallet: null
    }, null, 2));
    process.exit(0);
  }

  const apiBase = network === 'mainnet' ? 'https://api.nadapp.net' : 'https://dev-api.nad.fun';
  const url = `${apiBase}/agent/holdings/${wallet}?limit=100`;

  let data;
  try {
    const res = await fetch(url, {
      headers: { 'User-Agent': 'OpenClaw-Agent/1.0', 'Accept': 'application/json' }
    });
    data = await res.json();
  } catch (e) {
    console.log(JSON.stringify({
      error: String(e.message || e),
      url,
      positions: [],
      wallet
    }, null, 2));
    process.exit(1);
  }

  const tokens = data.tokens || [];
  const positions = [];
  for (const t of tokens) {
    const info = t.token_info || {};
    const balInfo = t.balance_info || {};
    const balance = parseFloat(balInfo.balance || 0) || 0;
    if (balance <= 0) continue;
    positions.push({
      address: info.token_id || info.address || '',
      symbol: info.symbol || '',
      name: info.name || '',
      balance
    });
  }

  const out = {
    timestamp: new Date().toISOString().replace(/\.\d{3}Z$/, '.000Z'),
    wallet,
    network,
    positionsCount: positions.length,
    positions,
    source: 'agent_api'
  };
  console.log(JSON.stringify(out, null, 2));
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
