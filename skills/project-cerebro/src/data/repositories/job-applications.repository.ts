/**
 * Job Applications repository - tracking job search pipeline
 */

import { DatabaseConnection } from '../database';
import { logger } from '../../lib/logger';
import { DatabaseError } from '../../lib/errors';
import { randomUUID } from 'crypto';

export type JobApplicationStatus =
  | 'SAVED'
  | 'APPLIED'
  | 'FOLLOW_UP_PENDING'
  | 'FOLLOW_UP_SENT'
  | 'RESPONDED'
  | 'INTERVIEW_SCHEDULED'
  | 'INTERVIEWED'
  | 'OFFER'
  | 'REJECTED'
  | 'WITHDRAWN';

export interface JobApplication {
  id: string;
  jobId?: string; // External job ID from JobSpy/LinkedIn/etc
  company: string;
  position: string;
  url?: string;
  source?: string; // linkedin, indeed, glassdoor, etc
  status: JobApplicationStatus;
  salary?: string;
  location?: string;
  jobType?: string; // full-time, contract, etc
  description?: string;
  notes?: string;
  resumeUsed?: string;
  coverLetterGenerated: boolean;
  appliedAt?: number;
  followUpAt?: number;
  followUpSentAt?: number;
  lastContactAt?: number;
  responseAt?: number;
  interviewAt?: number;
  rejectedAt?: number;
  createdAt: number;
  updatedAt: number;
}

export interface CreateJobApplicationInput {
  jobId?: string;
  company: string;
  position: string;
  url?: string;
  source?: string;
  status?: JobApplicationStatus;
  salary?: string;
  location?: string;
  jobType?: string;
  description?: string;
  notes?: string;
  resumeUsed?: string;
}

export class JobApplicationsRepository {
  constructor(private db: DatabaseConnection) {}

  /**
   * Get all job applications
   */
  getAll(options?: { status?: JobApplicationStatus; limit?: number }): JobApplication[] {
    try {
      let query = 'SELECT * FROM job_applications';
      const params: any[] = [];

      if (options?.status) {
        query += ' WHERE status = ?';
        params.push(options.status);
      }

      query += ' ORDER BY updatedAt DESC';

      if (options?.limit) {
        query += ' LIMIT ?';
        params.push(options.limit);
      }

      const stmt = this.db.getDb().prepare(query);
      const rows = stmt.all(...params) as any[];
      return rows.map(this.mapRow);
    } catch (error) {
      logger.error('Failed to get job applications', error as Error);
      throw new DatabaseError('Failed to get job applications');
    }
  }

  /**
   * Get job application by ID
   */
  getById(id: string): JobApplication | null {
    try {
      const stmt = this.db.getDb().prepare('SELECT * FROM job_applications WHERE id = ?');
      const row = stmt.get(id) as any;
      return row ? this.mapRow(row) : null;
    } catch (error) {
      logger.error('Failed to get job application', error as Error, { id });
      throw new DatabaseError('Failed to get job application');
    }
  }

  /**
   * Get job application by external job ID
   */
  getByJobId(jobId: string): JobApplication | null {
    try {
      const stmt = this.db.getDb().prepare('SELECT * FROM job_applications WHERE jobId = ?');
      const row = stmt.get(jobId) as any;
      return row ? this.mapRow(row) : null;
    } catch (error) {
      logger.error('Failed to get job application by jobId', error as Error, { jobId });
      throw new DatabaseError('Failed to get job application by jobId');
    }
  }

  /**
   * Check if a job application already exists (by jobId or company+position)
   */
  exists(jobId?: string, company?: string, position?: string): boolean {
    try {
      if (jobId) {
        const stmt = this.db.getDb().prepare('SELECT 1 FROM job_applications WHERE jobId = ?');
        return !!stmt.get(jobId);
      }
      if (company && position) {
        const stmt = this.db.getDb().prepare(
          'SELECT 1 FROM job_applications WHERE company = ? AND position = ?'
        );
        return !!stmt.get(company, position);
      }
      return false;
    } catch (error) {
      logger.error('Failed to check job application existence', error as Error);
      return false;
    }
  }

