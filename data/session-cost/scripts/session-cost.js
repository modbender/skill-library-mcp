#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');

const DEFAULT_PATH = path.join(os.homedir(), '.openclaw', 'agents', 'main', 'sessions');

function parseArgs(argv) {
  const args = {
    path: DEFAULT_PATH,
    offset: null,
    format: 'text',
    details: false,
    detailsSessionId: null,
    provider: null,
    table: false,
    help: false
  };
  let i = 0;

  while (i < argv.length) {
    if (argv[i] === '--help' || argv[i] === '-h') {
      args.help = true;
    } else if (argv[i] === '--offset' && i + 1 < argv.length) {
      args.offset = argv[++i];
    } else if (argv[i] === '--format' && i + 1 < argv.length) {
      args.format = argv[++i];
    } else if (argv[i] === '--json') {
      args.format = 'json';  // backwards compat
    } else if (argv[i] === '--path' && i + 1 < argv.length) {
      args.path = argv[++i];
    } else if (argv[i] === '--provider' && i + 1 < argv.length) {
      args.provider = argv[++i].toLowerCase();
    } else if (argv[i] === '--table') {
      args.table = true;
    } else if (argv[i] === '--details') {
      args.details = true;
      if (i + 1 < argv.length && !argv[i + 1].startsWith('-')) {
        args.detailsSessionId = argv[++i];
      }
    }
    i++;
  }

  return args;
}

function parseTimeOffset(offsetStr) {
  if (!offsetStr) return null;

  const match = offsetStr.match(/^(\d+)([mhd])$/);
  if (!match) {
    console.error('Invalid time format. Use: 30m, 2h, 7d');
    process.exit(1);
  }

  const value = parseInt(match[1]);
  const unit = match[2];

  let ms;
  switch (unit) {
    case 'm': ms = value * 60 * 1000; break;
    case 'h': ms = value * 60 * 60 * 1000; break;
    case 'd': ms = value * 24 * 60 * 60 * 1000; break;
  }

  return Date.now() - ms;
}

function findJsonlFiles(dirPath) {
  const files = [];

  function walk(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);

      if (entry.isDirectory()) {
        walk(fullPath);
      } else if (entry.isFile() && entry.name.endsWith('.jsonl')) {
        files.push(fullPath);
      }
    }
  }

  walk(dirPath);
  return files;
}

function analyzeSession(filePath, cutoffTime) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n').filter(l => l.trim());

  const usage = {
    input: 0,
    output: 0,
    cacheRead: 0,
    cacheWrite: 0,
    totalTokens: 0,
    costInput: 0,
    costOutput: 0,
    costCacheRead: 0,
    costCacheWrite: 0,
    costTotal: 0
  };

  let api = null;
  let model = null;
  let provider = null;
  let sessionId = null;
  let firstTimestamp = null;
  let lastTimestamp = null;

  for (const line of lines) {
    try {
      const record = JSON.parse(line);

      if (record.type === 'session') {
        sessionId = record.id;
      }

      if (record.timestamp) {
        const ts = new Date(record.timestamp).getTime();
        if (!firstTimestamp || ts < firstTimestamp) firstTimestamp = ts;
        if (!lastTimestamp || ts > lastTimestamp) lastTimestamp = ts;
      }

      if (record.type === 'message' && record.message?.usage) {
        const msg = record.message;

        const u = msg.usage;
        usage.input += u.input || 0;
        usage.output += u.output || 0;
        usage.cacheRead += u.cacheRead || 0;
        usage.cacheWrite += u.cacheWrite || 0;
        usage.totalTokens += u.totalTokens || 0;

        if (u.cost) {
          usage.costInput += u.cost.input || 0;
          usage.costOutput += u.cost.output || 0;
          usage.costCacheRead += u.cost.cacheRead || 0;
          usage.costCacheWrite += u.cost.cacheWrite || 0;
          usage.costTotal += u.cost.total || 0;
        }

        // Use last provider/model with non-zero cost (prefer real API calls over delivery wrappers)
        if (u.cost && u.cost.total > 0) {
          if (msg.api) api = msg.api;
          if (msg.model) model = msg.model;
          if (msg.provider) provider = msg.provider;
        }
      }
    } catch (err) {
      // Skip malformed lines
    }
  }

  if (cutoffTime && firstTimestamp && firstTimestamp < cutoffTime) {
    return null;
  }

  return {
    file: path.basename(filePath),
    fullPath: filePath,
    sessionId,
    api: api || 'unknown',
    provider: provider || 'unknown',
    model: model || 'unknown',
    usage,
    firstTimestamp: firstTimestamp ? new Date(firstTimestamp).toISOString() : null,
    lastTimestamp: lastTimestamp ? new Date(lastTimestamp).toISOString() : null,
    durationMin: firstTimestamp && lastTimestamp ?
      Math.round((lastTimestamp - firstTimestamp) / 1000 / 60) : 0
  };
}

