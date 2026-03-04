/**
 * Shared types used across Memento plugin modules.
 */

/**
 * Minimal logger interface compatible with OpenClaw's plugin API logger.
 * Defined once here to avoid duplication across the codebase.
 */
export type PluginLogger = {
  info: (...args: any[]) => void;
  warn: (...args: any[]) => void;
  error: (...args: any[]) => void;
  debug?: (...args: any[]) => void;
};
