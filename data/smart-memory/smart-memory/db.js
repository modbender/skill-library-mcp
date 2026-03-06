/**
 * SQLite database layer with FTS5 and optional sqlite-vec support
 */

import Database from 'better-sqlite3';
import path from 'path';
import fs from 'fs';

const DEFAULT_DB_PATH = path.join(process.cwd(), 'vector-memory.db');

// Track sqlite-vec availability
let sqliteVecAvailable = false;
let sqliteVecPath = null;

/**
 * Initialize database with schema
 * @param {string} dbPath - Path to SQLite database
 * @returns {Database}
 */
export function initDatabase(dbPath = DEFAULT_DB_PATH) {
    const dbDir = path.dirname(dbPath);
    if (!fs.existsSync(dbDir)) {
        fs.mkdirSync(dbDir, { recursive: true });
    }
    
    const db = new Database(dbPath);
    db.pragma('journal_mode = WAL'); // Better concurrency
    
    // Check for sqlite-vec extension
    checkSqliteVec(db);
    
    // Create tables
    createSchema(db);
    
    return db;
}

/**
 * Check if sqlite-vec extension is available
 */
function checkSqliteVec(db) {
    // Common paths for sqlite-vec
    const possiblePaths = [
        '/usr/lib/sqlite3/vec0.so',
        '/usr/local/lib/sqlite3/vec0.so',
        path.join(process.cwd(), 'vec0.so'),
        path.join(process.env.HOME || '', '.local/lib/vec0.so'),
    ];
    
    for (const extPath of possiblePaths) {
        if (fs.existsSync(extPath)) {
            try {
                db.loadExtension(extPath);
                sqliteVecAvailable = true;
                sqliteVecPath = extPath;
                console.error(`✓ sqlite-vec loaded: ${extPath}`);
                return;
            } catch (err) {
                // Try next path
            }
        }
    }
    
    // Try without path (system installed)
    try {
        db.loadExtension('vec0');
        sqliteVecAvailable = true;
        sqliteVecPath = 'vec0 (system)';
        console.error('✓ sqlite-vec loaded (system)');
    } catch (err) {
        console.error('ℹ sqlite-vec not available, using JS cosine similarity');
    }
}

/**
 * Create database schema
 */
function createSchema(db) {
    // Main chunks table
    db.exec(`
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            start_line INTEGER NOT NULL,
            end_line INTEGER NOT NULL,
            content TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            embedding BLOB,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(path, start_line, end_line)
        );
        
        CREATE INDEX IF NOT EXISTS idx_chunks_path ON chunks(path);
        CREATE INDEX IF NOT EXISTS idx_chunks_hash ON chunks(content_hash);
    `);
    
    // FTS5 virtual table for full-text search
    db.exec(`
        CREATE VIRTUAL TABLE IF NOT EXISTS fts_chunks USING fts5(
            content,
            content='chunks',
            content_rowid='id'
        );
        
        -- Triggers to keep FTS index in sync
        CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
            INSERT INTO fts_chunks(rowid, content) VALUES (new.id, new.content);
        END;
        
        CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
            INSERT INTO fts_chunks(fts_chunks, rowid, content) VALUES ('delete', old.id, old.content);
        END;
        
        CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
            INSERT INTO fts_chunks(fts_chunks, rowid, content) VALUES ('delete', old.id, old.content);
            INSERT INTO fts_chunks(rowid, content) VALUES (new.id, new.content);
        END;
    `);
    
    // Virtual table for sqlite-vec if available
    if (sqliteVecAvailable) {
        try {
            db.exec(`
                CREATE VIRTUAL TABLE IF NOT EXISTS vec_chunks USING vec0(
                    chunk_id INTEGER PRIMARY KEY,
                    embedding float[384]
                );
            `);
            console.error('✓ vec0 virtual table created');
        } catch (err) {
            console.error('⚠ Failed to create vec0 table:', err.message);
            sqliteVecAvailable = false;
        }
    }
    
    // Metadata table
    db.exec(`
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT
        );
    `);
    
    // Memory settings table (for mode toggles, etc.)
    db.exec(`
        CREATE TABLE IF NOT EXISTS memory_settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    `);
}

/**
 * Check if sqlite-vec is available
 * @returns {boolean}
 */
export function isSqliteVecAvailable() {
    return sqliteVecAvailable;
}

/**
 * Insert or update a chunk
 * @param {Database} db
 * @param {Object} chunk
 * @param {Float32Array} embedding
 */
export function upsertChunk(db, chunk, embedding) {
    const embeddingBlob = Buffer.from(embedding.buffer);
    
    const insert = db.prepare(`
        INSERT INTO chunks (path, start_line, end_line, content, content_hash, embedding)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(path, start_line, end_line) DO UPDATE SET
            content = excluded.content,
            content_hash = excluded.content_hash,
            embedding = excluded.embedding,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
    `);
    
    const result = insert.get(
        chunk.path,
        chunk.startLine,
        chunk.endLine,
        chunk.content,
        chunk.hash,
        embeddingBlob
    );
    
    const chunkId = result.id;
    
    // Also insert into vec0 table if available
    if (sqliteVecAvailable) {
        try {
            const insertVec = db.prepare(`
                INSERT INTO vec_chunks (chunk_id, embedding)
                VALUES (?, ?)
                ON CONFLICT(chunk_id) DO UPDATE SET
                    embedding = excluded.embedding
            `);
            insertVec.run(chunkId, embeddingBlob);
        } catch (err) {
            // vec0 insert failed, continue without it
        }
    }
    
    return chunkId;
}

