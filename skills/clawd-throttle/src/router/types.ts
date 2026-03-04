import type { ComplexityTier } from '../classifier/types.js';
import type { RoutingMode } from '../config/types.js';

export type ApiProvider =
  | 'anthropic' | 'google' | 'openai' | 'deepseek'
  | 'xai' | 'moonshot' | 'mistral' | 'ollama';

export interface ModelSpec {
  id: string;
  displayName: string;
  provider: ApiProvider;
  inputCostPerMTok: number;
  outputCostPerMTok: number;
  maxContextTokens: number;
}

export type OverrideKind =
  | 'heartbeat'
  | 'summary'
  | 'force_opus'
  | 'force_sonnet'
  | 'force_flash'
  | 'force_model'
  | 'sub_agent_inherit'
  | 'sub_agent_stepdown'
  | 'none';

export interface OverrideResult {
  kind: OverrideKind;
  forcedModelId?: string;
}

export interface RoutingDecision {
  model: ModelSpec;
  tier: ComplexityTier;
  mode: RoutingMode;
  override: OverrideKind;
  reasoning: string;
}
