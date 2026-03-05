#!/usr/bin/env node
/**
 * Predicate Snapshot Skill for OpenClaw
 *
 * MCP server that provides ML-powered DOM snapshots for browser automation.
 * Reduces token usage by 95% compared to raw accessibility tree dumps.
 */

import { PredicateSnapshotTool } from './snapshot';
import { PredicateActTool } from './act';

export interface ToolContext {
  page?: unknown; // Playwright Page object
  browserSession?: unknown; // browser-use session
}

export interface ToolResult {
  success: boolean;
  data?: string;
  error?: string;
}

/**
 * MCP tool definitions for OpenClaw integration
 */
export const mcpTools = {
  'predicate-snapshot': {
    description: 'Capture ML-ranked DOM snapshot optimized for LLM (95% token reduction)',
    parameters: {
      limit: {
        type: 'number',
        description: 'Maximum elements to return',
        default: 50,
      },
      includeOrdinal: {
        type: 'boolean',
        description: 'Include ordinal ranking for list items',
        default: true,
      },
    },
    handler: async (
      params: { limit?: number; includeOrdinal?: boolean },
      context: ToolContext
    ): Promise<ToolResult> => {
      const tool = new PredicateSnapshotTool();
      return tool.execute(params, context);
    },
  },

  'predicate-snapshot-local': {
    description: 'Local snapshot without ML re-ranking (free, lower accuracy)',
    parameters: {
      limit: {
        type: 'number',
        description: 'Maximum elements to return',
        default: 50,
      },
    },
    handler: async (
      params: { limit?: number },
      context: ToolContext
    ): Promise<ToolResult> => {
      const tool = new PredicateSnapshotTool({ useLocal: true });
      return tool.execute(params, context);
    },
  },

  'predicate-act': {
    description: 'Execute action on element by Predicate ID',
    parameters: {
      action: {
        type: 'string',
        enum: ['click', 'type', 'scroll'],
        description: 'Action to perform',
      },
      elementId: {
        type: 'number',
        description: 'Predicate element ID from snapshot',
      },
      value: {
        type: 'string',
        description: 'Value for type action',
        optional: true,
      },
    },
    handler: async (
      params: { action: string; elementId: number; value?: string },
      context: ToolContext
    ): Promise<ToolResult> => {
      const tool = new PredicateActTool();
      // Validate and cast action type
      const validActions = ['click', 'type', 'scroll'] as const;
      if (!validActions.includes(params.action as typeof validActions[number])) {
        return {
          success: false,
          error: `Invalid action: ${params.action}. Must be one of: click, type, scroll`,
        };
      }
      return tool.execute(
        { ...params, action: params.action as 'click' | 'type' | 'scroll' },
        context
      );
    },
  },
};

/**
 * CLI entry point
 */
async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command || command === '--help' || command === '-h') {
    console.log(`
Predicate Snapshot Skill for OpenClaw

Usage:
  predicate-snapshot [options]     Capture ML-ranked DOM snapshot
  predicate-snapshot-local         Capture local snapshot (no API key)
  predicate-act <action> <id>      Execute action on element

Options:
  --limit=N          Maximum elements (default: 50)
  --include-ordinal  Include ordinal ranking

Environment:
  PREDICATE_API_KEY  API key for ML-powered snapshots

Examples:
  predicate-snapshot --limit=30
  predicate-act click 42
  predicate-act type 15 "search query"
`);
    process.exit(0);
  }

  // This is a stub - actual execution requires browser context from OpenClaw
  console.log('This skill requires OpenClaw browser context to execute.');
  console.log('Install via: npx clawdhub@latest install predicate-snapshot');
  process.exit(1);
}

// Run if executed directly
if (require.main === module) {
  main().catch(console.error);
}

export { PredicateSnapshotTool, takeDirectSnapshot } from './snapshot';
export { PredicateActTool } from './act';
export { PlaywrightCDPAdapter, createBrowserUseSession } from './playwright-adapter';