function sumUsage(sessions) {
  return sessions.reduce((acc, r) => ({
    input: acc.input + r.usage.input,
    output: acc.output + r.usage.output,
    cacheRead: acc.cacheRead + r.usage.cacheRead,
    cacheWrite: acc.cacheWrite + r.usage.cacheWrite,
    totalTokens: acc.totalTokens + r.usage.totalTokens,
    costInput: acc.costInput + r.usage.costInput,
    costOutput: acc.costOutput + r.usage.costOutput,
    costCacheRead: acc.costCacheRead + r.usage.costCacheRead,
    costCacheWrite: acc.costCacheWrite + r.usage.costCacheWrite,
    costTotal: acc.costTotal + r.usage.costTotal
  }), {
    input: 0, output: 0, cacheRead: 0, cacheWrite: 0, totalTokens: 0,
    costInput: 0, costOutput: 0, costCacheRead: 0, costCacheWrite: 0, costTotal: 0
  });
}

function groupByModel(results) {
  const groups = {};
  for (const r of results) {
    const key = `${r.provider}/${r.model}`;
    if (!groups[key]) groups[key] = [];
    groups[key].push(r);
  }
  return groups;
}

function formatTokens(tokens) {
  if (tokens >= 1000000) {
    return (tokens / 1000000).toFixed(1) + 'M';
  } else if (tokens >= 1000) {
    return (tokens / 1000).toFixed(1) + 'K';
  }
  return tokens.toString();
}

function printTableHeader() {
  console.log('Model'.padEnd(35) + 'Duration'.padEnd(12) + 'Tokens'.padEnd(14) + 'Cache'.padEnd(20) + 'Cost'.padEnd(12) + 'Session');
  console.log('─'.repeat(125));
}

function printTableRow(result) {
  const session = (result.sessionId || 'unknown').slice(0, 32);
  const model = `${result.provider}/${result.model}`.slice(0, 32);
  const duration = `${result.durationMin} min`;
  const tokens = formatTokens(result.usage.totalTokens);
  const cache = `${formatTokens(result.usage.cacheRead)} / ${formatTokens(result.usage.cacheWrite)}`;
  const cost = `$${result.usage.costTotal.toFixed(4)}`;

  console.log(
    model.padEnd(35) +
    duration.padEnd(12) +
    tokens.padEnd(14) +
    cache.padEnd(20) +
    cost.padEnd(12) +
    session
  );
}

function printModelSummary(label, sessions, totals) {
  console.log(`\n${label}`);
  console.log('-'.repeat(80));
  console.log(`  Sessions: ${sessions.length}`);
  console.log(`  Tokens:   ${totals.totalTokens.toLocaleString()} (input: ${totals.input.toLocaleString()}, output: ${totals.output.toLocaleString()})`);
  console.log(`  Cache:    read: ${totals.cacheRead.toLocaleString()} tokens, write: ${totals.cacheWrite.toLocaleString()} tokens`);
  console.log(`  Cost:     $${totals.costTotal.toFixed(4)}`);
  console.log(`    Input:       $${totals.costInput.toFixed(4)}`);
  console.log(`    Output:      $${totals.costOutput.toFixed(4)}`);
  console.log(`    Cache read:  $${totals.costCacheRead.toFixed(4)}  (included in total, discounted rate)`);
  console.log(`    Cache write: $${totals.costCacheWrite.toFixed(4)}  (included in total)`);
}

function buildJsonOutput(results, groups, offset) {
  const modelSummaries = {};
  for (const [model, sessions] of Object.entries(groups)) {
    const totals = sumUsage(sessions);
    modelSummaries[model] = {
      sessions: sessions.length,
      tokens: { input: totals.input, output: totals.output, total: totals.totalTokens },
      cache: { read: totals.cacheRead, write: totals.cacheWrite },
      cost: {
        total: round4(totals.costTotal),
        input: round4(totals.costInput),
        output: round4(totals.costOutput),
        cacheRead: round4(totals.costCacheRead),
        cacheWrite: round4(totals.costCacheWrite)
      }
    };
  }

  const modelKeys = Object.keys(modelSummaries);
  const output = { models: modelSummaries };

  if (modelKeys.length > 1) {
    const grandTotals = sumUsage(results);
    output.grandTotal = {
      sessions: results.length,
      tokens: { input: grandTotals.input, output: grandTotals.output, total: grandTotals.totalTokens },
      cache: { read: grandTotals.cacheRead, write: grandTotals.cacheWrite },
      cost: {
        total: round4(grandTotals.costTotal),
        input: round4(grandTotals.costInput),
        output: round4(grandTotals.costOutput),
        cacheRead: round4(grandTotals.costCacheRead),
        cacheWrite: round4(grandTotals.costCacheWrite)
      }
    };
  }

  if (offset) output.offset = offset;

  return output;
}

