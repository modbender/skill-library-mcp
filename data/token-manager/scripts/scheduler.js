#!/usr/bin/env node
/**
 * Token Scheduler - Scheduled Monitoring & Alerts
 * 
 * Auto-checks balance and sends proactive alerts when thresholds are met.
 * 
 * Security Notice:
 * - Reads API keys from environment variables only
 * - Stores alert state locally in .data/
 * - Sends messages only to configured channels (no external data leak)
 */

const fs = require('fs');
const path = require('path');
const { queryBalance } = require('./manager.js');

const DATA_DIR = path.join(__dirname, '..', '.data');
const ALERT_STATE_FILE = path.join(DATA_DIR, 'alert-state.json');

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

// Load alert state
function loadState() {
  try {
    if (fs.existsSync(ALERT_STATE_FILE)) {
      return JSON.parse(fs.readFileSync(ALERT_STATE_FILE, 'utf8'));
    }
  } catch (e) {}
  return { 
    lastAlert: null, 
    alertCount: 0,
    lastBalance: null,
    history: []
  };
}

function saveState(state) {
  fs.writeFileSync(ALERT_STATE_FILE, JSON.stringify(state, null, 2));
}

// Format alert message
function formatAlert(balance, threshold, provider) {
  const emoji = balance < 1 ? '🚨' : balance < threshold ? '⚠️' : '💡';
  const urgency = balance < 1 ? 'URGENT' : balance < threshold ? 'WARNING' : 'NOTICE';
  
  return {
    en: `${emoji} [${urgency}] Token Manager Alert
Provider: ${provider}
Current Balance: ¥${balance.toFixed(2)}
Threshold: ¥${threshold}

Recommendations:
${balance < 1 ? '- Add funds immediately' : '- Consider adding funds'}
- Enable save mode: /thinking off
- Use sub-agents for large tasks
- Switch to cheaper models (GPT-4o-mini, Claude Haiku)`,
    
    cn: `${emoji} [${urgency === 'URGENT' ? '紧急' : urgency === 'WARNING' ? '警告' : '提醒'}] Token 管家提醒
提供商: ${provider}
当前余额: ¥${balance.toFixed(2)}
阈值: ¥${threshold}

建议:
${balance < 1 ? '- 立即充值' : '- 考虑充值'}
- 开启省钱模式: /thinking off
- 大任务使用子代理
- 切换到更便宜的模型 (GPT-4o-mini, Claude Haiku)`
  };
}

// Check balance and alert if needed
async function checkAndAlert(provider, threshold) {
  const state = loadState();
  const apiKey = process.env.MOONSHOT_API_KEY || 
                 process.env.OPENAI_API_KEY || 
                 process.env.ANTHROPIC_API_KEY;
  
  if (!apiKey) {
    return { 
      success: false, 
      error: 'No API key found in environment variables' 
    };
  }
  
  const balance = await queryBalance(provider, apiKey);
  
  if (!balance.success) {
    return { 
      success: false, 
      error: balance.error 
    };
  }
  
  // Record history
  state.history.push({
    timestamp: new Date().toISOString(),
    provider,
    balance: balance.balance
  });
  
  // Keep only last 30 days
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
  state.history = state.history.filter(h => new Date(h.timestamp) > thirtyDaysAgo);
  
  const currentBalance = balance.balance;
  const shouldAlert = currentBalance < threshold;
  
  // Cooldown logic: 1 hour for normal, 30 min for urgent
  const now = Date.now();
  const cooldownMs = currentBalance < 1 ? 1800000 : 3600000; // 30 min or 1 hour
  const alreadyAlerted = state.lastAlert && 
    (now - new Date(state.lastAlert).getTime()) < cooldownMs;
  
  if (shouldAlert && !alreadyAlerted) {
    const alertMsg = formatAlert(currentBalance, threshold, provider);
    
    // Update state
    state.lastAlert = new Date().toISOString();
    state.alertCount++;
    state.lastBalance = currentBalance;
    saveState(state);
    
    return {
      success: true,
      alert: true,
      balance: currentBalance,
      threshold: threshold,
      provider: provider,
      messages: alertMsg,
      action: currentBalance < 1 ? 'urgent' : 'warning'
    };
  }
  
  // Save state even if no alert
  state.lastBalance = currentBalance;
  saveState(state);
  
  return { 
    success: true, 
    alert: false, 
    balance: currentBalance,
    provider: provider,
    nextCheck: alreadyAlerted ? new Date(state.lastAlert + cooldownMs).toISOString() : null
  };
}

// Get alert statistics
function getStats() {
  const state = loadState();
  const now = new Date();
  const last24h = state.history.filter(h => {
    const checkTime = new Date(h.timestamp);
    return (now - checkTime) < 86400000; // 24 hours
  });
  
  return {
    totalChecks: state.history.length,
    alertsSent: state.alertCount,
    last24hChecks: last24h.length,
    lastAlert: state.lastAlert,
    currentBalance: state.lastBalance,
    trend: last24h.length > 1 ? 
      (last24h[last24h.length - 1].balance - last24h[0].balance).toFixed(2) : 0
  };
}

// CLI mode
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  switch (command) {
    case 'check':
      // check <provider> <threshold>
      const provider = args[1] || 'moonshot';
      const threshold = parseFloat(args[2]) || 5;
      const result = await checkAndAlert(provider, threshold);
      console.log(JSON.stringify(result, null, 2));
      process.exit(result.alert ? 1 : 0); // Exit 1 triggers message
      break;
    
    case 'stats':
      console.log(JSON.stringify(getStats(), null, 2));
      break;
    
    default:
      console.log(JSON.stringify({
        usage: 'node scheduler.js <command> [args]',
        commands: {
          check: 'Check balance and alert if needed (provider threshold)',
          stats: 'Show alert statistics'
        }
      }, null, 2));
  }
}

module.exports = { checkAndAlert, getStats, formatAlert };

if (require.main === module) {
  main();
}