  /**
   * Create a job application
   */
  create(input: CreateJobApplicationInput): JobApplication {
    try {
      const now = Date.now();
      const id = randomUUID();

      const stmt = this.db.getDb().prepare(`
        INSERT INTO job_applications (
          id, jobId, company, position, url, source, status, salary, location,
          jobType, description, notes, resumeUsed, coverLetterGenerated,
          createdAt, updatedAt
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);

      stmt.run(
        id,
        input.jobId || null,
        input.company,
        input.position,
        input.url || null,
        input.source || null,
        input.status || 'SAVED',
        input.salary || null,
        input.location || null,
        input.jobType || null,
        input.description || null,
        input.notes || null,
        input.resumeUsed || null,
        0, // coverLetterGenerated
        now,
        now
      );

      logger.info('Job application created', { id, company: input.company, position: input.position });
      return this.getById(id)!;
    } catch (error) {
      logger.error('Failed to create job application', error as Error, { input });
      throw new DatabaseError('Failed to create job application');
    }
  }

  /**
   * Update a job application
   */
  update(id: string, updates: Partial<JobApplication>): JobApplication | null {
    try {
      const existing = this.getById(id);
      if (!existing) return null;

      const now = Date.now();
      const stmt = this.db.getDb().prepare(`
        UPDATE job_applications SET
          jobId = ?,
          company = ?,
          position = ?,
          url = ?,
          source = ?,
          status = ?,
          salary = ?,
          location = ?,
          jobType = ?,
          description = ?,
          notes = ?,
          resumeUsed = ?,
          coverLetterGenerated = ?,
          appliedAt = ?,
          followUpAt = ?,
          followUpSentAt = ?,
          lastContactAt = ?,
          responseAt = ?,
          interviewAt = ?,
          rejectedAt = ?,
          updatedAt = ?
        WHERE id = ?
      `);

      stmt.run(
        updates.jobId ?? existing.jobId,
        updates.company ?? existing.company,
        updates.position ?? existing.position,
        updates.url ?? existing.url,
        updates.source ?? existing.source,
        updates.status ?? existing.status,
        updates.salary ?? existing.salary,
        updates.location ?? existing.location,
        updates.jobType ?? existing.jobType,
        updates.description ?? existing.description,
        updates.notes ?? existing.notes,
        updates.resumeUsed ?? existing.resumeUsed,
        updates.coverLetterGenerated !== undefined
          ? (updates.coverLetterGenerated ? 1 : 0)
          : (existing.coverLetterGenerated ? 1 : 0),
        updates.appliedAt ?? existing.appliedAt,
        updates.followUpAt ?? existing.followUpAt,
        updates.followUpSentAt ?? existing.followUpSentAt,
        updates.lastContactAt ?? existing.lastContactAt,
        updates.responseAt ?? existing.responseAt,
        updates.interviewAt ?? existing.interviewAt,
        updates.rejectedAt ?? existing.rejectedAt,
        now,
        id
      );

      logger.info('Job application updated', { id, status: updates.status });
      return this.getById(id);
    } catch (error) {
      logger.error('Failed to update job application', error as Error, { id });
      throw new DatabaseError('Failed to update job application');
    }
  }

  /**
   * Mark job as applied
   */
  markApplied(id: string, followUpDays: number = 3): JobApplication | null {
    const now = Date.now();
    const followUpAt = now + followUpDays * 24 * 60 * 60 * 1000;
    return this.update(id, {
      status: 'FOLLOW_UP_PENDING',
      appliedAt: now,
      followUpAt,
    });
  }

  /**
   * Get jobs needing follow-up
   */
  getPendingFollowUps(): JobApplication[] {
    try {
      const now = Date.now();
      const stmt = this.db.getDb().prepare(`
        SELECT * FROM job_applications
        WHERE status = 'FOLLOW_UP_PENDING' AND followUpAt <= ?
        ORDER BY followUpAt ASC
      `);
      const rows = stmt.all(now) as any[];
      return rows.map(this.mapRow);
    } catch (error) {
      logger.error('Failed to get pending follow-ups', error as Error);
      throw new DatabaseError('Failed to get pending follow-ups');
    }
  }

  /**
   * Delete a job application
   */
  delete(id: string): boolean {
    try {
      const stmt = this.db.getDb().prepare('DELETE FROM job_applications WHERE id = ?');
      const result = stmt.run(id);
      logger.info('Job application deleted', { id });
      return result.changes > 0;
    } catch (error) {
      logger.error('Failed to delete job application', error as Error, { id });
      throw new DatabaseError('Failed to delete job application');
    }
  }

  /**
   * Get statistics
   */
  getStats(): Record<JobApplicationStatus, number> {
    try {
      const stmt = this.db.getDb().prepare(
        'SELECT status, COUNT(*) as count FROM job_applications GROUP BY status'
      );
      const rows = stmt.all() as any[];
      const stats: Record<string, number> = {
        SAVED: 0,
        APPLIED: 0,
        FOLLOW_UP_PENDING: 0,
        FOLLOW_UP_SENT: 0,
        RESPONDED: 0,
        INTERVIEW_SCHEDULED: 0,
        INTERVIEWED: 0,
        OFFER: 0,
        REJECTED: 0,
        WITHDRAWN: 0,
      };
      for (const row of rows) {
        stats[row.status] = row.count;
      }
      return stats as Record<JobApplicationStatus, number>;
    } catch (error) {
      logger.error('Failed to get job application stats', error as Error);
      throw new DatabaseError('Failed to get job application stats');
    }
  }

  private mapRow(row: any): JobApplication {
    return {
      id: row.id,
      jobId: row.jobId,
      company: row.company,
      position: row.position,
      url: row.url,
      source: row.source,
      status: row.status,
      salary: row.salary,
      location: row.location,
      jobType: row.jobType,
      description: row.description,
      notes: row.notes,
      resumeUsed: row.resumeUsed,
      coverLetterGenerated: !!row.coverLetterGenerated,
      appliedAt: row.appliedAt,
      followUpAt: row.followUpAt,
      followUpSentAt: row.followUpSentAt,
      lastContactAt: row.lastContactAt,
      responseAt: row.responseAt,
      interviewAt: row.interviewAt,
      rejectedAt: row.rejectedAt,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
    };
  }
}
