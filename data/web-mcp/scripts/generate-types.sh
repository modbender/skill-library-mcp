#!/bin/bash
# generate-types.sh - Genera TypeScript types per WebMCP

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TARGET_DIR="${1:-.}"

echo "📝 Generating WebMCP types..."

cat > "$TARGET_DIR/types/webmcp.d.ts" << 'EOF'
// Auto-generated WebMCP TypeScript definitions

declare global {
  interface Window {
    webMCP?: WebMCPBridge;
  }
  
  interface Navigator {
    modelContext?: ModelContext;
  }
}

export interface ModelContext {
  registerTool<TParams = unknown, TResult = unknown>(
    name: string,
    handler: ToolHandler<TParams, TResult>
  ): Promise<void>;
  
  unregisterTool(name: string): Promise<void>;
  
  dispatchAndWait<TParams = unknown, TResult = unknown>(
    name: string,
    params: TParams
  ): Promise<TResult>;
  
  on<T = unknown>(event: string, callback: (data: T) => void): void;
  off<T = unknown>(event: string, callback: (data: T) => void): void;
}

export type ToolHandler<TParams = unknown, TResult = unknown> = (
  params: TParams,
  context: WebMCPContext
) => Promise<TResult> | TResult;

export interface WebMCPContext {
  sessionId: string;
  timestamp: number;
  metadata?: Record<string, unknown>;
}

export interface WebMCPBridge {
  version: string;
  isReady: boolean;
  registerTool: ModelContext['registerTool'];
  unregisterTool: ModelContext['unregisterTool'];
  dispatchAndWait: ModelContext['dispatchAndWait'];
}

export interface WebMCPTool<TParams = unknown, TResult = unknown> {
  name: string;
  description: string;
  parameters?: JSONSchema;
  execute: ToolHandler<TParams, TResult>;
}

export interface JSONSchema {
  type: string;
  properties?: Record<string, JSONSchemaProperty>;
  required?: string[];
}

export interface JSONSchemaProperty {
  type: string;
  description?: string;
  enum?: unknown[];
}

export interface WebMCPConfig {
  name: string;
  version: string;
  tools?: Record<string, ToolConfig>;
  bridge?: BridgeConfig;
}

export interface ToolConfig {
  enabled: boolean;
  timeout?: number;
  retries?: number;
}

export interface BridgeConfig {
  enabled: boolean;
  scriptPath: string;
  debug?: boolean;
}

export {};
EOF

echo "✅ Types generated: types/webmcp.d.ts"
