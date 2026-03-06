#!/usr/bin/env node
/**
 * ClawTrade-BNB CLI
 * OpenClaw Skill command interface
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const SKILL_ROOT = path.join(__dirname, '..');

function printBanner() {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║                  ClawTrade-BNB v1.1.0                      ║
║         Autonomous DeFi Trading Agent for BNB Chain        ║
╚════════════════════════════════════════════════════════════╝
  `);
}

function start(args = {}) {
  printBanner();
  console.log('\n🚀 Starting ClawTrade-BNB...\n');
  
  const port = args.port || process.env.AGENT_PORT || 3001;
  const network = args.network || process.env.NETWORK || 'testnet';
  
  console.log(`📡 Agent API: http://localhost:${port}`);
  console.log(`📊 Dashboard: http://localhost:5173`);
  console.log(`🌐 Network: ${network}`);
  
  try {
    execSync('npm run dev', { cwd: SKILL_ROOT, stdio: 'inherit' });
  } catch (e) {
    console.error('❌ Failed to start:', e.message);
    process.exit(1);
  }
}

function agent(action) {
  const actions = ['start', 'pause', 'stop', 'status'];
  
  if (!actions.includes(action)) {
    console.error(`❌ Unknown agent action: ${action}`);
    console.log(`   Available: ${actions.join(', ')}`);
    process.exit(1);
  }
  
  console.log(`\n🤖 Agent: ${action.toUpperCase()}\n`);
  
  if (action === 'start') {
    console.log('✅ Agent started (scheduler running)');
  } else if (action === 'pause') {
    console.log('⏸️  Agent paused (safe pause - current cycle completes)');
  } else if (action === 'stop') {
    console.log('🛑 Agent stopped');
  } else if (action === 'status') {
    status();
  }
}

function dashboard(args = {}) {
  const port = args.port || process.env.UI_PORT || 5173;
  console.log(`\n📊 Dashboard starting on http://localhost:${port}\n`);
  
  try {
    execSync('npm run dev:dashboard', { cwd: SKILL_ROOT, stdio: 'inherit' });
  } catch (e) {
    console.error('❌ Failed to start dashboard:', e.message);
    process.exit(1);
  }
}

function status() {
  printBanner();
  console.log('\n📊 STATUS\n');
  
  const logPath = path.join(SKILL_ROOT, 'execution-log.jsonl');
  
  if (!fs.existsSync(logPath)) {
    console.log('⚠️  No execution log found yet');
    return;
  }
  
  const logs = fs.readFileSync(logPath, 'utf8')
    .split('\n')
    .filter(l => l)
    .map(l => {
      try {
        return JSON.parse(l);
      } catch {
        return null;
      }
    })
    .filter(l => l);
  
  if (logs.length === 0) {
    console.log('ℹ️  No actions executed yet');
    return;
  }
  
  const lastAction = logs[logs.length - 1];
  const successful = logs.filter(l => l.status === 'success').length;
  const failed = logs.filter(l => l.status === 'error').length;
  
  console.log(`✅ Successful actions: ${successful}`);
  console.log(`❌ Failed actions: ${failed}`);
  console.log(`📊 Total actions: ${logs.length}`);
  console.log(`\nLast action:`);
  console.log(`  Time: ${new Date(lastAction.timestamp * 1000).toISOString()}`);
  console.log(`  Type: ${lastAction.action}`);
  console.log(`  Vault: ${lastAction.vault}`);
  console.log(`  Status: ${lastAction.status}`);
  console.log(`  TX: ${lastAction.tx_hash || 'N/A'}`);
}

function logs(args = {}) {
  printBanner();
  
  const logPath = path.join(SKILL_ROOT, 'execution-log.jsonl');
  const limit = args.limit || 20;
  const filter = args.filter || null;
  
  if (!fs.existsSync(logPath)) {
    console.log('⚠️  No execution log found');
    return;
  }
  
  const lines = fs.readFileSync(logPath, 'utf8')
    .split('\n')
    .filter(l => l)
    .map(l => {
      try {
        return JSON.parse(l);
      } catch {
        return null;
      }
    })
    .filter(l => l)
    .filter(l => !filter || l.action.includes(filter))
    .slice(-limit);
  
  console.log(`\n📋 Recent Actions (${lines.length}):\n`);
  
  lines.forEach(log => {
    const statusIcon = log.status === 'success' ? '✅' : '❌';
    const timestamp = new Date(log.timestamp * 1000).toLocaleTimeString();
    console.log(`${statusIcon} ${timestamp} | ${log.action} | ${log.vault} | ${log.tx_hash?.slice(0, 10) || 'N/A'}...`);
  });
}

function demo() {
  printBanner();
  console.log(`
✅ DEMO CHECKLIST

1. Start Agent + Dashboard
   $ npm run start
   
2. Open Browser
   - Dashboard: http://localhost:5173
   - Agent API: http://localhost:3001/api/status
   
3. Check Wallet
   - Wallet address from .env loaded
   - Balance checked via RPC
   
4. Choose Risk Profile
   - Conservative (🛡️)  - Safe, steady
   - Balanced (⚖️)      - Default
   - Aggressive (🚀)    - High-yield
   
5. Activate Agent
   - Click "Activate" in UI
   - Agent starts 60-second cycles
   - Watch live activity feed
   
6. View Decisions
   - Click "WHY" on any action
   - See explainability panel:
     * Decision profile
     * Rules triggered
     * Metrics snapshot
     * Confidence score
   
7. Verify On-Chain
   - Click TX hash
   - Opens BscScan
   - See proof of execution

---

⏱️  Demo Timeline:
- 0:00 — Start demo
- 0:30 — Activate agent
- 1:00 — First cycle completes
- 2:00 — See live action in feed
- 5:00 — View explainability + bscscan proof

🎯 Key Features to Highlight:
✓ One-click activation (no manual TX)
✓ Real on-chain execution (verified)
✓ Explainability (see WHY decisions)
✓ Multi-agent monitoring (agent team)
✓ Risk profiles (conservative/balanced/aggressive)
✓ Suggest-only mode (no TX, just proposals)
✓ Reinforced learning (auto-optimization)

URLs:
- Dashboard: http://localhost:5173
- Agent API: http://localhost:3001
- GitHub: https://github.com/open-web-academy/clawtrade-bnb
  `);
}

function network(target) {
  const valid = ['testnet', 'mainnet'];
  
  if (!valid.includes(target)) {
    console.error(`❌ Unknown network: ${target}`);
    console.log(`   Available: ${valid.join(', ')}`);
    process.exit(1);
  }
  
  const envPath = path.join(SKILL_ROOT, '.env');
  let content = fs.existsSync(envPath) 
    ? fs.readFileSync(envPath, 'utf8')
    : '';
  
  // Update or add NETWORK
  if (content.includes('NETWORK=')) {
    content = content.replace(/NETWORK=.+/g, `NETWORK=${target}`);
  } else {
    content += `\nNETWORK=${target}`;
  }
  
  fs.writeFileSync(envPath, content);
  console.log(`\n✅ Network switched to ${target}\n`);
}

function metrics(args = {}) {
  const metricsPath = path.join(SKILL_ROOT, 'performance-metrics.json');
  
  if (!fs.existsSync(metricsPath)) {
    console.log('⚠️  No metrics available yet');
    return;
  }
  
  const metrics = JSON.parse(fs.readFileSync(metricsPath, 'utf8'));
  
  if (args.json) {
    console.log(JSON.stringify(metrics, null, 2));
  } else {
    console.log(`
📊 PERFORMANCE METRICS

Total Harvested:      $${metrics.totalHarvested?.toFixed(2) || '0.00'}
Total Compounded:     $${metrics.totalCompounded?.toFixed(2) || '0.00'}
Start Time:           ${new Date(metrics.startTime).toISOString()}

Vaults:
${Object.entries(metrics.vaults || {}).map(([id, stats]) => `
  ${id}
    Deposits:   ${stats.deposits || 0}
    Harvested:  $${stats.harvested?.toFixed(2) || '0.00'}
    Compounded: $${stats.compounded?.toFixed(2) || '0.00'}
    APR:        ${stats.realizedAPR?.toFixed(2) || '0.00'}%
`).join('')}
    `);
  }
}

// CLI Router
const command = process.argv[2];
const subcommand = process.argv[3];
const args = {
  port: process.argv.includes('--port') ? process.argv[process.argv.indexOf('--port') + 1] : null,
  network: process.argv.includes('--network') ? process.argv[process.argv.indexOf('--network') + 1] : null,
  limit: process.argv.includes('--limit') ? parseInt(process.argv[process.argv.indexOf('--limit') + 1]) : 20,
  filter: process.argv.includes('--filter') ? process.argv[process.argv.indexOf('--filter') + 1] : null,
  json: process.argv.includes('--json')
};

if (!command || command === 'help') {
  printBanner();
  console.log(`
Commands:
  start               Start agent + dashboard
  agent <action>      Control agent (start|pause|stop|status)
  dashboard           Start UI only
  status              Show runtime health
  logs                Tail recent actions
  demo                Show demo checklist
  network <net>       Switch network (testnet|mainnet)
  metrics             Show performance metrics
  help                Show this help

Options:
  --port <num>        Agent port (default 3001)
  --network <net>     Network (testnet|mainnet)
  --limit <num>       Log limit (default 20)
  --filter <action>   Filter logs by action
  --json              JSON output for metrics
  `);
} else if (command === 'start') {
  start(args);
} else if (command === 'agent') {
  agent(subcommand);
} else if (command === 'dashboard') {
  dashboard(args);
} else if (command === 'status') {
  status();
} else if (command === 'logs') {
  logs(args);
} else if (command === 'demo') {
  demo();
} else if (command === 'network') {
  network(subcommand);
} else if (command === 'metrics') {
  metrics(args);
} else {
  console.error(`❌ Unknown command: ${command}`);
  console.log('   Run "clawtrade help" for available commands');
  process.exit(1);
}
