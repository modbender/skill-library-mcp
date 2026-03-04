/**
 * File Manager for Memory Storage
 *
 * Handles reading/writing memories as markdown files with YAML frontmatter.
 * Each memory is stored as a single .md file organized by category.
 */

import * as fs from 'node:fs';
import * as path from 'node:path';
import { randomUUID } from 'node:crypto';
import type { Memory, MemoryCategory, CreateMemoryInput, UpdateMemoryInput } from './types.js';

// Simple YAML frontmatter parser/serializer (no external deps)
function parseYamlFrontmatter(content: string): { frontmatter: Record<string, unknown>; body: string } {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) {
    return { frontmatter: {}, body: content };
  }

  const [, yaml, body] = match;
  const frontmatter: Record<string, unknown> = {};

  for (const line of yaml.split('\n')) {
    const colonIdx = line.indexOf(':');
    if (colonIdx === -1) continue;

    const key = line.slice(0, colonIdx).trim();
    let value: unknown = line.slice(colonIdx + 1).trim();

    // Parse arrays: [item1, item2]
    if (typeof value === 'string' && value.startsWith('[') && value.endsWith(']')) {
      value = value.slice(1, -1).split(',').map(s => s.trim().replace(/^["']|["']$/g, '')).filter(Boolean);
    }
    // Parse numbers
    else if (typeof value === 'string' && /^-?\d+(\.\d+)?$/.test(value)) {
      value = parseFloat(value);
    }
    // Parse booleans
    else if (value === 'true') value = true;
    else if (value === 'false') value = false;
    else if (value === 'null') value = null;
    // Remove quotes from strings
    else if (typeof value === 'string') {
      value = value.replace(/^["']|["']$/g, '');
    }

    frontmatter[key] = value;
  }

  return { frontmatter, body: body.trim() };
}

function serializeYamlFrontmatter(data: Record<string, unknown>): string {
  const lines: string[] = [];

  for (const [key, value] of Object.entries(data)) {
    if (value === undefined) continue;
    if (value === null) {
      lines.push(`${key}: null`);
    } else if (Array.isArray(value)) {
      lines.push(`${key}: [${value.map(v => `"${v}"`).join(', ')}]`);
    } else if (typeof value === 'string') {
      // Quote strings with special chars
      if (value.includes(':') || value.includes('#') || value.includes('\n')) {
        lines.push(`${key}: "${value.replace(/"/g, '\\"')}"`);
      } else {
        lines.push(`${key}: ${value}`);
      }
    } else {
      lines.push(`${key}: ${value}`);
    }
  }

  return lines.join('\n');
}

export class MemoryFileManager {
  private memoriesPath: string;
  private deletedPath: string;

  constructor(memoriesPath: string) {
    this.memoriesPath = memoriesPath;
    this.deletedPath = path.join(memoriesPath, '.deleted');
    this.ensureDirectories();
  }

  private ensureDirectories(): void {
    // Create category directories
    const categories = ['facts', 'preferences', 'events', 'relationships', 'contexts', 'instructions', 'decisions', 'entities'];
    for (const cat of categories) {
      const dir = path.join(this.memoriesPath, cat);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    }
    // Create deleted directory
    if (!fs.existsSync(this.deletedPath)) {
      fs.mkdirSync(this.deletedPath, { recursive: true });
    }
  }

  private categoryToDir(category: MemoryCategory): string {
    // Pluralize category names for directory
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

  private getFilePath(id: string, category: MemoryCategory): string {
    return path.join(this.memoriesPath, this.categoryToDir(category), `${id}.md`);
  }

  /**
   * Create a new memory file
   */
  create(input: CreateMemoryInput): Memory {
    const id = randomUUID();
    const now = Date.now();

    const memory: Memory = {
      id,
      content: input.content,
      category: input.category,
      confidence: input.confidence ?? 0.8,
      importance: input.importance ?? 0.5,
      createdAt: now,
      updatedAt: now,
      lastAccessedAt: now,
      decayDays: input.decayDays ?? null,
      sourceChannel: input.sourceChannel,
      sourceMessageId: input.sourceMessageId,
      tags: input.tags ?? [],
      supersedes: undefined,
      deletedAt: undefined,
      deleteReason: undefined,
    };

    this.writeMemory(memory);
    return memory;
  }

  /**
   * Read a memory by ID
   */
  get(id: string): Memory | null {
    // Try to find in any category directory
    const categories: MemoryCategory[] = ['fact', 'preference', 'event', 'relationship', 'context', 'instruction', 'decision', 'entity'];

    for (const category of categories) {
      const filePath = this.getFilePath(id, category);
      if (fs.existsSync(filePath)) {
        return this.readMemoryFile(filePath);
      }

      // Also try short ID match
      if (id.length === 8) {
        const dir = path.join(this.memoriesPath, this.categoryToDir(category));
        if (fs.existsSync(dir)) {
          const files = fs.readdirSync(dir);
          const match = files.find(f => f.startsWith(id) && f.endsWith('.md'));
          if (match) {
            return this.readMemoryFile(path.join(dir, match));
          }
        }
      }
    }

    return null;
  }

  /**
   * Update an existing memory
   */
  update(id: string, updates: UpdateMemoryInput): Memory | null {
    const existing = this.get(id);
    if (!existing) return null;

    const updated: Memory = {
      ...existing,
      ...updates,
      content: updates.content ?? existing.content,
      updatedAt: Date.now(),
      tags: updates.tags ?? existing.tags,
    };

    // If category changed, move the file
    if (existing.category !== updated.category) {
      const oldPath = this.getFilePath(existing.id, existing.category);
      fs.unlinkSync(oldPath);
    }

    this.writeMemory(updated);
    return updated;
  }

  /**
   * Soft delete a memory (move to .deleted folder)
   */
  delete(id: string, reason?: string): boolean {
    const memory = this.get(id);
    if (!memory) return false;

    const oldPath = this.getFilePath(memory.id, memory.category);
    const deletedPath = path.join(this.deletedPath, `${memory.id}.md`);

    // Update memory with deletion info
    memory.deletedAt = Date.now();
    memory.deleteReason = reason;

    // Write to deleted folder
    this.writeMemoryToPath(memory, deletedPath);

    // Remove from active folder
    if (fs.existsSync(oldPath)) {
      fs.unlinkSync(oldPath);
    }

    return true;
  }

  /**
   * List all memories, optionally filtered
   */
  list(options: {
    category?: MemoryCategory;
    limit?: number;
    offset?: number;
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
  } = {}): { total: number; items: Memory[] } {
    const memories: Memory[] = [];
    const categories: MemoryCategory[] = options.category
      ? [options.category]
      : ['fact', 'preference', 'event', 'relationship', 'context', 'instruction', 'decision', 'entity'];

    for (const category of categories) {
      const dir = path.join(this.memoriesPath, this.categoryToDir(category));
      if (!fs.existsSync(dir)) continue;

      const files = fs.readdirSync(dir).filter(f => f.endsWith('.md'));
      for (const file of files) {
        const memory = this.readMemoryFile(path.join(dir, file));
        if (memory && !memory.deletedAt) {
          memories.push(memory);
        }
      }
    }

    // Sort
    const sortBy = options.sortBy ?? 'createdAt';
    const sortOrder = options.sortOrder ?? 'desc';
    memories.sort((a, b) => {
      const aVal = (a as any)[sortBy] ?? 0;
      const bVal = (b as any)[sortBy] ?? 0;
      return sortOrder === 'desc' ? bVal - aVal : aVal - bVal;
    });

    const total = memories.length;
    const offset = options.offset ?? 0;
    const limit = options.limit ?? 20;
    const items = memories.slice(offset, offset + limit);

    return { total, items };
  }

  /**
   * Get memories by category
   */
  getByCategory(category: MemoryCategory, limit: number = 50): Memory[] {
    const dir = path.join(this.memoriesPath, this.categoryToDir(category));
    if (!fs.existsSync(dir)) return [];

    const files = fs.readdirSync(dir).filter(f => f.endsWith('.md'));
    const memories: Memory[] = [];

    for (const file of files) {
      if (memories.length >= limit) break;
      const memory = this.readMemoryFile(path.join(dir, file));
      if (memory && !memory.deletedAt) {
        memories.push(memory);
      }
    }

    // Sort by importance
    memories.sort((a, b) => b.importance - a.importance);
    return memories.slice(0, limit);
  }

  /**
   * Count non-deleted memories
   */
  count(): number {
    let total = 0;
    const categories: MemoryCategory[] = ['fact', 'preference', 'event', 'relationship', 'context', 'instruction', 'decision', 'entity'];

    for (const category of categories) {
      const dir = path.join(this.memoriesPath, this.categoryToDir(category));
      if (fs.existsSync(dir)) {
        total += fs.readdirSync(dir).filter(f => f.endsWith('.md')).length;
      }
    }

    return total;
  }

  /**
   * Update last accessed time for memories
   */
  touchMany(ids: string[]): void {
    const now = Date.now();
    for (const id of ids) {
      const memory = this.get(id);
      if (memory) {
        memory.lastAccessedAt = now;
        this.writeMemory(memory);
      }
    }
  }

  /**
   * Get the memories directory path (for QMD collection)
   */
  getMemoriesPath(): string {
    return this.memoriesPath;
  }

  /**
   * Write a memory to its file
   */
  private writeMemory(memory: Memory): void {
    const filePath = this.getFilePath(memory.id, memory.category);
    this.writeMemoryToPath(memory, filePath);
  }

  private writeMemoryToPath(memory: Memory, filePath: string): void {
    const frontmatter = serializeYamlFrontmatter({
      id: memory.id,
      category: memory.category,
      confidence: memory.confidence,
      importance: memory.importance,
      created_at: new Date(memory.createdAt).toISOString(),
      updated_at: new Date(memory.updatedAt).toISOString(),
      last_accessed_at: memory.lastAccessedAt ? new Date(memory.lastAccessedAt).toISOString() : null,
      decay_days: memory.decayDays,
      source_channel: memory.sourceChannel || null,
      source_message_id: memory.sourceMessageId || null,
      tags: memory.tags,
      supersedes: memory.supersedes || null,
      deleted_at: memory.deletedAt ? new Date(memory.deletedAt).toISOString() : null,
      delete_reason: memory.deleteReason || null,
    });

    const content = `---\n${frontmatter}\n---\n\n${memory.content}\n`;

    // Atomic write: write to temp file, then rename
    const tempPath = `${filePath}.tmp`;
    fs.writeFileSync(tempPath, content, 'utf-8');
    fs.renameSync(tempPath, filePath);
  }

  /**
   * Read a memory from file
   */
  private readMemoryFile(filePath: string): Memory | null {
    try {
      const content = fs.readFileSync(filePath, 'utf-8');
      const { frontmatter, body } = parseYamlFrontmatter(content);

      return {
        id: frontmatter.id as string,
        content: body,
        category: frontmatter.category as MemoryCategory,
        confidence: (frontmatter.confidence as number) ?? 0.8,
        importance: (frontmatter.importance as number) ?? 0.5,
        createdAt: frontmatter.created_at ? new Date(frontmatter.created_at as string).getTime() : Date.now(),
        updatedAt: frontmatter.updated_at ? new Date(frontmatter.updated_at as string).getTime() : Date.now(),
        lastAccessedAt: frontmatter.last_accessed_at ? new Date(frontmatter.last_accessed_at as string).getTime() : Date.now(),
        decayDays: frontmatter.decay_days as number | null,
        sourceChannel: frontmatter.source_channel as string | undefined,
        sourceMessageId: frontmatter.source_message_id as string | undefined,
        tags: (frontmatter.tags as string[]) ?? [],
        supersedes: frontmatter.supersedes as string | undefined,
        deletedAt: frontmatter.deleted_at ? new Date(frontmatter.deleted_at as string).getTime() : undefined,
        deleteReason: frontmatter.delete_reason as string | undefined,
      };
    } catch (err) {
      console.error(`Failed to read memory file: ${filePath}`, err);
      return null;
    }
  }
}
