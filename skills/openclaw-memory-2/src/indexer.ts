/**
 * Indexer — FTS5 full-text search over workspace Markdown files.
 * Chunks files, indexes them, returns ranked results.
 */

import { readFileSync, existsSync, readdirSync } from 'fs';
import { join } from 'path';
import { createDB, DB } from './db';

export interface Chunk {
  id: string;
  file: string;
  lineStart: number;
  lineEnd: number;
  text: string;
  score?: number;
}

export interface IndexerConfig {
  workspace: string;
  chunkSize?: number;
}

export class MemoryIndexer {
  private db: DB;
  private workspace: string;
  private chunkSize: number;

  constructor(config: IndexerConfig) {
    this.workspace = config.workspace;
    this.chunkSize = config.chunkSize || 400;
    this.db = createDB();
    this.db.exec(`
      CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(
        file UNINDEXED, line_start UNINDEXED, line_end UNINDEXED, content,
        tokenize = 'unicode61'
      )
    `);
  }

  /** Index all memory files in workspace */
  index(): number {
    let total = 0;
    const files = this.findMemoryFiles();
    for (const file of files) {
      total += this.indexFile(file);
    }
    return total;
  }

  /** Index a single file */
  indexFile(filePath: string): number {
    if (!existsSync(filePath)) return 0;
    const content = readFileSync(filePath, 'utf-8');
    const chunks = this.chunk(content);
    for (const c of chunks) {
      this.db.run(
        'INSERT INTO chunks (file, line_start, line_end, content) VALUES (?, ?, ?, ?)',
        filePath, c.lineStart, c.lineEnd, c.text
      );
    }
    return chunks.length;
  }

  /** Search indexed memories */
  search(query: string, k = 5): Chunk[] {
    return this.db.all(
      'SELECT rowid, file, line_start, line_end, content, rank FROM chunks WHERE content MATCH ? ORDER BY rank LIMIT ?',
      query, k
    ).map((r: any) => ({
      id: String(r.rowid ?? ''),
      file: r.file,
      lineStart: r.line_start,
      lineEnd: r.line_end,
      text: r.content,
      score: Math.abs(r.rank ?? 0),
    }));
  }

  /** Rebuild index from scratch */
  rebuild(): number {
    this.db.exec('DROP TABLE IF EXISTS chunks');
    this.db.exec(`
      CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(
        file UNINDEXED, line_start UNINDEXED, line_end UNINDEXED, content,
        tokenize = 'unicode61'
      )
    `);
    return this.index();
  }

  close() { this.db.close(); }

  private findMemoryFiles(): string[] {
    const files: string[] = [];

    const memoryMd = join(this.workspace, 'MEMORY.md');
    if (existsSync(memoryMd)) files.push(memoryMd);

    const memoryDir = join(this.workspace, 'memory');
    if (existsSync(memoryDir)) {
      for (const f of readdirSync(memoryDir)) {
        if (f.match(/^\d{4}-\d{2}-\d{2}\.md$/)) files.push(join(memoryDir, f));
      }
    }

    const entDir = join(this.workspace, 'bank', 'entities');
    if (existsSync(entDir)) {
      for (const f of readdirSync(entDir)) {
        if (f.endsWith('.md')) files.push(join(entDir, f));
      }
    }

    const opinions = join(this.workspace, 'bank', 'opinions.md');
    if (existsSync(opinions)) files.push(opinions);

    return files;
  }

  private chunk(text: string): Array<{ text: string; lineStart: number; lineEnd: number }> {
    const lines = text.split('\n');
    const chunks: Array<{ text: string; lineStart: number; lineEnd: number }> = [];
    const step = Math.max(1, Math.floor(this.chunkSize * 0.8));
    for (let i = 0; i < lines.length; i += step) {
      const end = Math.min(i + this.chunkSize, lines.length);
      chunks.push({ text: lines.slice(i, end).join('\n'), lineStart: i + 1, lineEnd: end });
    }
    return chunks;
  }
}
