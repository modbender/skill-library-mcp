/**
 * Orchestration skill tests.
 */
import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import Database from 'better-sqlite3';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { runMigrations } from '../src/db.js';
import { createTask, listTasks, claimTask, completeTask, failTask, retryTask, getTask } from '../src/queue.js';
import { registerAgent, listAgents, agentStatus } from '../src/agents.js';
import { sweep } from '../src/sweep.js';
import { refreshInterchange } from '../src/interchange.js';
import { readMd } from '../../interchange/src/index.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

let db;

beforeEach(() => {
  db = new Database(':memory:');
  db.pragma('journal_mode = WAL');
  db.pragma('foreign_keys = ON');
  // Run migration SQL directly for in-memory DB
  const sql = fs.readFileSync(path.join(__dirname, '..', 'migrations', '001_initial.sql'), 'utf8');
  const upSection = sql.split('-- DOWN')[0].replace('-- UP', '').trim();
  db.exec(upSection);
});

afterEach(() => {
  db.close();
  // Clean up interchange files
  const interchangeDir = path.join(__dirname, '..', 'interchange');
  if (fs.existsSync(interchangeDir)) {
    fs.rmSync(interchangeDir, { recursive: true, force: true });
  }
});

describe('Task Lifecycle', () => {
  it('1. Create task → list shows it pending', () => {
    const task = createTask(db, { title: 'Test task', description: 'Do stuff', priority: 'high' });
    assert.ok(task.id.startsWith('task-'));
    assert.equal(task.status, 'pending');
    assert.equal(task.priority, 'high');

    const tasks = listTasks(db);
    assert.equal(tasks.length, 1);
    assert.equal(tasks[0].status, 'pending');
  });

  it('2. Claim task → DB updated, list shows claimed', () => {
    registerAgent(db, { name: 'agent-a', capabilities: ['coding'] });
    const task = createTask(db, { title: 'Claim me' });
    const claimed = claimTask(db, task.id, 'agent-a');
    assert.equal(claimed.status, 'claimed');
    assert.equal(claimed.assigned_agent, 'agent-a');

    const tasks = listTasks(db, { status: 'claimed' });
    assert.equal(tasks.length, 1);
  });

  it('3. Two agents claim same task → only one succeeds', () => {
    registerAgent(db, { name: 'agent-a' });
    registerAgent(db, { name: 'agent-b' });
    const task = createTask(db, { title: 'Race condition' });

    const claim1 = claimTask(db, task.id, 'agent-a');
    const claim2 = claimTask(db, task.id, 'agent-b');

    assert.ok(claim1 !== null);
    assert.equal(claim2, null);
  });

  it('4. Complete task → result recorded, handoff log updated', () => {
    registerAgent(db, { name: 'agent-a' });
    const task = createTask(db, { title: 'Complete me' });
    claimTask(db, task.id, 'agent-a');
    const completed = completeTask(db, task.id, { resultPath: '/output.md', summary: 'Done' });

    assert.equal(completed.status, 'completed');

    const result = db.prepare('SELECT * FROM results WHERE task_id = ?').get(task.id);
    assert.equal(result.output_path, '/output.md');
    assert.equal(result.summary, 'Done');

    const logs = db.prepare('SELECT * FROM handoff_log WHERE task_id = ? ORDER BY id').all(task.id);
    assert.ok(logs.some(l => l.action === 'completed'));
  });

  it('5. Task with unmet dependencies → claim rejected', () => {
    registerAgent(db, { name: 'agent-a' });
    const dep = createTask(db, { title: 'Dependency' });
    const task = createTask(db, { title: 'Dependent', dependsOn: [dep.id] });

    assert.throws(() => claimTask(db, task.id, 'agent-a'), /unmet dependencies/);
  });

  it('6. Task with met dependencies → claim succeeds', () => {
    registerAgent(db, { name: 'agent-a' });
    const dep = createTask(db, { title: 'Dependency' });
    claimTask(db, dep.id, 'agent-a');
    completeTask(db, dep.id);

    const task = createTask(db, { title: 'Dependent', dependsOn: [dep.id] });
    const claimed = claimTask(db, task.id, 'agent-a');
    assert.ok(claimed !== null);
    assert.equal(claimed.status, 'claimed');
  });

  it('7. Timed-out task → sweep marks failed', () => {
    registerAgent(db, { name: 'agent-a' });
    const task = createTask(db, { title: 'Slow task', timeout: 0 });
    claimTask(db, task.id, 'agent-a');

    // Manually set claimed_at to the past
    db.prepare("UPDATE tasks SET claimed_at = datetime('now', '-2 hours') WHERE id = ?").run(task.id);

    const result = sweep(db);
    assert.ok(result.timedOut >= 1);

    // Should be retried (pending) since retry_count < max_retries
    const updated = getTask(db, task.id);
    assert.equal(updated.status, 'pending');
  });

  it('8. Failed task with retries left → sweep re-queues as pending', () => {
    registerAgent(db, { name: 'agent-a' });
    const task = createTask(db, { title: 'Retry me', timeout: 0, maxRetries: 2 });
    claimTask(db, task.id, 'agent-a');
    db.prepare("UPDATE tasks SET claimed_at = datetime('now', '-2 hours') WHERE id = ?").run(task.id);

    const result = sweep(db);
    assert.equal(result.retried, 1);

    const updated = getTask(db, task.id);
    assert.equal(updated.status, 'pending');
    assert.equal(updated.retry_count, 1);
  });

  it('8b. Failed task with no retries left stays failed', () => {
    registerAgent(db, { name: 'agent-a' });
    const task = createTask(db, { title: 'No retries', timeout: 0, maxRetries: 0 });
    claimTask(db, task.id, 'agent-a');
    db.prepare("UPDATE tasks SET claimed_at = datetime('now', '-2 hours') WHERE id = ?").run(task.id);

    sweep(db);
    const updated = getTask(db, task.id);
    assert.equal(updated.status, 'failed');
  });
});

