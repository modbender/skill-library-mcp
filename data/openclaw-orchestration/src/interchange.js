/**
 * @module interchange
 * Generate ops/ and state/ .md files from DB state.
 */
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { writeMd, serializeTable } from '../../interchange/src/index.js';
import { taskToMd } from './protocol.js';
import { listTasks } from './queue.js';
import { listAgents } from './agents.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const INTERCHANGE_ROOT = path.join(__dirname, '..', 'interchange', 'orchestration');

/**
 * Refresh all interchange .md files from current DB state.
 * @param {import('better-sqlite3').Database} db
 */
export async function refreshInterchange(db) {
  await generateCapabilities();
  await generateAgentsMd(db);
  await generateSchemas(db);
  await generateQueue(db);
  await generateTaskFiles(db);
}

/**
 * Generate ops/capabilities.md
 */
async function generateCapabilities() {
  const fm = {
    skill: 'orchestration',
    type: 'summary',
    layer: 'ops',
    version: 1,
    generator: 'orchestration@1.0.0',
    tags: ['capabilities', 'reference'],
  };
  const content = `# Orchestration Capabilities

## Commands
- \`task create\` — Create a new task with title, description, priority, timeout, dependencies
- \`task list\` — List tasks with optional status/agent filters
- \`task claim\` — Atomically claim a pending task for an agent
- \`task complete\` — Mark a task completed with optional result path and summary
- \`task fail\` — Mark a task as failed
- \`task retry\` — Re-queue a failed task
- \`agent register\` — Register a new agent with capabilities
- \`agent list\` — List all registered agents
- \`agent status\` — Show agent status and active tasks
- \`sweep\` — Timeout stale tasks and retry eligible ones
- \`refresh\` — Regenerate all interchange .md files

## Supported Priorities
high, medium, low

## Task Statuses
pending, claimed, in-progress, completed, failed
`;
  await writeMd(path.join(INTERCHANGE_ROOT, 'ops', 'capabilities.md'), fm, content);
}

/**
 * Generate ops/agents.md
 * @param {import('better-sqlite3').Database} db
 */
async function generateAgentsMd(db) {
  const agents = listAgents(db);
  const fm = {
    skill: 'orchestration',
    type: 'summary',
    layer: 'ops',
    version: 1,
    generator: 'orchestration@1.0.0',
    tags: ['agents'],
  };

  let content = '# Registered Agents\n\n';
  if (agents.length === 0) {
    content += 'No agents registered.\n';
  } else {
    const headers = ['Name', 'Capabilities', 'Max Concurrent', 'Current Load'];
    const rows = agents.map(a => [a.name, a.capabilities.join(', '), String(a.max_concurrent), String(a.current_load)]);
    content += serializeTable(headers, rows) + '\n';
  }
  await writeMd(path.join(INTERCHANGE_ROOT, 'ops', 'agents.md'), fm, content);
}

/**
 * Generate ops/schemas.md
 * @param {import('better-sqlite3').Database} db
 */
async function generateSchemas(db) {
  const migrations = db.prepare('SELECT * FROM _migrations ORDER BY version').all();
  const fm = {
    skill: 'orchestration',
    type: 'summary',
    layer: 'ops',
    version: 1,
    generator: 'orchestration@1.0.0',
    tags: ['schema'],
  };

  let content = '# Database Schema\n\n';
  content += `## Current Version\n${migrations.length > 0 ? migrations[migrations.length - 1].version : 0}\n\n`;
  content += '## Applied Migrations\n';
  for (const m of migrations) {
    content += `- v${m.version}: ${m.name} (applied ${m.applied_at})\n`;
  }
  content += '\n';
  await writeMd(path.join(INTERCHANGE_ROOT, 'ops', 'schemas.md'), fm, content);
}

/**
 * Generate state/queue.md
 * @param {import('better-sqlite3').Database} db
 */
async function generateQueue(db) {
  const tasks = listTasks(db);
  const fm = {
    skill: 'orchestration',
    type: 'summary',
    layer: 'state',
    version: 1,
    generator: 'orchestration@1.0.0',
    tags: ['queue'],
  };

  let content = '# Task Queue\n\n';
  if (tasks.length === 0) {
    content += 'No tasks in queue.\n';
  } else {
    const headers = ['ID', 'Title', 'Status', 'Priority', 'Agent', 'Created'];
    const rows = tasks.map(t => [t.id, t.title, t.status, t.priority, t.assigned_agent || '-', t.created_at]);
    content += serializeTable(headers, rows) + '\n';
  }
  await writeMd(path.join(INTERCHANGE_ROOT, 'state', 'queue.md'), fm, content);
}

/**
 * Generate state/tasks/{id}.md for each task.
 * @param {import('better-sqlite3').Database} db
 */
async function generateTaskFiles(db) {
  const tasks = listTasks(db);
  for (const task of tasks) {
    const result = db.prepare('SELECT * FROM results WHERE task_id = ?').get(task.id);
    const { frontmatter, content } = taskToMd(task, result);
    await writeMd(
      path.join(INTERCHANGE_ROOT, 'state', 'tasks', `${task.id}.md`),
      frontmatter,
      content
    );
  }
}
