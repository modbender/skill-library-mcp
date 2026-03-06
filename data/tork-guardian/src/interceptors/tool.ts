/**
 * Tool Call Interceptor — Governs tool invocations by OpenClaw skills.
 *
 * Checks shell commands against blocklists, validates file paths
 * against allowed/blocked lists, and restricts network requests
 * under strict policy.
 */

import { TorkConfig, ToolCallDecision } from '../config';

export interface ToolCall {
  name: string;
  args: Record<string, unknown>;
}

const DANGEROUS_TOOLS = new Set([
  'shell_execute',
  'bash',
  'terminal',
  'file_write',
  'file_delete',
  'file_overwrite',
  'network_request',
  'http_request',
]);

export function governToolCall(tool: ToolCall, config: TorkConfig): ToolCallDecision {
  // Minimal policy: allow everything
  if (config.policy === 'minimal') {
    return { allowed: true };
  }

  // Check shell commands
  if (isShellTool(tool.name)) {
    return governShellCommand(tool, config);
  }

  // Check file operations
  if (isFileTool(tool.name)) {
    return governFileAccess(tool, config);
  }

  // Check network requests
  if (isNetworkTool(tool.name)) {
    return governNetworkRequest(tool, config);
  }

  return { allowed: true };
}

function isShellTool(name: string): boolean {
  return ['shell_execute', 'bash', 'terminal'].includes(name);
}

function isFileTool(name: string): boolean {
  return ['file_write', 'file_delete', 'file_overwrite', 'file_read'].includes(name);
}

function isNetworkTool(name: string): boolean {
  return ['network_request', 'http_request'].includes(name);
}

function governShellCommand(tool: ToolCall, config: TorkConfig): ToolCallDecision {
  const command = String(tool.args.command || tool.args.cmd || '');

  for (const blocked of config.blockShellCommands) {
    if (command.includes(blocked)) {
      return {
        allowed: false,
        reason: `Blocked shell command pattern: "${blocked}"`,
      };
    }
  }

  // Strict policy: block all shell commands not explicitly allowed
  if (config.policy === 'strict') {
    return {
      allowed: false,
      reason: 'Strict policy blocks all shell commands. Use standard or minimal policy to allow.',
    };
  }

  return { allowed: true };
}

function governFileAccess(tool: ToolCall, config: TorkConfig): ToolCallDecision {
  const path = String(tool.args.path || tool.args.file_path || '');

  // Check blocked paths
  for (const blocked of config.blockedPaths) {
    if (path.includes(blocked)) {
      return {
        allowed: false,
        reason: `Access to "${blocked}" is blocked by policy`,
      };
    }
  }

  // If allowedPaths is set, enforce whitelist
  if (config.allowedPaths.length > 0) {
    const isAllowed = config.allowedPaths.some((allowed) => path.startsWith(allowed));
    if (!isAllowed) {
      return {
        allowed: false,
        reason: `Path "${path}" is not in the allowed paths list`,
      };
    }
  }

  return { allowed: true };
}

function governNetworkRequest(tool: ToolCall, config: TorkConfig): ToolCallDecision {
  // Strict policy: block all network requests
  if (config.policy === 'strict') {
    return {
      allowed: false,
      reason: 'Strict policy blocks network requests from tools',
    };
  }

  return { allowed: true };
}
