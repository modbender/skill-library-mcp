import { getConfig } from '../config.js';
export const GATEWAY_STEP_PATH = getConfig().GATEWAY_STEP_PATH;

export const PROVIDER_ADAPTER_REQUEST_SCHEMA: Record<string, unknown> = {
  type: 'object',
  required: ['request_id', 'run_id', 'task_name', 'step', 'attempt', 'model', 'messages', 'tools'],
  additionalProperties: true,
  properties: {
    request_id: { type: 'string' },
    run_id: { type: 'string' },
    task_name: { type: 'string' },
    step: { type: 'integer', minimum: 1 },
    attempt: { type: 'integer', minimum: 1 },
    model: { type: 'string' },
    max_tokens: { type: 'integer', minimum: 1 },
    tier: { type: 'string' },
    messages: { type: 'array', items: { type: 'object', additionalProperties: true } },
    tools: { type: 'array', items: { type: 'object', additionalProperties: true } }
  }
};

export const PROVIDER_ADAPTER_RESPONSE_SCHEMA: Record<string, unknown> = {
  type: 'object',
  required: ['request_id'],
  additionalProperties: true,
  properties: {
    request_id: { type: 'string' },
    output_text: { type: 'string' },
    output_json: { type: 'object', additionalProperties: true },
    tool_calls: {
      type: 'array',
      items: {
        type: 'object',
        required: ['call_id', 'name', 'arguments'],
        additionalProperties: true,
        properties: {
          call_id: { type: 'string' },
          name: { type: 'string' },
          arguments: { type: 'object', additionalProperties: true }
        }
      }
    },
    usage: {
      type: 'object',
      additionalProperties: true,
      properties: {
        input_tokens: { type: 'number' },
        output_tokens: { type: 'number' }
      }
    },
    provider_latency_ms: { type: 'number' },
    model: { type: 'string' }
  }
};

export const PROVIDER_ADAPTER_REQUEST_EXAMPLE = {
  request_id: 'run_123:single_executor:a1:s1',
  run_id: 'run_123',
  task_name: 'single_executor',
  step: 1,
  attempt: 1,
  model: 'gpt-lite',
  max_tokens: 256,
  tier: 'cheap',
  messages: [
    { role: 'system', content: 'You are executor' },
    { role: 'user', content: 'Summarize this input' }
  ],
  tools: [
    {
      name: 'js_eval',
      description: 'Evaluate arithmetic-only expression and return numeric result',
      input_schema: { type: 'object', properties: { expression: { type: 'string' } }, required: ['expression'] }
    }
  ]
};

export const PROVIDER_ADAPTER_RESPONSE_EXAMPLE = {
  request_id: 'run_123:single_executor:a1:s1',
  tool_calls: [
    { call_id: 'call-1', name: 'js_eval', arguments: { expression: '6*7' } }
  ],
  usage: { input_tokens: 120, output_tokens: 30 },
  model: 'gateway-model-v1'
};
