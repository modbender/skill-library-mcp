#!/usr/bin/env node
// Safe SQLite backup before git commit
const path = require('path');
const projectDir = path.join(__dirname, '..', 'projects', 'the-orbital');
const Database = require(path.join(projectDir, 'node_modules', 'better-sqlite3'));
const dbPath = path.join(projectDir, 'data', 'orbital.db');
const backupPath = path.join(projectDir, 'data', 'orbital-backup.db');
try {
  const db = new Database(dbPath, { readonly: true });
  db.backup(backupPath).then(() => {
    console.log('✅ DB backup complete');
    db.close();
  });
} catch (e) {
  console.error('DB backup failed:', e.message);
}
