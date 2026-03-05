import { sleep } from '../lib/utils.js';
import type { LLMProvider, LLMRoundResult, LLMTaskContext } from './llm-provider.js';

const toolDirective = (input: string): string | undefined => {
  const match = input.match(/needs_tool:([a-zA-Z0-9_\-]+)/);
  return match?.[1];
};

export class MockLLMProvider implements LLMProvider {
  readonly id = 'mock';
  readonly supports_tools = true;
  readonly enabled = true;

  async executeRound(args: LLMTaskContext): Promise<LLMRoundResult> {
    const inputText = typeof args.task.input === 'string' ? args.task.input : JSON.stringify(args.task.input);
    const slow = inputText.match(/slow_ms_(\d+)/);
    if (slow) {
      await sleep(Number(slow[1]), args.signal);
    }

    if (inputText.includes('need_upgrade_once') && args.tier === 'cheap') {
      const error = new Error('Need stronger model') as Error & { code: string; retryable: boolean; suggested_action: 'upgrade'; at: string };
      error.code = 'MODEL_TOO_WEAK';
      error.retryable = true;
      error.suggested_action = 'upgrade';
      error.at = args.task.name;
      throw error;
    }

    if (inputText.includes('needs_tool_pair')) {
      const seenA = args.messages.some((m) => m.role === 'tool' && m.tool_call_id === `${args.task.name}-pair-1`);
      const seenB = args.messages.some((m) => m.role === 'tool' && m.tool_call_id === `${args.task.name}-pair-2`);
      if (!seenA || !seenB) {
        return {
          tool_calls: [
            { call_id: `${args.task.name}-pair-1`, name: 'js_eval', arguments: { expression: '1+1' } },
            { call_id: `${args.task.name}-pair-2`, name: 'js_eval', arguments: { expression: '2+2' } }
          ],
          usage: { input_tokens: 20, output_tokens: 10 },
          model: args.task.model
        };
      }
    }

    const directive = toolDirective(inputText);
    if (directive) {
      const hasToolResult = args.messages.some((m) => m.role === 'tool');
      if (!hasToolResult) {
        return {
          tool_calls: [{ call_id: `${args.task.name}-call-1`, name: directive, arguments: { expression: '6*7' } }],
          usage: { input_tokens: 16, output_tokens: 8 },
          model: args.task.model
        };
      }
    }

    return {
      output_json: {
        task: args.task.name,
        agent: args.task.agent,
        input: args.task.input,
        verified: true,
        provider: this.id,
        run_id: args.run_id
      },
      usage: { input_tokens: 18, output_tokens: 12 },
      model: args.task.model
    };
  }
}
