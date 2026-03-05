/**
 * Predicate Snapshot Tool
 *
 * Captures ML-ranked DOM snapshots using @predicatesystems/runtime.
 * Returns compact pipe-delimited format optimized for LLM consumption.
 *
 * Supports both:
 * - browser-use sessions (via BrowserUseAdapter)
 * - Plain Playwright pages (via PlaywrightCDPAdapter)
 */

import { backends } from '@predicatesystems/runtime';
import { createBrowserUseSession, PlaywrightCDPAdapter } from './playwright-adapter';
import type { ToolContext, ToolResult } from './index';

export interface SnapshotOptions {
  useLocal?: boolean;
}

export interface SnapshotParams {
  limit?: number;
  includeOrdinal?: boolean;
}

// Type guard to check if object has getOrCreateCdpSession method
function isBrowserUseSession(obj: unknown): boolean {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'getOrCreateCdpSession' in obj &&
    typeof (obj as Record<string, unknown>).getOrCreateCdpSession === 'function'
  );
}

// Type guard for Playwright page
function isPlaywrightPage(obj: unknown): boolean {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'context' in obj &&
    typeof (obj as Record<string, unknown>).context === 'function' &&
    'goto' in obj &&
    typeof (obj as Record<string, unknown>).goto === 'function'
  );
}

export class PredicateSnapshotTool {
  private useLocal: boolean;

  constructor(options: SnapshotOptions = {}) {
    this.useLocal = options.useLocal ?? false;
  }

  async execute(params: SnapshotParams, context: ToolContext): Promise<ToolResult> {
    const limit = params.limit ?? 50;

    try {
      // Validate context - need either browserSession or page
      if (!context.browserSession && !context.page) {
        return {
          success: false,
          error: 'No browser context available. Ensure OpenClaw has an active browser session.',
        };
      }

      // Check for API key (unless using local mode)
      const apiKey = process.env.PREDICATE_API_KEY;
      if (!this.useLocal && !apiKey) {
        return {
          success: false,
          error:
            'PREDICATE_API_KEY required for ML-powered snapshots. ' +
            'Get one at https://predicate.systems/keys or use /predicate-snapshot-local for free local mode.',
        };
      }

      // Determine the session to use
      let session: unknown;

      if (context.browserSession && isBrowserUseSession(context.browserSession)) {
        // Use browser-use session directly
        session = context.browserSession;
      } else if (context.page && isPlaywrightPage(context.page)) {
        // Convert Playwright page to browser-use compatible session
        session = createBrowserUseSession(context.page);
      } else if (context.browserSession) {
        // Try to use browserSession as-is (might be pre-wrapped)
        session = context.browserSession;
      } else {
        return {
          success: false,
          error:
            'Invalid browser context. Expected browser-use session or Playwright page ' +
            'with context().newCDPSession() support.',
        };
      }

      // Create PredicateContext and build snapshot
      const ctx = new backends.PredicateContext({
        predicateApiKey: this.useLocal ? undefined : apiKey,
        topElementSelector: {
          byImportance: Math.min(limit, 60),
          fromDominantGroup: 15,
          byPosition: 10,
        },
      });

      const result = await ctx.build(session);

      if (!result || !result.promptBlock) {
        return {
          success: false,
          error: 'Snapshot returned empty result',
        };
      }

      // Build response with metadata
      const response = this.formatResponse(result, limit, this.useLocal);

      return {
        success: true,
        data: response,
      };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);

      // Provide helpful error for common issues
      if (message.includes('getOrCreateCdpSession')) {
        return {
          success: false,
          error:
            'Browser session missing CDP support. This skill requires either:\n' +
            '- A browser-use session with CDP enabled\n' +
            '- A Playwright page (will be auto-wrapped)\n' +
            'Error: ' +
            message,
        };
      }

      return {
        success: false,
        error: `Snapshot failed: ${message}`,
      };
    }
  }

  private formatResponse(
    result: backends.SentienceContextState,
    limit: number,
    isLocal: boolean
  ): string {
    const lines: string[] = [];

    // Header with metadata
    lines.push(`# Predicate Snapshot${isLocal ? ' (Local)' : ''}`);
    lines.push(`# URL: ${result.url ?? 'unknown'}`);
    lines.push(`# Elements: showing top ${limit}`);
    lines.push(`# Format: ID|role|text|imp|is_primary|docYq|ord|DG|href`);
    lines.push('');

    // Element data (promptBlock contains the formatted output)
    lines.push(result.promptBlock);

    return lines.join('\n');
  }
}

/**
 * Low-level snapshot using CDPBackend directly.
 *
 * Use this when you need more control over the snapshot process
 * or want to use the raw snapshot() function from the SDK.
 */
export async function takeDirectSnapshot(
  context: ToolContext,
  options: SnapshotParams & { useApi?: boolean; predicateApiKey?: string } = {}
): Promise<ToolResult> {
  try {
    if (!context.page || !isPlaywrightPage(context.page)) {
      return {
        success: false,
        error: 'takeDirectSnapshot requires a Playwright page in context',
      };
    }

    const adapter = new PlaywrightCDPAdapter(context.page);
    const transport = await adapter.createTransport();
    const backend = new backends.CDPBackend(transport);

    try {
      const snap = await backends.snapshot(backend, {
        limit: options.limit ?? 50,
        useApi: options.useApi,
        predicateApiKey: options.predicateApiKey,
      });

      return {
        success: true,
        data: JSON.stringify(snap, null, 2),
      };
    } finally {
      await adapter.detach();
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      success: false,
      error: `Direct snapshot failed: ${message}`,
    };
  }
}

/**
 * Standalone function for direct usage
 */
export async function takePredicateSnapshot(
  context: ToolContext,
  options: SnapshotParams & SnapshotOptions = {}
): Promise<ToolResult> {
  const tool = new PredicateSnapshotTool({ useLocal: options.useLocal });
  return tool.execute(options, context);
}
