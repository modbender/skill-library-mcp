/**
 * Ultrawork Executor
 * 
 * Orchestrates parallel execution of tasks using OpenClaw tools.
 */

import { PERSONAS, type PersonaConfig } from './personas/mod.js';
import { planTask, shouldUseUltrawork, type TaskChunk } from './planner.js';

/**
 * Execute ultrawork mode - parallel task execution
 */
export interface UltraworkResult {
  success: boolean;
  chunks: TaskChunk[];
  results: unknown[];
  summary: string;
}

/**
 * Get persona config by name
 */
export function getPersonaConfig(name: string): PersonaConfig | undefined {
  const persona = PERSONAS[name.toLowerCase()];
  return persona?.config;
}

/**
 * Build task prompt with persona
 */
export function buildTaskPrompt(chunk: TaskChunk): string {
  const persona = chunk.persona ? PERSONAS[chunk.persona.toLowerCase()] : null;
  
  let prompt = chunk.task;
  
  if (persona) {
    prompt = `${persona.prompt}\n\n---\n\nTask: ${chunk.task}`;
  }
  
  return prompt;
}

/**
 * Format results into summary
 */
export function formatResults(chunks: TaskChunk[], results: unknown[]): string {
  const lines: string[] = ['## Ultrawork Results', ''];
  
  for (let i = 0; i < chunks.length; i++) {
    const chunk = chunks[i];
    const result = results[i];
    lines.push(`### ${chunk.label}`);
    lines.push(`- Persona: ${chunk.persona || 'default'}`);
    lines.push(`- Status: ${result ? 'completed' : 'pending'}`);
    if (result && typeof result === 'object') {
      const r = result as { result?: string };
      if (r.result) {
        lines.push(`- Result: ${r.result.substring(0, 100)}...`);
      }
    }
    lines.push('');
  }
  
  return lines.join('\n');
}

// Re-export for convenience
export { PERSONAS, planTask, shouldUseUltrawork };
