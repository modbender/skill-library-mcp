import fs from 'node:fs';
import path from 'node:path';

export const TOOL = 'costlens';
export const VERSION = '0.1.0';

const MODEL_RATES = {
  'gpt-4.1': { inputPer1k: 0.01, outputPer1k: 0.03 },
  'gpt-4o-mini': { inputPer1k: 0.00015, outputPer1k: 0.0006 },
  'claude-3-5-sonnet': { inputPer1k: 0.003, outputPer1k: 0.015 },
  default: { inputPer1k: 0.002, outputPer1k: 0.008 }
};

function nowIso() {
  return new Date().toISOString();
}

export function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith('--')) {
      args._.push(token);
      continue;
    }
    const key = token.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith('--')) {
      args[key] = true;
      continue;
    }
    args[key] = next;
    i += 1;
  }
  return args;
}

export function makeEnvelope(status, data = {}, errors = []) {
  return {
    tool: TOOL,
    version: VERSION,
    timestamp: nowIso(),
    status,
    data,
    errors
  };
}

function toNumber(value, fallback = 0) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function resolveRates(event) {
  const model = event.model || 'default';
  const base = MODEL_RATES[model] || MODEL_RATES.default;
  return {
    inputPer1k: toNumber(event.inputCostPer1k, base.inputPer1k),
    outputPer1k: toNumber(event.outputCostPer1k, base.outputPer1k)
  };
}

function dayOf(ts) {
  const d = new Date(ts || Date.now());
  return Number.isNaN(d.getTime()) ? 'unknown' : d.toISOString().slice(0, 10);
}

export function loadEvents(eventsPath) {
  const resolved = path.resolve(eventsPath);
  const raw = JSON.parse(fs.readFileSync(resolved, 'utf8'));
  if (!Array.isArray(raw)) {
    throw new Error('Events file must contain a JSON array');
  }
  return raw;
}

export function calculateCosts(events) {
  const totals = {
    inputTokens: 0,
    outputTokens: 0,
    totalTokens: 0,
    totalCost: 0
  };

  const byModel = {};
  const byDay = {};
  const invalidEvents = [];

  for (const event of events) {
    // Validate event structure
    if (!event || typeof event !== 'object') {
      invalidEvents.push({ event, reason: 'Invalid event structure' });
      continue;
    }
    
    const promptTokens = toNumber(event.promptTokens);
    const completionTokens = toNumber(event.completionTokens);
    
    // Validate non-negative tokens
    if (promptTokens < 0 || completionTokens < 0) {
      invalidEvents.push({ 
        event, 
        reason: `Negative token values: promptTokens=${promptTokens}, completionTokens=${completionTokens}` 
      });
      continue;
    }
    
    const totalTokens = promptTokens + completionTokens;
    const rates = resolveRates(event);
    const cost = (promptTokens / 1000) * rates.inputPer1k + (completionTokens / 1000) * rates.outputPer1k;

    totals.inputTokens += promptTokens;
    totals.outputTokens += completionTokens;
    totals.totalTokens += totalTokens;
    totals.totalCost += cost;

    const model = event.model || 'unknown';
    byModel[model] = byModel[model] || { model, calls: 0, tokens: 0, cost: 0 };
    byModel[model].calls += 1;
    byModel[model].tokens += totalTokens;
    byModel[model].cost += cost;

    const day = dayOf(event.timestamp);
    byDay[day] = byDay[day] || { day, calls: 0, tokens: 0, cost: 0 };
    byDay[day].calls += 1;
    byDay[day].tokens += totalTokens;
    byDay[day].cost += cost;
  }

  return {
    totals: {
      ...totals,
      totalCost: Number(totals.totalCost.toFixed(6))
    },
    byModel: Object.values(byModel).sort((a, b) => b.cost - a.cost),
    byDay: Object.values(byDay).sort((a, b) => a.day.localeCompare(b.day)),
    invalidEvents: invalidEvents.length > 0 ? invalidEvents : undefined
  };
}

export function checkBudget(summary, budget, thresholdPercent = 80) {
  const budgetNum = toNumber(budget);
  const thresholdNum = toNumber(thresholdPercent, 80);
  if (budgetNum <= 0) {
    throw new Error('Budget must be > 0');
  }

  const spent = summary.totals.totalCost;
  const usagePercent = (spent / budgetNum) * 100;
  const alertThreshold = Math.min(100, Math.max(0, thresholdNum));

  let level = 'ok';
  const alerts = [];
  if (usagePercent >= 100) {
    level = 'critical';
    alerts.push(`Budget exceeded: ${usagePercent.toFixed(2)}% used.`);
  } else if (usagePercent >= alertThreshold) {
    level = 'warning';
    alerts.push(`Budget threshold reached: ${usagePercent.toFixed(2)}% used (threshold ${alertThreshold}%).`);
  }

  return {
    budget: budgetNum,
    thresholdPercent: alertThreshold,
    spent: Number(spent.toFixed(6)),
    usagePercent: Number(usagePercent.toFixed(2)),
    remaining: Number((budgetNum - spent).toFixed(6)),
    level,
    alerts
  };
}

