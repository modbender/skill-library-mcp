#!/usr/bin/env node
/**
 * @module cli
 * Commander CLI entry point for the orchestration skill.
 */
import { Command } from 'commander';
import { initDb, closeDb } from './db.js';
import { createTask, listTasks, claimTask, completeTask, failTask, retryTask } from './queue.js';
import { registerAgent, listAgents, agentStatus } from './agents.js';
import { sweep } from './sweep.js';
import { refreshInterchange } from './interchange.js';
import { backup, restore } from './backup.js';

const program = new Command();
program.name('orch').description('Multi-agent task orchestration').version('1.0.0');

// Task commands
const task = program.command('task').description('Task management');

task.command('create <title>')
  .description('Create a new task')
  .option('--desc <description>', 'Task description', '')
  .option('--priority <priority>', 'Priority: high/medium/low', 'medium')
  .option('--timeout <minutes>', 'Timeout in minutes', '60')
  .option('--depends-on <ids>', 'Comma-separated dependency task IDs', '')
  .option('--created-by <agent>', 'Creating agent', 'cli')
  .option('--max-retries <n>', 'Max retries', '3')
  .action((title, opts) => {
    const db = initDb();
    const t = createTask(db, {
      title,
      description: opts.desc,
      priority: opts.priority,
      timeout: parseInt(opts.timeout, 10),
      dependsOn: opts.dependsOn ? opts.dependsOn.split(',').map(s => s.trim()) : [],
      createdBy: opts.createdBy,
      maxRetries: parseInt(opts.maxRetries, 10),
    });
    console.log(`Created task ${t.id}: ${t.title} [${t.priority}]`);
    closeDb();
  });

task.command('list')
  .description('List tasks')
  .option('--status <status>', 'Filter by status')
  .option('--agent <name>', 'Filter by agent')
  .action((opts) => {
    const db = initDb();
    const tasks = listTasks(db, { status: opts.status, agent: opts.agent });
    if (tasks.length === 0) { console.log('No tasks found.'); }
    else {
      for (const t of tasks) {
        console.log(`${t.id} | ${t.title} | ${t.status} | ${t.priority} | ${t.assigned_agent || '-'}`);
      }
    }
    closeDb();
  });

task.command('claim <task-id>')
  .description('Claim a task')
  .requiredOption('--agent <name>', 'Agent name')
  .action((taskId, opts) => {
    const db = initDb();
    try {
      const t = claimTask(db, taskId, opts.agent);
      if (t) console.log(`Task ${taskId} claimed by ${opts.agent}`);
      else console.error(`Failed to claim task ${taskId} (already taken or not pending)`);
    } catch (e) { console.error(e.message); }
    closeDb();
  });

task.command('complete <task-id>')
  .description('Complete a task')
  .option('--result-path <path>', 'Path to result file')
  .option('--summary <text>', 'Summary of result')
  .action((taskId, opts) => {
    const db = initDb();
    try {
      completeTask(db, taskId, { resultPath: opts.resultPath, summary: opts.summary });
      console.log(`Task ${taskId} completed.`);
    } catch (e) { console.error(e.message); }
    closeDb();
  });

task.command('fail <task-id>')
  .description('Fail a task')
  .option('--reason <text>', 'Reason for failure')
  .action((taskId, opts) => {
    const db = initDb();
    try {
      failTask(db, taskId, opts.reason);
      console.log(`Task ${taskId} marked as failed.`);
    } catch (e) { console.error(e.message); }
    closeDb();
  });

task.command('retry <task-id>')
  .description('Retry a failed task')
  .action((taskId) => {
    const db = initDb();
    try {
      retryTask(db, taskId);
      console.log(`Task ${taskId} re-queued for retry.`);
    } catch (e) { console.error(e.message); }
    closeDb();
  });

// Agent commands
const agent = program.command('agent').description('Agent management');

agent.command('register <name>')
  .description('Register a new agent')
  .option('--capabilities <list>', 'Comma-separated capabilities', '')
  .option('--max-concurrent <n>', 'Max concurrent tasks', '1')
  .action((name, opts) => {
    const db = initDb();
    try {
      const a = registerAgent(db, {
        name,
        capabilities: opts.capabilities ? opts.capabilities.split(',').map(s => s.trim()) : [],
        maxConcurrent: parseInt(opts.maxConcurrent, 10),
      });
      console.log(`Registered agent "${a.name}" with capabilities: ${a.capabilities.join(', ') || 'none'}`);
    } catch (e) { console.error(e.message); }
    closeDb();
  });

agent.command('list')
  .description('List all agents')
  .action(() => {
    const db = initDb();
    const agents = listAgents(db);
    if (agents.length === 0) { console.log('No agents registered.'); }
    else {
      for (const a of agents) {
        console.log(`${a.name} | capabilities: ${a.capabilities.join(', ')} | load: ${a.current_load}/${a.max_concurrent}`);
      }
    }
    closeDb();
  });

agent.command('status <name>')
  .description('Show agent status')
  .action((name) => {
    const db = initDb();
    try {
      const s = agentStatus(db, name);
      console.log(`Agent: ${s.name}`);
      console.log(`Capabilities: ${s.capabilities.join(', ')}`);
      console.log(`Load: ${s.current_load}/${s.max_concurrent}`);
      console.log(`Active tasks: ${s.activeTasks.length}`);
      for (const t of s.activeTasks) console.log(`  - ${t.id}: ${t.title}`);
    } catch (e) { console.error(e.message); }
    closeDb();
  });

// Top-level commands
program.command('sweep')
  .description('Timeout stale tasks and retry eligible ones')
  .action(() => {
    const db = initDb();
    const result = sweep(db);
    console.log(`Sweep complete: ${result.timedOut} timed out, ${result.retried} retried`);
    closeDb();
  });

program.command('refresh')
  .description('Regenerate all interchange .md files')
  .action(async () => {
    const db = initDb();
    await refreshInterchange(db);
    console.log('Interchange files refreshed.');
    closeDb();
  });

program.command('backup')
  .description('Backup the database')
  .option('--output <path>', 'Output file path')
  .action(async (opts) => {
    const db = initDb();
    try {
      const p = await backup(db, opts.output);
      console.log(`Backup saved to: ${p}`);
    } finally {
      closeDb();
    }
  });

program.command('restore <backup-file>')
  .description('Restore from a backup')
  .action((backupFile) => {
    restore(backupFile);
    console.log(`Database restored from: ${backupFile}`);
  });

program.parse();
