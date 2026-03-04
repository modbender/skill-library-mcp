import { TokenManager } from './core/TokenManager';
import { AgentOrchestrator, AgentTask, TaskResult } from './core/AgentOrchestrator';

/**
 * Butler - AI Agent Treasury & Orchestration Skill
 * 
 * Main interface for:
 * - Token allocation and management
 * - Agent spawning and orchestration
 * - Treasury management
 * - Security and compliance
 */

export class Butler {
  private tokenManager: TokenManager;
  private orchestrator: AgentOrchestrator;
  private version: string = '0.1.0';

  constructor(
    keysPath?: string,
    statePath?: string
  ) {
    this.tokenManager = new TokenManager(keysPath, statePath);
    this.orchestrator = new AgentOrchestrator(this.tokenManager);
  }

  /**
   * Allocate tokens for a task based on PRD
   */
  public allocateTokens(prdPath: string, preferredProvider?: string) {
    const estimate = this.tokenManager.estimateTokensForPRD(prdPath);
    console.log(`📊 Token estimate for ${prdPath}:`);
    console.log(`   Estimated: ${estimate.estimated.toLocaleString()} tokens`);
    console.log(`   Confidence: ${(estimate.confidence * 100).toFixed(0)}%`);

    const allocation = this.tokenManager.selectKey(estimate.estimated, preferredProvider);
    
    if (allocation.success) {
      console.log(`✅ Allocation successful:`);
      console.log(`   Key: ${allocation.key_id}`);
      console.log(`   Provider: ${allocation.provider}`);
      console.log(`   Budget: ${allocation.allocated?.toLocaleString()} tokens`);
      console.log(`   Rotate at: ${allocation.rotation_threshold?.toLocaleString()} tokens`);
    }

    return allocation;
  }

  /**
   * Spawn a sub-agent with budget allocation
   */
  public async spawnAgent(
    taskName: string,
    description: string,
    budgetTokens: number,
    options: {
      maxConcurrent?: number;
      retryOnFailure?: boolean;
      maxRetries?: number;
      timeoutMs?: number;
    } = {}
  ): Promise<TaskResult[]> {
    const task: AgentTask = {
      id: `task-${Date.now()}`,
      name: taskName,
      description,
      totalBudget: budgetTokens,
      subTasks: [],
      maxConcurrent: options.maxConcurrent || 3,
      retryOnFailure: options.retryOnFailure !== false,
      maxRetries: options.maxRetries || 2,
      timeoutMs: options.timeoutMs || 300000
    };

    return this.orchestrator.executeTask(task);
  }

  /**
   * Get current token status
   */
  public getStatus() {
    const tokenStatus = this.tokenManager.getStatus();
    const orchestratorStatus = this.orchestrator.getStatus();

    return {
      version: this.version,
      timestamp: new Date().toISOString(),
      tokens: tokenStatus,
      agents: orchestratorStatus
    };
  }

  /**
   * Get available keys for manual selection
   */
  public getAvailableKeys() {
    return this.tokenManager.getAvailableKeys();
  }

  /**
   * Monitor token usage and trigger alerts
   */
  public monitorUsage() {
    return this.tokenManager.getStatus();
  }

  /**
   * Manual key rotation (if needed)
   */
  public rotateKey(sessionId: string, newKeyId?: string) {
    console.log(`🔄 Rotating key for session ${sessionId}`);
    // Implementation would interact with tokenManager and orchestrator
    return { success: true };
  }

  /**
   * Aggregate results from multiple agents
   */
  public aggregateTaskResults(taskId: string) {
    return this.orchestrator.aggregateResults(taskId);
  }

  /**
   * Retry failed tasks
   */
  public async retryFailedTasks(taskId: string) {
    // Implementation would track failed tasks and retry
    return { success: true };
  }
}

export { TokenManager } from './core/TokenManager';
export { AgentOrchestrator, AgentTask, TaskResult } from './core/AgentOrchestrator';
