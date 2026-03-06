#!/usr/bin/env node
/**
 * Session Tracker - Cross-Session Usage Analytics
 * 
 * Tracks token usage across multiple sessions and generates insights.
 * 
 * Security Notice:
 * - All data stored locally in .data/
 * - No session content stored, only usage metrics
 * - No external data transmission
 */

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', '.data');
const SESSION_FILE = path.join(DATA_DIR, 'sessions.json');

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

// Load session data
function loadSessions() {
  try {
    if (fs.existsSync(SESSION_FILE)) {
      return JSON.parse(fs.readFileSync(SESSION_FILE, 'utf8'));
    }
  } catch (e) {}
  return { sessions: [], daily: {}, providers: {} };
}

function saveSessions(data) {
  fs.writeFileSync(SESSION_FILE, JSON.stringify(data, null, 2));
}

// Record a new session
function recordSession(sessionData) {
  const data = loadSessions();
  const now = new Date();
  const dateKey = now.toISOString().split('T')[0];
  
  const session = {
    id: `session_${now.getTime()}`,
    timestamp: now.toISOString(),
    date: dateKey,
    provider: sessionData.provider || 'unknown',
    model: sessionData.model || 'unknown',
    tokensIn: sessionData.tokensIn || 0,
    tokensOut: sessionData.tokensOut || 0,
    cost: sessionData.cost || 0,
    currency: sessionData.currency || 'CNY',
    duration: sessionData.duration || 0 // minutes
  };
  
  data.sessions.push(session);
  
  // Update daily stats
  if (!data.daily[dateKey]) {
    data.daily[dateKey] = {
      date: dateKey,
      totalTokens: 0,
      totalCost: 0,
      sessionCount: 0,
      providers: {}
    };
  }
  
  data.daily[dateKey].totalTokens += session.tokensIn + session.tokensOut;
  data.daily[dateKey].totalCost += session.cost;
  data.daily[dateKey].sessionCount++;
  
  // Provider breakdown
  if (!data.daily[dateKey].providers[session.provider]) {
    data.daily[dateKey].providers[session.provider] = {
      tokens: 0,
      cost: 0
    };
  }
  data.daily[dateKey].providers[session.provider].tokens += session.tokensIn + session.tokensOut;
  data.daily[dateKey].providers[session.provider].cost += session.cost;
  
  // Cleanup old sessions (keep 90 days)
  const ninetyDaysAgo = new Date();
  ninetyDaysAgo.setDate(ninetyDaysAgo.getDate() - 90);
  data.sessions = data.sessions.filter(s => new Date(s.timestamp) > ninetyDaysAgo);
  
  saveSessions(data);
  return session;
}

// Generate daily report
function generateDailyReport(date = null) {
  const data = loadSessions();
  const targetDate = date || new Date().toISOString().split('T')[0];
  
  const day = data.daily[targetDate];
  if (!day) {
    return { success: false, error: `No data for ${targetDate}` };
  }
  
  return {
    success: true,
    date: targetDate,
    summary: {
      totalTokens: day.totalTokens,
      totalCost: day.totalCost.toFixed(4),
      sessionCount: day.sessionCount,
      avgCostPerSession: (day.totalCost / day.sessionCount).toFixed(4)
    },
    providers: day.providers
  };
}

// Generate weekly report
function generateWeeklyReport() {
  const data = loadSessions();
  const now = new Date();
  const weekAgo = new Date(now - 7 * 24 * 60 * 60 * 1000);
  
  const weekSessions = data.sessions.filter(s => new Date(s.timestamp) > weekAgo);
  
  const totals = weekSessions.reduce((acc, s) => {
    acc.tokens += s.tokensIn + s.tokensOut;
    acc.cost += s.cost;
    acc.providers[s.provider] = (acc.providers[s.provider] || 0) + s.cost;
    return acc;
  }, { tokens: 0, cost: 0, providers: {} });
  
  return {
    success: true,
    period: 'Last 7 days',
    summary: {
      totalTokens: totals.tokens,
      totalCost: totals.cost.toFixed(4),
      sessionCount: weekSessions.length,
      avgDailyCost: (totals.cost / 7).toFixed(4)
    },
    providerBreakdown: totals.providers,
    trend: calculateTrend(data)
  };
}

