/**
 * @module backup
 * Database backup and restore.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_DB_PATH = path.join(__dirname, '..', 'data', 'orchestration.db');

/**
 * Backup the database using SQLite's backup API.
 * @param {import('better-sqlite3').Database} db
 * @param {string} [outputPath] - Output file path
 * @returns {string} Path to backup file
 */
export async function backup(db, outputPath) {
  const dest = outputPath || path.join(__dirname, '..', 'data', `backup-${Date.now()}.db`);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  await db.backup(dest);
  return dest;
}

/**
 * Restore database from a backup file.
 * @param {string} backupPath - Path to backup file
 * @param {string} [targetPath] - Target database path
 */
export function restore(backupPath, targetPath) {
  const dest = targetPath || DEFAULT_DB_PATH;
  if (!fs.existsSync(backupPath)) throw new Error(`Backup file not found: ${backupPath}`);
  // Warn if WAL/SHM files exist (active connections could cause corruption)
  const walPath = `${dest}-wal`;
  const shmPath = `${dest}-shm`;
  if (fs.existsSync(walPath) || fs.existsSync(shmPath)) {
    console.warn('⚠️  WAL/SHM files detected — close all DB connections before restoring to avoid corruption.');
  }
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(backupPath, dest);
}
