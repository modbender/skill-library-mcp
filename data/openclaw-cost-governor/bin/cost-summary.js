#!/usr/bin/env node
// Cost Governor v1.1.0 — OpenClaw Community — MIT License

const fs = require('fs');
const path = require('path');

// Auto-detect workspace
const WORKSPACE = process.env.OPENCLAW_WORKSPACE || path.join(process.env.HOME || '~', '.openclaw', 'workspace');
const COST_TRACKING_FILE = path.join(WORKSPACE, 'notes', 'cost-tracking.md');

/**
 * Parse cost tracking file
 * @returns {Array} Array of parsed entries
 */
function parseEntries() {
  if (!fs.existsSync(COST_TRACKING_FILE)) {
    return [];
  }
  
  const content = fs.readFileSync(COST_TRACKING_FILE, 'utf8');
  const entries = [];
  
  // Match entries: ### [YYYY-MM-DD HH:MM] Label
  const entryPattern = /### \[(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})\] (.+?)\n([\s\S]*?)(?=\n###|\n---\n|$)/g;
  
  let match;
  while ((match = entryPattern.exec(content)) !== null) {
    const [, date, time, label, body] = match;
    
    const estimatedMatch = body.match(/\*\*Estimated:\*\* \$([0-9.]+)/);
    const actualMatch = body.match(/\*\*Actual:\*\* \$([0-9.]+)/);
    const approvedMatch = body.match(/\*\*Approved:\*\* (yes|no|auto)/);
    const taskTypeMatch = body.match(/\*\*Task Type:\*\* (\w+)/);
    
    entries.push({
      date,
      time,
      label: label.trim(),
      estimated: estimatedMatch ? parseFloat(estimatedMatch[1]) : 0,
      actual: actualMatch ? parseFloat(actualMatch[1]) : 0,
      approved: approvedMatch ? approvedMatch[1] : 'unknown',
      taskType: taskTypeMatch ? taskTypeMatch[1] : 'unknown',
      pending: body.includes('(pending)')
    });
  }
  
  return entries;
}

/**
 * Generate daily summary
 * @param {string} date - Date in YYYY-MM-DD format (optional, defaults to today)
 */
function dailySummary(date = null) {
  const entries = parseEntries();
  
  if (entries.length === 0) {
    console.log('No spend data yet');
    return;
  }
  
  const targetDate = date || new Date().toISOString().substring(0, 10);
  const dailyEntries = entries.filter(e => e.date === targetDate);
  
  if (dailyEntries.length === 0) {
    console.log(`No spend data for ${targetDate}`);
    return;
  }
  
  let totalEstimated = 0;
  let totalActual = 0;
  
  console.log(`\n## Daily Spend — ${targetDate}\n`);
  console.log('### Subagent Spawns');
  console.log('| Task | Model | Est. | Actual | Ratio |');
  console.log('|------|-------|------|--------|-------|');
  
  dailyEntries.forEach(entry => {
    const ratio = entry.actual > 0 ? (entry.actual / entry.estimated).toFixed(2) : 'pending';
    console.log(`| ${entry.label} | ${entry.taskType} | $${entry.estimated.toFixed(2)} | $${entry.actual.toFixed(2)} | ${ratio} |`);
    totalEstimated += entry.estimated;
    totalActual += entry.actual;
  });
  
  console.log(`\n**Subagent Total:** $${totalEstimated.toFixed(2)} est / $${totalActual.toFixed(2)} actual`);
  console.log('\n### Automation (Prorated Daily)');
  console.log('Dream Cycle: $0.03');
  console.log('Daily Review: $0.05');
  console.log('Daily Index: $0.03');
  console.log('Weekly Health (prorated): $0.01');
  console.log('**Automation Total:** $0.12/day');
  console.log(`\n**Combined Daily Total:** $${(totalActual + 0.12).toFixed(2)}`);
}

/**
 * Generate monthly summary
 * @param {string} month - Month in YYYY-MM format (optional, defaults to current month)
 */
function monthlySummary(month = null) {
  const entries = parseEntries();
  
  if (entries.length === 0) {
    console.log('No spend data yet');
    return;
  }
  
  const targetMonth = month || new Date().toISOString().substring(0, 7);
  const monthlyEntries = entries.filter(e => e.date.startsWith(targetMonth));
  
  if (monthlyEntries.length === 0) {
    console.log(`No spend data for ${targetMonth}`);
    return;
  }
  
  let totalEstimated = 0;
  let totalActual = 0;
  const taskCounts = {};
  
  monthlyEntries.forEach(entry => {
    totalEstimated += entry.estimated;
    totalActual += entry.actual;
    taskCounts[entry.label] = (taskCounts[entry.label] || 0) + entry.actual;
  });
  
  const automationMonthly = 1.21; // Typical automation costs
  
  console.log(`\n## Monthly Spend — ${targetMonth}\n`);
  console.log(`**Subagent spawns:** $${totalActual.toFixed(2)} (${monthlyEntries.length} tasks)`);
  console.log(`**Automation (recurring):** $${automationMonthly.toFixed(2)} (cron jobs)`);
  console.log(`**Total:** $${(totalActual + automationMonthly).toFixed(2)}\n`);
  
  console.log('**Top cost drivers:**');
  const sorted = Object.entries(taskCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);
  
  sorted.forEach(([label, cost], i) => {
    console.log(`${i + 1}. ${label}: $${cost.toFixed(2)}`);
  });
}

// CLI
const args = process.argv.slice(2);
const mode = args[0];

if (mode === '--daily') {
  const date = args[1]; // Optional date arg
  dailySummary(date);
} else if (mode === '--monthly') {
  const month = args[1]; // Optional month arg
  monthlySummary(month);
} else {
  console.log('Usage: node cost-summary.js [--daily|--monthly] [date/month]');
  console.log('Examples:');
  console.log('  node cost-summary.js --daily');
  console.log('  node cost-summary.js --daily 2026-02-24');
  console.log('  node cost-summary.js --monthly');
  console.log('  node cost-summary.js --monthly 2026-02');
  process.exit(1);
}
