#!/usr/bin/env node
/**
 * 0x Swap API - Get Quote (v2 API)
 * Usage: node quote.js --sell WETH --buy USDC --amount 0.01 --chain base
 */

import axios from 'axios';
import { ethers } from 'ethers';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Chain ID mapping
const CHAINS = {
  ethereum: 1,
  base: 8453,
  polygon: 137,
  arbitrum: 42161,
  optimism: 10,
  sepolia: 11155111,
  'base-sepolia': 84532
};

// Token addresses (canonical)
const TOKENS = {
  1: {
    WETH: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    USDC: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    DAI: '0x6B175474E89094C44Da98b954EedeAC495271d0F'
  },
  8453: {
    WETH: '0x4200000000000000000000000000000000000006',
    USDC: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
    DAI: '0x50c5725949A6F0C72E6C4a641F24049A917DB0Cb'
  },
  137: {
    WETH: '0x7ceB23fD6bC0adD59E62ac25578270cFf1b2f96f',
    USDC: '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
    DAI: '0x53E0bca35eC356BD5ddDFEbdD1Fc0fD03FaBad39'
  },
  42161: {
    WETH: '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1',
    USDC: '0xaf88d065d77C72cE3972fD2c2bC7f8ce0C12c21c',
    DAI: '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1'
  },
  10: {
    WETH: '0x4200000000000000000000000000000000000006',
    USDC: '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85',
    DAI: '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1'
  }
};

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
  
  // If not a known token, assume it's already an address
  if (symbol.startsWith('0x')) return symbol;
  
  throw new Error(`Unknown token: ${symbol} on chain ${chainId}`);
}

async function getQuote(params) {
  const apiKey = getApiKey();
  if (!apiKey) {
    throw new Error('ZEROEX_API_KEY required. Get from https://dashboard.0x.org/');
  }
  
  const { sellToken, buyToken, amount, chain, taker } = params;
  
  const chainId = CHAINS[chain.toLowerCase()];
  if (!chainId) {
    throw new Error(`Unsupported chain: ${chain}. Supported: ${Object.keys(CHAINS).join(', ')}`);
  }
  
  const sellAddr = getTokenAddress(chainId, sellToken);
  const buyAddr = getTokenAddress(chainId, buyToken);
  
  // Determine decimals based on token
  const isEth = sellToken.toUpperCase() === 'ETH';
  const decimals = isEth ? 18 : 6;
  const sellAmount = ethers.parseUnits(amount.toString(), decimals).toString();
  
  // Use v2 API with Permit2
  const url = `https://api.0x.org/swap/permit2/quote?${new URLSearchParams({
    sellToken: sellAddr,
    buyToken: buyAddr,
    sellAmount,
    chainId: chainId.toString(),
    ...(taker && { taker })
  })}`;
  
  console.log(`Fetching quote from 0x API v2...`);
  console.log(`Chain: ${chain} (${chainId})`);
  console.log(`Sell: ${amount} ${sellToken} -> ${sellAddr}`);
  console.log(`Buy: ${buyToken}`);
  
  try {
    const response = await axios.get(url, {
      headers: { 
        '0x-api-key': apiKey,
        '0x-version': 'v2'
      }
    });
    
    const data = response.data;
    
    console.log('\n=== Quote Results ===');
    console.log(`Price: 1 ${sellToken} = ${Number(data.buyAmount) / Number(data.sellAmount) * (10**(sellToken.toUpperCase() === 'ETH' ? 18 : 6))} ${buyToken}`);
    console.log(`Sell: ${ethers.formatUnits(data.sellAmount, decimals)} ${sellToken}`);
    console.log(`Buy: ${ethers.formatUnits(data.buyAmount, buyToken.toUpperCase() === 'ETH' ? 18 : 6)} ${buyToken}`);
    console.log(`Min buy: ${ethers.formatUnits(data.minBuyAmount, buyToken.toUpperCase() === 'ETH' ? 18 : 6)} ${buyToken}`);
    console.log(`Gas estimate: ${data.gas} units`);
    console.log(`\nTo address: ${data.to}`);
    console.log(`Permit2 data: ${data.permit2 ? 'Included (gasless approval)' : 'Not included'}`);
    
    if (data.issues?.balance?.actual === '0') {
      console.log(`\n⚠️ Warning: Insufficient balance for swap!`);
    }
    if (data.issues?.allowance?.actual === '0') {
      console.log(`⚠️ Warning: Allowance not set. Run approve.js first.`);
    }
    
    return data;
  } catch (err) {
    if (err.response?.data) {
      console.error('API Error:', JSON.stringify(err.response.data, null, 2));
    } else {
      console.error('Error:', err.message);
    }
    throw err;
  }
}

// CLI
const args = process.argv.slice(2);
const params = {};
for (let i = 0; i < args.length; i += 2) {
  const key = args[i].replace('--', '');
  params[key] = args[i + 1];
}

if (!params.sell || !params.buy || !params.amount || !params.chain) {
  console.log('Usage: node quote.js --sell WETH --buy USDC --amount 0.01 --chain base [--taker WALLET]');
  console.log('\nSupported chains:', Object.keys(CHAINS).join(', '));
  console.log('Known tokens: WETH, USDC, DAI');
  console.log('\nExample: node quote.js --sell USDC --buy WETH --amount 1 --chain base --taker 0x...');
  process.exit(1);
}

getQuote(params).catch(e => process.exit(1));
