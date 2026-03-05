/**
 * @module agents
 * Agent registry logic.
 */
import { v4 as uuidv4 } from 'uuid';

/**
 * Register a new agent.
 * @param {import('better-sqlite3').Database} db
 * @param {object} opts
 * @param {string} opts.name
 * @param {string[]} [opts.capabilities]
 * @param {number} [opts.maxConcurrent]
 * @returns {object}
 */
export function registerAgent(db, opts) {
  const { name, capabilities = [], maxConcurrent = 1 } = opts;
  const id = `agent-${uuidv4().slice(0, 8)}`;

  try {
    db.prepare(`INSERT INTO agents (id, name, capabilities, max_concurrent) VALUES (?, ?, ?, ?)`)
      .run(id, name, JSON.stringify(capabilities), maxConcurrent);
  } catch (err) {
    if (err.message.includes('UNIQUE')) throw new Error(`Agent "${name}" already exists`);
    throw err;
  }

  return getAgent(db, name);
}

/**
 * Get an agent by name.
 * @param {import('better-sqlite3').Database} db
 * @param {string} name
 * @returns {object|null}
 */
export function getAgent(db, name) {
  const row = db.prepare('SELECT * FROM agents WHERE name = ?').get(name);
  if (row) row.capabilities = JSON.parse(row.capabilities);
  return row || null;
}

/**
 * List all agents.
 * @param {import('better-sqlite3').Database} db
 * @returns {object[]}
 */
export function listAgents(db) {
  return db.prepare('SELECT * FROM agents ORDER BY name').all()
    .map(r => ({ ...r, capabilities: JSON.parse(r.capabilities) }));
}

/**
 * Get agent status including current tasks.
 * @param {import('better-sqlite3').Database} db
 * @param {string} name
 * @returns {object}
 */
export function agentStatus(db, name) {
  const agent = getAgent(db, name);
  if (!agent) throw new Error(`Agent "${name}" not found`);
  const tasks = db.prepare("SELECT * FROM tasks WHERE assigned_agent = ? AND status IN ('claimed','in-progress')")
    .all(name).map(r => ({ ...r, depends_on: JSON.parse(r.depends_on) }));
  return { ...agent, activeTasks: tasks };
}
