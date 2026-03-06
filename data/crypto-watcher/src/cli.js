#!/usr/bin/env node

import { createPublicClient, http, formatEther, formatUnits } from 'viem';
import { mainnet, arbitrum, base, optimism, polygon } from 'viem/chains';
import fs from 'fs';
import path from 'path';
import os from 'os';

// Chain configs
const CHAINS = {
  eth: { chain: mainnet, rpc: 'https://eth.llamarpc.com' },
  arb: { chain: arbitrum, rpc: 'https://arb1.arbitrum.io/rpc' },
  base: { chain: base, rpc: 'https://mainnet.base.org' },
  op: { chain: optimism, rpc: 'https://mainnet.optimism.io' },
  matic: { chain: polygon, rpc: 'https://polygon-rpc.com' }
};

// Popular tokens (chainId -> tokens)
const TOKENS = {
  1: [ // Ethereum
    { symbol: 'USDC', address: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', decimals: 6 },
    { symbol: 'USDT', address: '0xdAC17F958D2ee523a2206206994597C13D831ec7', decimals: 6 },
    { symbol: 'WETH', address: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', decimals: 18 },
  ],
  42161: [ // Arbitrum
    { symbol: 'USDC', address: '0xaf88d065e77c8cC2239327C5EDb3A432268e5831', decimals: 6 },
    { symbol: 'WETH', address: '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1', decimals: 18 },
  ],
  8453: [ // Base
    { symbol: 'USDC', address: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913', decimals: 6 },
    { symbol: 'WETH', address: '0x4200000000000000000000000000000000000006', decimals: 18 },
  ]
};

const ERC20_ABI = [
  {
    name: 'balanceOf',
    type: 'function',
    stateMutability: 'view',
    inputs: [{ name: 'account', type: 'address' }],
    outputs: [{ name: '', type: 'uint256' }]
  }
];

// Config management
const CONFIG_DIR = path.join(os.homedir(), '.config', 'crypto-watcher');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');

function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
    }
  } catch (e) {}
  return { wallets: [], alerts: { gasThreshold: 20, balanceChangePercent: 5 } };
}

function saveConfig(config) {
  fs.mkdirSync(CONFIG_DIR, { recursive: true });
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}

// Create client for chain
function getClient(chainKey) {
  const { chain, rpc } = CHAINS[chainKey];
  return createPublicClient({ chain, transport: http(rpc) });
}

// Get ETH balance
async function getEthBalance(client, address) {
  const balance = await client.getBalance({ address });
  return formatEther(balance);
}

// Get token balance
async function getTokenBalance(client, tokenAddress, decimals, walletAddress) {
  try {
    const balance = await client.readContract({
      address: tokenAddress,
      abi: ERC20_ABI,
      functionName: 'balanceOf',
      args: [walletAddress]
    });
    return formatUnits(balance, decimals);
  } catch {
    return '0';
  }
}

// Get gas price
async function getGasPrice(chainKey = 'eth') {
  const client = getClient(chainKey);
  const gasPrice = await client.getGasPrice();
  return Number(gasPrice) / 1e9; // Convert to gwei
}

// Get prices from CoinGecko
async function getPrices() {
  try {
    const res = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=ethereum,usd-coin,tether&vs_currencies=usd');
    const data = await res.json();
    return {
      ETH: data.ethereum?.usd || 0,
      USDC: data['usd-coin']?.usd || 1,
      USDT: data.tether?.usd || 1,
      WETH: data.ethereum?.usd || 0
    };
  } catch {
    return { ETH: 0, USDC: 1, USDT: 1, WETH: 0 };
  }
}

// Get DeFi positions from DefiLlama
async function getDefiPositions(address) {
  try {
    const res = await fetch(`https://api.llama.fi/protocol/${address}`);
    if (!res.ok) {
      // Try alternative endpoint
      const altRes = await fetch(`https://coins.llama.fi/prices/current/ethereum:${address}`);
      return null;
    }
    return await res.json();
  } catch {
    return null;
  }
}

// Commands
async function cmdStatus(walletName, quiet = false) {
  const config = loadConfig();
  const wallets = walletName 
    ? config.wallets.filter(w => w.name === walletName || w.address.toLowerCase() === walletName.toLowerCase())
    : config.wallets;
  
  if (wallets.length === 0) {
    console.log('No wallets configured. Use: crypto-watcher add <address> --name <name>');
    return;
  }

  const prices = await getPrices();
  
  for (const wallet of wallets) {
    if (!quiet) console.log(`\n📍 ${wallet.name} (${wallet.address.slice(0, 6)}...${wallet.address.slice(-4)})`);
    
    let totalUsd = 0;
    
    for (const chainKey of wallet.chains || ['eth']) {
      const client = getClient(chainKey);
      const chainName = CHAINS[chainKey].chain.name;
      
      // ETH balance
      const ethBal = await getEthBalance(client, wallet.address);
      const ethUsd = parseFloat(ethBal) * prices.ETH;
      totalUsd += ethUsd;
      
      if (!quiet && parseFloat(ethBal) > 0.001) {
        console.log(`  ${chainName}: ${parseFloat(ethBal).toFixed(4)} ETH ($${ethUsd.toFixed(2)})`);
      }
      
      // Token balances
      const chainId = CHAINS[chainKey].chain.id;
      const tokens = TOKENS[chainId] || [];
      
      for (const token of tokens) {
        const bal = await getTokenBalance(client, token.address, token.decimals, wallet.address);
        const usdVal = parseFloat(bal) * (prices[token.symbol] || 0);
        totalUsd += usdVal;
        
        if (!quiet && parseFloat(bal) > 0.01) {
          console.log(`  ${chainName}: ${parseFloat(bal).toFixed(2)} ${token.symbol} ($${usdVal.toFixed(2)})`);
        }
      }
    }
    
    console.log(`  💰 Total: $${totalUsd.toFixed(2)}`);
  }
}

