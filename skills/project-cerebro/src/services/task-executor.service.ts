/**
 * Task executor service - handles task execution pipeline
 */

import { logger } from '../lib/logger';
import { TaskExecutionError } from '../lib/errors';
import { Task, TaskStatus } from '../domain/types/task';
import { TaskRepository } from '../data/repositories';
import { eventBus, EventType } from '../domain/events';

export interface TaskExecutor {
  execute(task: Task): Promise<void>;
}

export class TaskExecutorService {
  constructor(
    private taskRepo: TaskRepository,
    private executor: TaskExecutor
  ) {}

  /**
   * Execute a task
   */
  async executeTask(taskId: string): Promise<void> {
    const task = this.taskRepo.getById(taskId);

    logger.info('Starting task execution', {
      taskId: task.id,
      brainId: task.brainId,
      title: task.title,
    });

    // Emit execution started event
    await eventBus.emit({
      type: EventType.TASK_EXECUTION_STARTED,
      timestamp: Date.now(),
      payload: { task, brainId: task.brainId },
    });

    // Update status to EXECUTING
    this.taskRepo.updateStatus(taskId, TaskStatus.EXECUTING);

    try {
      // Execute the task
      await this.executor.execute(task);

      // Mark as COMPLETED
      this.taskRepo.updateStatus(taskId, TaskStatus.COMPLETED);

      logger.info('Task execution completed', {
        taskId: task.id,
        brainId: task.brainId,
      });

      // Emit completion event
      await eventBus.emit({
        type: EventType.TASK_EXECUTION_COMPLETED,
        timestamp: Date.now(),
        payload: {
          taskId: task.id,
          brainId: task.brainId,
          output: task.output,
        },
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);

      logger.error('Task execution failed', error as Error, {
        taskId: task.id,
        brainId: task.brainId,
        attempts: task.attempts + 1,
      });

      // Update task with error
      this.taskRepo.update({
        id: taskId,
        status: TaskStatus.FAILED,
        error: errorMessage,
        attempts: task.attempts + 1,
      });

      // Emit failure event
      await eventBus.emit({
        type: EventType.TASK_EXECUTION_FAILED,
        timestamp: Date.now(),
        payload: {
          taskId: task.id,
          brainId: task.brainId,
          error: errorMessage,
        },
      });

      // Check if we should retry
      if (task.retryPolicy && task.attempts < task.retryPolicy.maxAttempts) {
        await this.scheduleRetry(task);
      }

      throw new TaskExecutionError(errorMessage, { taskId: task.id });
    }
  }

  /**
   * Schedule a retry for a failed task
   */
  private async scheduleRetry(task: Task): Promise<void> {
    if (!task.retryPolicy) {
      return;
    }

    const { backoffType, backoffMs } = task.retryPolicy;
    const delay =
      backoffType === 'EXPONENTIAL'
        ? backoffMs * Math.pow(2, task.attempts)
        : backoffMs;

    const executeAt = Date.now() + delay;

    this.taskRepo.update({
      id: task.id,
      status: TaskStatus.READY,
      executeAt,
    });

    logger.info('Task scheduled for retry', {
      taskId: task.id,
      attempt: task.attempts + 1,
      maxAttempts: task.retryPolicy.maxAttempts,
      executeAt: new Date(executeAt).toISOString(),
    });
  }

  /**
   * Execute all ready tasks for a brain
   */
  async executeReadyTasks(brainId: string): Promise<void> {
    const tasks = this.taskRepo.getReadyTasks(brainId);

    if (tasks.length === 0) {
      return;
    }

    logger.info('Executing ready tasks', {
      brainId,
      taskCount: tasks.length,
    });

    for (const task of tasks) {
      try {
        await this.executeTask(task.id);
      } catch (error) {
        // Error already logged in executeTask
        // Continue with other tasks
      }
    }
  }
}
