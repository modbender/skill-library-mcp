/**
 * Tests for openclaw-monitor
 */

import { describe, it, before, after, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { initDb } from '../src/db.js';
import { addTokenEvent, addTaskEvent, addCronRun } from '../src/collector.js';
import { computeAggregate } from '../src/aggregator.js';
import { getStatus, getTokenReport, getCostReport, getCronReport, getTaskReport } from '../src/reports.js';
import { refreshInterchange } from '../src/interchange.js';
import { backup, restore } from '../src/backup.js';

let db;
let tmpDir;

before(() => {
  tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'monitor-test-'));
});

beforeEach(() => {
  const dbPath = path.join(tmpDir, `test-${Date.now()}.db`);
  db = initDb(dbPath);
});

after(() => {
  try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch {}
});

describe('Token Events', () => {
  it('should ingest and deduplicate', () => {
    const r1 = addTokenEvent(db, { model: 'gpt-4', tokens_in: 100, tokens_out: 50, cost: 0.01, event_id: 'tok-1', timestamp: '2026-02-19 00:00:00' });
    assert.equal(r1.inserted, true);
    const r2 = addTokenEvent(db, { model: 'gpt-4', tokens_in: 100, tokens_out: 50, cost: 0.01, event_id: 'tok-1', timestamp: '2026-02-19 00:00:00' });
    assert.equal(r2.inserted, false);
    const count = db.prepare('SELECT COUNT(*) AS c FROM token_events').get().c;
    assert.equal(count, 1);
  });
});

describe('Task Events', () => {
  it('should ingest and query by status', () => {
    addTaskEvent(db, { command: 'deploy', status: 'success', duration_ms: 1000, timestamp: '2026-02-19 00:00:00' });
    addTaskEvent(db, { command: 'test', status: 'failure', duration_ms: 500, error: 'boom', timestamp: '2026-02-19 00:00:00' });
    const failed = db.prepare("SELECT * FROM task_events WHERE status = 'failure'").all();
    assert.equal(failed.length, 1);
    assert.equal(failed[0].command, 'test');
  });
});

describe('Cron Runs', () => {
  it('should ingest and query by job name', () => {
    addCronRun(db, { job_name: 'backup', status: 'success', duration_ms: 200, started: '2026-02-19 00:00:00' });
    addCronRun(db, { job_name: 'cleanup', status: 'failure', duration_ms: 100, error: 'disk full', started: '2026-02-19 00:00:00' });
    const backups = db.prepare("SELECT * FROM cron_runs WHERE job_name = 'backup'").all();
    assert.equal(backups.length, 1);
  });
});

describe('Daily Aggregates', () => {
  it('should compute correct totals', () => {
    addTokenEvent(db, { model: 'gpt-4', tokens_in: 100, tokens_out: 50, cost: 0.01, timestamp: '2026-02-19 00:00:00' });
    addTokenEvent(db, { model: 'claude', tokens_in: 200, tokens_out: 100, cost: 0.02, timestamp: '2026-02-19 00:00:00' });
    addTaskEvent(db, { command: 'build', status: 'success', duration_ms: 500, timestamp: '2026-02-19 00:00:00' });
    addTaskEvent(db, { command: 'test', status: 'failure', duration_ms: 300, timestamp: '2026-02-19 00:00:00' });
    const agg = computeAggregate(db, '2026-02-19');
    assert.equal(agg.total_tokens_in, 300);
    assert.equal(agg.total_tokens_out, 150);
    assert.equal(agg.total_cost, 0.03);
    assert.equal(agg.task_success, 1);
    assert.equal(agg.task_failure, 1);
  });
});

describe('Token Report by Model', () => {
  it('should group correctly', () => {
    addTokenEvent(db, { model: 'gpt-4', tokens_in: 100, tokens_out: 50, cost: 0.01, timestamp: '2026-02-18 00:00:00' });
    addTokenEvent(db, { model: 'gpt-4', tokens_in: 200, tokens_out: 100, cost: 0.02, timestamp: '2026-02-18 00:00:00' });
    addTokenEvent(db, { model: 'claude', tokens_in: 50, tokens_out: 25, cost: 0.005, timestamp: '2026-02-18 00:00:00' });
    const report = getTokenReport(db, { period: '30d', by: 'model' });
    const gpt4 = report.find(r => r.group_key === 'gpt-4');
    assert.equal(gpt4.tokens_in, 300);
    assert.equal(gpt4.events, 2);
  });
});

