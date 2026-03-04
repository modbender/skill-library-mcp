#!/usr/bin/env node
/**
 * @module cli
 * Commander CLI entry point for openclaw-monitor.
 */

import { Command } from 'commander';
import { getDb, closeDb } from './db.js';
import { addTokenEvent, addTaskEvent, addCronRun } from './collector.js';
import { computeAggregate, computeAllMissing } from './aggregator.js';
import { getStatus, getTokenReport, getCronReport, getTaskReport, getCostReport } from './reports.js';
import { refreshInterchange } from './interchange.js';
import { backup, restore } from './backup.js';

const program = new Command();
program.name('monitor').description('OpenClaw monitoring dashboard').version('1.0.0');

program.command('status').description('Quick system health summary').action(() => {
  const db = getDb();
  const s = getStatus(db);
  const taskTotal = s.task_success + s.task_failure + s.task_timeout;
  const taskRate = taskTotal > 0 ? ((s.task_success / taskTotal) * 100).toFixed(1) : 'N/A';
  const taskIcon = taskTotal === 0 ? '⚪' : (s.task_failure + s.task_timeout === 0) ? '🟢' : '🔴';
  const cronIcon = (s.cron_ok + s.cron_fail === 0) ? '⚪' : s.cron_fail === 0 ? '🟢' : '🔴';

  console.log(`\n📊 System Status`);
  console.log(`  Tokens today: ${s.today_tokens_in.toLocaleString()} in / ${s.today_tokens_out.toLocaleString()} out ($${s.today_cost.toFixed(4)})`);
  console.log(`  ${taskIcon} Tasks: ${s.task_success} ok / ${s.task_failure} fail / ${s.task_timeout} timeout (${taskRate}% success)`);
  console.log(`  ${cronIcon} Crons: ${s.cron_ok} ok / ${s.cron_fail} fail`);
  if (s.recent_errors.length > 0) {
    console.log(`\n  ⚠️  Recent errors:`);
    s.recent_errors.forEach(e => console.log(`    - ${e.command}: ${e.error || 'unknown'}`));
  }
  closeDb();
});

program.command('tokens').description('Token usage report')
  .option('--period <period>', 'Time period (e.g. 7d, 30d)', '7d')
  .option('--by <grouping>', 'Group by model or skill', 'model')
  .action((opts) => {
    const db = getDb();
    const rows = getTokenReport(db, opts);
    console.log(`\n📈 Token Usage (last ${opts.period}, by ${opts.by})`);
    if (rows.length === 0) { console.log('  No data.'); closeDb(); return; }
    rows.forEach(r => console.log(`  ${r.group_key}: ${r.tokens_in.toLocaleString()} in / ${r.tokens_out.toLocaleString()} out — $${r.cost.toFixed(4)} (${r.events} events)`));
    closeDb();
  });

program.command('crons').description('Cron job health').action(() => {
  const db = getDb();
  const rows = getCronReport(db);
  console.log(`\n⏰ Cron Health`);
  if (rows.length === 0) { console.log('  No cron data.'); closeDb(); return; }
  rows.forEach(r => {
    const icon = r.failure === 0 ? '🟢' : '🔴';
    console.log(`  ${icon} ${r.job_name}: ${r.success}/${r.total} ok, avg ${r.avg_duration_ms}ms, last: ${r.last_run}`);
  });
  closeDb();
});

program.command('tasks').description('Recent task history')
  .option('--failed', 'Show only failed tasks')
  .action((opts) => {
    const db = getDb();
    const rows = getTaskReport(db, opts);
    console.log(`\n📋 Task History${opts.failed ? ' (failures only)' : ''}`);
    if (rows.length === 0) { console.log('  No tasks.'); closeDb(); return; }
    rows.forEach(r => {
      const icon = r.status === 'success' ? '✅' : '❌';
      console.log(`  ${icon} ${r.command} — ${r.status} (${r.duration_ms}ms) ${r.error ? '— ' + r.error : ''}`);
    });
    closeDb();
  });

