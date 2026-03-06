#!/usr/bin/env node
const { createPublicClient, http, erc20Abi } = require('viem');
const { privateKeyToAccount } = require('viem/accounts');
const { monadMainnet } = require('./monad-chains');
const { exec } = require('child_process');
const { promisify } = require('util');
const path = require('path');
const os = require('os');
const fs = require('fs').promises;

const execAsync = promisify(exec);
const defaultDataDir = path.join(os.homedir(), 'nadfunagent');

async function loadConfig() {
  const envPath = process.env.NADFUN_ENV_PATH || path.join(defaultDataDir, '.env');
  const envContent = await fs.readFile(envPath, 'utf-8');
  
  const config = {};
  envContent.split('\n').forEach(line => {
    const match = line.match(/^([^=]+)=(.*)$/);
    if (match) {
      config[match[1].trim()] = match[2].trim();
    }
  });
  
  return config;
}

async function checkTokenBalance(publicClient, tokenAddress, walletAddress) {
  try {
    const balance = await publicClient.readContract({
      address: tokenAddress,
      abi: erc20Abi,
      functionName: 'balanceOf',
      args: [walletAddress]
    });
    return balance;
  } catch (error) {
    return 0n;
  }
}

async function fetchAPI(url, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url, {
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'OpenClaw-Agent/1.0'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(r => setTimeout(r, 2000 * (i + 1)));
    }
  }
}

