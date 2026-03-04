/**
 * SQLite client using sql.js (pure JS implementation)
 */

import initSqlJs, { type Database, type SqlValue } from 'sql.js';
import { readFile, writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import { dirname } from 'path';
import { config } from '../config/index.js';
import { createLogger } from '../utils/logger.js';
import { DatabaseError } from '../errors/index.js';

const logger = createLogger('sqlite');

let db: Database | null = null;

/**
 * Initialize the SQLite database
 */
export async function initDatabase(): Promise<Database> {
  if (db) return db;

  try {
    const SQL = await initSqlJs();

    // Ensure data directory exists
    const dbDir = dirname(config.DATABASE_PATH);
    if (!existsSync(dbDir)) {
      await mkdir(dbDir, { recursive: true });
    }

    // Load existing database or create new one
    if (existsSync(config.DATABASE_PATH)) {
      logger.info(`Loading database from ${config.DATABASE_PATH}`);
      const buffer = await readFile(config.DATABASE_PATH);
      db = new SQL.Database(buffer);
    } else {
      logger.info(`Creating new database at ${config.DATABASE_PATH}`);
      db = new SQL.Database();
    }

    // Run migrations
    await runMigrations(db);

    return db;
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    throw new DatabaseError(`Failed to initialize database: ${message}`, 'INIT');
  }
}

/**
 * Get the database instance
 */
export function getDatabase(): Database {
  if (!db) {
    throw new DatabaseError('Database not initialized. Call initDatabase() first.', 'GET');
  }
  return db;
}

/**
 * Save the database to disk
 */
export async function saveDatabase(): Promise<void> {
  if (!db) return;

  try {
    const data = db.export();
    const buffer = Buffer.from(data);
    await writeFile(config.DATABASE_PATH, buffer);
    logger.debug('Database saved to disk');
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    throw new DatabaseError(`Failed to save database: ${message}`, 'SAVE');
  }
}

/**
 * Close the database connection
 */
export async function closeDatabase(): Promise<void> {
  if (db) {
    await saveDatabase();
    db.close();
    db = null;
    logger.info('Database closed');
  }
}

/**
 * Run database migrations
 */
async function runMigrations(database: Database): Promise<void> {
  // Create migrations table if not exists
  database.run(`
    CREATE TABLE IF NOT EXISTS migrations (
      id INTEGER PRIMARY KEY,
      name TEXT NOT NULL,
      applied_at TEXT NOT NULL
    )
  `);

  // Check which migrations have been applied
  const appliedMigrations = new Set<string>();
  const result = database.exec('SELECT name FROM migrations');
  if (result[0]) {
    for (const row of result[0].values) {
      appliedMigrations.add(row[0] as string);
    }
  }

  // Define migrations
  const migrations: { name: string; sql: string }[] = [
    {
      name: '001_create_leads_table',
      sql: `
        CREATE TABLE IF NOT EXISTS leads (
          id TEXT PRIMARY KEY,
          company_name TEXT NOT NULL,
          contact_name TEXT,
          email TEXT,
          phone TEXT,
          website TEXT,
          address TEXT,
          city TEXT,
          state TEXT,
          zip_code TEXT,
          trade TEXT NOT NULL,
          source TEXT NOT NULL,
          source_url TEXT,
          source_id TEXT,
          rating REAL,
          review_count INTEGER,
          normalized_name TEXT NOT NULL,
          normalized_phone TEXT,
          normalized_address TEXT,
          status TEXT NOT NULL DEFAULT 'New',
          notes TEXT DEFAULT '',
          confidence REAL DEFAULT 0,
          duplicate_of TEXT,
          metadata TEXT DEFAULT '{}',
          scraped_at TEXT NOT NULL,
          enriched_at TEXT,
          verified_at TEXT,
          created_at TEXT NOT NULL DEFAULT (datetime('now')),
          updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
      `,
    },
    {
      name: '002_create_leads_indexes',
      sql: `
        CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
        CREATE INDEX IF NOT EXISTS idx_leads_trade ON leads(trade);
        CREATE INDEX IF NOT EXISTS idx_leads_source ON leads(source);
        CREATE INDEX IF NOT EXISTS idx_leads_normalized_name ON leads(normalized_name);
        CREATE INDEX IF NOT EXISTS idx_leads_normalized_phone ON leads(normalized_phone);
        CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
        CREATE INDEX IF NOT EXISTS idx_leads_source_id ON leads(source, source_id);
      `,
    },
    {
      name: '003_create_scrape_jobs_table',
      sql: `
        CREATE TABLE IF NOT EXISTS scrape_jobs (
          id TEXT PRIMARY KEY,
          source TEXT NOT NULL,
          query TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'pending',
          attempts INTEGER DEFAULT 0,
          error TEXT,
          progress_found INTEGER DEFAULT 0,
          progress_processed INTEGER DEFAULT 0,
          created_at TEXT NOT NULL DEFAULT (datetime('now')),
          started_at TEXT,
          completed_at TEXT
        )
      `,
    },
    {
      name: '004_create_enrichment_jobs_table',
      sql: `
        CREATE TABLE IF NOT EXISTS enrichment_jobs (
          id TEXT PRIMARY KEY,
          lead_id TEXT NOT NULL,
          provider TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'pending',
          attempts INTEGER DEFAULT 0,
          error TEXT,
          created_at TEXT NOT NULL DEFAULT (datetime('now')),
          completed_at TEXT,
          FOREIGN KEY (lead_id) REFERENCES leads(id)
        )
      `,
    },
    {
      name: '005_add_verification_and_scoring_columns',
      sql: `
        ALTER TABLE leads ADD COLUMN email_verified INTEGER DEFAULT 0;
        ALTER TABLE leads ADD COLUMN email_verification_status TEXT;
        ALTER TABLE leads ADD COLUMN phone_verified INTEGER DEFAULT 0;
        ALTER TABLE leads ADD COLUMN phone_type TEXT;
        ALTER TABLE leads ADD COLUMN phone_carrier TEXT;
        ALTER TABLE leads ADD COLUMN lead_score INTEGER;
      `,
    },
  ];

  // Apply new migrations
  for (const migration of migrations) {
    if (!appliedMigrations.has(migration.name)) {
      logger.info(`Applying migration: ${migration.name}`);
      database.run(migration.sql);
      database.run(
        'INSERT INTO migrations (name, applied_at) VALUES (?, datetime("now"))',
        [migration.name]
      );
    }
  }

  logger.debug('Migrations complete');
}

/**
 * Execute a query and return results
 */
export function query<T>(sql: string, params: SqlValue[] = []): T[] {
  const database = getDatabase();
  const stmt = database.prepare(sql);
  stmt.bind(params);

  const results: T[] = [];
  while (stmt.step()) {
    results.push(stmt.getAsObject() as T);
  }
  stmt.free();

  return results;
}

/**
 * Execute a query that modifies data
 */
export function execute(sql: string, params: SqlValue[] = []): void {
  const database = getDatabase();
  database.run(sql, params);
}

/**
 * Get the number of rows affected by the last operation
 */
export function getChanges(): number {
  const database = getDatabase();
  const result = database.exec('SELECT changes()');
  return (result[0]?.values[0]?.[0] as number) ?? 0;
}
