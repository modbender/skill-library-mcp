import type { LLMProvider, LLMRoundResult, LLMTaskContext } from './llm-provider.js';
import { getConfig } from '../config.js';

export class AnthropicLLMProvider implements LLMProvider {
  readonly id = 'anthropic';
  readonly supports_tools = true;
  readonly enabled = Boolean(getConfig().ANTHROPIC_API_KEY);
  readonly notes = this.enabled ? 'Stub provider enabled. Implement endpoint-specific mapping before production use.' : 'Set ANTHROPIC_API_KEY to enable this provider';

  async executeRound(_args: LLMTaskContext): Promise<LLMRoundResult> {
    throw { code: 'PROVIDER_NOT_IMPLEMENTED', message: 'Anthropic provider stub is not implemented in this build', retryable: false, at: 'provider' };
  }
}
