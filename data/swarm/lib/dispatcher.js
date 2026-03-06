/**
 * Orchestrating Dispatcher
 * Coordinates specialized nodes for complex multi-step tasks
 * Max 5 nodes with smart reuse across phases
 */

const { WorkerNode } = require('./worker-node');
const config = require('../config');
const { metrics } = require('./metrics');
const { swarmEvents, EVENTS } = require('./events');
const { initDisplay } = require('./display');

class Dispatcher {
  constructor(options = {}) {
    this.nodes = new Map();
    this.taskQueue = [];
    this.results = new Map();
    this.nextTaskId = 1;
    this.maxNodes = config.scaling.maxNodes;
    this.logs = [];
    this.quiet = options.quiet || false;
    this.silent = options.silent || false; // No console output at all
    this.trackMetrics = options.trackMetrics !== false; // Default: track
    this.warnings = [];
    this.executionStart = null;
    
    // Initialize display unless silent
    if (!this.silent) {
      initDisplay({ enabled: !this.quiet, compact: options.compact });
    }
  }

  log(message) {
    const entry = { time: Date.now(), message };
    this.logs.push(entry);
    if (!this.quiet && !this.silent) {
      // Internal logs are now dim/quiet - display handles user-facing output
    }
  }

  // Emit event for listeners
  emit(event, data) {
    swarmEvents.emit(event, data);
  }

  // User-facing announcement (legacy - now uses events)
  announce(message) {
    if (!this.silent) {
      console.log(`\n🐝 ${message}`);
    }
  }

  // Get or create a node of specific type (with smart recycling)
  getOrCreateNode(nodeType) {
    // First, try to find an idle node of the same type
    for (const node of this.nodes.values()) {
      if (node.status === 'idle' && node.nodeType === nodeType) {
        return node;
      }
    }
    
    // Second, if under limit, create a new node
    if (this.nodes.size < this.maxNodes) {
      const id = `${nodeType}-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`;
      const node = new WorkerNode(id, nodeType);
      this.nodes.set(id, node);
      this.log(`Spawned ${nodeType} node: ${id}`);
      this.emit(EVENTS.WORKER_SPAWN, { workerId: id, nodeType });
      return node;
    }
    
    // Third, recycle an idle node of different type
    for (const [id, node] of this.nodes.entries()) {
      if (node.status === 'idle') {
        this.log(`Recycling ${node.nodeType} node → ${nodeType}`);
        this.emit(EVENTS.WORKER_RECYCLE, { workerId: id, fromType: node.nodeType, toType: nodeType });
        this.nodes.delete(id);
        const newId = `${nodeType}-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`;
        const newNode = new WorkerNode(newId, nodeType);
        this.nodes.set(newId, newNode);
        this.emit(EVENTS.WORKER_SPAWN, { workerId: newId, nodeType });
        return newNode;
      }
    }
    
    // No available nodes - this shouldn't happen in orchestrated flow
    throw new Error(`No available nodes (all ${this.maxNodes} busy)`);
  }

