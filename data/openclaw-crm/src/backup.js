import { copyFileSync, existsSync } from 'fs';
import { join } from 'path';

/**
 * Create a backup of the database by copying DB files.
 * @param {string} dbPath - Path to the main DB file (without extensions).
 * @param {string} [outDir='data'] - Output directory.
 * @param {string} [prefix='crm-backup'] - Backup prefix.
 * @returns {string} Path to the backup DB file.
 */
export function createBackup(dbPath, outDir = 'data', prefix = 'crm-backup') {
  const timestamp = new Date().toISOString().split('T')[0];
  const baseName = `${prefix}-${timestamp}.db`;
  const outPath = join(process.cwd(), outDir, baseName);
  copyDbFiles(dbPath, outPath.replace('.db', ''));
  return outPath;
}

function copyDbFiles(srcBase, destBase) {
  const extensions = ['', '.wal', '.shm'];
  extensions.forEach(ext => {
    const src = srcBase + ext;
    const dest = destBase + ext;
    if (existsSync(src)) {
      copyFileSync(src, dest);
    }
  });
}

/**
 * Restore database from backup by copying files.
 * @param {string} dbPath - Path to the main DB file (without extensions).
 * @param {string} backupPath - Path to the backup DB file (without extensions).
 * @throws {Error} If backup files not found.
 */
export function restoreFromBackup(dbPath, backupPath) {
  const backupBase = backupPath.replace(/\.db$/, '');
  if (!existsSync(backupBase + '.db')) {
    throw new Error(`Backup not found: ${backupPath}`);
  }
  // Optional: backup current
  try {
    createBackup(dbPath, 'data', 'pre-restore');
  } catch (e) {
    console.warn('Could not backup current DB:', e.message);
  }
  copyDbFiles(backupBase, dbPath);
  console.log(`Database restored from ${backupPath}`);
}