import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { calculateCosts, checkBudget, exportReport, runCli } from './src/index.js';

const events = JSON.parse(fs.readFileSync(new URL('./fixtures/events.json', import.meta.url), 'utf8'));

const summary = calculateCosts(events);
assert.equal(summary.totals.totalTokens, 9400);
assert.equal(summary.byModel.length, 3);
assert.equal(summary.totals.totalCost > 0, true);

const budgetWarning = checkBudget(summary, 0.08, 50);
assert.equal(budgetWarning.level, 'warning');

const budgetCritical = checkBudget(summary, 0.03, 80);
assert.equal(budgetCritical.level, 'critical');

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'costlens-'));
const eventsPath = path.join(tmpDir, 'events.json');
fs.writeFileSync(eventsPath, JSON.stringify(events, null, 2));

const reportPath = path.join(tmpDir, 'report.json');
const exported = exportReport({ hello: 'world' }, reportPath);
assert.equal(fs.existsSync(exported), true);

const monitorCode = await runCli(['monitor', '--events', eventsPath, '--budget', '0.1', '--threshold', '75']);
assert.equal(monitorCode, 0);

const budgetBlockedCode = await runCli(['budget', 'check', '--events', eventsPath, '--budget', '0.03', '--format', 'json']);
assert.equal(budgetBlockedCode, 2);

const reportCode = await runCli(['report', '--events', eventsPath, '--out', path.join(tmpDir, 'cost-report.json'), '--format', 'json']);
assert.equal(reportCode, 0);

console.log('costlens tests passed');