async function main() {
  console.log('🤖 Nad.fun Autonomous Trading - BONDING CURVE FOCUS');
  console.log('⏰ Time:', new Date().toISOString());
  console.log('');
  
  const config = await loadConfig();
  const privateKey = config.MONAD_PRIVATE_KEY;
  const apiUrl = 'https://api.nadapp.net';
  const baseUrl = 'https://nad.fun';
  
  const account = privateKeyToAccount(privateKey);
  const walletAddress = account.address;
  const rpcUrl = config.MONAD_RPC_URL || 'https://monad-mainnet.drpc.org';
  
  const publicClient = createPublicClient({
    chain: monadMainnet,
    transport: http(rpcUrl)
  });
  
  console.log('📊 Wallet:', walletAddress);
  console.log('');
  
  // STEP 1: Check positions using check-pnl.js for proper P&L calculation
  console.log('🔍 STEP 1: Checking positions for sell signals (+5% or -10%)...');
  
  try {
    // Use check-pnl.js which properly reads entry price from positions_report.json
    // and calculates P&L: (currentValueMON - entryValueMON) / entryValueMON * 100
    // With --auto-sell: automatically sells positions with P&L >= +5% or <= -10%
    const checkPnlCmd = `cd "${scriptDir}" && node check-pnl.js --auto-sell`;
    const { stdout: pnlOutput } = await execAsync(checkPnlCmd);
    console.log(pnlOutput);
    
    const sellMatches = pnlOutput.match(/✅ Sold \w+/g);
    const sellCount = sellMatches ? sellMatches.length : 0;
    if (sellCount > 0) {
      console.log(`   ✅ ${sellCount} position(s) sold automatically.`);
    }
    console.log(`   ✅ Position check complete`);
  } catch (error) {
    console.log(`   ⚠️  ${error.message}`);
  }
  
  console.log('');
  
  // STEP 2: Scan markets using multiple methods
  console.log('🔍 STEP 2: Scanning markets for bonding curve tokens...');
  
  const bondingTokens = new Map();
  
  // Method 1: New events
  try {
    const events = await fetchAPI(`${baseUrl}/api/token/new-event`);
    
    for (const event of events) {
      const tokenInfo = event.token_info;
      if (tokenInfo && tokenInfo.is_graduated === false) {
        bondingTokens.set(tokenInfo.token_id, tokenInfo);
      }
    }
    
    console.log(`   Method 1 (New Events): ${bondingTokens.size} bonding tokens`);
  } catch (error) {
    console.log(`   ⚠️  Method 1 failed`);
  }
  
  await new Promise(r => setTimeout(r, 2000));
  
  // Method 2: Creation time API (base64 encoded)
  try {
    const response = await fetch(`${apiUrl}/order/creation_time?page=1&limit=100&is_nsfw=false&direction=DESC`, {
      headers: { 'Accept': 'application/json', 'User-Agent': 'OpenClaw-Agent/1.0' }
    });
    
    const responseText = await response.text();
    const decoded = Buffer.from(responseText, 'base64').toString('utf-8');
    const data = JSON.parse(decoded);
    
    for (const token of data.tokens || []) {
      const tokenInfo = token.token_info;
      if (tokenInfo && tokenInfo.is_graduated === false && tokenInfo.token_id) {
        bondingTokens.set(tokenInfo.token_id, tokenInfo);
      }
    }
    
    console.log(`   Method 2 (Creation Time): ${bondingTokens.size} total bonding tokens`);
  } catch (error) {
    console.log(`   ⚠️  Method 2 failed`);
  }
  
  console.log('');
  
  // STEP 3: Analyze bonding tokens (LOWERED thresholds for early-stage)
  console.log('🔍 STEP 3: Analyzing bonding curve tokens...');
  console.log('   Using relaxed thresholds: liquidity ≥1 MON, holders ≥1');
  console.log('');
  
  const scoredTokens = [];
  
  for (const [tokenId, tokenInfo] of bondingTokens) {
    try {
      const marketData = await fetchAPI(`${apiUrl}/agent/market/${tokenId}`);
      
      const liquidity = parseFloat(marketData.market_info?.reserve_native || 0) / 1e18;
      const holders = parseInt(marketData.market_info?.holder_count || 0);
      const volume = parseFloat(marketData.market_info?.volume || 0) / 1e18;
      const percentChange = parseFloat(marketData.percent || 0);
      const isGraduated = marketData.token_info?.is_graduated;
      
      // Relaxed thresholds for bonding curve (early-stage)
      if (liquidity < 1 || holders < 1) continue;
      
      // CRITICAL: Verify still on bonding curve
      if (isGraduated === true) {
        console.log(`   ⚠️  Skipping ${tokenInfo.symbol}: graduated to DEX`);
        continue;
      }
      
      // Score calculation (adjusted for early-stage)
      let liquidityScore = 0;
      if (liquidity >= 100000) liquidityScore = 100;
      else if (liquidity >= 50000) liquidityScore = 80;
      else if (liquidity >= 10000) liquidityScore = 60;
      else if (liquidity >= 1000) liquidityScore = 40;
      else if (liquidity >= 100) liquidityScore = 20;
      
      let momentumScore = 0;
      if (percentChange >= 50) momentumScore = 100;
      else if (percentChange >= 20) momentumScore = 80;
      else if (percentChange >= 10) momentumScore = 60;
      else if (percentChange >= 5) momentumScore = 40;
      else if (percentChange >= 0) momentumScore = 20;
      
      let volumeScore = 0;
      if (volume >= 100000) volumeScore = 100;
      else if (volume >= 50000) volumeScore = 80;
      else if (volume >= 10000) volumeScore = 60;
      else if (volume >= 1000) volumeScore = 40;
      else if (volume >= 100) volumeScore = 20;
      
      let holderScore = 0;
      if (holders >= 100) holderScore = 100;
      else if (holders >= 50) holderScore = 80;
      else if (holders >= 10) holderScore = 60;
      else if (holders >= 5) holderScore = 40;
      else if (holders >= 1) holderScore = 20;
      
      const totalScore = Math.round(
        liquidityScore * 0.35 +
        momentumScore * 0.20 +
        volumeScore * 0.25 +
        holderScore * 0.10 +
        10 * 0.10
      );
      
      scoredTokens.push({
        address: tokenId,
        symbol: tokenInfo.symbol || 'UNKNOWN',
        liquidity,
        holders,
        volume,
        percentChange,
        score: totalScore
      });
      
      await new Promise(r => setTimeout(r, 400));
    } catch (error) {
      // Skip
    }
  }
  
  scoredTokens.sort((a, b) => b.score - a.score);
  
  console.log(`   Analyzed: ${scoredTokens.length} bonding curve tokens`);
  console.log('');
  
  // Print top 10
  console.log('📊 TOP BONDING CURVE TOKENS:');
  for (const token of scoredTokens.slice(0, 10)) {
    console.log(`   ${token.symbol}: Score ${token.score} | ${token.liquidity.toFixed(0)} MON | ${token.holders}H | Vol ${token.volume.toFixed(0)} | ${token.percentChange >= 0 ? '+' : ''}${token.percentChange.toFixed(1)}%`);
  }
  console.log('');
  
  // STEP 4: Buy top 5 scoring ≥50
  console.log('🔍 STEP 4: Executing buy orders (score ≥50, top 5)...');
  
  const buyTargets = scoredTokens.filter(t => t.score >= 50).slice(0, 5);
  
  if (buyTargets.length === 0) {
    console.log('   ❌ No bonding curve tokens scored ≥50');
  } else {
    console.log(`   Buying ${buyTargets.length} tokens:`);
    console.log('');
    
    for (const target of buyTargets) {
      console.log(`   💰 ${target.symbol} | Score ${target.score} | ${target.liquidity.toFixed(0)} MON liquidity`);
      
      const buyCmd = `cd "${scriptDir}" && NAD_PRIVATE_KEY=${privateKey} node buy-token.js ${target.address} 0.15 --slippage=300`;
      
      try {
        const { stdout } = await execAsync(buyCmd);
        console.log(stdout);
        
        await new Promise(r => setTimeout(r, 3000));
        const balance = await checkTokenBalance(publicClient, target.address, walletAddress);
        
        if (balance > 0n) {
          console.log(`   ✅ On-chain verified: ${(Number(balance) / 1e18).toFixed(2)} tokens`);
        }
      } catch (error) {
        console.log(`   ❌ ${error.message}`);
      }
      
      await new Promise(r => setTimeout(r, 3000));
    }
  }
  
  console.log('');
  
  // STEP 5: Final portfolio with P&L
  console.log('📊 STEP 4: Final Portfolio');
  try {
    const finalPnlCmd = `cd "${scriptDir}" && node check-pnl.js`;
    const { stdout: finalOutput } = await execAsync(finalPnlCmd);
    
    // Extract positions from output
    const lines = finalOutput.split('\n');
    const positions = [];
    let totalInvested = 0;
    
    for (const line of lines) {
      // Format: "SYMBOL: balance tokens | currentValue MON | Entry: entryValue MON | P&L +/-X% (source) | ACTION"
      const match = line.match(/(\w+):\s+([\d.]+)\s+tokens\s+\|\s+([\d.]+)\s+MON\s+\|\s+Entry:\s+([\d.]+)\s+MON\s+\|\s+P&L\s+([+-]?[\d.]+)%/);
      if (match) {
        const [, symbol, balance, currentValue, entryValue, pnl] = match;
        positions.push({
          symbol,
          balance: parseFloat(balance),
          currentValueMON: parseFloat(currentValue),
          entryValueMON: parseFloat(entryValue),
          pnlPercent: parseFloat(pnl)
        });
        totalInvested += parseFloat(entryValue);
      }
    }
    
    if (positions.length > 0) {
      console.log('');
      for (const pos of positions) {
        const pnlStr = pos.pnlPercent >= 0 ? `+${pos.pnlPercent.toFixed(2)}%` : `${pos.pnlPercent.toFixed(2)}%`;
        console.log(`${pos.symbol}: ${pos.balance.toFixed(2)} tokens | ${pos.currentValueMON.toFixed(4)} MON value | P&L: ${pnlStr}`);
      }
      console.log(`Total Invested This Cycle: ${totalInvested.toFixed(2)} MON`);
      console.log(`Active Positions: ${positions.length} tokens`);
    } else {
      console.log('   (Run check-pnl.js separately for detailed P&L)');
    }
  } catch (error) {
    console.log(`   ⚠️  Could not generate final portfolio: ${error.message}`);
  }
  
  console.log('');
  console.log('✅ Trading cycle complete!');
  console.log('');
  console.log('📊 SUMMARY:');
  console.log(`   Wallet: ${walletAddress}`);
  console.log(`   Bonding tokens scanned: ${bondingTokens.size}`);
  console.log(`   Bonding tokens analyzed: ${scoredTokens.length}`);
  console.log(`   Buy orders: ${buyTargets.length}`);
}

main().catch(console.error);
