/**
 * LLM Request Interceptor — Governs LLM API calls by scanning
 * message content for PII and enforcing redaction/denial policy.
 */

import { TorkClient } from '../client';
import { GovernResponse, TorkConfig } from '../config';

export interface LLMRequest {
  messages: { role: string; content: string }[];
  model?: string;
  [key: string]: unknown;
}

export interface GovernedLLMRequest {
  request: LLMRequest;
  governed: boolean;
  receipts: string[];
  pii_found: boolean;
}

export async function governLLMRequest(
  client: TorkClient,
  request: LLMRequest,
  config: TorkConfig,
): Promise<GovernedLLMRequest> {
  if (!config.redactPII) {
    return { request, governed: false, receipts: [], pii_found: false };
  }

  const governedMessages = [...request.messages];
  const receipts: string[] = [];
  let piiFound = false;

  for (let i = 0; i < governedMessages.length; i++) {
    const msg = governedMessages[i];
    if (!msg.content || typeof msg.content !== 'string') continue;

    const mode = config.policy === 'strict' ? 'deny' : 'redact';
    const result = await client.govern(msg.content, { mode });

    if (result.receipt?.receipt_id) {
      receipts.push(result.receipt.receipt_id);
    }

    if (result.pii_detected && result.pii_detected.length > 0) {
      piiFound = true;
    }

    if (result.action === 'deny') {
      throw new GovernanceDeniedError(
        `PII detected in message ${i} (${msg.role}). Policy '${config.policy}' denies this request.`,
        result,
      );
    }

    if (result.action === 'redact') {
      governedMessages[i] = { ...msg, content: result.output };
    }
  }

  return {
    request: { ...request, messages: governedMessages },
    governed: true,
    receipts,
    pii_found: piiFound,
  };
}

export class GovernanceDeniedError extends Error {
  readonly governResponse: GovernResponse;

  constructor(message: string, response: GovernResponse) {
    super(message);
    this.name = 'GovernanceDeniedError';
    this.governResponse = response;
  }
}
