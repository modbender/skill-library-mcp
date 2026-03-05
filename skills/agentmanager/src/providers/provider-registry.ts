import type { LLMProvider, ProviderDescriptor } from './llm-provider.js';
import { getConfig } from '../config.js';

export class ProviderRegistry {
  private readonly providers = new Map<string, LLMProvider>();

  register(provider: LLMProvider): void {
    this.providers.set(provider.id, provider);
  }

  get(providerId: string): LLMProvider | undefined {
    return this.providers.get(providerId);
  }

  list(includeDisabled = false, defaultProviderId = (getConfig().DEFAULT_PROVIDER_ID || getConfig().PROVIDER || (getConfig().GATEWAY_URL ? 'gateway' : (getConfig().LLM_PROVIDER || 'mock')))): ProviderDescriptor[] {
    return [...this.providers.values()]
      .filter((provider) => includeDisabled || provider.enabled !== false)
      .map((provider) => ({
        id: provider.id,
        enabled: provider.enabled !== false,
        default: provider.id === defaultProviderId,
        supports_tools: provider.supports_tools === true,
        notes: provider.notes
      }));
  }

  resolve(requestedIds: { taskProviderId?: string; runProviderId?: string }): LLMProvider {
    const byTask = requestedIds.taskProviderId ? this.get(requestedIds.taskProviderId) : undefined;
    if (byTask && byTask.enabled !== false) return byTask;

    const byRun = requestedIds.runProviderId ? this.get(requestedIds.runProviderId) : undefined;
    if (byRun && byRun.enabled !== false) return byRun;

    const preferred = (getConfig().DEFAULT_PROVIDER_ID || getConfig().PROVIDER || (getConfig().GATEWAY_URL ? 'gateway' : (getConfig().LLM_PROVIDER || 'mock')));
    const byEnv = this.get(preferred);
    if (byEnv && byEnv.enabled !== false) return byEnv;

    const mock = this.get('mock');
    if (mock && mock.enabled !== false) return mock;

    const fallback = [...this.providers.values()].find((provider) => provider.enabled !== false);
    if (fallback) return fallback;

    throw new Error('No enabled providers registered');
  }
}
