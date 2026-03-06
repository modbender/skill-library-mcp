/**
 * @module interchange
 * Generate ops/ and state/ interchange .md files.
 * ops/ files contain ZERO actual costs, token counts, or user data.
 */

import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { writeMd } from '../../interchange/src/index.js';
import { getStatus, getTokenReport, getCostReport, getCronReport } from './reports.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const INTERCHANGE_DIR = path.join(__dirname, '..', 'interchange', 'monitoring');

const BASE_META = {
  skill: 'monitoring',
  generator: 'monitoring@1.0.0',
};

/**
 * Generate all interchange files.
 * @param {import('better-sqlite3').Database} db
 */
export async function refreshInterchange(db) {
  await writeCapabilities();
  await writeHealth(db);
  await writeStatus(db);
  await writeTokenSpend(db);
}

/**
 * Write ops/capabilities.md — static command reference.
 */
async function writeCapabilities() {
  const meta = {
    ...BASE_META,
    type: 'summary',
    layer: 'ops',
    version: 1,
    tags: ['capabilities', 'reference'],
  };

  const content = `# Monitoring Capabilities

## Commands
- \`monitor status\` — System health summary
- \`monitor tokens [--period 7d|30d] [--by model|skill]\` — Token usage
- \`monitor crons\` — Cron job health
- \`monitor tasks [--failed]\` — Task history
- \`monitor cost [--period month|week]\` — Cost breakdown
- \`monitor ingest token|task|cron\` — Manual event ingestion
- \`monitor aggregate\` — Compute daily aggregates
- \`monitor refresh\` — Regenerate interchange files
- \`monitor backup\` / \`monitor restore\` — Backup and restore

## What It Monitors
- Token spend by model and skill
- Task success/failure/timeout rates
- Cron job reliability and timing
- Daily cost aggregates
`;

  await writeMd(path.join(INTERCHANGE_DIR, 'ops', 'capabilities.md'), meta, content);
}

/**
 * Write ops/health.md — status indicators only, NO actual costs/tokens.
 * @param {import('better-sqlite3').Database} db
 */
async function writeHealth(db) {
  const status = getStatus(db);

  const taskTotal = status.task_success + status.task_failure + status.task_timeout;
  const taskHealthy = taskTotal === 0 || (status.task_failure + status.task_timeout) / taskTotal < 0.1;
  const cronHealthy = status.cron_fail === 0;
  const hasActivity = status.today_tokens_in > 0 || taskTotal > 0;

  const taskIcon = taskTotal === 0 ? '⚪' : taskHealthy ? '🟢' : '🔴';
  const cronIcon = status.cron_ok + status.cron_fail === 0 ? '⚪' : cronHealthy ? '🟢' : '🔴';
  const overallIcon = (taskHealthy && cronHealthy) ? '🟢' : '🟡';

  const meta = {
    ...BASE_META,
    type: 'summary',
    layer: 'ops',
    version: 1,
    tags: ['health', 'status', 'system'],
  };

  const content = `# System Health

${overallIcon} **Overall:** ${taskHealthy && cronHealthy ? 'Healthy' : 'Degraded'}

## Subsystems
- ${taskIcon} **Tasks:** ${taskTotal === 0 ? 'No activity today' : taskHealthy ? 'Healthy' : 'Failures detected'}
- ${cronIcon} **Crons:** ${status.cron_ok + status.cron_fail === 0 ? 'No runs today' : cronHealthy ? 'All passing' : 'Failures detected'}
- ${hasActivity ? '🟢' : '⚪'} **Token Collection:** ${hasActivity ? 'Active' : 'No data today'}

## Recent Errors
${status.recent_errors.length === 0 ? 'None' : status.recent_errors.map(e => `- ${e.command}: ${e.error || 'unknown error'}`).join('\n')}
`;

  await writeMd(path.join(INTERCHANGE_DIR, 'ops', 'health.md'), meta, content);
}

/**
 * Write state/status.md — full detailed status with actual numbers.
 * @param {import('better-sqlite3').Database} db
 */
async function writeStatus(db) {
  const status = getStatus(db);
  const crons = getCronReport(db);
  const taskTotal = status.task_success + status.task_failure + status.task_timeout;
  const successRate = taskTotal > 0 ? ((status.task_success / taskTotal) * 100).toFixed(1) : 'N/A';

  const meta = {
    ...BASE_META,
    type: 'detail',
    layer: 'state',
    version: 1,
    tags: ['status', 'detail'],
  };

  const cronTable = crons.length === 0 ? 'No cron data.' :
    ['| Job | Success | Failure | Last Run | Avg Duration |', '| --- | --- | --- | --- | --- |',
      ...crons.map(c => `| ${c.job_name} | ${c.success} | ${c.failure} | ${c.last_run} | ${c.avg_duration_ms}ms |`)
    ].join('\n');

  const content = `# System Status (Detailed)

## Today's Token Spend
- **Tokens In:** ${status.today_tokens_in}
- **Tokens Out:** ${status.today_tokens_out}
- **Cost:** $${status.today_cost.toFixed(4)}

## Task Success Rate
- **Total:** ${taskTotal}
- **Success:** ${status.task_success} | **Failure:** ${status.task_failure} | **Timeout:** ${status.task_timeout}
- **Rate:** ${successRate}%

## Cron Health
${cronTable}

## Warnings
${status.recent_errors.length === 0 ? 'None' : status.recent_errors.map(e => `- ⚠️ ${e.command} failed: ${e.error || 'unknown'} (${e.timestamp})`).join('\n')}
`;

  await writeMd(path.join(INTERCHANGE_DIR, 'state', 'status.md'), meta, content);
}

/**
 * Write state/token-spend.md — 7-day breakdown.
 * @param {import('better-sqlite3').Database} db
 */
async function writeTokenSpend(db) {
  const cost = getCostReport(db, { period: '7d' });

  const meta = {
    ...BASE_META,
    type: 'detail',
    layer: 'state',
    version: 1,
    tags: ['tokens', 'cost', 'spend'],
  };

  // Find top model per day
  const rows = cost.by_day.map(d => {
    const dayModels = db.prepare(`
      SELECT model, SUM(cost) AS cost FROM token_events WHERE date(timestamp) = ? GROUP BY model ORDER BY cost DESC LIMIT 1
    `).get(d.date);
    return `| ${d.date} | ${d.tokens_in} | ${d.tokens_out} | $${d.cost.toFixed(4)} | ${dayModels?.model || '-'} |`;
  });

  const content = `# Token Spend (Last 7 Days)

| Date | Tokens In | Tokens Out | Cost | Top Model |
| --- | --- | --- | --- | --- |
${rows.join('\n')}

**Week Total:** $${cost.total.toFixed(4)}
`;

  await writeMd(path.join(INTERCHANGE_DIR, 'state', 'token-spend.md'), meta, content);
}
