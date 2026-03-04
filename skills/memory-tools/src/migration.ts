/**
 * Migration from v1 to v2
 *
 * Automatically detects legacy SQLite + LanceDB storage and migrates
 * memories to the new file-based format.
 */

import * as fs from 'node:fs';
import * as path from 'node:path';
import initSqlJs from 'sql.js';
import { MemoryFileManager } from './file-manager.js';
import type { Memory, MemoryCategory } from './types.js';

interface LegacyMemoryRow {
  id: string;
  content: string;
  category: string;
  confidence: number;
  importance: number;
  created_at: number;
  updated_at: number;
  last_accessed_at: number | null;
  decay_days: number | null;
  source_channel: string | null;
  source_message_id: string | null;
  tags: string;
  supersedes: string | null;
  deleted_at: number | null;
  delete_reason: string | null;
}

export interface MigrationResult {
  success: boolean;
  migratedCount: number;
  skippedCount: number;
  errors: string[];
  legacyPath: string;
  newPath: string;
}

/**
 * Check if legacy v1 databases exist
 */
export function hasLegacyDatabase(legacyDbPath: string): boolean {
  const sqlitePath = path.join(legacyDbPath, 'memory.db');
  const vectorsPath = path.join(legacyDbPath, 'vectors');

  return fs.existsSync(sqlitePath) || fs.existsSync(vectorsPath);
}

/**
 * Check if new v2 memories directory exists and has content
 */
export function hasNewMemories(memoriesPath: string): boolean {
  if (!fs.existsSync(memoriesPath)) return false;

  // Check if any category directory has .md files
  const categories = ['facts', 'preferences', 'events', 'relationships', 'contexts', 'instructions', 'decisions', 'entities'];

  for (const cat of categories) {
    const catDir = path.join(memoriesPath, cat);
    if (fs.existsSync(catDir)) {
      const files = fs.readdirSync(catDir).filter(f => f.endsWith('.md'));
      if (files.length > 0) return true;
    }
  }

  return false;
}

/**
 * Migrate from v1 SQLite database to v2 file-based storage
 */
export async function migrateFromV1(
  legacyDbPath: string,
  newMemoriesPath: string
): Promise<MigrationResult> {
  const result: MigrationResult = {
    success: false,
    migratedCount: 0,
    skippedCount: 0,
    errors: [],
    legacyPath: legacyDbPath,
    newPath: newMemoriesPath,
  };

  const sqlitePath = path.join(legacyDbPath, 'memory.db');

  if (!fs.existsSync(sqlitePath)) {
    result.errors.push('Legacy SQLite database not found');
    return result;
  }

  try {
    // Initialize sql.js
    const SQL = await initSqlJs();
    const buffer = fs.readFileSync(sqlitePath);
    const db = new SQL.Database(buffer);

    // Create file manager for new storage
    const fileManager = new MemoryFileManager(newMemoriesPath);

    // Read all memories from SQLite
    const stmt = db.prepare(`
      SELECT * FROM memories
      WHERE deleted_at IS NULL
      ORDER BY created_at ASC
    `);

    while (stmt.step()) {
      const row = stmt.getAsObject() as unknown as LegacyMemoryRow;

      try {
        // Convert row to Memory object
        const memory: Memory = {
          id: row.id,
          content: row.content,
          category: row.category as MemoryCategory,
          confidence: row.confidence ?? 0.8,
          importance: row.importance ?? 0.5,
          createdAt: row.created_at,
          updatedAt: row.updated_at,
          lastAccessedAt: row.last_accessed_at ?? row.created_at,
          decayDays: row.decay_days,
          sourceChannel: row.source_channel ?? undefined,
          sourceMessageId: row.source_message_id ?? undefined,
          tags: JSON.parse(row.tags || '[]'),
          supersedes: row.supersedes ?? undefined,
          deletedAt: undefined,
          deleteReason: undefined,
        };

        // Write to new file-based storage
        writeMemoryFile(fileManager, memory);
        result.migratedCount++;
      } catch (err: any) {
        result.errors.push(`Failed to migrate memory ${row.id}: ${err.message}`);
        result.skippedCount++;
      }
    }

    stmt.free();
    db.close();

    // Also migrate deleted memories to .deleted folder
    await migrateDeletedMemories(sqlitePath, newMemoriesPath);

    result.success = result.errors.length === 0;

    // Create a migration marker file
    const markerPath = path.join(legacyDbPath, '.migrated-to-v2');
    fs.writeFileSync(markerPath, JSON.stringify({
      migratedAt: new Date().toISOString(),
      migratedCount: result.migratedCount,
      newPath: newMemoriesPath,
    }, null, 2));

    return result;
  } catch (err: any) {
    result.errors.push(`Migration failed: ${err.message}`);
    return result;
  }
}

/**
 * Migrate deleted memories to .deleted folder
 */
