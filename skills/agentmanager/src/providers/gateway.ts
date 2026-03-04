import { z } from 'zod';
import type { LLMProvider, LLMRoundResult, LLMTaskContext } from './llm-provider.js';
import { GATEWAY_STEP_PATH } from './adapter-contract.js';
import { getConfig } from '../config.js';
import { checkOutboundUrl } from '../security/outbound-policy.js';

const GatewayResponseSchema = z.object({
  request_id: z.string().min(1),
  output_text: z.string().optional(),
  output_json: z.record(z.any()).optional(),
  tool_calls: z.array(z.object({
    call_id: z.string().min(1),
    name: z.string().min(1),
    arguments: z.record(z.any())
  })).optional(),
  usage: z.object({ input_tokens: z.number().optional(), output_tokens: z.number().optional() }).optional(),
  provider_latency_ms: z.number().optional(),
  model: z.string().optional()
});

const buildGatewayUrl = (): string | undefined => {
  const env = getConfig();
  if (!env.GATEWAY_URL) return undefined;
  try {
    return new URL(env.GATEWAY_STEP_PATH ?? GATEWAY_STEP_PATH, env.GATEWAY_URL).toString();
  } catch {
    return undefined;
  }
};

export class GatewayLLMProvider implements LLMProvider {
  readonly id = 'gateway';
  readonly supports_tools = true;
  readonly enabled = Boolean(getConfig().GATEWAY_URL);
  readonly notes = this.enabled ? 'Recommended provider for multi-source model routing' : 'Set GATEWAY_URL to enable this provider';

  async executeRound(args: LLMTaskContext): Promise<LLMRoundResult> {
    const env = getConfig();
    const endpoint = buildGatewayUrl();
    if (!this.enabled || !endpoint) {
      throw { code: 'GATEWAY_CONFIG', message: 'GATEWAY_URL is required', retryable: false, at: 'provider' };
    }

    await checkOutboundUrl(endpoint, { allowlistRaw: env.OUTBOUND_ALLOWLIST, allowHttp: false });

    const taskTimeout = args.task.timeout_ms ?? 30_000;
    const effectiveTimeout = Math.min(taskTimeout, env.GATEWAY_TIMEOUT_MS ?? 30_000);
    const timeoutSignal = AbortSignal.timeout(effectiveTimeout);
    const signal = args.signal ? AbortSignal.any([args.signal, timeoutSignal]) : timeoutSignal;

    const bodyPayload = JSON.stringify({
      request_id: args.requestId,
      run_id: args.runId,
      task_name: args.taskName,
      step: args.step,
      attempt: args.attempt,
      model: args.task.model,
      max_tokens: args.task.max_output_tokens,
      tier: args.tier,
      messages: args.messages,
      tools: args.tools.map((tool) => ({
        name: tool.name,
        description: tool.description,
        input_schema: tool.input_schema
      }))
    });
    if (Buffer.byteLength(bodyPayload, 'utf8') > env.MAX_PROVIDER_REQUEST_BYTES) {
      throw { code: 'OUTBOUND_PAYLOAD_REJECTED', message: 'Provider request exceeds MAX_PROVIDER_REQUEST_BYTES', retryable: false, at: 'provider' };
    }

    const started = Date.now();
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(env.GATEWAY_API_KEY ? { Authorization: `Bearer ${env.GATEWAY_API_KEY}` } : {})
      },
      redirect: 'error',
      signal,
      body: bodyPayload
    }).catch((error) => {
      throw {
        code: 'PROVIDER_HTTP',
        message: error instanceof Error ? error.message : 'Gateway request failed',
        retryable: true,
        suggested_action: 'retry',
        at: 'provider'
      };
    });

    if (!response.ok) {
      const status = response.status;
      throw {
        code: 'PROVIDER_HTTP',
        message: `Gateway request failed: ${status}`,
        retryable: status >= 500 || status === 429,
        suggested_action: status === 429 ? 'retry' : 'replan',
        at: 'provider'
      };
    }

    const contentType = response.headers.get('content-type') ?? '';
    if (!contentType.toLowerCase().includes('application/json')) {
      throw { code: 'GATEWAY_RESPONSE_INVALID', message: 'Gateway response must be application/json', retryable: false, at: 'provider' };
    }

    const parsed = GatewayResponseSchema.safeParse(await response.json());
    if (!parsed.success) {
      throw { code: 'GATEWAY_RESPONSE_INVALID', message: parsed.error.message, retryable: false, at: 'provider' };
    }
    if (parsed.data.request_id !== args.requestId) {
      throw { code: 'GATEWAY_RESPONSE_INVALID', message: 'request_id mismatch in gateway response', retryable: false, at: 'provider' };
    }

    return {
      ...parsed.data,
      provider_latency_ms: parsed.data.provider_latency_ms ?? (Date.now() - started)
    };
  }
}
