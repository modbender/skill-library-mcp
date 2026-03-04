import type { LLMProvider, LLMRoundResult, LLMTaskContext } from './llm-provider.js';
import { getConfig } from '../config.js';

const parseJson = (value: string | undefined): Record<string, unknown> => {
  if (!value) return {};
  try {
    const parsed = JSON.parse(value);
    return parsed && typeof parsed === 'object' ? parsed as Record<string, unknown> : {};
  } catch {
    return {};
  }
};

export class OpenAILLMProvider implements LLMProvider {
  readonly id = 'openai';
  readonly supports_tools = true;
  readonly enabled = Boolean(getConfig().OPENAI_API_KEY);
  readonly notes = this.enabled ? undefined : 'Set OPENAI_API_KEY to enable this provider';

  async executeRound(args: LLMTaskContext): Promise<LLMRoundResult> {
    if (!this.enabled) {
      throw { code: 'OPENAI_CONFIG', message: 'OPENAI_API_KEY is required', retryable: false, at: 'provider' };
    }

    const started = Date.now();
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${getConfig().OPENAI_API_KEY}`
      },
      signal: args.signal,
      body: JSON.stringify({
        model: args.task.model,
        messages: args.messages.map((message) => ({
          role: message.role,
          content: message.content,
          ...(message.role === 'tool' ? { tool_call_id: message.tool_call_id } : {}),
          ...(message.name ? { name: message.name } : {})
        })),
        tools: args.tools.map((tool) => ({
          type: 'function',
          function: { name: tool.name, description: tool.description, parameters: tool.input_schema }
        })),
        max_tokens: args.task.max_output_tokens,
        temperature: 0
      })
    });

    if (!response.ok) {
      throw { code: 'OPENAI_REQUEST_FAIL', message: `OpenAI request failed: ${response.status}`, retryable: response.status >= 500, at: 'provider' };
    }

    const payload = await response.json() as {
      model?: string;
      usage?: { prompt_tokens?: number; completion_tokens?: number };
      choices?: Array<{ message?: { content?: string; tool_calls?: Array<{ id?: string; function?: { name?: string; arguments?: string } }> } }>;
    };

    const message = payload.choices?.[0]?.message;
    const toolCalls = (message?.tool_calls ?? [])
      .map((call) => ({
        call_id: call.id ?? `${args.task.name}-tool-call`,
        name: call.function?.name ?? '',
        arguments: parseJson(call.function?.arguments)
      }))
      .filter((call) => call.name.length > 0);

    return {
      output_text: message?.content ?? undefined,
      tool_calls: toolCalls.length > 0 ? toolCalls : undefined,
      usage: {
        input_tokens: payload.usage?.prompt_tokens,
        output_tokens: payload.usage?.completion_tokens
      },
      provider_latency_ms: Date.now() - started,
      model: payload.model ?? args.task.model
    };
  }
}