async function cmdGas() {
  console.log('⛽ Gas Prices:\n');
  
  for (const [key, { chain }] of Object.entries(CHAINS)) {
    try {
      const gwei = await getGasPrice(key);
      const status = gwei < 15 ? '🟢' : gwei < 30 ? '🟡' : '🔴';
      console.log(`  ${status} ${chain.name}: ${gwei.toFixed(1)} gwei`);
    } catch {
      console.log(`  ⚪ ${chain.name}: unavailable`);
    }
  }
}

async function cmdAdd(address, name, chains) {
  const config = loadConfig();
  
  // Validate address
  if (!address.match(/^0x[a-fA-F0-9]{40}$/)) {
    console.log('❌ Invalid address format');
    return;
  }
  
  // Check if exists
  if (config.wallets.some(w => w.address.toLowerCase() === address.toLowerCase())) {
    console.log('❌ Wallet already exists');
    return;
  }
  
  config.wallets.push({
    address,
    name: name || `wallet-${config.wallets.length + 1}`,
    chains: chains ? chains.split(',') : ['eth']
  });
  
  saveConfig(config);
  console.log(`✅ Added ${name || address}`);
}

async function cmdRemove(nameOrAddress) {
  const config = loadConfig();
  const before = config.wallets.length;
  
  config.wallets = config.wallets.filter(w => 
    w.name !== nameOrAddress && w.address.toLowerCase() !== nameOrAddress.toLowerCase()
  );
  
  if (config.wallets.length < before) {
    saveConfig(config);
    console.log('✅ Removed');
  } else {
    console.log('❌ Wallet not found');
  }
}

async function cmdList() {
  const config = loadConfig();
  
  if (config.wallets.length === 0) {
    console.log('No wallets configured.');
    return;
  }
  
  console.log('📋 Watched Wallets:\n');
  for (const w of config.wallets) {
    console.log(`  ${w.name}: ${w.address}`);
    console.log(`    Chains: ${(w.chains || ['eth']).join(', ')}`);
  }
}

async function cmdDefi(address) {
  console.log(`\n🏦 DeFi Positions for ${address.slice(0, 6)}...${address.slice(-4)}\n`);
  
  // Use Zapper API alternative or show manual check
  console.log('  Checking DefiLlama...');
  
  try {
    const res = await fetch(`https://api.llama.fi/v2/historicalChainTvl`);
    // DefiLlama doesn't have per-address API, suggest alternatives
    console.log('\n  💡 For detailed DeFi positions, check:');
    console.log(`     • https://debank.com/profile/${address}`);
    console.log(`     • https://zapper.xyz/account/${address}`);
  } catch {
    console.log('  ❌ Could not fetch DeFi data');
  }
}

// Main CLI
async function main() {
  const args = process.argv.slice(2);
  const cmd = args[0];
  
  switch (cmd) {
    case 'status':
      await cmdStatus(args[1], args.includes('--quiet'));
      break;
    case 'gas':
      await cmdGas();
      break;
    case 'add':
      const nameIdx = args.indexOf('--name');
      const chainsIdx = args.indexOf('--chains');
      await cmdAdd(
        args[1],
        nameIdx > 0 ? args[nameIdx + 1] : null,
        chainsIdx > 0 ? args[chainsIdx + 1] : null
      );
      break;
    case 'remove':
      await cmdRemove(args[1]);
      break;
    case 'list':
      await cmdList();
      break;
    case 'defi':
      await cmdDefi(args[1] || loadConfig().wallets[0]?.address);
      break;
    default:
      console.log(`
crypto-watcher - Monitor crypto wallets and positions

Commands:
  status [name]     Check balances (--quiet for alerts only)
  gas               Show gas prices across chains
  add <addr>        Add wallet (--name <n> --chains eth,arb)
  remove <name>     Remove wallet
  list              List watched wallets
  defi <addr>       Check DeFi positions

Examples:
  crypto-watcher add 0x123...abc --name main --chains eth,arb,base
  crypto-watcher status
  crypto-watcher gas
      `);
  }
}

main().catch(console.error);
