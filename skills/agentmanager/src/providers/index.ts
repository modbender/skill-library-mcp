import { AnthropicLLMProvider } from './anthropic.js';
import { GatewayLLMProvider } from './gateway.js';
import type { LLMProvider } from './llm-provider.js';
import { MockLLMProvider } from './mock.js';
import { OpenAILLMProvider } from './openai.js';
import { ProviderRegistry } from './provider-registry.js';

export const createProviderRegistry = (): ProviderRegistry => {
  const registry = new ProviderRegistry();
  registry.register(new MockLLMProvider());
  registry.register(new OpenAILLMProvider());
  registry.register(new AnthropicLLMProvider());
  registry.register(new GatewayLLMProvider());
  return registry;
};

export const createDefaultLLMProvider = (): LLMProvider => createProviderRegistry().resolve({});