// Calculate cost trend
function calculateTrend(data) {
  const dates = Object.keys(data.daily).sort().slice(-7);
  if (dates.length < 2) return null;
  
  const costs = dates.map(d => data.daily[d].totalCost);
  const firstAvg = costs.slice(0, 3).reduce((a, b) => a + b, 0) / 3;
  const lastAvg = costs.slice(-3).reduce((a, b) => a + b, 0) / 3;
  const change = ((lastAvg - firstAvg) / firstAvg * 100).toFixed(1);
  
  return {
    direction: change > 0 ? 'up' : change < 0 ? 'down' : 'stable',
    changePercent: Math.abs(change),
    avgDailyCost: (costs.reduce((a, b) => a + b, 0) / costs.length).toFixed(4)
  };
}

// Get top recommendations based on history
function getRecommendations() {
  const data = loadSessions();
  const now = new Date();
  const weekAgo = new Date(now - 7 * 24 * 60 * 60 * 1000);
  const weekSessions = data.sessions.filter(s => new Date(s.timestamp) > weekAgo);
  
  const recommendations = [];
  
  if (weekSessions.length === 0) {
    return { success: true, recommendations: [] };
  }
  
  // Check for high-cost patterns
  const highCostSessions = weekSessions.filter(s => s.cost > 1); // > ¥1 per session
  if (highCostSessions.length > 3) {
    recommendations.push({
      priority: 'high',
      en: 'Multiple high-cost sessions detected. Consider using sub-agents or disabling reasoning for simpler tasks.',
      cn: '检测到多个高成本会话。建议对简单任务使用子代理或关闭推理。',
      action: 'optimize_large_sessions'
    });
  }
  
  // Check for expensive models
  const expensiveModels = weekSessions.filter(s => 
    s.model.includes('opus') || s.model.includes('gpt-4') && !s.model.includes('mini')
  );
  if (expensiveModels.length > 5) {
    recommendations.push({
      priority: 'medium',
      en: 'Frequent use of premium models. Consider cheaper alternatives (Claude Sonnet, GPT-4o-mini) for non-critical tasks.',
      cn: '频繁使用高级模型。对非关键任务考虑更便宜的替代方案 (Claude Sonnet, GPT-4o-mini)。',
      action: 'consider_cheaper_models'
    });
  }
  
  // Check daily spend
  const today = now.toISOString().split('T')[0];
  const todayCost = data.daily[today]?.totalCost || 0;
  if (todayCost > 10) {
    recommendations.push({
      priority: 'high',
      en: `Daily spending ¥${todayCost.toFixed(2)} exceeds ¥10. Consider enabling strict save mode.`,
      cn: `今日花费 ¥${todayCost.toFixed(2)} 超过 ¥10。建议开启严格省钱模式。`,
      action: 'enable_save_mode'
    });
  }
  
  return {
    success: true,
    basedOn: `${weekSessions.length} sessions in last 7 days`,
    recommendations: recommendations
  };
}

// CLI mode
function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  switch (command) {
    case 'record':
      // record <provider> <model> <tokensIn> <tokensOut> <cost> [currency]
      const session = recordSession({
        provider: args[1],
        model: args[2],
        tokensIn: parseInt(args[3]) || 0,
        tokensOut: parseInt(args[4]) || 0,
        cost: parseFloat(args[5]) || 0,
        currency: args[6] || 'CNY'
      });
      console.log(JSON.stringify({ success: true, session }, null, 2));
      break;
    
    case 'daily':
      console.log(JSON.stringify(generateDailyReport(args[1]), null, 2));
      break;
    
    case 'weekly':
      console.log(JSON.stringify(generateWeeklyReport(), null, 2));
      break;
    
    case 'recommend':
      console.log(JSON.stringify(getRecommendations(), null, 2));
      break;
    
    default:
      console.log(JSON.stringify({
        usage: 'node session-tracker.js <command> [args]',
        commands: {
          record: 'Record a session (provider model tokensIn tokensOut cost currency)',
          daily: 'Generate daily report [date]',
          weekly: 'Generate weekly report',
          recommend: 'Get usage recommendations'
        }
      }, null, 2));
  }
}

module.exports = {
  recordSession,
  generateDailyReport,
  generateWeeklyReport,
  getRecommendations,
  loadSessions
};

if (require.main === module) {
  main();
}
