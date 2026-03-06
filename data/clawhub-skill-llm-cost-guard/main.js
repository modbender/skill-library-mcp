#!/usr/bin/env node
'use strict';

/**
 * llm-cost-guard — LLM Token Budget & Spend Monitor
 * OpenClaw skill — main CLI entry point
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

const DATA_PATH = path.join(os.homedir(), '.openclaw', 'workspace', 'llm-cost-guard-data.json');
const CONFIG_PATH = path.join(os.homedir(), '.openclaw', 'workspace', 'llm-cost-guard-config.json');

// Default config
const DEFAULT_CONFIG = {
  dailyCostLimit: 5.00,
  monthlyCostLimit: 50.00,
  perUserDailyCostLimit: null,
  defaultModel: 'gpt-4o-mini',
  alertAt: 0.8,
  dataPath: DATA_PATH,
};

// Pricing per 1M tokens (input / output) in USD — Feb 2026
const PRICING = {
  'gpt-4o': { input: 2.50, output: 10.00 },
  'gpt-4o-mini': { input: 0.15, output: 0.60 },
  'gpt-4-turbo': { input: 10.00, output: 30.00 },
  'gpt-3.5-turbo': { input: 0.50, output: 1.50 },
  'o1': { input: 15.00, output: 60.00 },
  'o1-mini': { input: 3.00, output: 12.00 },
  'o3-mini': { input: 1.10, output: 4.40 },
  'claude-3-5-sonnet': { input: 3.00, output: 15.00 },
  'claude-3-5-haiku': { input: 0.80, output: 4.00 },
  'claude-3-opus': { input: 15.00, output: 75.00 },
  'claude-sonnet-4': { input: 3.00, output: 15.00 },
  'claude-haiku-4': { input: 0.80, output: 4.00 },
  'llama-3.3-70b': { input: 0.59, output: 0.79 },
  'llama-3.1-8b': { input: 0.05, output: 0.08 },
  'mixtral-8x7b': { input: 0.24, output: 0.24 },
  'ollama': { input: 0, output: 0 },
  'default': { input: 1.00, output: 3.00 },
};

function loadConfig() {
  try {
    return { ...DEFAULT_CONFIG, ...JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8')) };
  } catch {
    return { ...DEFAULT_CONFIG };
  }
}

function saveConfig(config) {
  fs.mkdirSync(path.dirname(CONFIG_PATH), { recursive: true });
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
}

function loadData() {
  try {
    return JSON.parse(fs.readFileSync(DATA_PATH, 'utf8'));
  } catch {
    return { entries: [], lastReset: new Date().toISOString().split('T')[0] };
  }
}

function saveData(data) {
  fs.mkdirSync(path.dirname(DATA_PATH), { recursive: true });
  fs.writeFileSync(DATA_PATH, JSON.stringify(data, null, 2));
}

function getPricing(model) {
  const key = Object.keys(PRICING).find(k =>
    model && (model.toLowerCase().includes(k) || k.includes(model.toLowerCase()))
  );
  return PRICING[key] || PRICING['default'];
}

function calcCost(inputTokens, outputTokens, model) {
  const p = getPricing(model);
  return parseFloat(((inputTokens / 1e6) * p.input + (outputTokens / 1e6) * p.output).toFixed(8));
}

function todayStr() {
  return new Date().toISOString().split('T')[0];
}

function getEntriesForPeriod(entries, period) {
  const today = todayStr();
  if (period === 'today') {
    return entries.filter(e => e.date === today);
  } else if (period === 'month') {
    const month = today.substring(0, 7);
    return entries.filter(e => e.date && e.date.startsWith(month));
  }
  return entries;
}

function summarize(entries) {
  const byModel = {};
  const byUser = {};
  let totalCost = 0;
  let totalInput = 0;
  let totalOutput = 0;

  for (const e of entries) {
    totalCost += e.cost || 0;
    totalInput += e.inputTokens || 0;
    totalOutput += e.outputTokens || 0;

    const m = e.model || 'unknown';
    byModel[m] = byModel[m] || { cost: 0, calls: 0 };
    byModel[m].cost += e.cost || 0;
    byModel[m].calls++;

    if (e.user) {
      byUser[e.user] = byUser[e.user] || { cost: 0, calls: 0 };
      byUser[e.user].cost += e.cost || 0;
      byUser[e.user].calls++;
    }
  }

  return {
    totalCost: parseFloat(totalCost.toFixed(6)),
    totalTokens: totalInput + totalOutput,
    totalCalls: entries.length,
    byModel,
    byUser,
  };
}

// ── Commands ──────────────────────────────────────────────────────────────────

function cmdStatus() {
  const config = loadConfig();
  const data = loadData();
  const todayEntries = getEntriesForPeriod(data.entries, 'today');
  const monthEntries = getEntriesForPeriod(data.entries, 'month');
  const todaySummary = summarize(todayEntries);
  const monthSummary = summarize(monthEntries);

  const dailyPct = config.dailyCostLimit > 0
    ? ((todaySummary.totalCost / config.dailyCostLimit) * 100).toFixed(1)
    : 'N/A';
  const monthPct = config.monthlyCostLimit > 0
    ? ((monthSummary.totalCost / config.monthlyCostLimit) * 100).toFixed(1)
    : 'N/A';

  console.log('\n💰 LLM Cost Guard — Status\n');
  console.log(`📅 Today (${todayStr()})`);
  console.log(`   Spend:  $${todaySummary.totalCost.toFixed(4)} / $${config.dailyCostLimit.toFixed(2)} (${dailyPct}%)`);
  console.log(`   Tokens: ${todaySummary.totalTokens.toLocaleString()} | Calls: ${todaySummary.totalCalls}`);

  const bar = buildBar(parseFloat(dailyPct) / 100);
  console.log(`   ${bar}`);

  if (parseFloat(dailyPct) >= 100) {
    console.log('   ⛔ DAILY BUDGET EXCEEDED');
  } else if (parseFloat(dailyPct) >= 80) {
    console.log('   ⚠️  Approaching daily limit (80%+)');
  }

  console.log(`\n📆 This Month`);
  console.log(`   Spend:  $${monthSummary.totalCost.toFixed(4)} / $${config.monthlyCostLimit.toFixed(2)} (${monthPct}%)`);
  console.log(`   Tokens: ${monthSummary.totalTokens.toLocaleString()} | Calls: ${monthSummary.totalCalls}`);
  console.log('');
}

function buildBar(ratio) {
  ratio = Math.min(1, Math.max(0, ratio));
  const filled = Math.round(ratio * 20);
  const color = ratio >= 1 ? '🔴' : ratio >= 0.8 ? '🟡' : '🟢';
  return `${color} [${'█'.repeat(filled)}${'░'.repeat(20 - filled)}]`;
}

function cmdReport(period = 'today') {
  const data = loadData();
  const entries = getEntriesForPeriod(data.entries, period);
  const summary = summarize(entries);

  console.log(`\n📊 LLM Cost Guard — Report (${period})\n`);
  console.log(`Total: $${summary.totalCost.toFixed(6)} | ${summary.totalTokens.toLocaleString()} tokens | ${summary.totalCalls} calls\n`);

  if (Object.keys(summary.byModel).length > 0) {
    console.log('By Model:');
    Object.entries(summary.byModel)
      .sort((a, b) => b[1].cost - a[1].cost)
      .forEach(([m, s]) => {
        console.log(`  ${m.padEnd(25)} $${s.cost.toFixed(6).padStart(10)}  (${s.calls} calls)`);
      });
  }

  if (Object.keys(summary.byUser).length > 0) {
    console.log('\nBy User:');
    Object.entries(summary.byUser)
      .sort((a, b) => b[1].cost - a[1].cost)
      .forEach(([u, s]) => {
        console.log(`  ${u.padEnd(25)} $${s.cost.toFixed(6).padStart(10)}  (${s.calls} calls)`);
      });
  }

  console.log('');
}

function cmdLog(args) {
  const argMap = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      argMap[args[i].slice(2)] = args[i + 1];
      i++;
    }
  }

  const model = argMap['model'] || loadConfig().defaultModel;
  const inputTokens = parseInt(argMap['input-tokens'] || argMap['input'] || '0', 10);
  const outputTokens = parseInt(argMap['output-tokens'] || argMap['output'] || '0', 10);
  const user = argMap['user'] || null;
  const cost = calcCost(inputTokens, outputTokens, model);

  const data = loadData();
  data.entries.push({
    date: todayStr(),
    ts: new Date().toISOString(),
    model,
    inputTokens,
    outputTokens,
    cost,
    user,
  });
  saveData(data);

  console.log(`✅ Logged: ${model} | in=${inputTokens} out=${outputTokens} tokens | $${cost.toFixed(6)}${user ? ` | user=${user}` : ''}`);
}

function cmdSetLimit(args) {
  const config = loadConfig();
  const type = args[0];
  if (type === 'daily') {
    config.dailyCostLimit = parseFloat(args[1]);
    saveConfig(config);
    console.log(`✅ Daily limit set to $${config.dailyCostLimit}`);
  } else if (type === 'monthly') {
    config.monthlyCostLimit = parseFloat(args[1]);
    saveConfig(config);
    console.log(`✅ Monthly limit set to $${config.monthlyCostLimit}`);
  } else if (type === 'user') {
    config.perUserDailyCostLimit = parseFloat(args[2]);
    saveConfig(config);
    console.log(`✅ Per-user daily limit set to $${config.perUserDailyCostLimit}`);
  } else {
    console.log('Usage: llm-cost-guard set-limit daily|monthly|user <USD>');
  }
}

function cmdReset(args) {
  const period = args[0] || 'today';
  const data = loadData();
  const today = todayStr();

  if (period === 'today') {
    data.entries = data.entries.filter(e => e.date !== today);
    saveData(data);
    console.log('✅ Today\'s data reset.');
  } else if (period === 'all') {
    data.entries = [];
    saveData(data);
    console.log('✅ All data reset.');
  } else {
    console.log('Usage: llm-cost-guard reset [today|all]');
  }
}

function cmdWatch() {
  console.log('👀 Watching LLM calls... (press Ctrl+C to stop)\n');
  const initialCount = loadData().entries.length;
  let lastCount = initialCount;

  const interval = setInterval(() => {
    const data = loadData();
    const current = data.entries.length;
    if (current > lastCount) {
      const newEntries = data.entries.slice(lastCount);
      newEntries.forEach(e => {
        console.log(`  ${e.ts} | ${e.model} | in=${e.inputTokens} out=${e.outputTokens} | $${(e.cost || 0).toFixed(6)}${e.user ? ` | ${e.user}` : ''}`);
      });
      lastCount = current;
    }
  }, 1000);

  process.on('SIGINT', () => {
    clearInterval(interval);
    console.log('\nStopped watching.');
    process.exit(0);
  });
}

function cmdHelp() {
  console.log(`
💰 llm-cost-guard v1.0.0

Commands:
  status              Show current spend vs budget
  report [period]     Full report (period: today|month|all)
  log                 Record an LLM call
    --model <name>    Model name (default: from config)
    --input <n>       Input token count
    --output <n>      Output token count
    --user <key>      User identifier (optional)
  set-limit daily <USD>      Set daily spend limit
  set-limit monthly <USD>    Set monthly spend limit
  set-limit user <key> <USD> Set per-user daily limit
  reset [today|all]   Reset counters
  watch               Live tail of LLM calls
  help                Show this help

Examples:
  llm-cost-guard status
  llm-cost-guard log --model gpt-4o --input 1500 --output 800 --user alice
  llm-cost-guard report month
  llm-cost-guard set-limit daily 5.00
  llm-cost-guard reset today
`);
}

// ── Main ──────────────────────────────────────────────────────────────────────

const [,, cmd, ...rest] = process.argv;

switch (cmd) {
  case 'status': cmdStatus(); break;
  case 'report': cmdReport(rest[0] || 'today'); break;
  case 'log': cmdLog(rest); break;
  case 'set-limit': cmdSetLimit(rest); break;
  case 'reset': cmdReset(rest); break;
  case 'watch': cmdWatch(); break;
  case 'help':
  case '--help':
  case undefined:
    cmdHelp(); break;
  default:
    console.error(`Unknown command: ${cmd}`);
    cmdHelp();
    process.exit(1);
}
