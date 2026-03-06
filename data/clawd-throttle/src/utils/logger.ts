import type { LogLevel } from '../config/types.js';

const LOG_LEVELS: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

let currentLevel: LogLevel = 'info';

export function setLogLevel(level: LogLevel): void {
  currentLevel = level;
}

export function createLogger(module: string) {
  const log = (level: LogLevel, message: string, ...args: unknown[]) => {
    if (LOG_LEVELS[level] >= LOG_LEVELS[currentLevel]) {
      const timestamp = new Date().toISOString();
      const prefix = `[${timestamp}] [${level.toUpperCase()}] [${module}]`;
      // Log to stderr because stdout is reserved for MCP JSON-RPC
      if (args.length > 0) {
        console.error(prefix, message, ...args);
      } else {
        console.error(prefix, message);
      }
    }
  };

  return {
    debug: (msg: string, ...args: unknown[]) => log('debug', msg, ...args),
    info: (msg: string, ...args: unknown[]) => log('info', msg, ...args),
    warn: (msg: string, ...args: unknown[]) => log('warn', msg, ...args),
    error: (msg: string, ...args: unknown[]) => log('error', msg, ...args),
  };
}
