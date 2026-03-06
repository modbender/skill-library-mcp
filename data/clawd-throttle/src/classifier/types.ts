export type ComplexityTier = 'simple' | 'standard' | 'complex';

export interface DimensionScores {
  tokenCount: number;
  codePresence: number;
  reasoningMarkers: number;
  simpleIndicators: number;
  multiStepPatterns: number;
  questionCount: number;
  systemPromptSignals: number;
  conversationDepth: number;
}

export interface DimensionWeights {
  tokenCount: number;
  codePresence: number;
  reasoningMarkers: number;
  simpleIndicators: number;
  multiStepPatterns: number;
  questionCount: number;
  systemPromptSignals: number;
  conversationDepth: number;
}

export interface ClassificationMeta {
  messageCount?: number;
  systemPrompt?: string;
}

export interface ClassificationResult {
  tier: ComplexityTier;
  score: number;
  dimensions: DimensionScores;
  classifiedInMs: number;
}
