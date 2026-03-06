/**
 * Heartbeat loop - periodic execution cycle
 */

import { logger } from '../lib/logger';
import { BrainService, SchedulerService } from '../services';
import { TaskRepository, RecurringTaskRepository } from '../data/repositories';

export class HeartbeatLoop {
  private intervalId: NodeJS.Timeout | null = null;
  private isRunning: boolean = false;

  constructor(
    private brainService: BrainService,
    private schedulerService: SchedulerService,
    private taskRepo: TaskRepository,
    private recurringRepo: RecurringTaskRepository,
    private intervalMs: number = 60000 // Default 1 minute
  ) {}

  /**
   * Start the heartbeat loop
   */
  start(): void {
    if (this.isRunning) {
      logger.warn('Heartbeat loop already running');
      return;
    }

    logger.info('Starting heartbeat loop', {
      intervalMs: this.intervalMs,
      intervalSeconds: this.intervalMs / 1000,
    });

    this.isRunning = true;
    this.intervalId = setInterval(() => this.tick(), this.intervalMs);
  }

  /**
   * Stop the heartbeat loop
   */
  stop(): void {
    if (!this.isRunning) {
      logger.warn('Heartbeat loop not running');
      return;
    }

    logger.info('Stopping heartbeat loop');

    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }

    this.isRunning = false;
  }

  /**
   * Single heartbeat tick
   */
  private async tick(): Promise<void> {
    logger.debug('Heartbeat tick');

    try {
      // 1. Process recurring tasks (create instances for due recurring tasks)
      await this.processRecurringTasks();

      // 2. Run brain heartbeats (auto-mode brains will pick up READY tasks)
      await this.brainService.heartbeatAll();
    } catch (error) {
      logger.error('Heartbeat tick failed', error as Error);
    }
  }

  /**
   * Process recurring tasks that are due
   */
  private async processRecurringTasks(): Promise<void> {
    const dueTasks = this.schedulerService.getDueTasks();

    if (dueTasks.length === 0) {
      return;
    }

    logger.info('Processing due recurring tasks', { count: dueTasks.length });

    for (const recurringTask of dueTasks) {
      try {
        // Create a one-time task instance
        this.taskRepo.create({
          brainId: recurringTask.brainId,
          title: recurringTask.title,
          description: recurringTask.description,
          payload: {
            ...recurringTask.payload,
            recurringTaskId: recurringTask.id,
          },
          modelOverride: recurringTask.modelOverride,
          sendDiscordNotification: recurringTask.sendDiscordNotification,
        });

        // Mark the recurring task as executed and compute next run
        this.schedulerService.markExecuted(recurringTask.id);

        logger.info('Recurring task instance created', {
          recurringTaskId: recurringTask.id,
          brainId: recurringTask.brainId,
        });
      } catch (error) {
        logger.error('Failed to process recurring task', error as Error, {
          recurringTaskId: recurringTask.id,
        });
      }
    }
  }
}
