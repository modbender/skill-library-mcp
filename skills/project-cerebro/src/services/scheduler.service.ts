/**
 * Scheduler service - handles schedule computation for recurring tasks
 */

import { logger } from '../lib/logger';
import { RecurringTask, RecurrencePattern } from '../domain/types/schedule';
import { RecurringTaskRepository } from '../data/repositories';

export class SchedulerService {
  constructor(private recurringTaskRepo: RecurringTaskRepository) {}

  /**
   * Compute next execution time for a recurring task
   */
  computeNextExecution(task: RecurringTask): number {
    const now = Date.now();
    const lastExecution = task.lastExecutedAt || task.createdAt;

    switch (task.pattern) {
      case RecurrencePattern.DAILY:
        return this.addDays(lastExecution, 1);

      case RecurrencePattern.WEEKLY:
        return this.addDays(lastExecution, 7);

      case RecurrencePattern.MONTHLY:
        return this.addMonths(lastExecution, 1);

      case RecurrencePattern.CUSTOM:
        if (task.cronExpression) {
          return this.computeFromCron(task.cronExpression, lastExecution);
        }
        throw new Error(`Custom pattern requires cronExpression`);

      default:
        throw new Error(`Unknown recurrence pattern: ${task.pattern}`);
    }
  }

  /**
   * Update next execution time for a recurring task
   */
  updateNextExecution(taskId: string): void {
    const task = this.recurringTaskRepo.getById(taskId);
    const nextExecutionAt = this.computeNextExecution(task);

    this.recurringTaskRepo.update({
      id: taskId,
      nextExecutionAt,
    });

    logger.debug('Updated next execution time', {
      taskId,
      nextExecutionAt: new Date(nextExecutionAt).toISOString(),
    });
  }

  /**
   * Mark recurring task as executed and compute next run
   */
  markExecuted(taskId: string): void {
    const now = Date.now();
    
    // First, update lastExecutedAt so computeNextExecution uses the correct base time
    this.recurringTaskRepo.update({
      id: taskId,
      lastExecutedAt: now,
    });
    
    // Now get the updated task and compute next execution
    const task = this.recurringTaskRepo.getById(taskId);
    const nextExecutionAt = this.computeNextExecution(task);

    this.recurringTaskRepo.update({
      id: taskId,
      nextExecutionAt,
    });

    logger.info('Recurring task executed, scheduled next run', {
      taskId,
      lastExecutedAt: new Date(now).toISOString(),
      nextExecutionAt: new Date(nextExecutionAt).toISOString(),
    });
  }

  /**
   * Add days to a timestamp
   */
  private addDays(timestamp: number, days: number): number {
    return timestamp + days * 24 * 60 * 60 * 1000;
  }

  /**
   * Add months to a timestamp
   */
  private addMonths(timestamp: number, months: number): number {
    const date = new Date(timestamp);
    date.setMonth(date.getMonth() + months);
    return date.getTime();
  }

  /**
   * Compute next execution from cron expression
   * Simple implementation - could be enhanced with a proper cron library
   */
  private computeFromCron(cronExpression: string, lastExecution: number): number {
    // For now, just parse simple formats like "0 9 * * *" (9 AM daily)
    // In production, use a library like 'cron-parser'
    const parts = cronExpression.split(' ');
    
    if (parts.length !== 5) {
      throw new Error(`Invalid cron expression: ${cronExpression}`);
    }

    // Simple daily pattern: "minute hour * * *"
    const minute = parseInt(parts[0], 10);
    const hour = parseInt(parts[1], 10);

    if (isNaN(minute) || isNaN(hour)) {
      throw new Error(`Invalid cron expression: ${cronExpression}`);
    }

    const date = new Date(lastExecution);
    date.setHours(hour, minute, 0, 0);

    // If the time has passed today, schedule for tomorrow
    if (date.getTime() <= Date.now()) {
      date.setDate(date.getDate() + 1);
    }

    return date.getTime();
  }

  /**
   * Get all tasks due for execution
   */
  getDueTasks(): RecurringTask[] {
    return this.recurringTaskRepo.findDue();
  }
}
