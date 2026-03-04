/**
 * Task repository - clean interface for task data access
 */

import { DatabaseConnection } from '../database';
import { logger } from '../../lib/logger';
import { DatabaseError, RecordNotFoundError } from '../../lib/errors';
import {
  Task,
  TaskStatus,
  CreateTaskInput,
  UpdateTaskInput,
  TaskDependency,
  TaskRetryPolicy,
} from '../../domain/types/task';

export class TaskRepository {
  constructor(private db: DatabaseConnection) {}

  /**
   * Create a new task
   */
  create(input: CreateTaskInput): Task {
    const now = Date.now();
    const task: Task = {
      id: this.generateId(),
      brainId: input.brainId,
      status: TaskStatus.READY,
      title: input.title,
      description: input.description,
      payload: input.payload || {},
      modelOverride: input.modelOverride,
      dependencies: input.dependencies || [],
      executeAt: input.executeAt,
      createdAt: now,
      updatedAt: now,
      attempts: 0,
      retryPolicy: input.retryPolicy,
      sendDiscordNotification: input.sendDiscordNotification ?? true,
    };

    try {
      const stmt = this.db.getDb().prepare(`
        INSERT INTO tasks (
          id, brainId, status, title, description, payload, modelOverride,
          dependencies, executeAt, createdAt, updatedAt, attempts, retryPolicy,
          sendDiscordNotification
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);

      stmt.run(
        task.id,
        task.brainId,
        task.status,
        task.title,
        task.description || null,
        JSON.stringify(task.payload),
        task.modelOverride || null,
        JSON.stringify(task.dependencies),
        task.executeAt || null,
        task.createdAt,
        task.updatedAt,
        task.attempts,
        task.retryPolicy ? JSON.stringify(task.retryPolicy) : null,
        task.sendDiscordNotification ? 1 : 0
      );

      logger.info('Task created', { taskId: task.id, brainId: task.brainId });
      return task;
    } catch (error) {
      logger.error('Failed to create task', error as Error, { task });
      throw new DatabaseError('Failed to create task');
    }
  }

  /**
   * Find task by ID
   */
  findById(id: string): Task | null {
    try {
      const stmt = this.db.getDb().prepare('SELECT * FROM tasks WHERE id = ?');
      const row = stmt.get(id) as any;
      return row ? this.mapRowToTask(row) : null;
    } catch (error) {
      logger.error('Failed to find task by id', error as Error, { id });
      throw new DatabaseError('Failed to find task by id');
    }
  }

  /**
   * Get task by ID (throws if not found)
   */
  getById(id: string): Task {
    const task = this.findById(id);
    if (!task) {
      throw new RecordNotFoundError('Task', id);
    }
    return task;
  }

  /**
   * Find all tasks for a brain
   */
  findByBrainId(brainId: string): Task[] {
    try {
      const stmt = this.db.getDb().prepare('SELECT * FROM tasks WHERE brainId = ? ORDER BY createdAt DESC');
      const rows = stmt.all(brainId) as any[];
      return rows.map(this.mapRowToTask);
    } catch (error) {
      logger.error('Failed to find tasks by brain id', error as Error, { brainId });
      throw new DatabaseError('Failed to find tasks by brain id');
    }
  }

  /**
   * Find tasks by status
   */
  findByStatus(status: TaskStatus): Task[] {
    try {
      const stmt = this.db.getDb().prepare('SELECT * FROM tasks WHERE status = ? ORDER BY createdAt DESC');
      const rows = stmt.all(status) as any[];
      return rows.map(this.mapRowToTask);
    } catch (error) {
      logger.error('Failed to find tasks by status', error as Error, { status });
      throw new DatabaseError('Failed to find tasks by status');
    }
  }

  /**
   * Get ready tasks for a brain (READY status and executeAt <= now or null)
   */
  getReadyTasks(brainId: string): Task[] {
    try {
      const now = Date.now();
      const stmt = this.db.getDb().prepare(`
        SELECT * FROM tasks 
        WHERE brainId = ? 
          AND status = ? 
          AND (executeAt IS NULL OR executeAt <= ?)
        ORDER BY createdAt ASC
      `);
      const rows = stmt.all(brainId, TaskStatus.READY, now) as any[];
      return rows.map(this.mapRowToTask);
    } catch (error) {
      logger.error('Failed to get ready tasks', error as Error, { brainId });
      throw new DatabaseError('Failed to get ready tasks');
    }
  }

  /**
   * Get all tasks
   */
  findAll(): Task[] {
    try {
      const stmt = this.db.getDb().prepare('SELECT * FROM tasks ORDER BY createdAt DESC');
      const rows = stmt.all() as any[];
      return rows.map(this.mapRowToTask);
    } catch (error) {
      logger.error('Failed to find all tasks', error as Error);
      throw new DatabaseError('Failed to find all tasks');
    }
  }

  /**
   * Update task
   */
  update(input: UpdateTaskInput): Task {
    const existing = this.getById(input.id);
    const now = Date.now();

    try {
      const updates: string[] = [];
      const values: any[] = [];

      if (input.status !== undefined) {
        updates.push('status = ?');
        values.push(input.status);
      }
      if (input.title !== undefined) {
        updates.push('title = ?');
        values.push(input.title);
      }
      if (input.description !== undefined) {
        updates.push('description = ?');
        values.push(input.description);
      }
      if (input.payload !== undefined) {
        updates.push('payload = ?');
        values.push(JSON.stringify(input.payload));
      }
      if (input.modelOverride !== undefined) {
        updates.push('modelOverride = ?');
        values.push(input.modelOverride);
      }
      if (input.dependencies !== undefined) {
        updates.push('dependencies = ?');
        values.push(JSON.stringify(input.dependencies));
      }
      if (input.executeAt !== undefined) {
        updates.push('executeAt = ?');
        values.push(input.executeAt);
      }
      if (input.error !== undefined) {
        updates.push('error = ?');
        values.push(input.error);
      }
      if (input.output !== undefined) {
        updates.push('output = ?');
        values.push(input.output);
      }
      if (input.attempts !== undefined) {
        updates.push('attempts = ?');
        values.push(input.attempts);
      }
      if (input.sendDiscordNotification !== undefined) {
        updates.push('sendDiscordNotification = ?');
        values.push(input.sendDiscordNotification ? 1 : 0);
      }

      updates.push('updatedAt = ?');
      values.push(now);

      values.push(input.id);

      const stmt = this.db.getDb().prepare(`
        UPDATE tasks SET ${updates.join(', ')} WHERE id = ?
      `);

      stmt.run(...values);

      logger.info('Task updated', { taskId: input.id });
      return this.getById(input.id);
    } catch (error) {
      logger.error('Failed to update task', error as Error, { taskId: input.id });
      throw new DatabaseError('Failed to update task');
    }
  }

  /**
   * Update task status
   */
  updateStatus(id: string, status: TaskStatus): Task {
    return this.update({ id, status });
  }

  /**
   * Delete task
   */
  delete(id: string): void {
    try {
      const stmt = this.db.getDb().prepare('DELETE FROM tasks WHERE id = ?');
      stmt.run(id);
      logger.info('Task deleted', { taskId: id });
    } catch (error) {
      logger.error('Failed to delete task', error as Error, { id });
      throw new DatabaseError('Failed to delete task');
    }
  }

  /**
   * Map database row to Task
   */
  private mapRowToTask(row: any): Task {
    return {
      id: row.id,
      brainId: row.brainId,
      brainName: row.brainName,
      status: (row.status === 'PENDING' ? TaskStatus.READY : row.status) as TaskStatus,
      title: row.title,
      description: row.description,
      payload: row.payload ? JSON.parse(row.payload) : {},
      modelOverride: row.modelOverride,
      dependencies: row.dependencies ? JSON.parse(row.dependencies) : [],
      executeAt: row.executeAt,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
      attempts: row.attempts,
      retryPolicy: row.retryPolicy ? JSON.parse(row.retryPolicy) : undefined,
      error: row.error,
      output: row.output,
      sendDiscordNotification: row.sendDiscordNotification === 1,
    };
  }

  /**
   * Generate a unique ID
   */
  private generateId(): string {
    return `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}
