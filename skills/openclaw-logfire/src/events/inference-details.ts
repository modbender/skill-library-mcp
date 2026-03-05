// SPDX-License-Identifier: MIT
/**
 * Opt-in GenAI event: gen_ai.client.inference.operation.details
 *
 * Emits a structured log event with the full request/response content
 * when captureInferenceEvents is enabled. This is privacy-sensitive
 * and disabled by default.
 */

import type { Span } from '@opentelemetry/api';
import { safeJsonStringify } from '../util.js';

export interface InferenceDetails {
  inputMessages?: unknown;
  outputMessages?: unknown;
  model?: string;
  inputTokens?: number;
  outputTokens?: number;
  toolDefinitions?: unknown;
}

/**
 * Record a gen_ai.client.inference.operation.details event on the span.
 */
export function emitInferenceDetailsEvent(
  span: Span,
  details: InferenceDetails,
): void {
  const attributes: Record<string, string | number> = {
    'gen_ai.operation.name': 'invoke_agent',
  };

  if (details.model) {
    attributes['gen_ai.request.model'] = details.model;
  }
  if (details.inputTokens !== undefined) {
    attributes['gen_ai.usage.input_tokens'] = details.inputTokens;
  }
  if (details.outputTokens !== undefined) {
    attributes['gen_ai.usage.output_tokens'] = details.outputTokens;
  }
  if (details.inputMessages !== undefined) {
    attributes['gen_ai.input.messages'] = safeJsonStringify(
      details.inputMessages,
    );
  }
  if (details.outputMessages !== undefined) {
    attributes['gen_ai.output.messages'] = safeJsonStringify(
      details.outputMessages,
    );
  }
  if (details.toolDefinitions !== undefined) {
    attributes['gen_ai.tool.definitions'] = safeJsonStringify(
      details.toolDefinitions,
    );
  }

  span.addEvent('gen_ai.client.inference.operation.details', attributes);
}
