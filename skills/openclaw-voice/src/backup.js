import Database from 'better-sqlite3';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

/**
 * Backup the database to a file.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {string|null} [outputPath=null] - Optional output path.
 * @returns {Promise<string>} Path to backup file.
 */
export async function backupDb(db, outputPath = null) {
  const __dirname = path.dirname(fileURLToPath(import.meta.url));
  let backupPath;
  if (!outputPath) {
    fs.mkdirSync(path.join(__dirname, '..', 'backups'), { recursive: true });
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').replace('T', '-');
    backupPath = path.join(__dirname, '..', 'backups', `voice-backup-${timestamp}.db`);
  } else {
    backupPath = outputPath;
    fs.mkdirSync(path.dirname(backupPath), { recursive: true });
  }
  await db.backup(backupPath);
  return backupPath;
}

/**
 * Restore database from a backup file.
 * @param {string} backupFile - Path to backup file.
 * @param {string|null} [dbPath=null] - Optional target DB path.
 * @returns {Promise<void>}
 * @throws {Error} If backup file not found.
 */
export async function restoreDb(backupFile, dbPath = null) {
  if (!fs.existsSync(backupFile)) {
    throw new Error(`Backup file ${backupFile} not found`);
  }
  const __dirname = path.dirname(fileURLToPath(import.meta.url));
  const defaultDbPath = path.join(__dirname, '..', 'data', 'voice.db');
  const targetPath = dbPath || defaultDbPath;
  fs.mkdirSync(path.dirname(targetPath), { recursive: true });
  const backupDb = new Database(backupFile);
  await backupDb.backup(targetPath);
  backupDb.close();
}