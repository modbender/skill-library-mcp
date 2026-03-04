#!/usr/bin/env node
/**
 * 0x Swap API - Execute Swap
 * Usage: node swap.js --sell WETH --buy USDC --amount 0.01 --chain base
 * 
 * Required environment variables:
 * - ZEROEX_API_KEY: Get from https://dashboard.0x.org/
 * - PRIVATE_KEY: Wallet private key (hex without 0x prefix)
 */

import axios from 'axios';
import { ethers } from 'ethers';

const CHAINS = {
  ethereum: 1,
  base: 8453,
  polygon: 137,
  arbitrum: 42161,
  optimism: 10,
  'base-sepolia': 84532
};

const TOKENS = {
  8453: {
    WETH: '0x4200000000000000000000000000000000000006',
    USDC: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'
  },
  1: {
    WETH: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    USDC: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
  }
};

function getPrivateKey() {
  const key = process.env.PRIVATE_KEY || process.env.ZEROEX_PRIVATE_KEY;
  if (!key) {
    throw new Error('PRIVATE_KEY environment variable required');
  }
  // Remove 0x prefix if present
  return key.startsWith('0x') ? key.slice(2) : key;
}

function getApiKey() {
  const key = process.env.ZEROEX_API_KEY;
  if (!key) {
    throw new Error('ZEROEX_API_KEY environment variable required. Get from https://dashboard.0x.org/');
  }
  return key;
}

function getTokenAddress(chainId, symbol) {
  const addr = TOKENS[chainId]?.[symbol.toUpperCase()];
  if (addr) return addr;
  if (symbol.startsWith('0x')) return symbol;
  throw new Error(`Unknown token: ${symbol}`);
}

function getRpcUrl(chain) {
  // Use custom RPC if provided
  if (process.env.RPC_URL) return process.env.RPC_URL;
  
  const rpcs = {
    base: 'https://mainnet.base.org',
    'base-sepolia': 'https://sepolia.base.org',
    ethereum: 'https://eth.llamarpc.com',
    polygon: 'https://polygon.llamarpc.com',
    arbitrum: 'https://arb1.arbitrum.io/rpc',
    optimism: 'https://mainnet.optimism.io'
  };
  return rpcs[chain.toLowerCase()] || rpcs.base;
}

async function executeSwap(params) {
  const privateKey = getPrivateKey();
  const apiKey = getApiKey();
  
  const { sell, buy, amount, chain } = params;
  
  const chainId = CHAINS[chain.toLowerCase()];
  if (!chainId) throw new Error(`Unsupported chain: ${chain}`);
  
  const sellAddr = getTokenAddress(chainId, sell);
  const buyAddr = getTokenAddress(chainId, buy);
  
  const provider = new ethers.JsonRpcProvider(getRpcUrl(chain));
  const wallet = new ethers.Wallet(privateKey, provider);
  
  console.log(`Wallet: ${wallet.address}`);
  console.log(`Chain: ${chain} (${chainId})`);
  console.log(`Selling: ${amount} ${sell}`);
  
  // Get quote
  const decimals = sell.toUpperCase() === 'ETH' ? 18 : 6;
  const sellAmount = ethers.parseUnits(amount.toString(), decimals).toString();
  
  const quoteUrl = `https://api.0x.org/swap/v1/quote?${new URLSearchParams({
    sellToken: sellAddr,
    buyToken: buyAddr,
    sellAmount,
    chainId: chainId.toString(),
    takerAddress: wallet.address
  })}`;
  
  console.log('\nFetching quote...');
  const quoteRes = await axios.get(quoteUrl, { headers: { '0x-api-key': apiKey } });
  const quote = quoteRes.data;
  
  console.log(`Quote: 1 ${sell} = ${quote.price} ${buy}`);
  console.log(`Buy amount: ${quote.buyAmount}`);
  
  // Check balance
  if (sell.toUpperCase() !== 'ETH') {
    const token = new ethers.Contract(sellAddr, [
      'function balanceOf(address) view returns (uint256)',
      'function decimals() view returns (uint8)',
      'function approve(address, uint256) returns (bool)'
    ], provider);
    const bal = await token.balanceOf(wallet.address);
    console.log(`\nToken balance: ${ethers.formatUnits(bal, decimals)} ${sell}`);
    
    if (BigInt(sellAmount) > bal) {
      throw new Error('Insufficient token balance');
    }
    
    // Check and set allowance - exact amount only!
    const allowance = await token.allowance(wallet.address, quote.to);
    console.log(`Current allowance: ${allowance}`);
    
    if (BigInt(allowance) < BigInt(sellAmount)) {
      console.log('\nSetting allowance (exact amount)...');
      // Approve only what we need - security best practice
      const approveTx = await token.approve(quote.to, sellAmount);
      await approveTx.wait();
      console.log(`Approved! TX: ${approveTx.hash}`);
    }
  } else {
    const bal = await provider.getBalance(wallet.address);
    console.log(`\nETH balance: ${ethers.formatEther(bal)} ETH`);
  }
  
  // Execute
  console.log('\nExecuting swap...');
  const tx = {
    to: quote.to,
    data: quote.data,
    value: quote.value || '0',
    gasLimit: quote.gas || '250000'
  };
  
  const resp = await wallet.sendTransaction(tx);
  console.log(`\nTransaction submitted: ${resp.hash}`);
  console.log('Waiting for confirmation...');
  
  const receipt = await resp.wait();
  console.log(`\n✅ Swap complete! Block: ${receipt.blockNumber}`);
  console.log(`Transaction: https://basescan.org/tx/${resp.hash}`);
  
  return receipt;
}

const args = process.argv.slice(2);
const params = {};
for (let i = 0; i < args.length; i += 2) {
  const key = args[i].replace('--', '');
  params[key] = args[i + 1];
}

if (!params.sell || !params.buy || !params.amount || !params.chain) {
  console.log('Usage: node swap.js --sell WETH --buy USDC --amount 0.01 --chain base');
  console.log('Supported chains: base, ethereum, polygon, arbitrum, optimism');
  console.log('\nEnvironment variables:');
  console.log('  ZEROEX_API_KEY: Get from https://dashboard.0x.org/');
  console.log('  PRIVATE_KEY: Your wallet private key');
  process.exit(1);
}

executeSwap(params).catch(e => {
  console.error(e.message);
  process.exit(1);
});