  // Wait for a node to become available
  async waitForNode(nodeType, timeoutMs = 30000) {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      try {
        return this.getOrCreateNode(nodeType);
      } catch (e) {
        // All busy, wait a bit
        await new Promise(r => setTimeout(r, 100));
      }
    }
    throw new Error(`Timeout waiting for ${nodeType} node`);
  }

  // Execute a single task
  async executeTask(task) {
    const node = await this.waitForNode(task.nodeType || 'analyze');
    task.id = task.id || this.nextTaskId++;
    
    const result = await node.execute(task);
    this.results.set(task.id, result);
    return result;
  }

  /**
   * Execute a single task and return the response string.
   * Convenience wrapper for reflection and other single-shot needs.
   */
  async dispatchSingle(task) {
    const result = await this.executeTask(task);
    return result;
  }

  // Execute multiple tasks in parallel (respecting max nodes)
  async executeParallel(tasks, phaseContext = {}) {
    const startTime = Date.now();
    this.log(`Executing ${tasks.length} tasks in parallel (max ${this.maxNodes} concurrent)`);
    
    // Group tasks by node type
    const tasksByType = {};
    tasks.forEach((task, idx) => {
      const type = task.nodeType || 'analyze';
      if (!tasksByType[type]) tasksByType[type] = [];
      tasksByType[type].push({ ...task, originalIndex: idx });
    });
    
    // Pre-allocate nodes for each type (up to maxNodes total)
    const typeCount = Object.keys(tasksByType).length;
    const nodesPerType = Math.floor(this.maxNodes / typeCount);
    
    // Execute all tasks with controlled concurrency
    const results = new Array(tasks.length);
    const executing = new Set();
    const pending = [...tasks.map((t, i) => ({ 
      ...t, 
      originalIndex: i, 
      id: this.nextTaskId++,
      label: t.label || t.metadata?.subject || t.instruction?.substring(0, 40) || `Task ${i + 1}`
    }))];
    
    let completed = 0;
    
    const executeNext = async () => {
      while (pending.length > 0 || executing.size > 0) {
        // Start new tasks up to max concurrency
        while (pending.length > 0 && executing.size < this.maxNodes) {
          const task = pending.shift();
          const node = await this.waitForNode(task.nodeType || 'analyze');
          
          // Emit task start event
          this.emit(EVENTS.TASK_START, { 
            taskId: task.id, 
            workerId: node.id,
            label: task.label,
            nodeType: task.nodeType || 'analyze'
          });
          
          const promise = (async () => {
            try {
              const result = await node.execute(task);
              results[task.originalIndex] = result;
              
              completed++;
              
              if (result.success) {
                this.emit(EVENTS.TASK_COMPLETE, { 
                  taskId: task.id, 
                  workerId: node.id,
                  durationMs: result.durationMs 
                });
              } else {
                this.emit(EVENTS.TASK_ERROR, { 
                  taskId: task.id, 
                  workerId: node.id,
                  error: result.error 
                });
              }
              
              // Emit progress
              this.emit(EVENTS.PROGRESS, { 
                completed, 
                total: tasks.length,
                phase: phaseContext.name 
              });
              
            } finally {
              executing.delete(promise);
            }
          })();
          
          executing.add(promise);
        }
        
        // Wait for at least one to complete
        if (executing.size > 0) {
          await Promise.race([...executing]);
        }
      }
    };
    
    await executeNext();
    
    const duration = Date.now() - startTime;
    const successful = results.filter(r => r?.success).length;
    this.log(`Parallel execution complete: ${successful}/${results.length} succeeded in ${duration}ms`);
    
    return {
      success: results.every(r => r?.success),
      results,
      totalDurationMs: duration,
      parallelEfficiency: results.length > 0 
        ? (results.reduce((sum, r) => sum + (r?.durationMs || 0), 0) / duration).toFixed(2)
        : 0,
    };
  }

  // Orchestrate a complex multi-phase task
  async orchestrate(phases, options = {}) {
    const startTime = Date.now();
    const phaseResults = [];
    
    // Count total tasks across all phases (estimate for dynamic phases)
    let estimatedTotalTasks = 0;
    for (const phase of phases) {
      if (Array.isArray(phase.tasks)) {
        estimatedTotalTasks += phase.tasks.length;
      } else {
        estimatedTotalTasks += 5; // Estimate for dynamic phases
      }
    }
    
    // Emit swarm start event
    this.emit(EVENTS.SWARM_START, {
      phases: phases.length,
      maxWorkers: this.maxNodes,
      totalTasks: estimatedTotalTasks,
    });
    
    this.log(`Starting orchestration with ${phases.length} phases`);
    
    for (let i = 0; i < phases.length; i++) {
      const phase = phases[i];
      this.log(`Phase ${i + 1}: ${phase.name}`);
      
      // Build tasks, potentially using previous phase results
      let tasks = phase.tasks;
      if (typeof tasks === 'function') {
        tasks = tasks(phaseResults);
      }
      
      if (!tasks || tasks.length === 0) {
        this.log(`Phase ${i + 1}: No tasks to execute`);
        phaseResults.push({ phase: phase.name, success: true, results: [], totalDurationMs: 0 });
        continue;
      }
      
      // Emit phase start event
      this.emit(EVENTS.PHASE_START, {
        index: i,
        name: phase.name,
        taskCount: tasks.length,
      });
      
      // Stage timeout — abort if a phase takes too long
      const stageTimeoutMs = phase.timeoutMs ?? options.stageTimeoutMs ?? 60000;
      
      // Execute phase tasks in parallel, with stage-level retry on failures
      const maxStageRetries = phase.retries ?? options.stageRetries ?? 1;
      let phaseResult;
      let stageAttempt = 0;
      const stageStart = Date.now();
      
      while (stageAttempt <= maxStageRetries) {
        // Check stage timeout before retrying
        if (Date.now() - stageStart > stageTimeoutMs) {
          this.log(`Phase ${i + 1}: stage timeout (${stageTimeoutMs}ms)`);
          if (!phaseResult) {
            phaseResult = { success: false, results: [], totalDurationMs: Date.now() - stageStart };
          }
          phaseResult.timedOut = true;
          break;
        }
        if (stageAttempt > 0) {
          this.log(`Phase ${i + 1}: retry ${stageAttempt}/${maxStageRetries}`);
          // Only re-run the failed tasks
          const failedIndices = phaseResult.results
            .map((r, idx) => (!r || !r.success) ? idx : -1)
            .filter(idx => idx >= 0);
          
          if (failedIndices.length === 0) break;
          
          const retryTasks = failedIndices.map(idx => tasks[idx]);
          const retryResult = await this.executeParallel(retryTasks, { name: `${phase.name} (retry)` });
          
          // Merge retry results back
          failedIndices.forEach((origIdx, retryIdx) => {
            if (retryResult.results[retryIdx]?.success) {
              phaseResult.results[origIdx] = retryResult.results[retryIdx];
            }
          });
          
          // Recalculate success
          phaseResult.success = phaseResult.results.every(r => r?.success);
          if (phaseResult.success) break;
        } else {
          phaseResult = await this.executeParallel(tasks, { name: phase.name });
        }
        stageAttempt++;
      }
      
      phaseResults.push({
        phase: phase.name,
        ...phaseResult,
      });
      
      // Emit phase complete event
      this.emit(EVENTS.PHASE_COMPLETE, {
        index: i,
        name: phase.name,
        success: phaseResult.success,
        durationMs: phaseResult.totalDurationMs,
        retries: stageAttempt > 0 ? stageAttempt : undefined,
      });
      
      if (!phaseResult.success && phase.required !== false) {
        this.log(`Phase ${i + 1} had failures after ${stageAttempt} retries, continuing...`);
      }
    }
    
    const totalDuration = Date.now() - startTime;
    
    // Calculate metrics
    const successCount = phaseResults.reduce((sum, p) => sum + (p.results?.filter(r => r?.success).length || 0), 0);
    const totalCount = phaseResults.reduce((sum, p) => sum + (p.results?.length || 0), 0);
    const failureCount = totalCount - successCount;
    
    // Calculate speedup estimate
    const estimatedSeq = totalCount * 2000; // ~2s per task estimate
    const speedup = estimatedSeq / totalDuration;
    
    // Emit swarm complete event
    this.emit(EVENTS.SWARM_COMPLETE, {
      totalTasks: totalCount,
      successCount,
      failureCount,
      durationMs: totalDuration,
      speedup: parseFloat(speedup.toFixed(2)),
    });
    
    // Track metrics
    if (this.trackMetrics) {
      const nodeTypes = [...new Set([...this.nodes.values()].map(n => n.nodeType))];
      const estimatedSeq = totalCount * 2000; // ~2s per task estimate
      
      metrics.logExecution({
        type: 'orchestration',
        taskCount: totalCount,
        phases: phases.length,
        nodeTypes,
        durationMs: totalDuration,
        successCount,
        failureCount,
        estimatedSequentialMs: estimatedSeq,
        speedup: parseFloat((estimatedSeq / totalDuration).toFixed(2)),
        nodesUsed: this.nodes.size,
        maxNodesHit: this.nodes.size >= this.maxNodes,
        taskDescription: options.description || null,
        warnings: this.warnings,
      });
      
      // Log edge cases
      if (failureCount > 0) {
        metrics.logEdgeCase({
          type: 'failure',
          description: `${failureCount}/${totalCount} tasks failed`,
          context: { phases: phases.map(p => p.name), duration: totalDuration },
        });
      }
      
      if (totalDuration > 30000) {
        metrics.logEdgeCase({
          type: 'slow',
          description: `Orchestration took ${(totalDuration/1000).toFixed(1)}s (>30s threshold)`,
          context: { taskCount: totalCount, phases: phases.length },
          suggestedFix: 'Consider reducing task complexity or increasing node limit',
        });
      }
    }
    
    return {
      success: phaseResults.every(p => p.success || p.results?.some(r => r?.success)),
      phases: phaseResults,
      totalDurationMs: totalDuration,
      nodeStats: this.getNodeStats(),
    };
  }

  // Get stats for all nodes
  getNodeStats() {
    const stats = [];
    for (const node of this.nodes.values()) {
      stats.push(node.getStats());
    }
    return stats;
  }

  // Get overall status
  getStatus() {
    const nodes = [...this.nodes.values()];
    return {
      totalNodes: nodes.length,
      maxNodes: this.maxNodes,
      byType: this.getNodesByType(),
      idle: nodes.filter(n => n.status === 'idle').length,
      busy: nodes.filter(n => n.status === 'busy').length,
    };
  }

  getNodesByType() {
    const byType = {};
    for (const node of this.nodes.values()) {
      byType[node.nodeType] = (byType[node.nodeType] || 0) + 1;
    }
    return byType;
  }

  // Clean up
  shutdown() {
    this.log(`Shutting down ${this.nodes.size} nodes`);
    this.nodes.clear();
  }
}

module.exports = { Dispatcher };
