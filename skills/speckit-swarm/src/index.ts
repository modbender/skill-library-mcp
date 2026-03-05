/**
 * Speckit Swarm - Agent Orchestration System
 * 
 * Native implementation of oh-my-opencode-style orchestration.
 * 
 * Usage:
 * - sessions_spawn with persona: "sisyphus", "hephaestus", "oracle", "librarian", "explore"
 * - parallel_spawn with task decomposition
 * - Detect "ulw" keyword for automatic ultrawork mode
 */

export { PERSONAS, type PersonaConfig } from './personas/mod.js';
export { SISYPHUS_SYSTEM_PROMPT, SISYPHUS_CONFIG } from './personas/sisyphus.js';
export { HEPHAESTUS_SYSTEM_PROMPT, HEPHAESTUS_CONFIG } from './personas/hephaestus.js';
export { ORACLE_SYSTEM_PROMPT, ORACLE_CONFIG } from './personas/oracle.js';
export { LIBRARIAN_SYSTEM_PROMPT, LIBRARIAN_CONFIG } from './personas/librarian.js';
export { EXPLORE_SYSTEM_PROMPT, EXPLORE_CONFIG } from './personas/explore.js';

export { planTask, shouldUseUltrawork, type TaskChunk, type PlanResult } from './planner.js';
export { getPersonaConfig, buildTaskPrompt, formatResults, type UltraworkResult } from './ultrawork.js';
