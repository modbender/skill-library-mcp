#!/usr/bin/env node
/**
 * Seed v1 Database with Test Data
 *
 * Creates a SQLite database with sample memories to test migration.
 */

import initSqlJs from 'sql.js';
import * as fs from 'node:fs';
import * as path from 'node:path';
import { randomUUID } from 'node:crypto';

const DB_PATH = process.env.HOME + '/.openclaw/memory/tools';
const DB_FILE = path.join(DB_PATH, 'memory.db');

async function main() {
  // Ensure directory exists
  fs.mkdirSync(DB_PATH, { recursive: true });

  // Initialize sql.js
  const SQL = await initSqlJs();
  const db = new SQL.Database();

  // Create schema (same as v1)
  db.run(`
    CREATE TABLE IF NOT EXISTS memories (
      id TEXT PRIMARY KEY,
      content TEXT NOT NULL,
      category TEXT NOT NULL,
      confidence REAL DEFAULT 0.8,
      importance REAL DEFAULT 0.5,
      created_at INTEGER NOT NULL,
      updated_at INTEGER NOT NULL,
      last_accessed_at INTEGER,
      decay_days INTEGER,
      source_channel TEXT,
      source_message_id TEXT,
      tags TEXT,
      supersedes TEXT,
      deleted_at INTEGER,
      delete_reason TEXT
    )
  `);

  db.run(`CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category)`);
  db.run(`CREATE INDEX IF NOT EXISTS idx_memories_confidence ON memories(confidence)`);

  // Seed test data
  const testMemories = [
    {
      content: 'User name is Alice',
      category: 'fact',
      confidence: 1.0,
      importance: 0.9,
      tags: ['identity'],
    },
    {
      content: 'User prefers dark mode in all applications',
      category: 'preference',
      confidence: 0.95,
      importance: 0.7,
      tags: ['ui', 'settings'],
    },
    {
      content: 'User has a meeting with Bob on Friday',
      category: 'event',
      confidence: 0.8,
      importance: 0.6,
      decayDays: 7,
      tags: ['calendar'],
    },
    {
      content: 'Always respond in a friendly, casual tone',
      category: 'instruction',
      confidence: 1.0,
      importance: 1.0,
      tags: ['communication'],
    },
    {
      content: 'User sister is named Sarah',
      category: 'relationship',
      confidence: 0.9,
      importance: 0.5,
      tags: ['family'],
    },
    {
      content: 'User is working on a React project called "Dashboard"',
      category: 'context',
      confidence: 0.7,
      importance: 0.6,
      tags: ['work', 'programming'],
    },
    {
      content: 'We decided to use PostgreSQL for the database',
      category: 'decision',
      confidence: 1.0,
      importance: 0.8,
      tags: ['architecture', 'database'],
    },
    {
      content: 'User email: alice@example.com',
      category: 'entity',
      confidence: 1.0,
      importance: 0.9,
      tags: ['contact'],
    },
    // Add a deleted memory
    {
      content: 'User favorite color is blue',
      category: 'preference',
      confidence: 0.8,
      importance: 0.3,
      tags: ['personal'],
      deleted: true,
      deleteReason: 'User corrected: favorite color is green',
    },
  ];

  const now = Date.now();
  let insertCount = 0;

  for (const mem of testMemories) {
    const id = randomUUID();
    const createdAt = now - Math.random() * 86400000 * 30; // Random time in last 30 days

    db.run(`
      INSERT INTO memories (
        id, content, category, confidence, importance,
        created_at, updated_at, last_accessed_at, decay_days,
        tags, deleted_at, delete_reason
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      id,
      mem.content,
      mem.category,
      mem.confidence,
      mem.importance,
      createdAt,
      createdAt,
      createdAt,
      mem.decayDays ?? null,
      JSON.stringify(mem.tags || []),
      mem.deleted ? now : null,
      mem.deleted ? mem.deleteReason : null,
    ]);

    insertCount++;
    console.log(`Created memory: [${mem.category}] ${mem.content.slice(0, 50)}...`);
  }

  // Save database
  const data = db.export();
  fs.writeFileSync(DB_FILE, Buffer.from(data));
  db.close();

  console.log(`\n✓ Created v1 database with ${insertCount} memories at ${DB_FILE}`);
}

main().catch(console.error);
