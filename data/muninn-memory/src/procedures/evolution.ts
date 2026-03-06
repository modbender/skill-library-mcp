/**
 * Procedure Evolution Module
 * LLM-powered failure analysis and auto-improvement
 */

import { Procedure, ProcedureStep, EvolutionEvent } from '../storage/index.js';

export interface FailureAnalysis {
  failedStep: number;
  failureReason: string;
  suggestedFix: string;
  newSteps: string[];
  confidence: number;
}

export interface ProcedureMetrics {
  successRate: number;
  recentTrend: 'improving' | 'stable' | 'declining';
  lastFailures: string[];
  reliability: number;  // Decay-weighted score 0-1
}

/**
 * Analyze a procedure failure using LLM
 */
export async function analyzeFailure(
  procedure: Procedure,
  failedAtStep: number,
  context: string
): Promise<FailureAnalysis> {
  // Call Ollama for failure analysis
  const prompt = `You are a workflow optimization expert. Analyze this procedure failure and suggest improvements.

PROCEDURE: "${procedure.title}"
DESCRIPTION: ${procedure.description || 'N/A'}

STEPS:
${procedure.steps.map((s, i) => `${i + 1}. ${s.description}`).join('\n')}

FAILURE:
- Failed at step ${failedAtStep}
- Context: ${context}

Analyze what went wrong and suggest improved steps. Respond in JSON format:
{
  "failedStep": <number>,
  "failureReason": "<why it failed>",
  "suggestedFix": "<specific improvement>",
  "newSteps": ["<improved step 1>", "<improved step 2>", ...],
  "confidence": <0.0-1.0>
}`;

  try {
    const response = await fetch('http://localhost:11434/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'llama3.2:latest',
        prompt,
        format: 'json',
        stream: false
      })
    });

    if (!response.ok) {
      throw new Error(`LLM request failed: ${response.statusText}`);
    }

    const data = await response.json() as { response: string };
    const analysis = JSON.parse(data.response) as FailureAnalysis;
    
    return analysis;
  } catch (error) {
    // Fallback: simple heuristic-based fix
    return {
      failedStep: failedAtStep,
      failureReason: context || 'Unknown failure',
      suggestedFix: 'Add error handling and retry logic',
      newSteps: procedure.steps.map((s, i) => 
        i + 1 === failedAtStep 
          ? `${s.description} [NOTE: Add error handling]`
          : s.description
      ),
      confidence: 0.5
    };
  }
}

/**
 * Calculate reliability score with decay
 * Recent successes count more than old ones
 */
export function calculateReliability(procedure: Procedure): ProcedureMetrics {
  const total = procedure.success_count + procedure.failure_count;
  
  if (total === 0) {
    return {
      successRate: 0,
      recentTrend: 'stable',
      lastFailures: [],
      reliability: 0
    };
  }

  // Base success rate
  const successRate = procedure.success_count / total;

  // Calculate trend from evolution log
  // Weight recent events more heavily
  const recentEvents = procedure.evolution_log.slice(-5);
  
  // Calculate weighted score (more recent = higher weight)
  let weightedSuccess = 0;
  let weightedFailure = 0;
  
  for (let i = 0; i < recentEvents.length; i++) {
    const weight = i + 1;  // Older events have lower weight
    const event = recentEvents[i];
    if (event.trigger === 'success_pattern') {
      weightedSuccess += weight;
    } else if (event.trigger === 'failure') {
      weightedFailure += weight;
    }
  }

  let recentTrend: 'improving' | 'stable' | 'declining';
  if (weightedSuccess > weightedFailure) {
    recentTrend = 'improving';
  } else if (weightedFailure > weightedSuccess) {
    recentTrend = 'declining';
  } else {
    recentTrend = 'stable';
  }

  const recentFailures = recentEvents.filter(e => e.trigger === 'failure').length;

  // Decay-weighted reliability
  // More recent events have higher weight
  const decayFactor = 0.9;  // Each older event has 90% weight
  let weightedScore = 0;
  let totalWeight = 0;

  for (let i = recentEvents.length - 1; i >= 0; i--) {
    const weight = Math.pow(decayFactor, recentEvents.length - 1 - i);
    const isSuccess = recentEvents[i].trigger === 'success_pattern';
    weightedScore += weight * (isSuccess ? 1 : 0);
    totalWeight += weight;
  }

  const reliability = totalWeight > 0 ? weightedScore / totalWeight : successRate;

  // Extract last failure reasons
  const lastFailures = recentEvents
    .filter(e => e.trigger === 'failure')
    .map(e => e.change)
    .slice(0, 3);

  return {
    successRate,
    recentTrend,
    lastFailures,
    reliability
  };
}

/**
 * Decide if a procedure should be auto-evolved
 */
export function shouldAutoEvolve(procedure: Procedure): boolean {
  const metrics = calculateReliability(procedure);
  
  // Auto-evolve if:
  // 1. Reliability is declining
  // 2. At least 2 failures
  // 3. Last failure was recent (within last 3 events)
  
  const recentFailures = procedure.evolution_log
    .slice(-3)
    .filter(e => e.trigger === 'failure').length;

  return (
    metrics.recentTrend === 'declining' &&
    procedure.failure_count >= 2 &&
    recentFailures >= 1
  );
}

/**
 * Generate improved procedure version
 */
export async function evolveProcedure(
  procedure: Procedure,
  failedAtStep: number,
  context: string
): Promise<{
  newSteps: ProcedureStep[];
  evolutionEvent: EvolutionEvent;
  analysis: FailureAnalysis;
}> {
  const analysis = await analyzeFailure(procedure, failedAtStep, context);
  
  // Create new steps from analysis
  const newSteps: ProcedureStep[] = analysis.newSteps.map((desc, i) => ({
    id: `step_${Date.now()}_${i}`,
    order: i + 1,
    description: desc
  }));

  const evolutionEvent: EvolutionEvent = {
    version: procedure.version + 1,
    trigger: 'failure',
    change: `LLM analysis: ${analysis.suggestedFix}. Confidence: ${(analysis.confidence * 100).toFixed(0)}%`,
    timestamp: new Date().toISOString()
  };

  return {
    newSteps,
    evolutionEvent,
    analysis
  };
}