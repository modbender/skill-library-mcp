import fs from 'node:fs';
import type { RoutingLogEntry } from './types.js';
import { createLogger } from '../utils/logger.js';

const log = createLogger('log-reader');

export class LogReader {
  private logFilePath: string;

  constructor(logFilePath: string) {
    this.logFilePath = logFilePath;
  }

  readSince(sinceIso: string): RoutingLogEntry[] {
    if (!fs.existsSync(this.logFilePath)) return [];

    const results: RoutingLogEntry[] = [];
    const lines = fs.readFileSync(this.logFilePath, 'utf-8').split('\n');
    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const entry = JSON.parse(line) as RoutingLogEntry;
        if (entry.timestamp >= sinceIso) {
          results.push(entry);
        }
      } catch {
        log.warn('Skipping malformed log line');
      }
    }
    return results;
  }

  getEntryById(requestId: string): RoutingLogEntry | null {
    if (!fs.existsSync(this.logFilePath)) return null;

    const lines = fs.readFileSync(this.logFilePath, 'utf-8').split('\n');
    for (let i = lines.length - 1; i >= 0; i--) {
      const line = lines[i]!.trim();
      if (!line) continue;
      try {
        const entry = JSON.parse(line) as RoutingLogEntry;
        if (entry.requestId === requestId) return entry;
      } catch { /* skip */ }
    }
    return null;
  }

  tail(limit: number): RoutingLogEntry[] {
    if (!fs.existsSync(this.logFilePath)) return [];

    const lines = fs.readFileSync(this.logFilePath, 'utf-8').split('\n').filter(l => l.trim());
    const startIdx = Math.max(0, lines.length - limit);
    const results: RoutingLogEntry[] = [];
    for (let i = lines.length - 1; i >= startIdx; i--) {
      try {
        results.push(JSON.parse(lines[i]!) as RoutingLogEntry);
      } catch { /* skip */ }
    }
    return results;
  }
}