function round4(n) {
  return Math.round(n * 10000) / 10000;
}

function formatDiscord(results, groups, offset) {
  const lines = [];

  // Header with emoji
  lines.push('💰 **Usage Summary**');
  if (offset) {
    lines.push(`(last ${offset})`);
  }
  lines.push('');

  // Grand totals
  const grandTotals = sumUsage(results);
  lines.push(`**Total Cost:** $${grandTotals.costTotal.toFixed(2)}`);
  lines.push(`**Total Tokens:** ${formatTokens(grandTotals.totalTokens)}`);
  lines.push(`**Sessions:** ${results.length}`);

  // Group by provider
  const byProvider = {};
  for (const r of results) {
    const p = r.provider;
    if (!byProvider[p]) {
      byProvider[p] = [];
    }
    byProvider[p].push(r);
  }

  if (Object.keys(byProvider).length > 1) {
    lines.push('');
    lines.push('**By Provider:**');
    for (const [provider, sessions] of Object.entries(byProvider)) {
      const totals = sumUsage(sessions);
      lines.push(`• ${provider}: $${totals.costTotal.toFixed(2)} (${formatTokens(totals.totalTokens)} tokens)`);
    }
  }

  // Top models (limit to 5)
  const modelEntries = Object.entries(groups)
    .map(([model, sessions]) => ({
      model,
      totals: sumUsage(sessions)
    }))
    .sort((a, b) => b.totals.costTotal - a.totals.costTotal)
    .slice(0, 5);

  if (modelEntries.length > 0) {
    lines.push('');
    lines.push('**Top Models:**');
    for (const entry of modelEntries) {
      lines.push(`• ${entry.model}: $${entry.totals.costTotal.toFixed(2)} (${formatTokens(entry.totals.totalTokens)} tokens)`);
    }
  }

  return lines.join('\n');
}

function printHelp() {
  console.log('Usage: node session-cost.js [options]');
  console.log('');
  console.log('Analyze OpenClaw session logs for token usage, costs, and performance metrics.');
  console.log('');
  console.log('Options:');
  console.log('  --path <dir>         Directory to scan for .jsonl files');
  console.log(`                       Default: ~/.openclaw/agents/main/sessions/`);
  console.log('  --offset <time>      Only include sessions from the last N units (30m, 2h, 7d)');
  console.log('  --provider <name>    Filter by model provider (anthropic, openai, ollama, etc.)');
  console.log('  --details [id]       Show per-session details. Optionally specify a session ID');
  console.log('                       to show only that session (looks for <id>.jsonl)');
  console.log('  --table              Show details in compact table format (use with --details)');
  console.log('  --format <type>      Output format: text (default), json, or discord');
  console.log('  --json               Shorthand for --format json (backwards compat)');
  console.log('  --help, -h           Show this help message');
  console.log('');
  console.log('Examples:');
  console.log('  node session-cost.js                          # Summary of all sessions');
  console.log('  node session-cost.js --details --table        # All sessions in table format');
  console.log('  node session-cost.js --details abc123         # Details for one session');
  console.log('  node session-cost.js --offset 24h             # Last 24 hours summary');
  console.log('  node session-cost.js --provider anthropic     # Only Anthropic sessions');
  console.log('  node session-cost.js --path /other/dir --json # Custom path, JSON output');
}

