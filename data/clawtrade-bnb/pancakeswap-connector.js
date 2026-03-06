#!/usr/bin/env node
/**
 * PancakeSwap Testnet Pool Finder
 * Connects to BNB testnet and searches for active pools
 */

const { ethers } = require('ethers');
const fs = require('fs');

// BNB Testnet config
const RPC_URL = 'https://bsc-testnet.publicnode.com';
const PANCAKESWAP_ROUTER_ADDRESS = '0xD99D0BC5273d5aeB3f8b81e34e64bF1b92ac1d5a'; // PancakeSwap Router V2 (testnet)
const PANCAKESWAP_FACTORY_ADDRESS = '0x6725f303b657a9451d8ba641348b6761a6cc7a17'; // PancakeSwap Factory (testnet)

// Common tokens on BNB testnet
const TOKENS = {
  WBNB: '0xae13d989dac2f0debff460ac112a837c89baa7cd',
  BUSD: '0xed24fc36f5ee211ea25a531cc15a9fa7d331875c',
  USDT: '0x337610d27c682e347c9cd60bd4b3b107c9d34ddf',
  USDC: '0x64544969541e58c3dffc53b36177417e3798f8f2',
  ETH: '0x8ba1f109551bd432803012645ac136ddd64dba72',
  LINK: '0x84b9b910527ad5c03a9ca831909e21e236ea7b06',
};

// Factory ABI (minimal for getting pairs)
const FACTORY_ABI = [
  'function getPair(address tokenA, address tokenB) external view returns (address pair)',
  'function allPairs(uint) external view returns (address)',
  'function allPairsLength() external view returns (uint)',
];

// Pair ABI (minimal for getting reserves)
const PAIR_ABI = [
  'function getReserves() external view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast)',
  'function token0() external view returns (address)',
  'function token1() external view returns (address)',
  'function balanceOf(address) external view returns (uint)',
];

// ERC20 ABI (minimal)
const ERC20_ABI = [
  'function decimals() external view returns (uint8)',
  'function symbol() external view returns (string)',
  'function name() external view returns (string)',
];

async function findActivePools() {
  console.log(`
╔════════════════════════════════════════════════════════╗
║  PancakeSwap Testnet Pool Finder                       ║
╠════════════════════════════════════════════════════════╣
║  Network: BNB Testnet (Chain ID: 97)                  ║
║  RPC: ${RPC_URL.slice(0, 40)}...
║  Factory: ${PANCAKESWAP_FACTORY_ADDRESS.slice(0, 10)}...${PANCAKESWAP_FACTORY_ADDRESS.slice(-8)}
╚════════════════════════════════════════════════════════╝
  `);

  const provider = new ethers.providers.JsonRpcProvider(RPC_URL);
  const factory = new ethers.Contract(PANCAKESWAP_FACTORY_ADDRESS, FACTORY_ABI, provider);

  try {
    console.log('🔍 Scanning for active pools...\n');

    const activePools = [];

    // Check common token pairs
    const tokenPairs = [
      ['WBNB', 'BUSD'],
      ['WBNB', 'USDT'],
      ['WBNB', 'USDC'],
      ['WBNB', 'ETH'],
      ['WBNB', 'LINK'],
      ['BUSD', 'USDT'],
      ['ETH', 'USDT'],
    ];

    for (const [token1, token2] of tokenPairs) {
      const addr1 = TOKENS[token1];
      const addr2 = TOKENS[token2];

      if (!addr1 || !addr2) {
        console.log(`⚠️  Token not found: ${token1} or ${token2}`);
        continue;
      }

      try {
        const pairAddress = await factory.getPair(addr1, addr2);

        if (pairAddress && pairAddress !== '0x0000000000000000000000000000000000000000') {
          console.log(`✓ Found pair: ${token1}-${token2}`);
          console.log(`  Address: ${pairAddress}`);

          // Get reserves
          const pair = new ethers.Contract(pairAddress, PAIR_ABI, provider);
          const [reserve0, reserve1] = await pair.getReserves();

          // Get token info
          const token0 = new ethers.Contract(addr1, ERC20_ABI, provider);
          const token1Contract = new ethers.Contract(addr2, ERC20_ABI, provider);

          const symbol0 = await token0.symbol();
          const symbol1 = await token1Contract.symbol();
          const decimals0 = await token0.decimals();
          const decimals1 = await token1Contract.decimals();

          const normalizedReserve0 = ethers.utils.formatUnits(reserve0, decimals0);
          const normalizedReserve1 = ethers.utils.formatUnits(reserve1, decimals1);

          console.log(`  Liquidity: ${normalizedReserve0.slice(0, 10)} ${symbol0} / ${normalizedReserve1.slice(0, 10)} ${symbol1}`);

          activePools.push({
            pair: `${token1}-${token2}`,
            address: pairAddress,
            token0: addr1,
            token1: addr2,
            symbol0,
            symbol1,
            reserve0: reserve0.toString(),
            reserve1: reserve1.toString(),
          });

          console.log();
        }
      } catch (err) {
        console.log(`⚠️  Error checking ${token1}-${token2}: ${err.message.slice(0, 50)}`);
      }
    }

    if (activePools.length > 0) {
      console.log(`\n📊 Found ${activePools.length} active pools\n`);

      // Save to file
      const poolFile = './pancakeswap-pools.json';
      fs.writeFileSync(poolFile, JSON.stringify(activePools, null, 2));
      console.log(`✅ Saved to: ${poolFile}\n`);

      // Display top recommendation
      console.log('🎯 Recommended pool for agent:');
      const topPool = activePools[0];
      console.log(`   Pair: ${topPool.pair}`);
      console.log(`   Address: ${topPool.address}`);
      console.log(`   Token0: ${topPool.symbol0}`);
      console.log(`   Token1: ${topPool.symbol1}\n`);

      return activePools;
    } else {
      console.log('❌ No active pools found');
      return [];
    }
  } catch (error) {
    console.error('❌ Error:', error.message);
    return [];
  }
}

// Run
if (require.main === module) {
  findActivePools().then(pools => {
    if (pools.length > 0) {
      console.log('Next step: Update config.scheduler.json with pool address');
    }
  }).catch(err => console.error('Fatal:', err));
}

module.exports = { findActivePools };
