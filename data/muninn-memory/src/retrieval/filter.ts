/**
 * LLM-Based Retrieval Filter
 * 
 * Post-filters semantic search results using LLM to improve precision
 * while maintaining recall by using recall-biased prompts.
 */

import type { Memory } from '../storage/index.js';

export interface FilterOptions {
  /** Maximum number of results to return */
  k?: number;
  /** Whether to use recall-biased filtering (keep borderline cases) */
  recallBiased?: boolean;
  /** Custom prompt template */
  promptTemplate?: string;
  /** LLM timeout in ms (default 2000) */
  timeout?: number;
}

/**
 * Filter memories using LLM to improve relevance ranking
 * With fast timeout fallback to avoid hanging
 * 
 * @param query - The search query
 * @param memories - Candidate memories from semantic search
 * @param options - Filter options
 * @returns Filtered and ranked memories
 */
export async function filterMemories(
  query: string,
  memories: Memory[],
  options: FilterOptions = {}
): Promise<Memory[]> {
  const { k = memories.length, recallBiased = true, timeout = 2000 } = options;
  
  // Return all if too few
  if (memories.length === 0) return [];
  if (memories.length <= 2) return memories.slice(0, k);
  
  // Try LLM filter with timeout
  try {
    const result = await Promise.race([
      llmFilter(query, memories, { recallBiased }),
      new Promise<Memory[]>((_, reject) => 
        setTimeout(() => reject(new Error('LLM timeout')), timeout)
      )
    ]);
    
    if (result && result.length > 0) {
      return result.slice(0, k);
    }
  } catch (error) {
    console.warn('LLM filter failed or timed out, using fallback:', error instanceof Error ? error.message : 'unknown');
  }
  
  // Fallback: Return top-k by salience + recency
  return fallbackFilter(memories, k);
}

/**
 * Fallback filter: score by salience + recency
 */
function fallbackFilter(memories: Memory[], k: number): Memory[] {
  const now = Date.now();
  const msPerMonth = 1000 * 60 * 60 * 24 * 30;
  
  return [...memories]
    .sort((a, b) => {
      // Combine salience with recency boost
      const scoreA = a.salience + (now - new Date(a.created_at).getTime()) / msPerMonth * 0.1;
      const scoreB = b.salience + (now - new Date(b.created_at).getTime()) / msPerMonth * 0.1;
      return scoreB - scoreA;
    })
    .slice(0, k);
}

/**
 * Post-retrieval scorer for temporal/contradiction questions
 */
export function scoreForQuestionType(memories: Memory[], query: string): Memory[] {
  const lowerQuery = query.toLowerCase();
  
  // Boost recent memories for "current" questions
  if (lowerQuery.includes('current') || lowerQuery.includes('now') || lowerQuery.includes('priority')) {
    return [...memories].sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
  }
  
  // For "how did X change", include all mentions
  if (lowerQuery.includes('change') || lowerQuery.includes('over time') || lowerQuery.includes('history')) {
    return memories; // Return all, let synthesis handle it
  }
  
  return memories;
}

/**
 * Actual LLM filter implementation
 */
async function llmFilter(
  query: string,
  memories: Memory[],
  options: { recallBiased?: boolean }
): Promise<Memory[]> {
  const { recallBiased = true } = options;
  
  // Return all if too few
  if (memories.length === 0) return [];
  if (memories.length <= 2) return memories;
  
  try {
    // Format candidates for LLM
    const candidatesText = formatCandidatesForLLM(memories);
    
    // Build prompt (recall-biased to keep borderline cases)
    const prompt = recallBiased
      ? buildRecallBiasedPrompt(query, candidatesText)
      : buildPrecisionPrompt(query, candidatesText);
    
    // Call LLM
    const response = await generateLLMResponse(prompt);
    
    // Parse response to get relevant indices
    const { relevantIndices } = parseLLMResponse(response);
    
    // Map indices back to memories, preserving original order
    const filtered = relevantIndices
      .filter(i => i >= 0 && i < memories.length)
      .map(i => memories[i]);
    
    // If LLM returns empty or invalid, fall back to original
    if (filtered.length === 0) {
      return memories;
    }
    
    return filtered;
  } catch (error) {
    console.warn('LLM filter failed, using fallback:', error);
    // Fallback: return original memories sorted by salience
    return [...memories].sort((a, b) => b.salience - a.salience);
  }
}

/**
 * Format memories as numbered list for LLM consumption
 */
function formatCandidatesForLLM(memories: Memory[]): string {
  return memories
    .map((m, i) => `[${i}] ${m.content}`)
    .join('\n\n');
}

/**
 * Build recall-biased prompt (prefer including borderline cases)
 */
function buildRecallBiasedPrompt(query: string, candidates: string): string {
  return `Given the question: "${query}"

Select ALL memory entries that could be relevant, even if uncertain.
It's better to include borderline cases than miss relevant information.
When in doubt, include the memory.

Memories to evaluate:
${candidates}

Return JSON with "relevantIndices" array containing indices of relevant memories:
{"relevantIndices": [0, 3, 5]}`;
}

/**
 * Build precision-biased prompt (only highly relevant)
 */
function buildPrecisionPrompt(query: string, candidates: string): string {
  return `Given the question: "${query}"

Select ONLY the most directly relevant memory entries.
Exclude entries that are tangentially related or uncertain.

Memories to evaluate:
${candidates}

Return JSON with "relevantIndices" array containing indices of highly relevant memories:
{"relevantIndices": [0, 3, 5]}`;
}

/**
 * Parse LLM JSON response
 */
function parseLLMResponse(response: string): { relevantIndices: number[] } {
  try {
    // Try to extract JSON from response
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      console.warn('No JSON found in LLM response');
      return { relevantIndices: [] };
    }
    
    const parsed = JSON.parse(jsonMatch[0]);
    
    // Handle different response formats
    if (Array.isArray(parsed)) {
      return { relevantIndices: parsed };
    }
    if (parsed.relevantIndices) {
      return { relevantIndices: parsed.relevantIndices };
    }
    if (parsed.relevant || parsed.indices || parsed.results) {
      return { relevantIndices: parsed.relevant || parsed.indices || parsed.results };
    }
    
    // Try to extract any array of numbers
    for (const key of Object.keys(parsed)) {
      if (Array.isArray(parsed[key]) && parsed[key].every((v: any) => typeof v === 'number')) {
        return { relevantIndices: parsed[key] };
      }
    }
    
    console.warn('Could not parse LLM response format');
    return { relevantIndices: [] };
  } catch (error) {
    console.warn('Failed to parse LLM response:', error);
    return { relevantIndices: [] };
  }
}

/**
 * Generate LLM response (uses global mock or Ollama)
 */
async function generateLLMResponse(prompt: string, timeoutMs: number = 10000): Promise<string> {
  // Use global mock if available (for testing)
  if (typeof (globalThis as any).generateLLMResponse === 'function') {
    return (globalThis as any).generateLLMResponse(prompt);
  }
  
  // Use Ollama cloud model (faster than local for this use case)
  const model = 'glm-5:cloud';
  
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    
    const response = await fetch('http://localhost:11434/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: model,
        prompt: prompt,
        stream: false,
        format: 'json'
      }),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (response.ok) {
      const data = await response.json() as { response: string };
      return data.response;
    }
    
    throw new Error(`Model ${model}: ${response.statusText}`);
  } catch (e) {
    throw e;
  }
}
