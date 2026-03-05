import fs from 'node:fs';
import type { ModelSpec, ApiProvider } from './types.js';
import type { ThrottleConfig, RoutingMode } from '../config/types.js';
import type { ComplexityTier } from '../classifier/types.js';
import type { ProviderConfig } from '../proxy/types.js';
import { createLogger } from '../utils/logger.js';

const log = createLogger('model-registry');

interface ModelCatalogFile {
  models: ModelSpec[];
}

export type RoutingTable = Record<RoutingMode, Record<ComplexityTier, string[]>>;

const ALL_PROVIDERS: ApiProvider[] = [
  'anthropic', 'google', 'openai', 'deepseek',
  'xai', 'moonshot', 'mistral', 'ollama',
];

export class ModelRegistry {
  private models: Map<string, ModelSpec>;

  constructor(catalogPath: string) {
    this.models = new Map();
    const raw = fs.readFileSync(catalogPath, 'utf-8');
    const catalog = JSON.parse(raw) as ModelCatalogFile;
    for (const model of catalog.models) {
      this.models.set(model.id, model);
    }
    log.info(`Loaded ${this.models.size} models from catalog`);
  }

  getById(id: string): ModelSpec {
    const model = this.models.get(id);
    if (!model) {
      throw new Error(`Unknown model ID: ${id}`);
    }
    return model;
  }

  getAll(): ModelSpec[] {
    return Array.from(this.models.values());
  }

  getCheapest(): ModelSpec {
    return this.getAll().sort(
      (a, b) => a.inputCostPerMTok - b.inputCostPerMTok
    )[0]!;
  }

  /**
   * Check if a provider has a usable API key configured.
   * Special case: ollama is "configured" if its baseUrl is set (always true by default).
   */
  isProviderConfigured(provider: ApiProvider, config: ThrottleConfig): boolean {
    if (provider === 'ollama') {
      return config.ollama.baseUrl.length > 0;
    }
    const providerConfig = config[provider] as { apiKey: string; baseUrl: string };
    return providerConfig.apiKey.length > 0;
  }

  /**
   * Get the provider config (apiKey + baseUrl) for any provider.
   */
  getProviderConfig(provider: ApiProvider, config: ThrottleConfig): ProviderConfig {
    const section = config[provider] as { apiKey: string; baseUrl: string };
    return { apiKey: section.apiKey, baseUrl: section.baseUrl };
  }

  /**
   * Return the first available model from a preference list.
   * A model is "available" if its provider has a configured API key.
   */
  resolvePreference(preferenceList: string[], config: ThrottleConfig): ModelSpec | null {
    for (const modelId of preferenceList) {
      const model = this.models.get(modelId);
      if (model && this.isProviderConfigured(model.provider, config)) {
        return model;
      }
    }
    return null;
  }

  /**
   * Get the cheapest available model across all configured providers.
   */
  getCheapestAvailable(config: ThrottleConfig): ModelSpec | null {
    const available = this.getAll()
      .filter(m => this.isProviderConfigured(m.provider, config))
      .sort((a, b) => a.inputCostPerMTok - b.inputCostPerMTok);
    return available[0] ?? null;
  }

  /**
   * Get the most expensive model in the catalog (for savings baseline).
   */
  getMostExpensive(): ModelSpec {
    return this.getAll().sort(
      (a, b) => b.outputCostPerMTok - a.outputCostPerMTok
    )[0]!;
  }

  /**
   * Return list of providers that have API keys configured.
   */
  getConfiguredProviders(config: ThrottleConfig): ApiProvider[] {
    return ALL_PROVIDERS.filter(p => this.isProviderConfigured(p, config));
  }
}

/**
 * Load the routing preference table from a JSON file.
 */
export function loadRoutingTable(tablePath: string): RoutingTable {
  const raw = fs.readFileSync(tablePath, 'utf-8');
  const table = JSON.parse(raw) as RoutingTable;
  log.info(`Loaded routing table from ${tablePath}`);
  return table;
}
