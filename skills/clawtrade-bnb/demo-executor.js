#!/usr/bin/env node
/**
 * Demo Executor
 * Simulates real decision cycles with actual vault data
 * Generates execution events every 30 seconds
 */

const fs = require('fs');
const path = require('path');
const { ethers } = require('ethers');

// Load configuration
const deployedConfig = JSON.parse(fs.readFileSync('./config.deployed.json', 'utf8'));
const schedulerConfig = JSON.parse(fs.readFileSync('./config.scheduler.json', 'utf8'));

// Parse .env file
const envPath = path.join(__dirname, '.env');
let envConfig = {};
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf8');
  envContent.split('\n').forEach(line => {
    const [key, val] = line.split('=');
    if (key && val) envConfig[key.trim()] = val.trim();
  });
}

const RPC_URL = envConfig.RPC_URL || deployedConfig.rpc;
const PRIVATE_KEY = envConfig.PRIVATE_KEY;

// Initialize provider and wallet
const provider = new ethers.providers.JsonRpcProvider(RPC_URL);
const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

console.log(`
╔════════════════════════════════════════════════════════╗
║  Yield Farming Agent - Demo Executor (Real Data)       ║
╠════════════════════════════════════════════════════════╣
║  Wallet: ${wallet.address.slice(0, 10)}...${wallet.address.slice(-8)}
║  Network: ${deployedConfig.network}
║  Vaults: ${deployedConfig.contracts.length}
║  Cycle Interval: ${schedulerConfig.scheduler.execution_interval_seconds}s
╚════════════════════════════════════════════════════════╝
`);

const ACTIONS = ['DEPOSIT', 'WITHDRAW', 'HARVEST', 'COMPOUND', 'REBALANCE', 'NOOP'];
const logFile = path.join(__dirname, 'execution-log.jsonl');

// Calculate net APR for a vault
function calculateNetAPR(vault) {
  const baseAPR = vault.apr || 10;
  const fees = vault.fees || 0.5;
  const riskPenalty = (vault.risk_score || 0.3) * 0.10;
  return baseAPR - fees - riskPenalty;
}

// Generate decision based on vault metrics
function generateDecision(vault, idx) {
  const netAPR = calculateNetAPR(vault);
  const randomConfidence = 0.75 + Math.random() * 0.25;
  
  let action = 'NOOP';
  let reason = 'Stable vault, no action needed';

  if (netAPR > 12) {
    action = idx % 3 === 0 ? 'DEPOSIT' : 'COMPOUND';
    reason = `High APR (${netAPR.toFixed(2)}%) - ${action.toLowerCase()}`;
  } else if (netAPR < 5) {
    action = 'HARVEST';
    reason = `Low APR (${netAPR.toFixed(2)}%) - harvest rewards`;
  } else if (vault.risk_score > schedulerConfig.agent.risk_threshold) {
    action = 'REBALANCE';
    reason = `High risk score (${vault.risk_score}) exceeds threshold`;
  }

  return {
    action,
    reason,
    confidence: parseFloat(randomConfidence.toFixed(2)),
    netAPR: parseFloat(netAPR.toFixed(2))
  };
}

// Append execution record to log
function logExecution(cycle) {
  const record = JSON.stringify(cycle);
  fs.appendFileSync(logFile, record + '\n');
  console.log(`✓ [${new Date(cycle.timestamp * 1000).toISOString()}] ${cycle.action} on ${cycle.vault_id}`);
}

// Execute one cycle
async function executeCycle() {
  try {
    const cycleNum = fs.existsSync(logFile) 
      ? fs.readFileSync(logFile, 'utf8').split('\n').filter(l => l).length + 1
      : 1;

    const timestamp = Math.floor(Date.now() / 1000);
    
    console.log(`\n📊 Execution Cycle #${cycleNum} @ ${new Date(timestamp * 1000).toISOString()}`);
    
    // Process each vault
    for (let i = 0; i < deployedConfig.contracts.length; i++) {
      const contract = deployedConfig.contracts[i];
      const vaultConfig = schedulerConfig.vaults.find(v => v.id === contract.vaultId) || contract;

      const decision = generateDecision(vaultConfig, i);
      
      // Generate transaction hash (simulated)
      const txHash = '0x' + require('crypto').randomBytes(32).toString('hex');
      
      const record = {
        cycle: cycleNum,
        timestamp,
        vault_id: contract.vaultId,
        vault_name: contract.name,
        action: decision.action,
        reason: decision.reason,
        confidence: decision.confidence,
        net_apr: decision.netAPR,
        risk_score: vaultConfig.risk_score,
        tx_hash: decision.action !== 'NOOP' ? txHash : null,
        state_hash: '0x' + require('crypto').randomBytes(32).toString('hex').slice(0, 16),
        status: 'success',
        gas_used: Math.floor(Math.random() * 300000) + 50000,
        gas_price_gwei: 5 + Math.random() * 10,
        execution_time_ms: Math.floor(Math.random() * 5000) + 500
      };

      logExecution(record);
    }

    console.log(`✅ Cycle #${cycleNum} completed with ${deployedConfig.contracts.length} vault decisions`);

  } catch (error) {
    console.error('❌ Cycle error:', error.message);
    logExecution({
      timestamp: Math.floor(Date.now() / 1000),
      action: 'ERROR',
      vault_id: 'scheduler',
      error: error.message,
      state_hash: '0xERROR'
    });
  }
}

// Main loop
async function start() {
  console.log(`🚀 Starting demo executor (cycles every ${schedulerConfig.scheduler.execution_interval_seconds}s)...\n`);

  // Execute immediately first
  await executeCycle();

  // Then schedule
  setInterval(executeCycle, schedulerConfig.scheduler.execution_interval_seconds * 1000);
}

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\n🛑 Shutting down demo executor...');
  console.log(`📊 Execution log: ${logFile}`);
  console.log(`📈 Total events logged: ${fs.existsSync(logFile) ? fs.readFileSync(logFile, 'utf8').split('\n').filter(l => l).length : 0}`);
  process.exit(0);
});

// Start if running directly
if (require.main === module) {
  start().catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
  });
}

module.exports = { executeCycle };
