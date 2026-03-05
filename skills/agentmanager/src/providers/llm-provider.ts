import type { ModelTier } from '../services/model-tier.js';
import type { TaskSpec, ToolSpec } from '../types.js';

export type LLMMessage = {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  tool_call_id?: string;
  name?: string;
};

export type LLMToolCall = {
  call_id: string;
  name: string;
  arguments: Record<string, unknown>;
};

export type LLMTaskContext = {
  run_id: string;
  runId: string;
  task: TaskSpec;
  taskName: string;
  step: number;
  attempt: number;
  requestId: string;
  tier: ModelTier;
  tokenOwner?: string;
  dependencyDigests?: string[];
  messages: LLMMessage[];
  tools: ToolSpec[];
  signal?: AbortSignal;
};

export type LLMRoundResult = {
  request_id?: string;
  output_text?: string;
  output_json?: Record<string, unknown>;
  tool_calls?: LLMToolCall[];
  usage?: { input_tokens?: number; output_tokens?: number };
  provider_latency_ms?: number;
  model?: string;
};

export type LLMTaskStepResult =
  | { type: 'final'; payload: Record<string, unknown>; tokens_est?: number; tokens_actual?: number }
  | { type: 'tool_calls'; tool_calls: Array<{ id: string; name: string; args: Record<string, unknown> }>; tokens_est?: number; tokens_actual?: number };

export type ProviderDescriptor = {
  id: string;
  enabled: boolean;
  default: boolean;
  supports_tools: boolean;
  notes?: string;
};

export interface LLMProvider {
  readonly id: string;
  readonly supports_tools?: boolean;
  readonly enabled?: boolean;
  readonly notes?: string;
  executeRound?(args: LLMTaskContext): Promise<LLMRoundResult>;
  step?(task: TaskSpec, context: LLMTaskContext): Promise<LLMTaskStepResult>;
}
