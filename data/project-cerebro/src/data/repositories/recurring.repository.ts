/**
 * Recurring task repository
 */

import { DatabaseConnection } from '../database';
import { logger } from '../../lib/logger';
import { DatabaseError, RecordNotFoundError } from '../../lib/errors';
import {
  RecurringTask,
  CreateRecurringTaskInput,
  UpdateRecurringTaskInput,
} from '../../domain/types/schedule';

export class RecurringTaskRepository {
  constructor(private db: DatabaseConnection) {}

  /**
   * Create a new recurring task
   */
  create(input: CreateRecurringTaskInput): RecurringTask {
    const now = Date.now();
    const nextExecutionAt = input.nextExecutionAt || now + 60 * 60 * 1000; // Default: 1 hour from now
    const task: RecurringTask = {
      id: this.generateId(),
      brainId: input.brainId,
      title: input.title,
      description: input.description,
      pattern: input.pattern,
      cronExpression: input.cronExpression,
      payload: input.payload || {},
      modelOverride: input.modelOverride,
      active: true,
      createdAt: now,
      updatedAt: now,
      nextExecutionAt,
      sendDiscordNotification: input.sendDiscordNotification ?? true,
      triggersReport: input.triggersReport ?? false,
      reportDelayMinutes: input.reportDelayMinutes ?? 0,
    };

    try {
      // Insert with both old and new column names for backward compatibility
      const stmt = this.db.getDb().prepare(`
        INSERT INTO recurring_tasks (
          id, brainId, title, description, pattern, cronExpression,
          payload, modelOverride, active, createdAt, updatedAt, nextExecutionAt,
          scheduleType, enabled, sendDiscordNotification, triggersReport, reportDelayMinutes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);

      stmt.run(
        task.id,
        task.brainId,
        task.title,
        task.description || null,
        task.pattern,
        task.cronExpression || null,
        JSON.stringify(task.payload),
        task.modelOverride || null,
        task.active ? 1 : 0,
        task.createdAt,
        task.updatedAt,
        task.nextExecutionAt,
        task.pattern, // scheduleType = pattern for backward compatibility
        task.active ? 1 : 0, // enabled = active for backward compatibility
        task.sendDiscordNotification ? 1 : 0,
        task.triggersReport ? 1 : 0,
        task.reportDelayMinutes
      );

      logger.info('Recurring task created', { taskId: task.id, brainId: task.brainId });
      return task;
    } catch (error) {
      logger.error('Failed to create recurring task', error as Error, { task });
      throw new DatabaseError('Failed to create recurring task');
    }
  }

  /**
   * Find recurring task by ID
   */
  findById(id: string): RecurringTask | null {
    try {
      const stmt = this.db.getDb().prepare('SELECT * FROM recurring_tasks WHERE id = ?');
      const row = stmt.get(id) as any;
      return row ? this.mapRowToRecurringTask(row) : null;
    } catch (error) {
      logger.error('Failed to find recurring task by id', error as Error, { id });
      throw new DatabaseError('Failed to find recurring task by id');
    }
  }

  /**
   * Get recurring task by ID (throws if not found)
   */
  getById(id: string): RecurringTask {
    const task = this.findById(id);
    if (!task) {
      throw new RecordNotFoundError('RecurringTask', id);
    }
    return task;
  }

  /**
   * Find all recurring tasks for a brain
   */
  findByBrainId(brainId: string): RecurringTask[] {
    try {
      const stmt = this.db.getDb().prepare('SELECT * FROM recurring_tasks WHERE brainId = ? ORDER BY createdAt DESC');
      const rows = stmt.all(brainId) as any[];
      return rows.map(this.mapRowToRecurringTask);
    } catch (error) {
      logger.error('Failed to find recurring tasks by brain id', error as Error, { brainId });
      throw new DatabaseError('Failed to find recurring tasks by brain id');
    }
  }

  /**
   * Find all active recurring tasks
   */
  findActive(): RecurringTask[] {
    try {
      // Support both old schema (enabled) and new schema (active)
      const stmt = this.db.getDb().prepare('SELECT * FROM recurring_tasks WHERE (active = 1 OR enabled = 1) ORDER BY nextExecutionAt ASC');
      const rows = stmt.all() as any[];
      return rows.map(this.mapRowToRecurringTask);
    } catch (error) {
      logger.error('Failed to find active recurring tasks', error as Error);
      throw new DatabaseError('Failed to find active recurring tasks');
    }
  }

  /**
   * Find recurring tasks due for execution
   */
  findDue(): RecurringTask[] {
    try {
      const now = Date.now();
      // Support both old schema (enabled) and new schema (active)
      const stmt = this.db.getDb().prepare(`
        SELECT * FROM recurring_tasks 
        WHERE (active = 1 OR enabled = 1)
          AND nextExecutionAt IS NOT NULL 
          AND nextExecutionAt <= ?
        ORDER BY nextExecutionAt ASC
      `);
      const rows = stmt.all(now) as any[];
      return rows.map(this.mapRowToRecurringTask);
    } catch (error) {
      logger.error('Failed to find due recurring tasks', error as Error);
      throw new DatabaseError('Failed to find due recurring tasks');
    }
  }

  /**
   * Get all recurring tasks
   */
  findAll(): RecurringTask[] {
    try {
      const stmt = this.db.getDb().prepare('SELECT * FROM recurring_tasks ORDER BY createdAt DESC');
      const rows = stmt.all() as any[];
      return rows.map(this.mapRowToRecurringTask);
    } catch (error) {
      logger.error('Failed to find all recurring tasks', error as Error);
      throw new DatabaseError('Failed to find all recurring tasks');
    }
  }

  /**
   * Update recurring task
   */
  update(input: UpdateRecurringTaskInput): RecurringTask {
    const existing = this.getById(input.id);
    const now = Date.now();

    try {
      const updates: string[] = [];
      const values: any[] = [];

      if (input.brainId !== undefined) {
        updates.push('brainId = ?');
        values.push(input.brainId);
      }
      if (input.title !== undefined) {
        updates.push('title = ?');
        values.push(input.title);
      }
      if (input.description !== undefined) {
        updates.push('description = ?');
        values.push(input.description);
      }
      if (input.pattern !== undefined) {
        updates.push('pattern = ?');
        values.push(input.pattern);
      }
      if (input.cronExpression !== undefined) {
        updates.push('cronExpression = ?');
        values.push(input.cronExpression);
      }
      if (input.payload !== undefined) {
        updates.push('payload = ?');
        values.push(JSON.stringify(input.payload));
      }
      if (input.modelOverride !== undefined) {
        updates.push('modelOverride = ?');
        values.push(input.modelOverride);
      }
      if (input.active !== undefined) {
        updates.push('active = ?');
        values.push(input.active ? 1 : 0);
        // Also update legacy enabled column for backward compatibility
        updates.push('enabled = ?');
        values.push(input.active ? 1 : 0);
      }
      if (input.lastExecutedAt !== undefined) {
        updates.push('lastExecutedAt = ?');
        values.push(input.lastExecutedAt);
      }
      if (input.nextExecutionAt !== undefined) {
        updates.push('nextExecutionAt = ?');
        values.push(input.nextExecutionAt);
      }
      if (input.sendDiscordNotification !== undefined) {
        updates.push('sendDiscordNotification = ?');
        values.push(input.sendDiscordNotification ? 1 : 0);
      }
      if (input.triggersReport !== undefined) {
        updates.push('triggersReport = ?');
        values.push(input.triggersReport ? 1 : 0);
      }
      if (input.reportDelayMinutes !== undefined) {
        updates.push('reportDelayMinutes = ?');
        values.push(input.reportDelayMinutes);
      }

      updates.push('updatedAt = ?');
      values.push(now);

      values.push(input.id);

      const stmt = this.db.getDb().prepare(`
        UPDATE recurring_tasks SET ${updates.join(', ')} WHERE id = ?
      `);

      stmt.run(...values);

      logger.info('Recurring task updated', { taskId: input.id });
      return this.getById(input.id);
    } catch (error) {
      logger.error('Failed to update recurring task', error as Error, { taskId: input.id });
      throw new DatabaseError('Failed to update recurring task');
    }
  }

  /**
   * Delete recurring task
   */
  delete(id: string): void {
    try {
      const stmt = this.db.getDb().prepare('DELETE FROM recurring_tasks WHERE id = ?');
      stmt.run(id);
      logger.info('Recurring task deleted', { taskId: id });
    } catch (error) {
      logger.error('Failed to delete recurring task', error as Error, { id });
      throw new DatabaseError('Failed to delete recurring task');
    }
  }

  /**
   * Map database row to RecurringTask
   */
  private mapRowToRecurringTask(row: any): RecurringTask {
    return {
      id: row.id,
      brainId: row.brainId,
      title: row.title,
      description: row.description,
      // Support both old schema (scheduleType) and new schema (pattern)
      pattern: row.pattern || row.scheduleType,
      cronExpression: row.cronExpression,
      payload: row.payload ? JSON.parse(row.payload) : {},
      modelOverride: row.modelOverride,
      // Support both old schema (enabled) and new schema (active)
      active: (row.active === 1) || (row.enabled === 1),
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
      lastExecutedAt: row.lastExecutedAt,
      nextExecutionAt: row.nextExecutionAt,
      sendDiscordNotification: row.sendDiscordNotification === 1,
      triggersReport: row.triggersReport === 1,
      reportDelayMinutes: row.reportDelayMinutes ?? 0,
    };
  }

  /**
   * Generate a unique ID
   */
  private generateId(): string {
    return `recurring_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}
