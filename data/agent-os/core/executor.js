const fs = require('fs');
const path = require('path');

/**
 * Executor: Run tasks sequentially, track progress, save state
 */
class Executor {
  constructor(projectId, agents, taskRouter) {
    this.projectId = projectId;
    this.agents = agents;
    this.taskRouter = taskRouter;
    this.projectPath = path.join(__dirname, `../data/${projectId}-project.json`);
    this.project = this.loadProject();
  }

  /**
   * Load project state from disk
   */
  loadProject() {
    try {
      if (fs.existsSync(this.projectPath)) {
        return JSON.parse(fs.readFileSync(this.projectPath, 'utf8'));
      }
    } catch (e) {
      console.warn(`Failed to load project ${this.projectId}:`, e.message);
    }
    return {
      projectId: this.projectId,
      createdAt: new Date().toISOString(),
      goal: null,
      taskTypes: [],
      tasks: [],
      status: 'planning', // planning, executing, paused, complete, failed
      startedAt: null,
      completedAt: null,
      notes: [],
    };
  }

  /**
   * Save project state to disk
   */
  saveProject() {
    try {
      const dir = path.dirname(this.projectPath);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(this.projectPath, JSON.stringify(this.project, null, 2), 'utf8');
    } catch (e) {
      console.error(`Failed to save project ${this.projectId}:`, e.message);
    }
  }

  /**
   * Initialize project with goal and task types
   */
  async initializeProject(goal, taskTypes) {
    console.log(`\n📋 Initializing project: "${goal}"`);
    console.log(`   Task types: ${taskTypes.join(', ')}\n`);

    this.project.goal = goal;
    this.project.taskTypes = taskTypes;
    this.project.tasks = this.taskRouter.decompose(goal, taskTypes);
    this.project.status = 'executing';
    this.project.startedAt = new Date().toISOString();

    this.saveProject();

    // Print task plan
    console.log('📑 Task Plan:');
    this.project.tasks.forEach((task) => {
      console.log(`  [${task.id}] ${task.name} → ${task.assignedAgentName} (${task.estimatedMinutes}m)`);
    });
    console.log('');

    return this.project;
  }

  /**
   * Execute all tasks sequentially
   */
  async execute() {
    console.log(`🚀 Starting execution for "${this.project.goal}"\n`);

    while (true) {
      const nextTask = this.taskRouter.getNextTask(this.project.tasks);
      if (!nextTask) break;

      await this.executeTask(nextTask);
    }

    // Mark complete
    this.project.status = 'complete';
    this.project.completedAt = new Date().toISOString();
    this.saveProject();

    console.log(`\n✅ Project complete! All tasks finished.`);
    console.log(`   Status: ${this.taskRouter.getProjectStatus(this.project.tasks)}`);
  }

  /**
   * Execute a single task
   */
  async executeTask(task) {
    const agent = this.agents.find((a) => a.id === task.assignedAgent);
    if (!agent) {
      console.error(`❌ No agent found for task ${task.id}`);
      return;
    }

    console.log(`⏳ [Task ${task.id}] ${task.name} (${agent.name})`);
    task.status = 'in-progress';
    this.saveProject();

    agent.startTask(task);

    try {
      // Simulate task execution with progress
      for (let i = 0; i <= 100; i += 25) {
        agent.updateProgress(i, `  Progress: ${i}%`);
        await this.sleep(500); // Simulate work
      }

      // Mark task complete
      const output = `Task "${task.name}" completed successfully.`;
      task.output = output;
      task.status = 'complete';
      agent.completeTask(output);
      this.saveProject();

      console.log(`✅ [Task ${task.id}] Complete\n`);
    } catch (error) {
      console.error(`❌ [Task ${task.id}] Error: ${error.message}`);
      task.status = 'blocked';
      agent.recordError(error);
      this.saveProject();
    }
  }

  /**
   * Get current project status (for dashboard)
   */
  getStatus() {
    const projectStatus = this.taskRouter.getProjectStatus(this.project.tasks);
    const agentStatuses = this.agents.map((a) => a.getStatus());

    return {
      projectId: this.projectId,
      goal: this.project.goal,
      status: this.project.status,
      progress: projectStatus.progress,
      taskStats: projectStatus,
      agents: agentStatuses,
      tasks: this.project.tasks,
      startedAt: this.project.startedAt,
      completedAt: this.project.completedAt,
    };
  }

  /**
   * Utility: sleep
   */
  sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

module.exports = Executor;
