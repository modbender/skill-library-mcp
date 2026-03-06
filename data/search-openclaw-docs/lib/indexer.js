/**
 * File-Level Indexer
 * Builds SQLite index with FTS5 for keyword search
 */

const fs = require('fs');
const path = require('path');
const { extractFileMetadata } = require('./metadata');

/**
 * Find all markdown files recursively
 */
function findMarkdownFiles(dir, files = []) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    
    if (entry.isDirectory()) {
      // Skip non-English docs and node_modules
      if (!['zh-CN', 'node_modules', '.git'].includes(entry.name)) {
        findMarkdownFiles(fullPath, files);
      }
    } else if (entry.name.endsWith('.md')) {
      files.push(fullPath);
    }
  }
  
  return files;
}

/**
 * Build the index
 */
async function buildIndex(docsPath, indexPath, options = {}) {
  const { onProgress } = options;
  
  // Ensure directory exists
  const indexDir = path.dirname(indexPath);
  fs.mkdirSync(indexDir, { recursive: true });
  
  // Remove old index
  if (fs.existsSync(indexPath)) {
    fs.unlinkSync(indexPath);
  }
  
  // Load SQLite
  const Database = require('better-sqlite3');
  const db = new Database(indexPath);
  
  // Create tables
  db.exec(`
    -- Main file metadata
    CREATE TABLE files (
      id INTEGER PRIMARY KEY,
      path TEXT UNIQUE,
      rel_path TEXT,
      title TEXT,
      headers TEXT,
      keywords TEXT,
      summary TEXT
    );
    
    -- FTS5 for fast keyword search
    CREATE VIRTUAL TABLE files_fts USING fts5(
      rel_path,
      title,
      headers,
      keywords,
      summary,
      content='files',
      content_rowid='id',
      tokenize='porter unicode61'
    );
    
    -- Triggers to keep FTS in sync
    CREATE TRIGGER files_ai AFTER INSERT ON files BEGIN
      INSERT INTO files_fts(rowid, rel_path, title, headers, keywords, summary)
      VALUES (new.id, new.rel_path, new.title, new.headers, new.keywords, new.summary);
    END;
    
    CREATE INDEX idx_files_path ON files(path);
  `);
  
  // Find files
  const files = findMarkdownFiles(docsPath);
  
  // Prepare insert
  const insert = db.prepare(`
    INSERT INTO files (path, rel_path, title, headers, keywords, summary)
    VALUES (?, ?, ?, ?, ?, ?)
  `);
  
  let indexed = 0;
  let errors = 0;
  
  for (let i = 0; i < files.length; i++) {
    const filePath = files[i];
    const relPath = filePath.replace(docsPath + '/', '');
    
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const meta = extractFileMetadata(content, filePath);
      
      insert.run(
        filePath,
        relPath,
        meta.title,
        meta.headers.join(' | '),
        meta.keywords.join(' '),
        meta.summary
      );
      
      indexed++;
      
      if (onProgress && (i % 20 === 0 || i === files.length - 1)) {
        onProgress({ current: i + 1, total: files.length, indexed, errors });
      }
      
    } catch (e) {
      errors++;
      console.error(`  ❌ ${relPath}: ${e.message}`);
    }
  }
  
  db.close();
  
  return { total: files.length, indexed, errors };
}

module.exports = {
  buildIndex,
  findMarkdownFiles
};
