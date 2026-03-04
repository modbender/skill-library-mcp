#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(process.env.HOME, '.openclaw/workspace/data/income');
const INCOME_FILE = path.join(DATA_DIR, 'income.jsonl');
const EXPENSE_FILE = path.join(DATA_DIR, 'expenses.jsonl');

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

const CHANNELS = [
  'github-bounty',
  'clawhub',
  'toku-agency',
  'fiverr',
  'trading',
  'medium',
  'youtube',
  'consulting',
  'other'
];

function addIncome(source, amount, description) {
  const entry = {
    timestamp: new Date().toISOString(),
    source,
    amount: parseFloat(amount),
    description,
    type: 'income'
  };
  
  fs.appendFileSync(INCOME_FILE, JSON.stringify(entry) + '\n');
  console.log(`✅ Added income: $${amount} from ${source}`);
}

function addExpense(category, amount, description) {
  const entry = {
    timestamp: new Date().toISOString(),
    category,
    amount: parseFloat(amount),
    description,
    type: 'expense'
  };
  
  fs.appendFileSync(EXPENSE_FILE, JSON.stringify(entry) + '\n');
  console.log(`✅ Added expense: $${amount} for ${category}`);
}

function getReport(period = 'week') {
  const now = new Date();
  const cutoff = new Date();
  
  if (period === 'day') {
    cutoff.setDate(cutoff.getDate() - 1);
  } else if (period === 'week') {
    cutoff.setDate(cutoff.getDate() - 7);
  } else if (period === 'month') {
    cutoff.setMonth(cutoff.getMonth() - 1);
  }
  
  const income = readTransactions(INCOME_FILE, cutoff);
  const expenses = readTransactions(EXPENSE_FILE, cutoff);
  
  const totalIncome = income.reduce((sum, t) => sum + t.amount, 0);
  const totalExpense = expenses.reduce((sum, t) => sum + t.amount, 0);
  const netProfit = totalIncome - totalExpense;
  
  console.log(`\n📊 ${period.toUpperCase()} REPORT`);
  console.log('='.repeat(50));
  console.log(`💰 Total Income:  $${totalIncome.toFixed(2)}`);
  console.log(`📉 Total Expense: $${totalExpense.toFixed(2)}`);
  console.log(`💵 Net Profit:    $${netProfit.toFixed(2)}`);
  console.log('='.repeat(50));
  
  // Income by channel
  const byChannel = {};
  income.forEach(t => {
    byChannel[t.source] = (byChannel[t.source] || 0) + t.amount;
  });
  
  console.log('\n📈 Income by Channel:');
  Object.entries(byChannel)
    .sort((a, b) => b[1] - a[1])
    .forEach(([channel, amount]) => {
      const percentage = (amount / totalIncome * 100).toFixed(1);
      console.log(`  ${channel}: $${amount.toFixed(2)} (${percentage}%)`);
    });
}

function readTransactions(file, cutoff) {
  if (!fs.existsSync(file)) return [];
  
  return fs.readFileSync(file, 'utf8')
    .split('\n')
    .filter(line => line.trim())
    .map(line => JSON.parse(line))
    .filter(t => new Date(t.timestamp) >= cutoff);
}

function showChannels() {
  const income = readTransactions(INCOME_FILE, new Date(0));
  const expenses = readTransactions(EXPENSE_FILE, new Date(0));
  
  const byChannel = {};
  income.forEach(t => {
    if (!byChannel[t.source]) {
      byChannel[t.source] = { income: 0, expense: 0 };
    }
    byChannel[t.source].income += t.amount;
  });
  
  console.log('\n📊 Channel Performance (All Time)');
  console.log('='.repeat(60));
  console.log('Channel'.padEnd(20) + 'Income'.padEnd(15) + 'ROI');
  console.log('-'.repeat(60));
  
  Object.entries(byChannel)
    .sort((a, b) => b[1].income - a[1].income)
    .forEach(([channel, data]) => {
      const roi = data.expense > 0 ? (data.income / data.expense).toFixed(2) : '∞';
      console.log(
        channel.padEnd(20) +
        `$${data.income.toFixed(2)}`.padEnd(15) +
        `${roi}x`
      );
    });
}

// CLI
const args = process.argv.slice(2);
const command = args[0];

if (command === 'income') {
  const source = args[args.indexOf('--source') + 1];
  const amount = args[args.indexOf('--amount') + 1];
  const description = args[args.indexOf('--description') + 1] || '';
  addIncome(source, amount, description);
} else if (command === 'expense') {
  const category = args[args.indexOf('--category') + 1];
  const amount = args[args.indexOf('--amount') + 1];
  const description = args[args.indexOf('--description') + 1] || '';
  addExpense(category, amount, description);
} else if (command === 'report') {
  const period = args[args.indexOf('--period') + 1] || 'week';
  getReport(period);
} else if (command === 'channels') {
  showChannels();
} else {
  console.log('Usage:');
  console.log('  node tracker.js income --source <channel> --amount <amount> [--description <desc>]');
  console.log('  node tracker.js expense --category <category> --amount <amount> [--description <desc>]');
  console.log('  node tracker.js report [--period day|week|month]');
  console.log('  node tracker.js channels');
}