async function migrateDeletedMemories(sqlitePath: string, newMemoriesPath: string): Promise<void> {
  const SQL = await initSqlJs();
  const buffer = fs.readFileSync(sqlitePath);
  const db = new SQL.Database(buffer);

  const deletedPath = path.join(newMemoriesPath, '.deleted');
  if (!fs.existsSync(deletedPath)) {
    fs.mkdirSync(deletedPath, { recursive: true });
  }

  const stmt = db.prepare(`
    SELECT * FROM memories
    WHERE deleted_at IS NOT NULL
    ORDER BY deleted_at ASC
  `);

  while (stmt.step()) {
    const row = stmt.getAsObject() as unknown as LegacyMemoryRow;

    try {
      const memory: Memory = {
        id: row.id,
        content: row.content,
        category: row.category as MemoryCategory,
        confidence: row.confidence ?? 0.8,
        importance: row.importance ?? 0.5,
        createdAt: row.created_at,
        updatedAt: row.updated_at,
        lastAccessedAt: row.last_accessed_at ?? row.created_at,
        decayDays: row.decay_days,
        sourceChannel: row.source_channel ?? undefined,
        sourceMessageId: row.source_message_id ?? undefined,
        tags: JSON.parse(row.tags || '[]'),
        supersedes: row.supersedes ?? undefined,
        deletedAt: row.deleted_at ?? undefined,
        deleteReason: row.delete_reason ?? undefined,
      };

      // Write to .deleted folder
      const filePath = path.join(deletedPath, `${memory.id}.md`);
      writeMemoryToFile(memory, filePath);
    } catch {
      // Ignore errors for deleted memories
    }
  }

  stmt.free();
  db.close();
}

/**
 * Write a memory to the file manager
 */
function writeMemoryFile(fileManager: MemoryFileManager, memory: Memory): void {
  // Use internal method to write with existing ID
  const memoriesPath = fileManager.getMemoriesPath();
  const categoryDir = getCategoryDir(memory.category);
  const filePath = path.join(memoriesPath, categoryDir, `${memory.id}.md`);

  writeMemoryToFile(memory, filePath);
}

/**
 * Write a memory to a specific file path
 */
function writeMemoryToFile(memory: Memory, filePath: string): void {
  const frontmatter = [
    `id: ${memory.id}`,
    `category: ${memory.category}`,
    `confidence: ${memory.confidence}`,
    `importance: ${memory.importance}`,
    `created_at: ${new Date(memory.createdAt).toISOString()}`,
    `updated_at: ${new Date(memory.updatedAt).toISOString()}`,
    `last_accessed_at: ${memory.lastAccessedAt ? new Date(memory.lastAccessedAt).toISOString() : 'null'}`,
    `decay_days: ${memory.decayDays ?? 'null'}`,
    `source_channel: ${memory.sourceChannel || 'null'}`,
    `source_message_id: ${memory.sourceMessageId || 'null'}`,
    `tags: [${memory.tags.map(t => `"${t}"`).join(', ')}]`,
    `supersedes: ${memory.supersedes || 'null'}`,
  ];

  if (memory.deletedAt) {
    frontmatter.push(`deleted_at: ${new Date(memory.deletedAt).toISOString()}`);
    frontmatter.push(`delete_reason: ${memory.deleteReason || 'null'}`);
  }

  const content = `---\n${frontmatter.join('\n')}\n---\n\n${memory.content}\n`;

  // Ensure directory exists
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  fs.writeFileSync(filePath, content, 'utf-8');
}

function getCategoryDir(category: MemoryCategory): string {
  const map: Record<MemoryCategory, string> = {
    fact: 'facts',
    preference: 'preferences',
    event: 'events',
    relationship: 'relationships',
    context: 'contexts',
    instruction: 'instructions',
    decision: 'decisions',
    entity: 'entities',
  };
  return map[category];
}

/**
 * Print migration banner for users
 */
export function printMigrationRequired(legacyPath: string): void {
  console.log(`
╔════════════════════════════════════════════════════════════════════╗
║                     MIGRATION REQUIRED                             ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  memory-tools v2 uses a new file-based storage format.             ║
║                                                                    ║
║  Your existing memories at:                                        ║
║    ${legacyPath.padEnd(54)}║
║                                                                    ║
║  Will be automatically migrated to markdown files.                 ║
║  Your original database will be preserved as a backup.             ║
║                                                                    ║
║  This is a one-time migration. It should only take a moment.       ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
`);
}

/**
 * Print migration success message
 */
export function printMigrationSuccess(result: MigrationResult): void {
  console.log(`
╔════════════════════════════════════════════════════════════════════╗
║                   MIGRATION COMPLETE                               ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  ✓ Migrated ${String(result.migratedCount).padEnd(4)} memories to file-based storage            ║
${result.skippedCount > 0 ? `║  ⚠ Skipped ${String(result.skippedCount).padEnd(4)} memories (see errors below)              ║\n` : ''}║                                                                    ║
║  New storage location:                                             ║
║    ${result.newPath.padEnd(54)}║
║                                                                    ║
║  Your original database has been preserved at:                     ║
║    ${result.legacyPath.padEnd(54)}║
║                                                                    ║
║  You can now use memory-tools with QMD-powered search!             ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
`);

  if (result.errors.length > 0) {
    console.log('\nMigration warnings:');
    for (const err of result.errors.slice(0, 10)) {
      console.log(`  - ${err}`);
    }
    if (result.errors.length > 10) {
      console.log(`  ... and ${result.errors.length - 10} more`);
    }
  }
}