export function exportReport(report, outPath) {
  const resolved = path.resolve(outPath);
  fs.mkdirSync(path.dirname(resolved), { recursive: true });
  fs.writeFileSync(resolved, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  return resolved;
}

function fmtMoney(v) {
  return `$${Number(v).toFixed(4)}`;
}

function renderMonitorTable(summary, budgetStatus, invalidEvents) {
  const lines = [];
  lines.push('CostLens Monitor');
  lines.push(`Total calls: ${summary.byModel.reduce((n, m) => n + m.calls, 0)}`);
  lines.push(`Total tokens: ${summary.totals.totalTokens}`);
  lines.push(`Total cost: ${fmtMoney(summary.totals.totalCost)}`);
  if (budgetStatus) {
    lines.push(`Budget: ${fmtMoney(budgetStatus.budget)} | Used: ${budgetStatus.usagePercent}% | Level: ${budgetStatus.level}`);
  }
  lines.push('');
  lines.push('Top models by cost:');
  for (const row of summary.byModel.slice(0, 5)) {
    lines.push(`- ${row.model}: calls=${row.calls} tokens=${row.tokens} cost=${fmtMoney(row.cost)}`);
  }
  
  if (invalidEvents && invalidEvents.length > 0) {
    lines.push('');
    lines.push(`WARNING: ${invalidEvents.length} invalid events skipped:`);
    for (const item of invalidEvents.slice(0, 3)) {
      lines.push(`  - ${item.reason}`);
    }
    if (invalidEvents.length > 3) {
      lines.push(`  ... and ${invalidEvents.length - 3} more`);
    }
  }
  
  return lines.join('\n');
}

function printHelp() {
  console.log(`costlens usage:
  costlens monitor --events <path> [--budget <amount>] [--threshold <percent>] [--format <table|json>]
  costlens report --events <path> --out <path> [--budget <amount>] [--threshold <percent>] [--format <table|json>]
  costlens budget check --events <path> --budget <amount> [--threshold <percent>] [--format <table|json>]`);
}

export async function runCli(argv) {
  const args = parseArgs(argv);
  const command = args._[0];
  const format = args.format || 'table';

  if (!command || args.help) {
    printHelp();
    return command ? 0 : 1;
  }

  try {
    if (command === 'monitor' || command === 'report' || (command === 'budget' && args._[1] === 'check')) {
      const eventsPath = args.events;
      if (!eventsPath) {
        console.error(JSON.stringify(makeEnvelope('error', {}, ['--events is required']), null, 2));
        return 1;
      }

      const summary = calculateCosts(loadEvents(eventsPath));
      const needBudget = args.budget || command === 'budget';
      const budgetStatus = needBudget ? checkBudget(summary, args.budget, args.threshold || 80) : null;

      const report = {
        generatedAt: nowIso(),
        summary,
        budget: budgetStatus,
        invalidEvents: summary.invalidEvents
      };

      if (command === 'report') {
        if (!args.out) {
          console.error(JSON.stringify(makeEnvelope('error', {}, ['--out is required for report']), null, 2));
          return 1;
        }
        const outPath = exportReport(report, args.out);
        if (format === 'json') {
          console.log(JSON.stringify(makeEnvelope('ok', { outPath, report }), null, 2));
        } else {
          console.log(`Report exported: ${outPath}`);
        }
        return 0;
      }

      const status = budgetStatus?.level === 'critical' ? 'blocked' : budgetStatus?.level === 'warning' ? 'warning' : 'ok';
      const errors = [];
      if (budgetStatus?.alerts?.length) errors.push(...budgetStatus.alerts);
      if (summary.invalidEvents?.length) errors.push(`${summary.invalidEvents.length} invalid events skipped`);
      
      if (format === 'json') {
        console.log(JSON.stringify(makeEnvelope(status, report, errors), null, 2));
      } else {
        console.log(renderMonitorTable(summary, budgetStatus, summary.invalidEvents));
        if (budgetStatus?.alerts?.length) {
          console.log('');
          for (const alert of budgetStatus.alerts) {
            console.log(`ALERT: ${alert}`);
          }
        }
      }
      return status === 'blocked' ? 2 : 0;
    }

    printHelp();
    return 1;
  } catch (error) {
    console.error(JSON.stringify(makeEnvelope('error', {}, [error instanceof Error ? error.message : String(error)]), null, 2));
    return 1;
  }
}
