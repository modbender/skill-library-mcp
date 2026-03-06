#!/usr/bin/env node
/**
 * PancakeSwap Autonomous Agent
 * Monitors pool metrics and executes real swaps based on APR/slippage
 */

const fs = require('fs');
const PancakeSwapReader = require('./pancakeswap-reader');
const PancakeSwapExecutor = require('./pancakeswap-executor');

// Config
const POOL_ADDRESS = '0x51a92448E8D1360B84589E1255aadAb4e685811C'; // WBNB-LINK
const TOKEN0 = '0xae13d989dac2f0debff460ac112a837c89baa7cd'; // WBNB
const TOKEN1 = '0x84b9b910527ad5c03a9ca831909e21e236ea7b06'; // LINK

// Load env
const envPath = './.env';
let envConfig = {};
if (fs.existsSync(envPath)) {
  const content = fs.readFileSync(envPath, 'utf8');
  content.split('\n').forEach(line => {
    const [key, val] = line.split('=');
    if (key && val) envConfig[key.trim()] = val.trim();
  });
}

const PRIVATE_KEY = envConfig.PRIVATE_KEY;

// Decision thresholds
const MIN_APR = 5;
const MAX_SLIPPAGE = 2;
const SWAP_AMOUNT = 0.01; // 0.01 BNB per trade

let cycleCount = 0;

async function analyzePool() {
  try {
    const reader = new PancakeSwapReader(POOL_ADDRESS);
    await reader.initialize();

    console.log('\n📊 PancakeSwap Pool Analysis');
    console.log('═'.repeat(50));

    // Get pool data
    const poolData = await reader.getPoolData();
    if (!poolData) {
      console.log('❌ Failed to read pool data');
      return null;
    }

    console.log(`\nPool: ${poolData.symbol0}-${poolData.symbol1}`);
    console.log(`Liquidity:`);
    console.log(`  ${poolData.symbol0}: ${poolData.normalizedReserve0.toFixed(4)}`);
    console.log(`  ${poolData.symbol1}: ${poolData.normalizedReserve1.toFixed(6)}`);

    // Get price
    const priceData = await reader.calculatePrice();
    console.log(`\nPrice:`);
    console.log(`  1 ${poolData.symbol1} = ${priceData.price.toFixed(6)} ${poolData.symbol0}`);
    console.log(`  1 ${poolData.symbol0} = ${priceData.inverse.toFixed(6)} ${poolData.symbol1}`);

    // Get APR
    const aprData = await reader.calculateAPR();
    console.log(`\nAPR Analysis:`);
    console.log(`  Estimated APR: ${aprData.apr.toFixed(2)}%`);
    console.log(`  Daily Volume: ${aprData.estimatedDailyVolume.toFixed(2)}`);
    console.log(`  Daily Fees: ${aprData.dailyFees.toFixed(6)} ${poolData.symbol0}`);
    console.log(`  Pool TVL: ${aprData.tvl.toFixed(2)} ${poolData.symbol0}`);

    // Get slippage for test trade
    const slippageData = await reader.getSlippage(SWAP_AMOUNT, true);
    console.log(`\nSlippage Analysis (${SWAP_AMOUNT} ${poolData.symbol0}):`);
    console.log(`  Amount Out: ${slippageData.amountOut.toFixed(6)} ${poolData.symbol1}`);
    console.log(`  Slippage: ${slippageData.slippage.toFixed(2)}%`);
    console.log(`  Price Impact: ${slippageData.priceImpact.toFixed(2)}%`);

    // Make decision
    console.log('\n🤖 Decision Logic:');
    let decision = 'HOLD';
    let reason = [];

    if (aprData.apr < MIN_APR) {
      reason.push(`Low APR (${aprData.apr.toFixed(2)}% < ${MIN_APR}%)`);
    } else {
      reason.push(`✓ Good APR (${aprData.apr.toFixed(2)}%)`);
      decision = 'EXECUTE';
    }

    if (slippageData.slippage > MAX_SLIPPAGE) {
      reason.push(`High slippage (${slippageData.slippage.toFixed(2)}% > ${MAX_SLIPPAGE}%)`);
      decision = 'HOLD';
    } else {
      reason.push(`✓ Low slippage (${slippageData.slippage.toFixed(2)}%)`);
    }

    console.log(`  ${reason.join(' | ')}`);
    console.log(`  ➜ Decision: ${decision}`);

    return {
      decision,
      reason: reason.join(' | '),
      poolData,
      priceData,
      aprData,
      slippageData,
    };

  } catch (error) {
    console.error('❌ Analysis error:', error.message);
    return null;
  }
}

async function executeCycle() {
  cycleCount++;
  console.log(`\n${'═'.repeat(60)}`);
  console.log(`Cycle #${cycleCount} @ ${new Date().toISOString()}`);
  console.log(`${'═'.repeat(60)}`);

  const analysis = await analyzePool();
  if (!analysis) return;

  if (analysis.decision === 'EXECUTE') {
    console.log('\n⚡ Executing real swap...');
    
    try {
      const executor = new PancakeSwapExecutor(PRIVATE_KEY, POOL_ADDRESS, TOKEN0, TOKEN1);
      
      // Calculate min output with 1% slippage tolerance
      const minAmountOut = analysis.slippageData.amountOut * 0.99;
      
      console.log(`\n💼 Swap Details:`);
      console.log(`  Input: ${SWAP_AMOUNT} WBNB`);
      console.log(`  Expected: ${analysis.slippageData.amountOut.toFixed(6)} LINK`);
      console.log(`  Min Output (1% slippage): ${minAmountOut.toFixed(6)} LINK`);
      
      // Execute
      const result = await executor.executeSwap(SWAP_AMOUNT, minAmountOut, true);
      console.log(`\n✅ Swap completed successfully!`);
      console.log(`  TX: https://testnet.bscscan.com/tx/${result.tx_hash}`);
      
    } catch (error) {
      console.error(`\n❌ Execution error: ${error.message}`);
    }
  } else {
    console.log('\n⏸️ Holding position (unfavorable market conditions)');
  }
}

// Main
async function start() {
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║  PancakeSwap Autonomous Agent                             ║
╠═══════════════════════════════════════════════════════════╣
║  Pool: WBNB-LINK (${POOL_ADDRESS.slice(0,10)}...)
║  Strategy: Monitor APR & execute profitable swaps         ║
║  Cycle Interval: 60 seconds                               ║
╚═══════════════════════════════════════════════════════════╝
  `);

  if (!PRIVATE_KEY) {
    console.error('❌ PRIVATE_KEY not found in .env');
    process.exit(1);
  }

  // Execute immediately
  await executeCycle();

  // Schedule
  setInterval(executeCycle, 60000);
}

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\n🛑 Shutting down...');
  console.log(`📊 Total cycles executed: ${cycleCount}`);
  process.exit(0);
});

if (require.main === module) {
  start().catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
  });
}

module.exports = { executeCycle };
