const Agent = require('./agent');
const TaskRouter = require('./task-router');
const Executor = require('./executor');

/**
 * AgentOS: Complete system for multi-agent project execution
 */
class AgentOS {
  constructor(projectId = 'agent-os-' + Date.now()) {
    this.projectId = projectId;
    this.agents = [];
    this.taskRouter = null;
    this.executor = null;
  }

  /**
   * Register an agent
   */
  registerAgent(id, name, capabilities = []) {
    const agent = new Agent(id, name, capabilities);
    this.agents.push(agent);
    console.log(`✅ Registered agent: ${name} (${capabilities.join(', ')})`);
    return agent;
  }

  /**
   * Initialize the system
   */
  initialize() {
    this.taskRouter = new TaskRouter(this.agents);
    this.executor = new Executor(this.projectId, this.agents, this.taskRouter);
    console.log(`✅ AgentOS initialized (Project: ${this.projectId})`);
  }

  /**
   * Run a project
   */
  async runProject(goal, taskTypes = []) {
    if (!this.executor) this.initialize();

    await this.executor.initializeProject(goal, taskTypes);
    await this.executor.execute();

    return this.getStatus();
  }

  /**
   * Get full system status
   */
  getStatus() {
    if (!this.executor) return null;
    return this.executor.getStatus();
  }

  /**
   * Get agent status by ID
   */
  getAgentStatus(agentId) {
    const agent = this.agents.find((a) => a.id === agentId);
    return agent ? agent.getStatus() : null;
  }

  /**
   * Export for saving
   */
  toJSON() {
    return {
      projectId: this.projectId,
      agents: this.agents.map((a) => a.getStatus()),
      status: this.getStatus(),
    };
  }
}

module.exports = { AgentOS, Agent, TaskRouter, Executor };
