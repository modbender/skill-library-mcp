/**
 * Base brain implementation - refactored with clean dependencies
 */

import { logger } from '../lib/logger';
import {
  IBrain,
  BrainConfig,
  BrainState,
  BrainStatus,
  Task,
  TaskStatus,
} from '../domain/types';
import { TaskRepository } from '../data/repositories';
import { DiscordAdapter, OpenClawAdapter } from '../integrations';
import { TaskExecutorService } from '../services';

export abstract class BaseBrain implements IBrain {
  public id: string;
  public name: string;
  public status: BrainStatus = BrainStatus.IDLE;
  public autoMode: boolean = false;

  protected config: BrainConfig;
  protected taskRepo: TaskRepository;
  protected discordAdapter: DiscordAdapter;
  protected openClawAdapter: OpenClawAdapter;
  protected taskExecutor: TaskExecutorService;

  constructor(
    config: BrainConfig,
    taskRepo: TaskRepository,
    discordAdapter: DiscordAdapter,
    openClawAdapter: OpenClawAdapter,
    taskExecutor: TaskExecutorService
  ) {
    this.id = config.id;
    this.name = config.name;
    this.config = config;
    this.taskRepo = taskRepo;
    this.discordAdapter = discordAdapter;
    this.openClawAdapter = openClawAdapter;
    this.taskExecutor = taskExecutor;
  }

  /**
   * Initialize the brain
   */
  async init(): Promise<void> {
    logger.info('Initializing brain', { brainId: this.id, name: this.name });

    // Register message handler for this brain's Discord channel
    this.discordAdapter.onMessage(this.config.discordChannelId, async (message) => {
      await this.handleUserMessage(message);
    });

    logger.info('Brain initialized', { brainId: this.id });
  }

  /**
   * Toggle auto mode
   */
  toggleAutoMode(enabled: boolean): void {
    this.autoMode = enabled;
    logger.info('Brain auto mode toggled', { brainId: this.id, enabled });
  }

  /**
   * Handle user message (to be implemented by subclasses)
   */
  abstract handleUserMessage(message: string): Promise<void>;

  /**
   * Heartbeat - process ready tasks
   */
  async onHeartbeat(): Promise<void> {
    await this.processTasks(false);
  }

  /**
   * Force run - execute all ready tasks immediately
   */
  async forceRun(): Promise<void> {
    logger.info('Force run triggered', { brainId: this.id });
    await this.processTasks(true);
  }

  /**
   * Get brain state
   */
  getState(): BrainState {
    return {
      id: this.id,
      name: this.name,
      type: this.config.type,
      status: this.status,
      autoMode: this.autoMode,
      description: this.config.description,
      discordChannelId: this.config.discordChannelId,
      openClawAgentId: this.config.openClawAgentId,
    };
  }

  /**
   * Process ready tasks for this brain
   */
  protected async processTasks(force: boolean): Promise<void> {
    const tasks = this.taskRepo.getReadyTasks(this.id);

    if (tasks.length === 0) {
      return;
    }

    logger.info('Found ready tasks', { brainId: this.id, count: tasks.length });

    for (const task of tasks) {
      // Execute if AutoMode is ON, Forced, or if it's a recurring task instance
      const isRecurring = !!task.payload?.recurringTaskId;
      if (this.autoMode || force || isRecurring) {
        try {
          await this.taskExecutor.executeTask(task.id);
        } catch (error) {
          // Error already logged in task executor
        }
      }
    }
  }

  /**
   * Send a message to this brain's Discord channel
   */
  protected async sendMessage(content: string): Promise<void> {
    try {
      await this.discordAdapter.sendMessage(this.config.discordChannelId, content);
    } catch (error) {
      logger.error('Failed to send Discord message', error as Error, {
        brainId: this.id,
      });
    }
  }

  /**
   * Execute task with OpenClaw agent
   */
  protected async executeWithAgent(task: Task, prompt: string): Promise<string> {
    if (!this.config.openClawAgentId) {
      throw new Error(`Brain ${this.id} has no OpenClaw agent configured`);
    }

    return await this.openClawAdapter.executeTask(this.config.openClawAgentId, {
      prompt,
      model: task.modelOverride,
      thinking: 'low',
    });
  }
}
