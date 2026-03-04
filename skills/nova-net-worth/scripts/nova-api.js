#!/usr/bin/env node

/**
 * Nova Net Worth API Client
 *
 * Query your financial data from Nova Net Worth.
 * Requires: NOVA_API_KEY environment variable
 *
 * Usage:
 *   node nova-api.js <command> [options]
 *
 * Commands:
 *   briefing             Full financial snapshot (recommended for "how are my finances?")
 *   summary              Net worth, MoM change, health score
 *   accounts             All accounts with balances
 *   transactions         Recent transactions (filterable)
 *   goals                Financial goals with progress
 *   spending [--months]  Monthly spending by category
 *   insights             AI-generated financial insights
 *   history [--days]     Net worth trend over time
 *   health               Financial health score breakdown
 *
 * Options:
 *   --months N           Months of spending data (1-12)
 *   --days N             Days of history (1-365)
 *   --limit N            Max transactions (1-100)
 *   --category CAT       Filter transactions by Plaid category
 *   --account ID         Filter transactions by account ID
 *   --since ISO_DATE     Delta polling — only transactions after this date
 *   --pretty             Human-readable formatted output
 *   --json               Raw JSON output (default)
 */

const https = require('https');
const http = require('http');

const API_KEY = process.env.NOVA_API_KEY;
const BASE_URL = process.env.NOVA_API_URL || 'https://api.novanetworth.com';

if (!API_KEY) {
  console.error(JSON.stringify({
    success: false,
    error: {
      code: 'MISSING_API_KEY',
      message: 'Set NOVA_API_KEY environment variable. Get your key at app.novanetworth.com → Settings → Integrations'
    }
  }, null, 2));
  process.exit(1);
}

if (!API_KEY.startsWith('nova_')) {
  console.error(JSON.stringify({
    success: false,
    error: {
      code: 'INVALID_API_KEY',
      message: 'API key must start with "nova_". Get your key at app.novanetworth.com → Settings → Integrations'
    }
  }, null, 2));
  process.exit(1);
}

// Parse CLI args
const args = process.argv.slice(2);
const command = args.find(a => !a.startsWith('--'));
const pretty = args.includes('--pretty');

function parseFlag(flag, defaultValue) {
  const idx = args.indexOf(flag);
  if (idx === -1 || idx + 1 >= args.length) return defaultValue;
  return args[idx + 1];
}

function parseIntFlag(flag, defaultValue) {
  const val = parseFlag(flag, null);
  if (val === null) return defaultValue;
  return parseInt(val, 10) || defaultValue;
}

// Map commands to API paths
const ENDPOINTS = {
  briefing: '/api/v1/agent/briefing',
  summary: '/api/v1/agent/summary',
  accounts: '/api/v1/agent/accounts',
  transactions: () => {
    const params = new URLSearchParams();
    const days = parseIntFlag('--days', 30);
    const limit = parseIntFlag('--limit', 50);
    const category = parseFlag('--category', null);
    const account = parseFlag('--account', null);
    const since = parseFlag('--since', null);
    if (since) params.set('since', since);
    else params.set('days', String(days));
    params.set('limit', String(limit));
    if (category) params.set('category', category);
    if (account) params.set('account', account);
    return `/api/v1/agent/transactions?${params}`;
  },
  goals: '/api/v1/agent/goals',
  spending: () => {
    const months = parseIntFlag('--months', 1);
    return `/api/v1/agent/spending?months=${months}`;
  },
  insights: '/api/v1/agent/insights',
  history: () => {
    const days = parseIntFlag('--days', 30);
    return `/api/v1/agent/net-worth/history?days=${days}`;
  },
  health: '/api/v1/agent/health-score',
  holdings: () => {
    const params = new URLSearchParams();
    const account = parseFlag('--account', null);
    const summary = args.includes('--summary');
    if (account) params.set('accountId', account);
    if (summary) params.set('summary', 'true');
    const qs = params.toString();
    return `/api/holdings${qs ? '?' + qs : ''}`;
  },
};

if (!command || !ENDPOINTS[command]) {
  console.error(`Usage: nova-api.js <command> [options]

Commands:
  briefing             Full financial snapshot (recommended first call)
  summary              Net worth, MoM change, health score
  accounts             All accounts with balances
  transactions         Recent transactions (filterable)
  goals                Financial goals with progress
  spending [--months]  Monthly spending by category (default: 1)
  insights             AI-generated financial insights
  history [--days]     Net worth trend over time (default: 30)
  health               Financial health score breakdown
  holdings             Investment holdings with positions and gain/loss

Options:
  --months N           Months of spending data (1-12)
  --days N             Days of history/transactions (1-365/90)
  --limit N            Max transactions to return (1-100, default: 50)
  --category CAT       Filter transactions by Plaid category
  --account ID         Filter transactions/holdings by account ID
  --since ISO_DATE     Only transactions after this date
  --summary            Holdings: aggregate by ticker across accounts
  --pretty             Human-readable output
  --json               Raw JSON output (default)`);
  process.exit(1);
}

