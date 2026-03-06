import { TokenManager, AllocationResult } from './TokenManager';

/**
 * Agent Orchestrator
 * Responsibilities:
 * - Decompose complex tasks into sub-tasks
 * - Spawn OpenClaw sub-agents with allocated budgets
 * - Route API keys to each agent
 * - Aggregate results
 * - Handle failures and retries
 */

export interface SubTask {
  id: string;
  description: string;
  estimatedTokens: number;
  priority: 'low' | 'medium' | 'high' | 'critical';
  dependencies: string[]; // IDs of tasks that must complete first
}

export interface AgentTask {
  id: string;
  name: string;
  description: string;
  totalBudget: number;
  subTasks: SubTask[];
  maxConcurrent: number;
  retryOnFailure: boolean;
  maxRetries: number;
  timeoutMs: number;
}

export interface AgentSpawnResult {
  success: boolean;
  sessionId?: string;
  agentLabel?: string;
  allocatedBudget?: number;
  keyId?: string;
  provider?: string;
  message?: string;
  error?: string;
}

export interface TaskResult {
  taskId: string;
  subTaskId: string;
  status: 'success' | 'failure' | 'pending';
  tokensUsed: number;
  result?: any;
  error?: string;
  duration: number;
}

export class AgentOrchestrator {
  private tokenManager: TokenManager;
  private tasks: Map<string, AgentTask> = new Map();
  private results: Map<string, TaskResult[]> = new Map();
  private activeSessions: Map<string, AgentSpawnResult> = new Map();

  constructor(tokenManager: TokenManager) {
    this.tokenManager = tokenManager;
  }

  /**
   * Decompose a complex task into manageable sub-tasks
   */
  public decomposeTask(task: AgentTask): SubTask[] {
    console.log(`📋 Decomposing task: ${task.name}`);

    // Use provided sub-tasks or auto-decompose
    if (task.subTasks && task.subTasks.length > 0) {
      return task.subTasks;
    }

    // Auto-decompose based on description
    const autoSubTasks: SubTask[] = [];

    // Simple heuristic: split by keywords
    const keywords = ['research', 'analyze', 'write', 'validate', 'integrate', 'test'];
    const parts = task.description.split(' ');

    let currentSubTask = '';
    let tokenCount = 0;

    parts.forEach((part, index) => {
      currentSubTask += part + ' ';
      tokenCount += 50; // Rough estimate

      if (keywords.some(k => part.toLowerCase().includes(k)) || index === parts.length - 1) {
        if (currentSubTask.trim()) {
          autoSubTasks.push({
            id: `${task.id}-subtask-${autoSubTasks.length + 1}`,
            description: currentSubTask.trim(),
            estimatedTokens: Math.max(tokenCount, 10000),
            priority: 'medium',
            dependencies: autoSubTasks.length > 0 ? [autoSubTasks[autoSubTasks.length - 1].id] : []
          });
        }
        currentSubTask = '';
        tokenCount = 0;
      }
    });

    console.log(`✨ Auto-decomposed into ${autoSubTasks.length} sub-tasks`);
    return autoSubTasks;
  }

  /**
   * Allocate budget across sub-tasks based on complexity
   */
  public allocateBudget(task: AgentTask): Map<string, number> {
    const budget = new Map<string, number>();

    if (task.subTasks.length === 0) {
      return budget;
    }

    // Calculate total estimated tokens
    const totalEstimated = task.subTasks.reduce((sum, st) => sum + st.estimatedTokens, 0);

    // Allocate proportionally with priority boost
    task.subTasks.forEach(subTask => {
      const priorityMultiplier = {
        low: 0.5,
        medium: 1.0,
        high: 1.5,
        critical: 2.0
      }[subTask.priority];

      const weightedTokens = subTask.estimatedTokens * priorityMultiplier;
      const allocation = Math.ceil((weightedTokens / totalEstimated) * task.totalBudget);

      budget.set(subTask.id, allocation);

      console.log(`  💰 ${subTask.id}: ${allocation.toLocaleString()} tokens (${subTask.priority})`);
    });

    return budget;
  }

  /**
   * Spawn a sub-agent for a task with allocated budget
   */
  public async spawnSubAgent(
    task: AgentTask,
    subTask: SubTask,
    allocatedBudget: number
  ): Promise<AgentSpawnResult> {
    console.log(`🚀 Spawning agent for sub-task: ${subTask.id}`);

    // Get allocation from token manager
    const allocation = this.tokenManager.selectKey(allocatedBudget);

    if (!allocation.success) {
      return {
        success: false,
        error: `Failed to allocate tokens: ${allocation.message}`
      };
    }

    // Track in token manager
    const sessionId = `butler-${task.id}-${subTask.id}-${Date.now()}`;
    this.tokenManager.trackSession(sessionId, allocation, {
      prd: subTask.description,
      agent_name: `agent-${task.name}`
    });

    // In a real implementation, this would spawn an actual OpenClaw sub-agent
    // For now, we simulate the spawn with metadata
    const result: AgentSpawnResult = {
      success: true,
      sessionId,
      agentLabel: `butler-${task.name}`,
      allocatedBudget,
      keyId: allocation.key_id,
      provider: allocation.provider,
      message: `Agent spawned with ${allocatedBudget.toLocaleString()} tokens`
    };

    this.activeSessions.set(sessionId, result);
    console.log(`  ✅ ${result.message}`);

    return result;
  }

