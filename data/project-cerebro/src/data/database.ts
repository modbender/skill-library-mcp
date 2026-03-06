/**
 * Database wrapper using better-sqlite3 for synchronous, promisified API
 */

import Database from 'better-sqlite3';
import { logger } from '../lib/logger';
import { DatabaseError } from '../lib/errors';

export class DatabaseConnection {
  private db: Database.Database;
  private isInitialized: boolean = false;

  constructor(private dbPath: string) {
    try {
      this.db = new Database(dbPath);
      this.db.pragma('journal_mode = WAL');
      logger.info('Database connection established', { dbPath });
    } catch (error) {
      logger.error('Failed to connect to database', error as Error, { dbPath });
      throw new DatabaseError('Failed to connect to database', { dbPath });
    }
  }

  /**
   * Initialize database schema
   */
  init(): void {
    if (this.isInitialized) {
      return;
    }

    try {
      // Tasks table
      this.db.exec(`
        CREATE TABLE IF NOT EXISTS tasks (
          id TEXT PRIMARY KEY,
          brainId TEXT NOT NULL,
          brainName TEXT,
          status TEXT NOT NULL,
          title TEXT NOT NULL,
          description TEXT,
          payload TEXT,
          modelOverride TEXT,
          dependencies TEXT,
          executeAt INTEGER,
          createdAt INTEGER NOT NULL,
          updatedAt INTEGER NOT NULL,
          attempts INTEGER DEFAULT 0,
          retryPolicy TEXT,
          error TEXT,
          output TEXT
        )
      `);

      // Jobs table
      this.db.exec(`
        CREATE TABLE IF NOT EXISTS jobs (
          id TEXT PRIMARY KEY,
          title TEXT NOT NULL,
          company TEXT NOT NULL,
          url TEXT,
          status TEXT NOT NULL,
          salary TEXT,
          location TEXT,
          notes TEXT,
          appliedAt INTEGER,
          createdAt INTEGER NOT NULL,
          updatedAt INTEGER NOT NULL
        )
      `);

      // Recurring tasks table
      this.db.exec(`
        CREATE TABLE IF NOT EXISTS recurring_tasks (
          id TEXT PRIMARY KEY,
          brainId TEXT NOT NULL,
          brainName TEXT,
          title TEXT NOT NULL,
          description TEXT,
          pattern TEXT NOT NULL,
          cronExpression TEXT,
          payload TEXT,
          modelOverride TEXT,
          active INTEGER DEFAULT 1,
          createdAt INTEGER NOT NULL,
          updatedAt INTEGER NOT NULL,
          lastExecutedAt INTEGER,
          nextExecutionAt INTEGER
        )
      `);

      // Brain configs table
      this.db.exec(`
        CREATE TABLE IF NOT EXISTS brain_configs (
          brainId TEXT PRIMARY KEY,
          config TEXT NOT NULL,
          updatedAt INTEGER NOT NULL
        )
      `);

      // Create indexes
      this.db.exec(`
        CREATE INDEX IF NOT EXISTS idx_tasks_brainId ON tasks(brainId);
        CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
        CREATE INDEX IF NOT EXISTS idx_tasks_executeAt ON tasks(executeAt);
        CREATE INDEX IF NOT EXISTS idx_recurring_tasks_brainId ON recurring_tasks(brainId);
        CREATE INDEX IF NOT EXISTS idx_recurring_tasks_nextExecutionAt ON recurring_tasks(nextExecutionAt);
      `);

      // Migration: Add sendDiscordNotification column to tasks table
      try {
        this.db.exec(`ALTER TABLE tasks ADD COLUMN sendDiscordNotification INTEGER DEFAULT 1`);
        logger.info('Added sendDiscordNotification column to tasks table');
      } catch (e) {
        // Column already exists
      }

      // Migration: Add sendDiscordNotification column to recurring_tasks table
      try {
        this.db.exec(`ALTER TABLE recurring_tasks ADD COLUMN sendDiscordNotification INTEGER DEFAULT 1`);
        logger.info('Added sendDiscordNotification column to recurring_tasks table');
      } catch (e) {
        // Column already exists
      }

      // Migration: Add triggersReport column to recurring_tasks table
      try {
        this.db.exec(`ALTER TABLE recurring_tasks ADD COLUMN triggersReport INTEGER DEFAULT 0`);
        logger.info('Added triggersReport column to recurring_tasks table');
      } catch (e) {
        // Column already exists
      }

      // Migration: Add reportDelayMinutes column to recurring_tasks table
      try {
        this.db.exec(`ALTER TABLE recurring_tasks ADD COLUMN reportDelayMinutes INTEGER DEFAULT 0`);
        logger.info('Added reportDelayMinutes column to recurring_tasks table');
      } catch (e) {
        // Column already exists
      }

      // Back-compat columns used by the API layer / UI schema
      // (The repo historically used scheduleType/enabled; the DB now stores pattern/active.)
      try {
        this.db.exec(`ALTER TABLE recurring_tasks ADD COLUMN scheduleType TEXT`);
        logger.info('Added scheduleType column to recurring_tasks table');
      } catch (e) {
        // Column already exists
      }

      try {
        this.db.exec(`ALTER TABLE recurring_tasks ADD COLUMN enabled INTEGER DEFAULT 1`);
        logger.info('Added enabled column to recurring_tasks table');
      } catch (e) {
        // Column already exists
      }

      // Brains table (source of truth for brain definitions)
      this.db.exec(`
        CREATE TABLE IF NOT EXISTS brains (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          channelKey TEXT NOT NULL,
          type TEXT DEFAULT 'context',
          description TEXT,
          openClawAgentId TEXT,
          discordChannelId TEXT,
          enabled INTEGER DEFAULT 1,
          createdAt INTEGER NOT NULL,
          updatedAt INTEGER NOT NULL
        )
      `);

      // Enhanced jobs table for job application tracking
      this.db.exec(`
        CREATE TABLE IF NOT EXISTS job_applications (
          id TEXT PRIMARY KEY,
          jobId TEXT UNIQUE,
          company TEXT NOT NULL,
          position TEXT NOT NULL,
          url TEXT,
          source TEXT,
          status TEXT NOT NULL DEFAULT 'SAVED',
          salary TEXT,
          location TEXT,
          jobType TEXT,
          description TEXT,
          notes TEXT,
          resumeUsed TEXT,
          coverLetterGenerated INTEGER DEFAULT 0,
          appliedAt INTEGER,
          followUpAt INTEGER,
          followUpSentAt INTEGER,
          lastContactAt INTEGER,
          responseAt INTEGER,
          interviewAt INTEGER,
          rejectedAt INTEGER,
          createdAt INTEGER NOT NULL,
          updatedAt INTEGER NOT NULL
        )
      `);

      // Create indexes for job_applications
      this.db.exec(`
        CREATE INDEX IF NOT EXISTS idx_job_applications_status ON job_applications(status);
        CREATE INDEX IF NOT EXISTS idx_job_applications_company ON job_applications(company);
        CREATE INDEX IF NOT EXISTS idx_job_applications_followUpAt ON job_applications(followUpAt);
      `);

      this.isInitialized = true;
      logger.info('Database schema initialized');
    } catch (error) {
      logger.error('Failed to initialize database schema', error as Error);
      throw new DatabaseError('Failed to initialize database schema');
    }
  }

  /**
   * Get the underlying database instance
   */
  getDb(): Database.Database {
    return this.db;
  }

  /**
   * Close database connection
   */
  close(): void {
    try {
      this.db.close();
      logger.info('Database connection closed');
    } catch (error) {
      logger.error('Failed to close database connection', error as Error);
      throw new DatabaseError('Failed to close database connection');
    }
  }

  /**
   * Execute a transaction
   */
  transaction<T>(fn: () => T): T {
    const txn = this.db.transaction(fn);
    return txn();
  }
}

let dbInstance: DatabaseConnection | null = null;

/**
 * Get singleton database instance
 */
export const getDatabase = (dbPath?: string): DatabaseConnection => {
  if (!dbInstance) {
    if (!dbPath) {
      throw new DatabaseError('Database path must be provided on first call');
    }
    dbInstance = new DatabaseConnection(dbPath);
    dbInstance.init();
  }
  return dbInstance;
};

/**
 * Close database connection
 */
export const closeDatabase = (): void => {
  if (dbInstance) {
    dbInstance.close();
    dbInstance = null;
  }
};
