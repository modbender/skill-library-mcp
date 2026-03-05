const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = path.join(process.env.HOME || '/home/ubuntu', '.openclaw/workspace/outputs');
const USAGE_FILE = path.join(OUTPUT_DIR, 'token-usage.json');
const CONFIG_FILE = path.join(__dirname, 'config.json');

// Default config
const DEFAULT_CONFIG = {
  dailyLimit: 100000,
  jobLimits: {},
  alertThreshold: 0.8,
  freeModels: [
    'nvidia/moonshotai/kimi-k2.5',
    'google/gemini-2.0-flash-exp',
    'nvidia/deepseek-ai/deepseek-r1'
  ]
};

function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      return { ...DEFAULT_CONFIG, ...JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8')) };
    }
  } catch (e) {
    console.error('Config load error:', e.message);
  }
  return DEFAULT_CONFIG;
}

function loadUsage() {
  try {
    if (fs.existsSync(USAGE_FILE)) {
      return JSON.parse(fs.readFileSync(USAGE_FILE, 'utf8'));
    }
  } catch (e) {
    // Ignore
  }
  return { date: new Date().toISOString().slice(0, 10), totalTokens: 0, jobs: {} };
}

function saveUsage(usage) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  fs.writeFileSync(USAGE_FILE, JSON.stringify(usage, null, 2));
}

function getToday() {
  return new Date().toISOString().slice(0, 10);
}

function resetIfNewDay(usage) {
  const today = getToday();
  if (usage.date !== today) {
    return { date: today, totalTokens: 0, jobs: {} };
  }
  return usage;
}

// Track tokens for a job
function track(jobName, inputTokens, outputTokens, model) {
  let usage = loadUsage();
  usage = resetIfNewDay(usage);
  
  const total = inputTokens + outputTokens;
  
  if (!usage.jobs[jobName]) {
    usage.jobs[jobName] = { input: 0, output: 0, model, runs: 0 };
  }
  
  usage.jobs[jobName].input += inputTokens;
  usage.jobs[jobName].output += outputTokens;
  usage.jobs[jobName].runs += 1;
  usage.jobs[jobName].model = model;
  usage.totalTokens += total;
  
  saveUsage(usage);
  console.log(`Tracked ${total} tokens for ${jobName} (${model})`);
  return usage;
}

// Check status
function status() {
  const config = loadConfig();
  let usage = loadUsage();
  usage = resetIfNewDay(usage);
  
  console.log(`\n📊 Token Budget — ${usage.date}`);
  console.log(`Total: ${usage.totalTokens.toLocaleString()} / ${config.dailyLimit.toLocaleString()} (${Math.round(usage.totalTokens / config.dailyLimit * 100)}%)\n`);
  
  for (const [job, data] of Object.entries(usage.jobs)) {
    const jobLimit = config.jobLimits[job] || config.dailyLimit / 10;
    const pct = Math.round((data.input + data.output) / jobLimit * 100);
    console.log(`  ${job}: ${(data.input + data.output).toLocaleString()} tokens (${pct}%) — ${data.runs} runs`);
  }
  
  return usage;
}

// Check specific job
function checkJob(jobName) {
  const config = loadConfig();
  const usage = loadUsage();
  const job = usage.jobs[jobName];
  
  if (!job) {
    console.log(`No data for job: ${jobName}`);
    return;
  }
  
  const total = job.input + job.output;
  const limit = config.jobLimits[jobName] || config.dailyLimit / 10;
  const remaining = Math.max(0, limit - total);
  
  console.log(`\n🔍 ${jobName}`);
  console.log(`  Model: ${job.model}`);
  console.log(`  Runs: ${job.runs}`);
  console.log(`  Input: ${job.input.toLocaleString()}`);
  console.log(`  Output: ${job.output.toLocaleString()}`);
  console.log(`  Total: ${total.toLocaleString()} / ${limit.toLocaleString()}`);
  console.log(`  Remaining: ${remaining.toLocaleString()}`);
  
  if (total > limit) {
    console.log(`  ⚠️ OVER BUDGET by ${(total - limit).toLocaleString()} tokens`);
  }
}

// Check alerts
function alert() {
  const config = loadConfig();
  const usage = loadUsage();
  const alerts = [];
  
  // Daily limit
  if (usage.totalTokens > config.dailyLimit * config.alertThreshold) {
    alerts.push(`Daily limit: ${usage.totalTokens}/${config.dailyLimit} (${Math.round(usage.totalTokens / config.dailyLimit * 100)}%)`);
  }
  
  // Job limits
  for (const [job, data] of Object.entries(usage.jobs)) {
    const limit = config.jobLimits[job] || config.dailyLimit / 10;
    const total = data.input + data.output;
    if (total > limit * config.alertThreshold) {
      alerts.push(`${job}: ${total}/${limit} (${Math.round(total / limit * 100)}%)`);
    }
  }
  
  if (alerts.length > 0) {
    console.log('🚨 Token Budget Alerts:');
    alerts.forEach(a => console.log(`  - ${a}`));
  } else {
    console.log('✅ All budgets healthy');
  }
  
  return alerts;
}

// Recommend cheaper models
function recommend() {
  const config = loadConfig();
  const usage = loadUsage();
  
  console.log('\n💡 Model Recommendations:');
  console.log(`Free models: ${config.freeModels.join(', ')}\n`);
  
  for (const [job, data] of Object.entries(usage.jobs)) {
    const isFree = config.freeModels.some(m => data.model?.includes(m));
    if (!isFree && data.input + data.output > 5000) {
      console.log(`  ${job}: currently using ${data.model} — switch to ${config.freeModels[0]} to save ~${(data.input + data.output).toLocaleString()} tokens/run`);
    }
  }
}

// CLI
const args = process.argv.slice(2);
const cmd = args[0];

if (cmd === 'track' && args[1] && args[2]) {
  track(args[1], parseInt(args[2]) || 0, parseInt(args[3]) || 0, args[4] || 'unknown');
} else if (cmd === 'status') {
  status();
} else if (cmd === 'check' && args[1]) {
  checkJob(args[1]);
} else if (cmd === 'alert') {
  alert();
} else if (cmd === 'recommend') {
  recommend();
} else {
  console.log('Usage:');
  console.log('  node track-usage.js track <job> <input> <output> <model>');
  console.log('  node track-usage.js status');
  console.log('  node track-usage.js check <job>');
  console.log('  node track-usage.js alert');
  console.log('  node track-usage.js recommend');
}