describe('Token Report by Period', () => {
  it('should filter by date', () => {
    addTokenEvent(db, { model: 'gpt-4', tokens_in: 100, tokens_out: 50, cost: 0.01, timestamp: '2026-02-18 00:00:00' });
    addTokenEvent(db, { model: 'gpt-4', tokens_in: 100, tokens_out: 50, cost: 0.01, timestamp: '2020-01-01 00:00:00' });
    const report = getTokenReport(db, { period: '30d' });
    assert.equal(report.length, 1);
  });
});

describe('Cost Report', () => {
  it('should compute correct totals with breakdown', () => {
    addTokenEvent(db, { model: 'gpt-4', tokens_in: 100, tokens_out: 50, cost: 0.05, timestamp: '2026-02-18 00:00:00' });
    addTokenEvent(db, { model: 'claude', tokens_in: 200, tokens_out: 100, cost: 0.10, timestamp: '2026-02-18 00:00:00' });
    const report = getCostReport(db, { period: 'month' });
    assert.ok(Math.abs(report.total - 0.15) < 0.001);
    assert.equal(report.by_model.length, 2);
    assert.equal(report.by_model[0].model, 'claude'); // highest cost first
  });
});

describe('Status Report', () => {
  it('should include all health indicators', () => {
    const status = getStatus(db);
    assert.ok('today_tokens_in' in status);
    assert.ok('today_tokens_out' in status);
    assert.ok('today_cost' in status);
    assert.ok('task_success' in status);
    assert.ok('task_failure' in status);
    assert.ok('task_timeout' in status);
    assert.ok('cron_ok' in status);
    assert.ok('cron_fail' in status);
    assert.ok('recent_errors' in status);
  });
});

describe('Interchange Refresh', () => {
  it('should generate valid .md files with correct layer separation', async () => {
    addTokenEvent(db, { model: 'gpt-4', tokens_in: 500, tokens_out: 200, cost: 0.05, timestamp: '2026-02-18 00:00:00' });
    addTaskEvent(db, { command: 'build', status: 'success', duration_ms: 100, timestamp: '2026-02-18 00:00:00' });
    await refreshInterchange(db);

    const interDir = path.join(path.dirname(new URL(import.meta.url).pathname), '..', 'interchange', 'monitoring');

    // Check ops/health.md exists and has no costs
    const healthPath = path.join(interDir, 'ops', 'health.md');
    assert.ok(fs.existsSync(healthPath), 'ops/health.md should exist');
    const healthContent = fs.readFileSync(healthPath, 'utf8');
    assert.ok(!healthContent.includes('$0.'), 'ops/health.md should not contain dollar amounts');
    assert.ok(!healthContent.includes('500'), 'ops/health.md should not contain token counts');

    // Check ops/capabilities.md exists
    assert.ok(fs.existsSync(path.join(interDir, 'ops', 'capabilities.md')));

    // Check state/status.md has actual data
    const statusPath = path.join(interDir, 'state', 'status.md');
    assert.ok(fs.existsSync(statusPath), 'state/status.md should exist');

    // Check state/token-spend.md exists
    assert.ok(fs.existsSync(path.join(interDir, 'state', 'token-spend.md')));

    // Verify frontmatter has correct layer
    assert.ok(healthContent.includes('layer: ops'));
    const statusContent = fs.readFileSync(statusPath, 'utf8');
    assert.ok(statusContent.includes('layer: state'));
  });
});

describe('Backup/Restore', () => {
  it('should round-trip correctly', async () => {
    addTokenEvent(db, { model: 'gpt-4', tokens_in: 100, tokens_out: 50, cost: 0.01, timestamp: '2026-02-19 00:00:00' });
    const backupPath = path.join(tmpDir, 'test-backup.db');
    await backup(db, backupPath);
    assert.ok(fs.existsSync(backupPath));

    const restorePath = path.join(tmpDir, 'restored.db');
    restore(backupPath, restorePath);
    const db2 = initDb(restorePath);
    const count = db2.prepare('SELECT COUNT(*) AS c FROM token_events').get().c;
    assert.equal(count, 1);
    db2.close();
  });
});
