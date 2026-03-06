import fs from 'node:fs';
import path from 'node:path';
import type { RoutingLogEntry } from './types.js';
import type { ModelSpec } from '../router/types.js';
import { createLogger } from '../utils/logger.js';

const log = createLogger('log-writer');

export class LogWriter {
  private logFilePath: string;

  constructor(logFilePath: string) {
    this.logFilePath = logFilePath;
    fs.mkdirSync(path.dirname(logFilePath), { recursive: true });
  }

  append(entry: RoutingLogEntry): void {
    try {
      const line = JSON.stringify(entry) + '\n';
      fs.appendFileSync(this.logFilePath, line, 'utf-8');
    } catch (err) {
      log.error('Failed to write routing log entry', err);
    }
  }
}

export function estimateCost(
  model: ModelSpec,
  inputTokens: number,
  outputTokens: number,
): number {
  return (inputTokens / 1_000_000) * model.inputCostPerMTok
       + (outputTokens / 1_000_000) * model.outputCostPerMTok;
}
