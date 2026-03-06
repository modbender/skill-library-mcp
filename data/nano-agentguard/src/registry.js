/**
 * Registry - Agent Registration & Metadata
 *
 * Tracks agents with their owners, permissions, and status
 */

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const { v4: uuidv4 } = require('uuid');

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);

class Registry {
  constructor(registryPath) {
    this.registryPath = registryPath || path.join(process.env.HOME, '.agentguard', 'registry.json');
    this.agents = null;
  }

  /**
   * Load registry from disk
   */
  async load() {
    if (this.agents) return this.agents;

    if (fs.existsSync(this.registryPath)) {
      const data = await readFile(this.registryPath, 'utf8');
      this.agents = JSON.parse(data);
    } else {
      this.agents = { agents: {}, version: '1.0' };
    }

    return this.agents;
  }

  /**
   * Save registry to disk
   */
  async save() {
    await writeFile(this.registryPath, JSON.stringify(this.agents, null, 2));
  }

  /**
   * Register a new agent
   */
  async register(agentId, options = {}) {
    await this.load();

    if (this.agents.agents[agentId]) {
      throw new Error(`Agent already registered: ${agentId}`);
    }

    const agent = {
      id: agentId,
      uuid: uuidv4(),
      owner: options.owner || 'unknown',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      status: 'active',
      permissions: {
        level: options.level || 'read',
        dangerous: options.dangerous || 'require-approval'
      },
      metadata: options.metadata || {},
      stats: {
        operations: 0,
        approvals: 0,
        denials: 0
      }
    };

    this.agents.agents[agentId] = agent;
    await this.save();

    return agent;
  }

  /**
   * Get agent by ID
   */
  async get(agentId) {
    await this.load();

    const agent = this.agents.agents[agentId];
    if (!agent) {
      throw new Error(`Agent not found: ${agentId}`);
    }

    return agent;
  }

  /**
   * Update agent
   */
  async update(agentId, updates) {
    await this.load();

    const agent = this.agents.agents[agentId];
    if (!agent) {
      throw new Error(`Agent not found: ${agentId}`);
    }

    Object.assign(agent, updates, {
      updatedAt: new Date().toISOString()
    });

    await this.save();
    return agent;
  }

  /**
   * Unregister agent
   */
  async unregister(agentId) {
    await this.load();

    if (!this.agents.agents[agentId]) {
      return false;
    }

    delete this.agents.agents[agentId];
    await this.save();

    return true;
  }

  /**
   * List all agents
   */
  async list(filter = {}) {
    await this.load();

    let agents = Object.values(this.agents.agents);

    if (filter.owner) {
      agents = agents.filter(a => a.owner === filter.owner);
    }
    if (filter.status) {
      agents = agents.filter(a => a.status === filter.status);
    }
    if (filter.level) {
      agents = agents.filter(a => a.permissions.level === filter.level);
    }

    return agents;
  }

  /**
   * Update agent stats
   */
  async incrementStats(agentId, field) {
    await this.load();

    const agent = this.agents.agents[agentId];
    if (agent) {
      agent.stats[field] = (agent.stats[field] || 0) + 1;
      await this.save();
    }
  }
}

module.exports = Registry;
