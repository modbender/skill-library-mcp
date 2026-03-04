import { parseArgs } from 'node:util';
import { loadConfig } from './config/index.js';
import { LogReader } from './logging/reader.js';
import { computeStats, formatStatsTable } from './logging/stats.js';

const { values } = parseArgs({
  options: {
    days: { type: 'string', short: 'd', default: '30' },
    format: { type: 'string', short: 'f', default: 'table' },
    help: { type: 'boolean', short: 'h', default: false },
  },
  strict: false,
});

if (values.help) {
  console.log(`
Clawd Throttle - Routing Statistics

Usage: npm run stats -- [options]

Options:
  -d, --days <n>       Lookback period in days (default: 30)
  -f, --format <fmt>   Output format: table or json (default: table)
  -h, --help           Show this help message

Examples:
  npm run stats                     Show last 30 days (table)
  npm run stats -- -d 7             Show last 7 days
  npm run stats -- -f json          Output as JSON
  npm run stats -- -d 90 -f json    Last 90 days as JSON
`);
  process.exit(0);
}

const config = loadConfig();
const reader = new LogReader(config.logging.logFilePath);

const days = parseInt(values.days as string, 10) || 30;
const since = new Date();
since.setDate(since.getDate() - days);

const entries = reader.readSince(since.toISOString());
const stats = computeStats(entries);

if (values.format === 'json') {
  console.log(JSON.stringify(stats, null, 2));
} else {
  console.log(formatStatsTable(stats, days));
}
