const fs = require('fs');
const path = require('path');

/**
 * Agent: Persistent AI worker with memory, state, and task execution
 */
class Agent {
  constructor(id, name, capabilities = []) {
    this.id = id;
    this.name = name;
    this.capabilities = capabilities; // ['research', 'design', 'development', etc]
    this.memoryPath = path.join(__dirname, `../data/${id}-memory.json`);
    this.statePath = path.join(__dirname, `../data/${id}-state.json`);
    this.memory = this.loadMemory();
    this.state = this.loadState();
  }

  /**
   * Load persistent memory (lessons learned, past tasks)
   */
  loadMemory() {
    try {
      if (fs.existsSync(this.memoryPath)) {
        return JSON.parse(fs.readFileSync(this.memoryPath, 'utf8'));
      }
    } catch (e) {
      console.warn(`Failed to load memory for ${this.id}:`, e.message);
    }
    return {
      id: this.id,
      name: this.name,
      capabilities: this.capabilities,
      tasksCompleted: 0,
      totalTokensBurned: 0,
      successRate: {}, // { taskType: 0.85, ... }
      lastActiveAt: null,
      lessons: [], // What we learned
    };
  }

  /**
   * Load current execution state
   */
  loadState() {
    try {
      if (fs.existsSync(this.statePath)) {
        return JSON.parse(fs.readFileSync(this.statePath, 'utf8'));
      }
    } catch (e) {
      console.warn(`Failed to load state for ${this.id}:`, e.message);
    }
    return {
      agentId: this.id,
      currentTask: null,
      progress: 0, // 0-100
      status: 'idle', // idle, working, blocked, done
      blockers: [],
      startedAt: null,
      estimatedCompletion: null,
      output: null,
      error: null,
    };
  }

  /**
   * Save memory to disk
   */
  saveMemory() {
    try {
      const dir = path.dirname(this.memoryPath);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(this.memoryPath, JSON.stringify(this.memory, null, 2), 'utf8');
    } catch (e) {
      console.error(`Failed to save memory for ${this.id}:`, e.message);
    }
  }

  /**
   * Save state to disk
   */
  saveState() {
    try {
      const dir = path.dirname(this.statePath);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(this.statePath, JSON.stringify(this.state, null, 2), 'utf8');
    } catch (e) {
      console.error(`Failed to save state for ${this.id}:`, e.message);
    }
  }

  /**
   * Start a task
   */
  startTask(task) {
    this.state.currentTask = task;
    this.state.status = 'working';
    this.state.progress = 0;
    this.state.startedAt = new Date().toISOString();
    this.state.blockers = [];
    this.state.error = null;
    this.saveState();
  }

  /**
   * Update progress
   */
  updateProgress(progress, message = '') {
    this.state.progress = Math.min(100, progress);
    if (message) {
      console.log(`[${this.name}] ${message}`);
    }
    this.saveState();
  }

  /**
   * Complete task with output
   */
  completeTask(output) {
    this.state.currentTask = null;
    this.state.status = 'done';
    this.state.progress = 100;
    this.state.output = output;
    this.memory.tasksCompleted++;
    this.memory.lastActiveAt = new Date().toISOString();
    this.saveState();
    this.saveMemory();
    return output;
  }

  /**
   * Hit a blocker
   */
  setBlocker(message) {
    this.state.status = 'blocked';
    this.state.blockers.push({
      message,
      timestamp: new Date().toISOString(),
    });
    this.saveState();
  }

  /**
   * Record an error
   */
  recordError(error) {
    this.state.status = 'blocked';
    this.state.error = {
      message: error.message || String(error),
      timestamp: new Date().toISOString(),
      stack: error.stack,
    };
    this.saveState();
  }

  /**
   * Learn a lesson (captured for next agent)
   */
  learnLesson(category, lesson) {
    this.memory.lessons.push({
      category,
      lesson,
      learnedAt: new Date().toISOString(),
    });
    this.saveMemory();
  }

  /**
   * Reset to idle (ready for next task)
   */
  reset() {
    this.state = {
      agentId: this.id,
      currentTask: null,
      progress: 0,
      status: 'idle',
      blockers: [],
      startedAt: null,
      estimatedCompletion: null,
      output: null,
      error: null,
    };
    this.saveState();
  }

  /**
   * Get agent status (for dashboard)
   */
  getStatus() {
    return {
      id: this.id,
      name: this.name,
      capabilities: this.capabilities,
      status: this.state.status,
      currentTask: this.state.currentTask,
      progress: this.state.progress,
      blockers: this.state.blockers,
      error: this.state.error,
      lastActiveAt: this.memory.lastActiveAt,
      tasksCompleted: this.memory.tasksCompleted,
    };
  }
}

module.exports = Agent;
