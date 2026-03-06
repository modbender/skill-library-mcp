/**
 * Job repository
 */

import { DatabaseConnection } from '../database';
import { logger } from '../../lib/logger';
import { DatabaseError, RecordNotFoundError } from '../../lib/errors';
import { Job, CreateJobInput, UpdateJobInput, JobStatus } from '../../domain/types/job';

export class JobRepository {
  constructor(private db: DatabaseConnection) {}

  /**
   * Create a new job
   */
  create(input: CreateJobInput): Job {
    const now = Date.now();
    const job: Job = {
      id: this.generateId(),
      title: input.title,
      company: input.company,
      url: input.url,
      status: input.status || JobStatus.DISCOVERED,
      salary: input.salary,
      location: input.location,
      notes: input.notes,
      appliedAt: input.appliedAt,
      createdAt: now,
      updatedAt: now,
    };

    try {
      const stmt = this.db.getDb().prepare(`
        INSERT INTO jobs (
          id, title, company, url, status, salary, location, notes, appliedAt, createdAt, updatedAt
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);

      stmt.run(
        job.id,
        job.title,
        job.company,
        job.url || null,
        job.status,
        job.salary || null,
        job.location || null,
        job.notes || null,
        job.appliedAt || null,
        job.createdAt,
        job.updatedAt
      );

      logger.info('Job created', { jobId: job.id, company: job.company });
      return job;
    } catch (error) {
      logger.error('Failed to create job', error as Error, { job });
      throw new DatabaseError('Failed to create job');
    }
  }

  /**
   * Find job by ID
   */
  findById(id: string): Job | null {
    try {
      const stmt = this.db.getDb().prepare('SELECT * FROM jobs WHERE id = ?');
      const row = stmt.get(id) as any;
      return row ? this.mapRowToJob(row) : null;
    } catch (error) {
      logger.error('Failed to find job by id', error as Error, { id });
      throw new DatabaseError('Failed to find job by id');
    }
  }

  /**
   * Get job by ID (throws if not found)
   */
  getById(id: string): Job {
    const job = this.findById(id);
    if (!job) {
      throw new RecordNotFoundError('Job', id);
    }
    return job;
  }

  /**
   * Find all jobs
   */
  findAll(): Job[] {
    try {
      const stmt = this.db.getDb().prepare('SELECT * FROM jobs ORDER BY createdAt DESC');
      const rows = stmt.all() as any[];
      return rows.map(this.mapRowToJob);
    } catch (error) {
      logger.error('Failed to find all jobs', error as Error);
      throw new DatabaseError('Failed to find all jobs');
    }
  }

  /**
   * Find jobs by status
   */
  findByStatus(status: JobStatus): Job[] {
    try {
      const stmt = this.db.getDb().prepare('SELECT * FROM jobs WHERE status = ? ORDER BY createdAt DESC');
      const rows = stmt.all(status) as any[];
      return rows.map(this.mapRowToJob);
    } catch (error) {
      logger.error('Failed to find jobs by status', error as Error, { status });
      throw new DatabaseError('Failed to find jobs by status');
    }
  }

  /**
   * Update job
   */
  update(input: UpdateJobInput): Job {
    const existing = this.getById(input.id);
    const now = Date.now();

    try {
      const updates: string[] = [];
      const values: any[] = [];

      if (input.title !== undefined) {
        updates.push('title = ?');
        values.push(input.title);
      }
      if (input.company !== undefined) {
        updates.push('company = ?');
        values.push(input.company);
      }
      if (input.url !== undefined) {
        updates.push('url = ?');
        values.push(input.url);
      }
      if (input.status !== undefined) {
        updates.push('status = ?');
        values.push(input.status);
      }
      if (input.salary !== undefined) {
        updates.push('salary = ?');
        values.push(input.salary);
      }
      if (input.location !== undefined) {
        updates.push('location = ?');
        values.push(input.location);
      }
      if (input.notes !== undefined) {
        updates.push('notes = ?');
        values.push(input.notes);
      }
      if (input.appliedAt !== undefined) {
        updates.push('appliedAt = ?');
        values.push(input.appliedAt);
      }

      updates.push('updatedAt = ?');
      values.push(now);

      values.push(input.id);

      const stmt = this.db.getDb().prepare(`
        UPDATE jobs SET ${updates.join(', ')} WHERE id = ?
      `);

      stmt.run(...values);

      logger.info('Job updated', { jobId: input.id });
      return this.getById(input.id);
    } catch (error) {
      logger.error('Failed to update job', error as Error, { jobId: input.id });
      throw new DatabaseError('Failed to update job');
    }
  }

  /**
   * Delete job
   */
  delete(id: string): void {
    try {
      const stmt = this.db.getDb().prepare('DELETE FROM jobs WHERE id = ?');
      stmt.run(id);
      logger.info('Job deleted', { jobId: id });
    } catch (error) {
      logger.error('Failed to delete job', error as Error, { id });
      throw new DatabaseError('Failed to delete job');
    }
  }

  /**
   * Map database row to Job
   */
  private mapRowToJob(row: any): Job {
    return {
      id: row.id,
      title: row.title,
      company: row.company,
      url: row.url,
      status: row.status as JobStatus,
      salary: row.salary,
      location: row.location,
      notes: row.notes,
      appliedAt: row.appliedAt,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
    };
  }

  /**
   * Generate a unique ID
   */
  private generateId(): string {
    return `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}