  /**
   * Execute a task with multiple sub-agents
   */
  public async executeTask(task: AgentTask): Promise<TaskResult[]> {
    console.log(`\n🎯 Executing task: ${task.name}`);
    console.log(`   Budget: ${task.totalBudget.toLocaleString()} tokens`);

    // Step 1: Decompose
    const subTasks = this.decomposeTask(task);
    task.subTasks = subTasks;

    // Step 2: Allocate
    const budgetAllocation = this.allocateBudget(task);

    // Step 3: Spawn agents with smart concurrency
    const taskResults: TaskResult[] = [];
    const inFlight = new Map<string, Promise<AgentSpawnResult>>();

    for (const subTask of subTasks) {
      // Wait if we hit concurrency limit
      while (inFlight.size >= task.maxConcurrent) {
        const results = await Promise.allSettled(Array.from(inFlight.values()));
        inFlight.clear();
      }

      const budget = budgetAllocation.get(subTask.id) || 10000;

      // Spawn agent (wrapped in promise)
      const spawnPromise = this.spawnSubAgent(task, subTask, budget);
      inFlight.set(subTask.id, spawnPromise);

      // Wait for dependent tasks
      if (subTask.dependencies.length > 0) {
        await this.waitForDependencies(subTask.dependencies, taskResults);
      }
    }

    // Wait for all to complete
    const allResults = await Promise.allSettled(Array.from(inFlight.values()));

    allResults.forEach((result, index) => {
      const subTaskId = Array.from(inFlight.keys())[index];
      if (result.status === 'fulfilled') {
        const spawnResult = result.value;
        taskResults.push({
          taskId: task.id,
          subTaskId,
          status: spawnResult.success ? 'success' : 'failure',
          tokensUsed: spawnResult.allocatedBudget || 0,
          result: spawnResult,
          duration: 0
        });
      } else {
        taskResults.push({
          taskId: task.id,
          subTaskId,
          status: 'failure',
          tokensUsed: 0,
          error: String(result.reason),
          duration: 0
        });
      }
    });

    // Store results
    this.results.set(task.id, taskResults);

    console.log(`\n✨ Task execution complete: ${task.name}`);
    console.log(`   Success: ${taskResults.filter(r => r.status === 'success').length}/${taskResults.length}`);

    return taskResults;
  }

  /**
   * Wait for dependent tasks to complete
   */
  private async waitForDependencies(dependencyIds: string[], results: TaskResult[]): Promise<void> {
    for (const depId of dependencyIds) {
      const depResult = results.find(r => r.subTaskId === depId);
      if (!depResult || depResult.status === 'pending') {
        // In production, would implement actual polling/waiting
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    }
  }

  /**
   * Aggregate results from all sub-agents
   */
  public aggregateResults(taskId: string): any {
    const results = this.results.get(taskId) || [];

    const aggregated = {
      taskId,
      totalSubTasks: results.length,
      successful: results.filter(r => r.status === 'success').length,
      failed: results.filter(r => r.status === 'failure').length,
      totalTokensUsed: results.reduce((sum, r) => sum + r.tokensUsed, 0),
      successRate: (results.filter(r => r.status === 'success').length / results.length) * 100,
      details: results.map(r => ({
        id: r.subTaskId,
        status: r.status,
        tokensUsed: r.tokensUsed,
        error: r.error
      }))
    };

    return aggregated;
  }

  /**
   * Handle task failure with retries
   */
  public async retryTask(
    task: AgentTask,
    failedSubTaskIds: string[],
    retryCount: number = 0
  ): Promise<TaskResult[]> {
    if (retryCount >= task.maxRetries) {
      console.error(`❌ Task ${task.id} exceeded max retries`);
      return [];
    }

    console.log(`🔄 Retrying ${failedSubTaskIds.length} failed sub-tasks (attempt ${retryCount + 1})`);

    const retryTasks = task.subTasks.filter(st => failedSubTaskIds.includes(st.id));
    const retryBudget = task.totalBudget * 0.5; // Use 50% of original budget for retry

    const retryTask: AgentTask = {
      ...task,
      id: `${task.id}-retry-${retryCount + 1}`,
      totalBudget: retryBudget,
      subTasks: retryTasks
    };

    return this.executeTask(retryTask);
  }

  /**
   * Get status of all active sessions
   */
  public getStatus(): Record<string, any> {
    return {
      activeSessions: this.activeSessions.size,
      sessions: Array.from(this.activeSessions.entries()).map(([id, result]) => ({
        id,
        provider: result.provider,
        budget: result.allocatedBudget,
        status: result.success ? 'running' : 'failed'
      })),
      completedTasks: this.results.size
    };
  }
}
