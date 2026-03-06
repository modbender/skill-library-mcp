/**
 * OpenClaw Plugin SDK Types
 *
 * Minimal type definitions for OpenClaw plugin development.
 * These match the OpenClaw plugin API.
 */

export interface PluginLogger {
  debug?: (message: string) => void;
  info: (message: string) => void;
  warn: (message: string) => void;
  error: (message: string) => void;
}

export interface OpenClawPluginApi {
  id: string;
  name: string;
  version?: string;
  description?: string;
  source: string;
  config: Record<string, unknown>;
  pluginConfig?: Record<string, unknown>;
  logger: PluginLogger;
  registerTool: (tool: AnyAgentTool, opts?: { name?: string }) => void;
  registerHook: (events: string | string[], handler: unknown, opts?: unknown) => void;
  registerCli: (registrar: (ctx: { program: unknown }) => void, opts?: { commands?: string[] }) => void;
  registerService: (service: { id: string; start: () => void; stop?: () => void }) => void;
  resolvePath: (input: string) => string;
  on: (hookName: string, handler: unknown, opts?: { priority?: number }) => void;
}

export interface AnyAgentTool {
  name: string;
  label?: string;
  description: string;
  parameters: unknown;
  execute: (toolCallId: string, params: unknown) => Promise<ToolResult>;
}

export interface ToolResult {
  content: Array<{ type: 'text'; text: string }>;
  details?: Record<string, unknown>;
}

export interface PluginHookBeforeAgentStartResult {
  systemPrompt?: string;
  prependContext?: string;
}
