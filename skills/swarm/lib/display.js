/**
 * Swarm Display
 * Pretty console output for swarm operations
 */

const { swarmEvents, EVENTS } = require('./events');

class SwarmDisplay {
  constructor(options = {}) {
    this.enabled = options.enabled !== false;
    this.compact = options.compact || false;
    this.isTTY = process.stdout.isTTY;
    
    // State for live updates
    this.tasks = new Map();
    this.workers = new Map();
    this.startTime = null;
    this.totalTasks = 0;
    this.completedTasks = 0;
    this.failedTasks = 0;
    this.currentPhase = null;
    
    // Bind event handlers
    if (this.enabled) {
      this.attachListeners();
    }
  }
  
  attachListeners() {
    swarmEvents.on(EVENTS.SWARM_START, (data) => this.onSwarmStart(data));
    swarmEvents.on(EVENTS.SWARM_COMPLETE, (data) => this.onSwarmComplete(data));
    swarmEvents.on(EVENTS.PHASE_START, (data) => this.onPhaseStart(data));
    swarmEvents.on(EVENTS.TASK_START, (data) => this.onTaskStart(data));
    swarmEvents.on(EVENTS.TASK_COMPLETE, (data) => this.onTaskComplete(data));
    swarmEvents.on(EVENTS.TASK_ERROR, (data) => this.onTaskError(data));
    swarmEvents.on(EVENTS.WORKER_SPAWN, (data) => this.onWorkerSpawn(data));
    swarmEvents.on(EVENTS.PROGRESS, (data) => this.onProgress(data));
  }
  
  detach() {
    swarmEvents.removeAllListeners();
  }
  
  // === Event Handlers ===
  
  onSwarmStart(data) {
    this.startTime = Date.now();
    this.totalTasks = data.totalTasks || 0;
    this.completedTasks = 0;
    this.failedTasks = 0;
    
    console.log('');
    console.log(`🐝 ${this.bold('Swarm initializing...')}`);
    console.log(`   ${this.dim(`${data.phases} phase(s), up to ${data.maxWorkers} workers`)}`);
    console.log('');
  }
  
  onSwarmComplete(data) {
    const duration = ((Date.now() - this.startTime) / 1000).toFixed(1);
    const successRate = this.totalTasks > 0 
      ? Math.round((this.completedTasks / this.totalTasks) * 100) 
      : 100;
    
    console.log('');
    console.log(`🐝 ${this.bold('Swarm complete')} ${this.green('✓')}`);
    console.log(`   ${this.completedTasks}/${this.totalTasks} tasks (${successRate}% success)`);
    console.log(`   ${duration}s total`);
    
    if (data.speedup && data.speedup > 1) {
      console.log(`   ${this.cyan(`⚡ ${data.speedup.toFixed(1)}x faster`)} than sequential`);
    }
    
    if (this.failedTasks > 0) {
      console.log(`   ${this.yellow(`⚠ ${this.failedTasks} failed`)}`);
    }
    
    console.log('');
  }
  
  onPhaseStart(data) {
    this.currentPhase = data.name;
    console.log(`   ${this.dim('─'.repeat(40))}`);
    console.log(`   Phase ${data.index + 1}: ${this.bold(data.name)} (${data.taskCount} tasks)`);
  }
  
  onTaskStart(data) {
    this.tasks.set(data.taskId, {
      label: data.label || `Task ${data.taskId}`,
      worker: data.workerId,
      startTime: Date.now(),
    });
    
    if (!this.compact) {
      const label = this.truncate(data.label || `Task ${data.taskId}`, 35);
      console.log(`   ├─ ${this.dim('Worker ' + this.getWorkerNum(data.workerId))}: ${label}...`);
    }
  }
  
  onTaskComplete(data) {
    this.completedTasks++;
    const task = this.tasks.get(data.taskId);
    const duration = task ? Date.now() - task.startTime : data.durationMs;
    
    if (!this.compact && task) {
      const label = this.truncate(task.label, 35);
      // Move cursor up and overwrite the line
      if (this.isTTY) {
        process.stdout.write(`\x1b[1A\x1b[2K`);
        console.log(`   ├─ ${this.green('✓')} ${label} ${this.dim(`(${duration}ms)`)}`);
      }
    }
    
    this.tasks.delete(data.taskId);
  }
  
  onTaskError(data) {
    this.failedTasks++;
    const task = this.tasks.get(data.taskId);
    
    if (task) {
      const label = this.truncate(task.label, 35);
      if (this.isTTY) {
        process.stdout.write(`\x1b[1A\x1b[2K`);
      }
      console.log(`   ├─ ${this.red('✗')} ${label} ${this.dim(`(${data.error})`)}`);
    }
    
    this.tasks.delete(data.taskId);
  }
  
  onWorkerSpawn(data) {
    this.workers.set(data.workerId, {
      type: data.nodeType,
      num: this.workers.size + 1,
    });
  }
  
  onProgress(data) {
    // For non-TTY environments, show periodic progress
    if (!this.isTTY && data.completed % 5 === 0) {
      console.log(`   Progress: ${data.completed}/${data.total}`);
    }
  }
  
  // === Helpers ===
  
  getWorkerNum(workerId) {
    const worker = this.workers.get(workerId);
    return worker ? worker.num : '?';
  }
  
  truncate(str, len) {
    if (!str) return '';
    return str.length > len ? str.substring(0, len - 3) + '...' : str;
  }
  
  // === ANSI Colors (with fallback for non-TTY) ===
  
  bold(str) {
    return this.isTTY ? `\x1b[1m${str}\x1b[0m` : str;
  }
  
  dim(str) {
    return this.isTTY ? `\x1b[2m${str}\x1b[0m` : str;
  }
  
  green(str) {
    return this.isTTY ? `\x1b[32m${str}\x1b[0m` : str;
  }
  
  red(str) {
    return this.isTTY ? `\x1b[31m${str}\x1b[0m` : str;
  }
  
  yellow(str) {
    return this.isTTY ? `\x1b[33m${str}\x1b[0m` : str;
  }
  
  cyan(str) {
    return this.isTTY ? `\x1b[36m${str}\x1b[0m` : str;
  }
  
  // === Progress Bar ===
  
  progressBar(completed, total, width = 20) {
    const percent = total > 0 ? completed / total : 0;
    const filled = Math.round(width * percent);
    const empty = width - filled;
    return `[${'█'.repeat(filled)}${'░'.repeat(empty)}] ${completed}/${total}`;
  }
}

// Singleton display instance
let displayInstance = null;

function initDisplay(options = {}) {
  if (displayInstance) {
    displayInstance.detach();
  }
  displayInstance = new SwarmDisplay(options);
  return displayInstance;
}

function getDisplay() {
  if (!displayInstance) {
    displayInstance = new SwarmDisplay();
  }
  return displayInstance;
}

module.exports = { SwarmDisplay, initDisplay, getDisplay };
