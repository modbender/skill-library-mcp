import type { ClassificationResult } from '../classifier/types.js';
import type { RoutingMode } from '../config/types.js';
import type { ThrottleConfig } from '../config/types.js';
import type { RoutingDecision, OverrideResult } from './types.js';
import type { ModelRegistry, RoutingTable } from './model-registry.js';

export function routeRequest(
  classification: ClassificationResult,
  mode: RoutingMode,
  override: OverrideResult,
  registry: ModelRegistry,
  config: ThrottleConfig,
  routingTable: RoutingTable,
): RoutingDecision {
  // If an override is active, use the forced model
  if (override.kind !== 'none' && override.forcedModelId) {
    const model = registry.getById(override.forcedModelId);
    return {
      model,
      tier: classification.tier,
      mode,
      override: override.kind,
      reasoning: `Override ${override.kind}: forced to ${model.displayName}`,
    };
  }

  // Preference-list routing: pick first available model
  const preferenceList = routingTable[mode]?.[classification.tier];
  if (!preferenceList || preferenceList.length === 0) {
    throw new Error(`No routing entry for mode=${mode}, tier=${classification.tier}`);
  }

  const model = registry.resolvePreference(preferenceList, config);
  if (model) {
    return {
      model,
      tier: classification.tier,
      mode,
      override: 'none',
      reasoning: `Mode=${mode}, Tier=${classification.tier}, Score=${classification.score.toFixed(3)} => ${model.displayName}`,
    };
  }

  // Fallback: try ANY available model (cheapest first)
  const fallback = registry.getCheapestAvailable(config);
  if (!fallback) {
    throw new Error('No models available — configure at least one provider API key');
  }

  return {
    model: fallback,
    tier: classification.tier,
    mode,
    override: 'none',
    reasoning: `Fallback: no preferred model available for mode=${mode}, tier=${classification.tier}. Using ${fallback.displayName}`,
  };
}
