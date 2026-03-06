import { describe, it, expect } from 'vitest';
import { routeRequest } from '../../../src/router/engine.js';
import { ModelRegistry, loadRoutingTable } from '../../../src/router/model-registry.js';
import type { ClassificationResult } from '../../../src/classifier/types.js';
import type { OverrideResult } from '../../../src/router/types.js';
import type { ThrottleConfig } from '../../../src/config/types.js';
import path from 'node:path';

const registry = new ModelRegistry(path.resolve('data/model-catalog.json'));
const routingTable = loadRoutingTable(path.resolve('data/routing-table.json'));
const noOverride: OverrideResult = { kind: 'none' };

function makeConfig(keys: Partial<Record<string, string>> = {}): ThrottleConfig {
  return {
    mode: 'standard',
    anthropic: { apiKey: keys.anthropic ?? '', baseUrl: 'https://api.anthropic.com', authType: 'auto' as const },
    google: { apiKey: keys.google ?? '', baseUrl: 'https://generativelanguage.googleapis.com' },
    openai: { apiKey: keys.openai ?? '', baseUrl: 'https://api.openai.com/v1' },
    deepseek: { apiKey: keys.deepseek ?? '', baseUrl: 'https://api.deepseek.com/v1' },
    xai: { apiKey: keys.xai ?? '', baseUrl: 'https://api.x.ai/v1' },
    moonshot: { apiKey: keys.moonshot ?? '', baseUrl: 'https://api.moonshot.ai/v1' },
    mistral: { apiKey: keys.mistral ?? '', baseUrl: 'https://api.mistral.ai/v1' },
    ollama: { apiKey: '', baseUrl: keys.ollama ?? 'http://localhost:11434/v1' },
    logging: { level: 'info', logFilePath: '' },
    classifier: { weightsPath: '', thresholds: { simpleMax: 0.30, complexMin: 0.65 } },
    modelCatalogPath: '',
    routingTablePath: '',
    http: { port: 8484, enabled: false },
  } as ThrottleConfig;
}

function makeClassification(tier: 'simple' | 'standard' | 'complex', score: number): ClassificationResult {
  return {
    tier,
    score,
    dimensions: {
      tokenCount: 0, codePresence: 0, reasoningMarkers: 0,
      simpleIndicators: 0, multiStepPatterns: 0, questionCount: 0,
      systemPromptSignals: 0, conversationDepth: 0,
    },
    classifiedInMs: 0.1,
  };
}

describe('Multi-provider preference-list routing', () => {
  describe('only Google key configured', () => {
    const config = makeConfig({ google: 'test-google-key' });

    it('eco/simple routes to Flash (Grok Fast not configured)', () => {
      const result = routeRequest(makeClassification('simple', 0.1), 'eco', noOverride, registry, config, routingTable);
      // Preference: grok-fast (xai, no), flash (google, yes)
      expect(result.model.id).toBe('gemini-2.5-flash');
    });

    it('eco/standard routes to Flash', () => {
      const result = routeRequest(makeClassification('standard', 0.4), 'eco', noOverride, registry, config, routingTable);
      expect(result.model.id).toBe('gemini-2.5-flash');
    });

    it('eco/complex falls back when no preferred model available', () => {
      const result = routeRequest(makeClassification('complex', 0.8), 'eco', noOverride, registry, config, routingTable);
      // Preference: haiku (no), deepseek-reasoner (no), kimi-k2.5 (no), grok-3-mini (no)
      // Fallback: cheapest available across Google + Ollama
      expect(result.model.id).toBe('ollama-default');
      expect(result.reasoning).toContain('Fallback');
    });

    it('standard/complex falls back since no Anthropic/OpenAI/xAI configured', () => {
      const result = routeRequest(makeClassification('complex', 0.8), 'standard', noOverride, registry, config, routingTable);
      expect(result.model.provider === 'google' || result.model.provider === 'ollama').toBe(true);
    });
  });

  describe('Google + DeepSeek configured', () => {
    const config = makeConfig({ google: 'test-google', deepseek: 'test-deepseek' });

    it('eco/standard routes to Flash (first in preference)', () => {
      const result = routeRequest(makeClassification('standard', 0.4), 'eco', noOverride, registry, config, routingTable);
      expect(result.model.id).toBe('gemini-2.5-flash');
    });

    it('eco/complex routes to DeepSeek Reasoner', () => {
      const result = routeRequest(makeClassification('complex', 0.8), 'eco', noOverride, registry, config, routingTable);
      // Preference: haiku (no), deepseek-reasoner (yes)
      expect(result.model.id).toBe('deepseek-reasoner');
    });

    it('standard/standard routes to Flash', () => {
      // Preference: haiku (no), grok-fast (no), flash (yes)
      const result = routeRequest(makeClassification('standard', 0.4), 'standard', noOverride, registry, config, routingTable);
      expect(result.model.id).toBe('gemini-2.5-flash');
    });
  });

  describe('all providers configured', () => {
    const config = makeConfig({
      anthropic: 'test', google: 'test', openai: 'test',
      deepseek: 'test', xai: 'test', moonshot: 'test', mistral: 'test',
    });

    it('eco/simple routes to Grok Fast (first in preference)', () => {
      const result = routeRequest(makeClassification('simple', 0.1), 'eco', noOverride, registry, config, routingTable);
      expect(result.model.id).toBe('grok-4-1-fast-non-reasoning');
    });

    it('standard/standard routes to Haiku (first in preference)', () => {
      const result = routeRequest(makeClassification('standard', 0.4), 'standard', noOverride, registry, config, routingTable);
      expect(result.model.id).toBe('claude-haiku-4-5');
    });

    it('standard/complex routes to Sonnet', () => {
      const result = routeRequest(makeClassification('complex', 0.8), 'standard', noOverride, registry, config, routingTable);
      expect(result.model.id).toBe('claude-sonnet-4-5');
    });

    it('gigachad/complex routes to Opus 4.6', () => {
      const result = routeRequest(makeClassification('complex', 0.8), 'gigachad', noOverride, registry, config, routingTable);
      expect(result.model.id).toBe('claude-opus-4-6');
    });
  });

  describe('fallback behavior', () => {
    it('uses cheapest available when no preferred model is configured', () => {
      const config = makeConfig({});
      const result = routeRequest(makeClassification('complex', 0.8), 'standard', noOverride, registry, config, routingTable);
      expect(result.model.id).toBe('ollama-default');
      expect(result.reasoning).toContain('Fallback');
    });
  });

  describe('provider configuration checks', () => {
    it('ollama is always configured (no API key needed)', () => {
      const config = makeConfig({});
      const providers = registry.getConfiguredProviders(config);
      expect(providers).toContain('ollama');
    });

    it('reports all configured providers', () => {
      const config = makeConfig({ anthropic: 'key', openai: 'key' });
      const providers = registry.getConfiguredProviders(config);
      expect(providers).toContain('anthropic');
      expect(providers).toContain('openai');
      expect(providers).toContain('ollama');
      expect(providers).not.toContain('google');
      expect(providers).not.toContain('deepseek');
    });

    it('resolvePreference returns null when no model available', () => {
      const config = makeConfig({});
      const result = registry.resolvePreference(['claude-opus-4-5', 'gpt-5.2', 'grok-4-0709'], config);
      expect(result).toBeNull();
    });

    it('resolvePreference returns first available model', () => {
      const config = makeConfig({ openai: 'key' });
      const result = registry.resolvePreference(['claude-opus-4-5', 'gpt-5.2', 'grok-4-0709'], config);
      expect(result?.id).toBe('gpt-5.2');
    });
  });
});
