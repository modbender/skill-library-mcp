import fs from 'node:fs';
import { performance } from 'node:perf_hooks';
import type {
  ClassificationResult,
  ClassificationMeta,
  DimensionScores,
  DimensionWeights,
  ComplexityTier,
} from './types.js';
import {
  scoreTokenCount,
  scoreCodePresence,
  scoreReasoningMarkers,
  scoreSimpleIndicators,
  scoreMultiStepPatterns,
  scoreQuestionCount,
  scoreSystemPromptSignals,
  scoreConversationDepth,
} from './dimensions.js';

const DEFAULT_WEIGHTS: DimensionWeights = {
  tokenCount: 0.20,
  codePresence: 0.15,
  reasoningMarkers: 0.18,
  simpleIndicators: -0.15,
  multiStepPatterns: 0.15,
  questionCount: 0.07,
  systemPromptSignals: 0.10,
  conversationDepth: 0.10,
};

export function loadWeights(weightsPath: string): DimensionWeights {
  if (!weightsPath || !fs.existsSync(weightsPath)) {
    return { ...DEFAULT_WEIGHTS };
  }
  const raw = fs.readFileSync(weightsPath, 'utf-8');
  return JSON.parse(raw) as DimensionWeights;
}

export function classifyPrompt(
  text: string,
  meta: ClassificationMeta,
  weights: DimensionWeights,
  thresholds: { simpleMax: number; complexMin: number },
): ClassificationResult {
  const t0 = performance.now();

  const dimensions: DimensionScores = {
    tokenCount: scoreTokenCount(text),
    codePresence: scoreCodePresence(text),
    reasoningMarkers: scoreReasoningMarkers(text),
    simpleIndicators: scoreSimpleIndicators(text),
    multiStepPatterns: scoreMultiStepPatterns(text),
    questionCount: scoreQuestionCount(text),
    systemPromptSignals: scoreSystemPromptSignals(meta.systemPrompt),
    conversationDepth: scoreConversationDepth(meta.messageCount),
  };

  let composite = 0;
  const keys = Object.keys(weights) as (keyof DimensionWeights)[];
  for (const key of keys) {
    composite += dimensions[key] * weights[key];
  }

  composite = Math.max(0, Math.min(1, composite));

  let tier: ComplexityTier;
  if (composite <= thresholds.simpleMax) {
    tier = 'simple';
  } else if (composite >= thresholds.complexMin) {
    tier = 'complex';
  } else {
    tier = 'standard';
  }

  const t1 = performance.now();

  return {
    tier,
    score: composite,
    dimensions,
    classifiedInMs: t1 - t0,
  };
}