/**
 * Delete chunks for a specific file
 * @param {Database} db
 * @param {string} filePath
 */
export function deleteFileChunks(db, filePath) {
    // Delete from vec0 first (if available) to maintain FK consistency
    if (sqliteVecAvailable) {
        try {
            const deleteVec = db.prepare(`
                DELETE FROM vec_chunks 
                WHERE chunk_id IN (SELECT id FROM chunks WHERE path = ?)
            `);
            deleteVec.run(filePath);
        } catch (err) {
            // Continue even if vec0 delete fails
        }
    }
    
    const deleteChunks = db.prepare('DELETE FROM chunks WHERE path = ?');
    return deleteChunks.run(filePath).changes;
}

/**
 * Get all chunks for a file (for checking if sync needed)
 * @param {Database} db
 * @param {string} filePath
 * @returns {Array}
 */
export function getFileChunks(db, filePath) {
    const stmt = db.prepare('SELECT content_hash FROM chunks WHERE path = ?');
    return stmt.all(filePath);
}

/**
 * Search using sqlite-vec (k-nearest neighbors)
 * @param {Database} db
 * @param {Float32Array} queryEmbedding
 * @param {number} limit
 * @returns {Array}
 */
export function searchVectorKNN(db, queryEmbedding, limit = 20) {
    const embeddingBlob = Buffer.from(queryEmbedding.buffer);
    
    const stmt = db.prepare(`
        SELECT 
            c.id,
            c.path,
            c.start_line,
            c.end_line,
            c.content,
            distance as vec_distance
        FROM vec_chunks
        JOIN chunks c ON c.id = vec_chunks.chunk_id
        WHERE embedding MATCH ?
        ORDER BY distance
        LIMIT ?
    `);
    
    return stmt.all(embeddingBlob, limit);
}

/**
 * Search using FTS5 (BM25 ranking)
 * @param {Database} db
 * @param {string} query
 * @param {number} limit
 * @returns {Array}
 */
export function searchFTS(db, query, limit = 20) {
    // Sanitize query for FTS5
    const sanitizedQuery = query
        .replace(/"/g, '""')  // Escape quotes
        .split(/\s+/)
        .map(term => `"${term}"`)
        .join(' OR ');
    
    const stmt = db.prepare(`
        SELECT 
            c.id,
            c.path,
            c.start_line,
            c.end_line,
            c.content,
            rank as fts_rank
        FROM fts_chunks
        JOIN chunks c ON c.id = fts_chunks.rowid
        WHERE fts_chunks MATCH ?
        ORDER BY rank
        LIMIT ?
    `);
    
    return stmt.all(sanitizedQuery, limit);
}

/**
 * Get all chunks with embeddings (for JS cosine fallback)
 * @param {Database} db
 * @returns {Array}
 */
export function getAllChunksWithEmbeddings(db) {
    const stmt = db.prepare('SELECT id, path, start_line, end_line, content, embedding FROM chunks WHERE embedding IS NOT NULL');
    return stmt.all();
}

/**
 * Set metadata value
 * @param {Database} db
 * @param {string} key
 * @param {string} value
 */
export function setMeta(db, key, value) {
    const stmt = db.prepare('INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)');
    stmt.run(key, value);
}

/**
 * Get metadata value
 * @param {Database} db
 * @param {string} key
 * @returns {string|null}
 */
export function getMeta(db, key) {
    const stmt = db.prepare('SELECT value FROM meta WHERE key = ?');
    const result = stmt.get(key);
    return result ? result.value : null;
}

/**
 * Set memory setting value
 * @param {Database} db
 * @param {string} key
 * @param {string} value
 */
export function setSetting(db, key, value) {
    const stmt = db.prepare(`
        INSERT INTO memory_settings (key, value, updated_at) 
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET
            value = excluded.value,
            updated_at = CURRENT_TIMESTAMP
    `);
    stmt.run(key, value);
}

/**
 * Get memory setting value
 * @param {Database} db
 * @param {string} key
 * @returns {string|null}
 */
export function getSetting(db, key) {
    const stmt = db.prepare('SELECT value FROM memory_settings WHERE key = ?');
    const result = stmt.get(key);
    return result ? result.value : null;
}

/**
 * Get database statistics
 * @param {Database} db
 * @returns {Object}
 */
export function getStats(db) {
    const chunkCount = db.prepare('SELECT COUNT(*) as count FROM chunks').get().count;
    const lastSync = getMeta(db, 'last_sync');
    const modelName = getMeta(db, 'model_name');
    
    return {
        chunkCount,
        lastSync,
        modelName,
        sqliteVecAvailable,
    };
}
