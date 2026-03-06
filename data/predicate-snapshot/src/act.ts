/**
 * Predicate Act Tool
 *
 * Executes actions on elements by their Predicate ID.
 * Works with snapshots captured by PredicateSnapshotTool.
 */

import type { ToolContext, ToolResult } from './index';

export interface ActParams {
  action: 'click' | 'type' | 'scroll';
  elementId: number;
  value?: string;
}

// Element cache to map Predicate IDs to selectors
// In production, this would be populated from the last snapshot
const elementCache = new Map<number, { selector: string; bbox?: { x: number; y: number } }>();

export class PredicateActTool {
  async execute(params: ActParams, context: ToolContext): Promise<ToolResult> {
    const { action, elementId, value } = params;

    try {
      // Validate context
      if (!context.page) {
        return {
          success: false,
          error: 'No page context available. Ensure OpenClaw has an active browser session.',
        };
      }

      // Validate parameters
      if (!action) {
        return {
          success: false,
          error: 'Action is required. Use: click, type, or scroll',
        };
      }

      if (elementId === undefined || elementId === null) {
        return {
          success: false,
          error: 'Element ID is required. Get IDs from /predicate-snapshot output.',
        };
      }

      if (action === 'type' && !value) {
        return {
          success: false,
          error: 'Value is required for type action',
        };
      }

      // Execute action
      // Note: In production, this would use the actual Playwright page
      // and element mapping from the snapshot
      const result = await this.executeAction(context.page, action, elementId, value);

      return {
        success: true,
        data: result,
      };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return {
        success: false,
        error: `Action failed: ${message}`,
      };
    }
  }

  private async executeAction(
    page: unknown,
    action: string,
    elementId: number,
    value?: string
  ): Promise<string> {
    // Type assertion for Playwright page
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const playwrightPage = page as any;

    // Build selector from element ID
    // The Predicate extension adds data-predicate-id attributes
    const selector = `[data-predicate-id="${elementId}"]`;

    switch (action) {
      case 'click':
        await playwrightPage.click(selector);
        return `Clicked element ${elementId}`;

      case 'type':
        await playwrightPage.fill(selector, value ?? '');
        return `Typed "${value}" into element ${elementId}`;

      case 'scroll':
        await playwrightPage.evaluate(
          (sel: string) => {
            const el = document.querySelector(sel);
            if (el) {
              el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
          },
          selector
        );
        return `Scrolled to element ${elementId}`;

      default:
        throw new Error(`Unknown action: ${action}`);
    }
  }
}

/**
 * Update element cache from snapshot
 * Called internally after each snapshot to enable act commands
 */
export function updateElementCache(
  elements: Array<{ id: number; selector?: string; bbox?: { x: number; y: number } }>
): void {
  elementCache.clear();
  for (const el of elements) {
    if (el.selector) {
      elementCache.set(el.id, { selector: el.selector, bbox: el.bbox });
    }
  }
}

/**
 * Standalone function for direct usage
 */
export async function executePredicateAction(
  context: ToolContext,
  params: ActParams
): Promise<ToolResult> {
  const tool = new PredicateActTool();
  return tool.execute(params, context);
}