describe('Agent Management', () => {
  it('9. Agent register → shows in agent list with capabilities', () => {
    registerAgent(db, { name: 'research-bot', capabilities: ['research', 'writing'], maxConcurrent: 3 });
    const agents = listAgents(db);
    assert.equal(agents.length, 1);
    assert.equal(agents[0].name, 'research-bot');
    assert.deepEqual(agents[0].capabilities, ['research', 'writing']);
    assert.equal(agents[0].max_concurrent, 3);
  });

  it('Agent status shows active tasks', () => {
    registerAgent(db, { name: 'agent-a', capabilities: ['coding'] });
    const task = createTask(db, { title: 'Active task' });
    claimTask(db, task.id, 'agent-a');

    const status = agentStatus(db, 'agent-a');
    assert.equal(status.activeTasks.length, 1);
    assert.equal(status.current_load, 1);
  });
});

describe('Interchange', () => {
  it('10. Interchange refresh → generates valid .md files with correct frontmatter', async () => {
    registerAgent(db, { name: 'agent-a', capabilities: ['coding'] });
    const task = createTask(db, { title: 'Interchange test', createdBy: 'test-agent' });

    await refreshInterchange(db);

    const interchangeDir = path.join(__dirname, '..', 'interchange', 'orchestration');

    // Check ops files exist
    assert.ok(fs.existsSync(path.join(interchangeDir, 'ops', 'capabilities.md')));
    assert.ok(fs.existsSync(path.join(interchangeDir, 'ops', 'agents.md')));
    assert.ok(fs.existsSync(path.join(interchangeDir, 'ops', 'schemas.md')));

    // Check state files
    assert.ok(fs.existsSync(path.join(interchangeDir, 'state', 'queue.md')));
    assert.ok(fs.existsSync(path.join(interchangeDir, 'state', 'tasks', `${task.id}.md`)));

    // Validate frontmatter
    const taskMd = readMd(path.join(interchangeDir, 'state', 'tasks', `${task.id}.md`));
    assert.equal(taskMd.meta.skill, 'orchestration');
    assert.equal(taskMd.meta.layer, 'state');
    assert.equal(taskMd.meta.task_id, task.id);
    assert.equal(taskMd.meta.status, 'pending');
    assert.equal(taskMd.meta.created_by, 'test-agent');

    const queueMd = readMd(path.join(interchangeDir, 'state', 'queue.md'));
    assert.equal(queueMd.meta.skill, 'orchestration');
    assert.equal(queueMd.meta.layer, 'state');
    assert.ok(queueMd.content.includes(task.id));
  });
});

describe('Manual retry', () => {
  it('Retry a failed task manually', () => {
    const task = createTask(db, { title: 'Fail then retry', maxRetries: 3 });
    registerAgent(db, { name: 'agent-a' });
    claimTask(db, task.id, 'agent-a');
    failTask(db, task.id, 'oops');

    const failed = getTask(db, task.id);
    assert.equal(failed.status, 'failed');

    retryTask(db, task.id);
    const retried = getTask(db, task.id);
    assert.equal(retried.status, 'pending');
    assert.equal(retried.retry_count, 1);
  });
});
