/**
 * @module backup
 * Backup and restore the monitoring database.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_DB_PATH = path.join(__dirname, '..', 'data', 'monitor.db');

/**
 * Backup the database using SQLite's backup API.
 * @param {import('better-sqlite3').Database} db
 * @param {string} [outputPath] - Destination path
 * @returns {Promise<string>} Path to the backup file
 */
export async function backup(db, outputPath) {
  const dest = outputPath || path.join(__dirname, '..', 'data', `backup-${new Date().toISOString().slice(0, 10)}.db`);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  await db.backup(dest);
  return dest;
}

/**
 * Restore the database from a backup file.
 * @param {string} backupPath - Source backup file
 * @param {string} [dbPath] - Target database path
 * @returns {string} Path to the restored database
 */
export function restore(backupPath, dbPath) {
  const dest = dbPath || DEFAULT_DB_PATH;
  if (!fs.existsSync(backupPath)) {
    throw new Error(`Backup file not found: ${backupPath}`);
  }
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(backupPath, dest);
  return dest;
}