// ---- Pretty formatters ----

function centsToMoney(cents, currency = 'USD') {
  const dollars = (cents / 100).toLocaleString('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
  return dollars;
}

function signedMoney(cents, currency = 'USD') {
  const prefix = cents >= 0 ? '+' : '';
  return prefix + centsToMoney(cents, currency);
}

function formatDate(iso) {
  if (!iso) return 'N/A';
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function prettyBriefing(data) {
  const lines = [];
  lines.push(`💰 ${data.user.firstName}'s Financial Briefing`);
  lines.push('─'.repeat(40));
  lines.push(`Net Worth:     ${centsToMoney(data.netWorth.current, data.netWorth.currency)}`);
  lines.push(`  vs Last Mo:  ${signedMoney(data.netWorth.change, data.netWorth.currency)}`);
  lines.push(`Spending:      ${centsToMoney(data.spending.currentMonth, data.spending.currency)} this month`);
  if (data.spending.changePercent !== null) {
    const arrow = data.spending.changePercent > 0 ? '↑' : data.spending.changePercent < 0 ? '↓' : '→';
    lines.push(`  vs Last Mo:  ${arrow} ${Math.abs(data.spending.changePercent)}%`);
  }
  lines.push(`Health Score:  ${data.healthScore.score}/100 (${data.healthScore.grade})`);
  lines.push(`Accounts:      ${data.accountCount}`);
  lines.push('');

  if (data.topAccounts.length > 0) {
    lines.push('📊 Top Accounts');
    for (const a of data.topAccounts.slice(0, 5)) {
      lines.push(`  ${a.name.padEnd(25)} ${centsToMoney(a.balance, a.currency).padStart(12)}`);
    }
    lines.push('');
  }

  if (data.goals.length > 0) {
    lines.push('🎯 Goals');
    for (const g of data.goals) {
      const bar = '█'.repeat(Math.round(g.progressPercent / 5)) + '░'.repeat(20 - Math.round(g.progressPercent / 5));
      lines.push(`  ${g.name}: ${bar} ${g.progressPercent}%`);
    }
    lines.push('');
  }

  if (data.insights.length > 0) {
    lines.push('💡 Insights');
    for (const i of data.insights) {
      lines.push(`  • ${i.title}`);
      if (i.recommendation) lines.push(`    → ${i.recommendation}`);
    }
  }

  return lines.join('\n');
}

function prettySummary(data) {
  return [
    `Net Worth: ${centsToMoney(data.netWorth.amount, data.netWorth.currency)}`,
    `Change:    ${signedMoney(data.monthOverMonthChange.amount, data.monthOverMonthChange.currency)}`,
    `Accounts:  ${data.accountCount}`,
    `Health:    ${data.financialHealthScore}/100`,
    `Tier:      ${data.subscriptionTier}`,
    `Last Sync: ${data.lastSyncTime ? formatDate(data.lastSyncTime) : 'N/A'}`,
  ].join('\n');
}

function prettyAccounts(data) {
  const lines = [`📊 ${data.accounts.length} Accounts\n`];
  for (const [group, accts] of Object.entries(data.groupedByType)) {
    lines.push(`${group.toUpperCase()}`);
    for (const a of accts) {
      const status = a.isActive ? '' : ' (inactive)';
      lines.push(`  ${a.name.padEnd(30)} ${centsToMoney(a.currentBalance, a.currency).padStart(12)}${status}`);
    }
    lines.push('');
  }
  return lines.join('\n');
}

function prettyTransactions(data) {
  const lines = [`📋 ${data.count} Transactions\n`];
  for (const tx of data.transactions) {
    const date = formatDate(tx.date);
    const pending = tx.pending ? ' (pending)' : '';
    lines.push(`  ${date}  ${(tx.merchant || tx.name).padEnd(25)} ${centsToMoney(tx.amount, tx.currency).padStart(10)}  ${tx.category}${pending}`);
  }
  return lines.join('\n');
}

function prettySpending(data) {
  const lines = [`💸 Spending — ${data.months} month(s)\n`];
  lines.push(`Total: ${centsToMoney(data.total, data.currency)}`);
  if (data.comparisonToPreviousPeriod.changePercent !== null) {
    const arrow = data.comparisonToPreviousPeriod.changePercent > 0 ? '↑' : '↓';
    lines.push(`vs Previous: ${arrow} ${Math.abs(data.comparisonToPreviousPeriod.changePercent)}%\n`);
  }
  for (const c of data.byCategory) {
    lines.push(`  ${c.category.padEnd(30)} ${centsToMoney(c.amount, data.currency).padStart(10)}`);
  }
  return lines.join('\n');
}

function prettyHealth(data) {
  const lines = [`❤️ Financial Health: ${data.totalScore}/100 (${data.grade})\n`];
  for (const [key, val] of Object.entries(data.breakdown)) {
    const label = key.replace(/([A-Z])/g, ' $1').trim();
    lines.push(`  ${label.padEnd(25)} ${val.score}/100 (weight: ${(val.weight * 100).toFixed(0)}%)`);
  }
  if (data.recommendations?.length > 0) {
    lines.push('\n📋 Recommendations');
    for (const r of data.recommendations) {
      lines.push(`  • ${r}`);
    }
  }
  return lines.join('\n');
}

function prettyHoldings(data) {
  const lines = [];
  const holdings = data.holdings || [];
  if (holdings.length === 0) {
    return '📊 No investment holdings found.';
  }

  // Group by account
  const byAcct = {};
  for (const h of holdings) {
    const acct = h.accountName || 'Unknown';
    if (!byAcct[acct]) byAcct[acct] = [];
    byAcct[acct].push(h);
  }

  lines.push(`📊 Investment Holdings — ${holdings.length} positions\n`);

  for (const [acct, positions] of Object.entries(byAcct)) {
    const acctTotal = positions.reduce((s, p) => s + (p.value || 0), 0);
    lines.push(`═══ ${acct} (${centsToMoney(acctTotal)}) ═══`);
    for (const p of positions) {
      const sym = (p.symbol || '???').padEnd(8);
      const qty = Number(p.quantity).toFixed(1).padStart(9);
      const val = centsToMoney(p.value || 0).padStart(10);
      let gainStr = '';
      if (p.costBasis && p.costBasis > 0) {
        const gain = p.value - p.costBasis;
        const pct = ((gain / p.costBasis) * 100).toFixed(1);
        gainStr = `  ${gain >= 0 ? '+' : ''}${centsToMoney(gain)} (${gain >= 0 ? '+' : ''}${pct}%)`;
      }
      lines.push(`  ${sym} ${qty} shares ${val}${gainStr}`);
    }
    lines.push('');
  }

  if (data.summary) {
    lines.push('─'.repeat(40));
    lines.push(`Total Value:     ${centsToMoney(data.summary.totalValue)}`);
    if (data.summary.totalCostBasis) {
      lines.push(`Total Cost:      ${centsToMoney(data.summary.totalCostBasis)}`);
      lines.push(`Total Gain/Loss: ${signedMoney(data.summary.totalGainLoss)} (${data.summary.totalGainLossPercent >= 0 ? '+' : ''}${data.summary.totalGainLossPercent.toFixed(1)}%)`);
    }
  }

  return lines.join('\n');
}

const PRETTY_FORMATTERS = {
  briefing: prettyBriefing,
  summary: prettySummary,
  accounts: prettyAccounts,
  transactions: prettyTransactions,
  spending: prettySpending,
  health: prettyHealth,
  holdings: prettyHoldings,
};

// ---- Request ----

const endpoint = typeof ENDPOINTS[command] === 'function'
  ? ENDPOINTS[command]()
  : ENDPOINTS[command];

const fullUrl = `${BASE_URL}${endpoint}`;
const parsed = new URL(fullUrl);

const options = {
  hostname: parsed.hostname,
  port: parsed.port || (parsed.protocol === 'https:' ? 443 : 80),
  path: parsed.pathname + parsed.search,
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'Accept': 'application/json',
    'User-Agent': 'nova-openclaw-skill/1.1.0',
  },
};

const client = parsed.protocol === 'https:' ? https : http;

const req = client.request(options, (res) => {
  let data = '';
  res.on('data', (chunk) => { data += chunk; });
  res.on('end', () => {
    const remaining = res.headers['x-ratelimit-remaining'];
    const limit = res.headers['x-ratelimit-limit'];
    if (remaining !== undefined) {
      process.stderr.write(`Rate limit: ${remaining}/${limit} remaining\n`);
    }

    try {
      const json = JSON.parse(data);

      if (pretty && json.success && json.data && PRETTY_FORMATTERS[command]) {
        console.log(PRETTY_FORMATTERS[command](json.data));
      } else {
        console.log(JSON.stringify(json, null, 2));
      }

      process.exit(res.statusCode >= 400 ? 1 : 0);
    } catch {
      console.error(`HTTP ${res.statusCode}: ${data}`);
      process.exit(1);
    }
  });
});

req.on('error', (err) => {
  console.error(JSON.stringify({
    success: false,
    error: {
      code: 'NETWORK_ERROR',
      message: err.message,
    }
  }, null, 2));
  process.exit(1);
});

req.setTimeout(30000, () => {
  req.destroy();
  console.error(JSON.stringify({
    success: false,
    error: {
      code: 'TIMEOUT',
      message: 'Request timed out after 30 seconds',
    }
  }, null, 2));
  process.exit(1);
});

req.end();