program.command('cost').description('Cost breakdown')
  .option('--period <period>', 'week or month', 'week')
  .action((opts) => {
    const db = getDb();
    const report = getCostReport(db, opts);
    console.log(`\n💰 Cost Report (${opts.period})`);
    console.log(`  Total: $${report.total.toFixed(4)}`);
    if (report.by_model.length > 0) {
      console.log(`\n  By Model:`);
      report.by_model.forEach(r => console.log(`    ${r.model}: $${r.cost.toFixed(4)}`));
    }
    if (report.by_day.length > 0) {
      console.log(`\n  By Day:`);
      report.by_day.forEach(r => console.log(`    ${r.date}: $${r.cost.toFixed(4)}`));
    }
    closeDb();
  });

// Ingest subcommands
const ingest = program.command('ingest').description('Manual event ingestion');

ingest.command('token').description('Ingest a token event')
  .requiredOption('--model <model>', 'Model name')
  .requiredOption('--in <n>', 'Tokens in', parseInt)
  .requiredOption('--out <n>', 'Tokens out', parseInt)
  .requiredOption('--cost <c>', 'Cost in USD', parseFloat)
  .option('--skill <skill>', 'Skill name')
  .action((opts) => {
    const db = getDb();
    const result = addTokenEvent(db, { model: opts.model, tokens_in: opts.in, tokens_out: opts.out, cost: opts.cost, skill: opts.skill });
    console.log(result.inserted ? `✅ Token event ingested (${result.event_id})` : `⏭️  Duplicate, skipped`);
    closeDb();
  });

ingest.command('task').description('Ingest a task event')
  .requiredOption('--command <cmd>', 'Command name')
  .requiredOption('--status <status>', 'success|failure|timeout')
  .requiredOption('--duration <ms>', 'Duration in ms', parseInt)
  .option('--error <error>', 'Error message')
  .action((opts) => {
    const db = getDb();
    const result = addTaskEvent(db, { command: opts.command, status: opts.status, duration_ms: opts.duration, error: opts.error });
    console.log(result.inserted ? `✅ Task event ingested (${result.event_id})` : `⏭️  Duplicate, skipped`);
    closeDb();
  });

ingest.command('cron').description('Ingest a cron event')
  .requiredOption('--job <name>', 'Job name')
  .requiredOption('--status <status>', 'success|failure')
  .requiredOption('--duration <ms>', 'Duration in ms', parseInt)
  .option('--error <error>', 'Error message')
  .action((opts) => {
    const db = getDb();
    const result = addCronRun(db, { job_name: opts.job, status: opts.status, duration_ms: opts.duration, error: opts.error });
    console.log(result.inserted ? `✅ Cron event ingested (${result.event_id})` : `⏭️  Duplicate, skipped`);
    closeDb();
  });

program.command('aggregate').description('Compute daily aggregates')
  .option('--date <date>', 'Specific date (YYYY-MM-DD)')
  .action((opts) => {
    const db = getDb();
    if (opts.date) {
      const row = computeAggregate(db, opts.date);
      console.log(`✅ Aggregated ${opts.date}: ${row.total_tokens_in} in, ${row.total_tokens_out} out, $${row.total_cost.toFixed(4)}, ${row.task_success} ok / ${row.task_failure} fail`);
    } else {
      const count = computeAllMissing(db);
      console.log(`✅ Aggregated ${count} missing date(s)`);
    }
    closeDb();
  });

program.command('refresh').description('Regenerate interchange .md files').action(async () => {
  const db = getDb();
  await refreshInterchange(db);
  console.log('✅ Interchange files refreshed');
  closeDb();
});

program.command('backup').description('Backup database')
  .option('--output <path>', 'Output path')
  .action(async (opts) => {
    const db = getDb();
    const p = await backup(db, opts.output);
    console.log(`✅ Backed up to ${p}`);
    closeDb();
  });

program.command('restore').description('Restore database')
  .argument('<backup-file>', 'Path to backup file')
  .action((file) => {
    restore(file);
    console.log(`✅ Restored from ${file}`);
  });

program.parse();