function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.help) {
    printHelp();
    process.exit(0);
  }

  if (!fs.existsSync(args.path)) {
    console.error(`Error: Path does not exist: ${args.path}`);
    process.exit(1);
  }

  const cutoffTime = parseTimeOffset(args.offset);

  // Single session mode: look for <id>.jsonl
  if (args.detailsSessionId) {
    const sessionFile = path.join(args.path, `${args.detailsSessionId}.jsonl`);
    if (!fs.existsSync(sessionFile)) {
      console.error(`Error: Session file not found: ${sessionFile}`);
      process.exit(1);
    }

    const result = analyzeSession(sessionFile, cutoffTime);
    if (!result) {
      console.log('Session did not match the time criteria.');
      return;
    }

    if (args.format === 'json') {
      console.log(JSON.stringify(result, null, 2));
      return;
    }

    console.log(`Session: ${result.sessionId || 'unknown'}`);
    console.log(`Model: ${result.provider}/${result.model} (${result.api})`);
    console.log(`Duration: ${result.durationMin} minutes`);
    console.log(`Timestamps: ${result.firstTimestamp || 'N/A'} → ${result.lastTimestamp || 'N/A'}`);
    console.log(`Tokens: input=${result.usage.input.toLocaleString()}, output=${result.usage.output.toLocaleString()}, total=${result.usage.totalTokens.toLocaleString()}`);
    console.log(`Cache: read=${result.usage.cacheRead.toLocaleString()}, write=${result.usage.cacheWrite.toLocaleString()}`);
    console.log(`Cost: $${result.usage.costTotal.toFixed(4)} (input=$${result.usage.costInput.toFixed(4)}, output=$${result.usage.costOutput.toFixed(4)})`);
    return;
  }

  const files = findJsonlFiles(args.path);
  let results = [];

  for (const file of files) {
    const result = analyzeSession(file, cutoffTime);
    if (result) results.push(result);
  }

  if (results.length === 0) {
    if (args.format === 'json') {
      console.log(JSON.stringify({ models: {}, sessions: 0 }));
    } else {
      console.log('No sessions matched the criteria.');
    }
    return;
  }

  // Filter by provider if specified
  if (args.provider) {
    const originalCount = results.length;
    results = results.filter(r => r.provider.toLowerCase() === args.provider);
    if (results.length === 0 && args.format !== 'json') {
      console.log(`No sessions matched provider filter: ${args.provider}`);
      console.log(`(Found ${originalCount} sessions total, but none matched the provider)`);
      return;
    }
  }

  // Sort by timestamp (newest first)
  results.sort((a, b) => {
    const aTime = a.lastTimestamp || a.firstTimestamp || 0;
    const bTime = b.lastTimestamp || b.firstTimestamp || 0;
    return new Date(bTime) - new Date(aTime);
  });

  const groups = groupByModel(results);
  const modelKeys = Object.keys(groups);

  // JSON output
  if (args.format === 'json') {
    console.log(JSON.stringify(buildJsonOutput(results, groups, args.offset), null, 2));
    return;
  }

  // Discord output
  if (args.format === 'discord') {
    console.log(formatDiscord(results, groups, args.offset));
    return;
  }

  // Text output
  const filters = [];
  if (args.offset && cutoffTime) {
    filters.push(`sessions from the last ${args.offset} (since ${new Date(cutoffTime).toISOString()})`);
  }
  if (args.provider) {
    filters.push(`provider=${args.provider}`);
  }
  if (filters.length > 0) {
    console.log(`Filtering: ${filters.join(', ')}\n`);
  }

  console.log(`Found ${files.length} .jsonl files, ${results.length} matched\n`);

  // Per-session details (only when --details is used)
  if (args.details) {
    console.log('SESSION DETAILS');
    console.log('='.repeat(125));

    if (args.table) {
      printTableHeader();
      for (const r of results) {
        printTableRow(r);
      }
    } else {
      for (const r of results) {
        console.log(`\nSession: ${r.sessionId || 'unknown'}`);
        console.log(`Model: ${r.provider}/${r.model} (${r.api})`);
        console.log(`Duration: ${r.durationMin} minutes`);
        console.log(`Timestamps: ${r.firstTimestamp || 'N/A'} → ${r.lastTimestamp || 'N/A'}`);
        console.log(`Tokens: input=${r.usage.input.toLocaleString()}, output=${r.usage.output.toLocaleString()}, total=${r.usage.totalTokens.toLocaleString()}`);
        console.log(`Cache: read=${r.usage.cacheRead.toLocaleString()}, write=${r.usage.cacheWrite.toLocaleString()}`);
        console.log(`Cost: $${r.usage.costTotal.toFixed(4)} (input=$${r.usage.costInput.toFixed(4)}, output=$${r.usage.costOutput.toFixed(4)})`);
      }
    }
  }

  // Summary grouped by model
  console.log('\n' + '='.repeat(100));
  console.log('SUMMARY BY MODEL');
  console.log('='.repeat(100));

  for (const [model, sessions] of Object.entries(groups)) {
    const totals = sumUsage(sessions);
    printModelSummary(model, sessions, totals);
  }

  // Grand total only when multiple models
  if (modelKeys.length > 1) {
    const grandTotals = sumUsage(results);
    console.log('\n' + '='.repeat(100));
    console.log('GRAND TOTAL');
    console.log('='.repeat(100));
    printModelSummary(`All models (${modelKeys.length})`, results, grandTotals);
  }
}

main();
