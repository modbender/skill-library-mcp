/**
 * Persona exports
 */

export { SISYPHUS_SYSTEM_PROMPT, SISYPHUS_CONFIG } from './sisyphus.js';
export { HEPHAESTUS_SYSTEM_PROMPT, HEPHAESTUS_CONFIG } from './hephaestus.js';
export { ORACLE_SYSTEM_PROMPT, ORACLE_CONFIG } from './oracle.js';
export { LIBRARIAN_SYSTEM_PROMPT, LIBRARIAN_CONFIG } from './librarian.js';
export { EXPLORE_SYSTEM_PROMPT, EXPLORE_CONFIG } from './explore.js';

export interface PersonaConfig {
  model: string;
  thinking: string;
  temperature: number;
}

export const PERSONAS: Record<string, { prompt: string; config: PersonaConfig }> = {
  sisyphus: {
    prompt: SISYPHUS_SYSTEM_PROMPT,
    config: SISYPHUS_CONFIG,
  },
  hephaestus: {
    prompt: HEPHAESTUS_SYSTEM_PROMPT,
    config: HEPHAESTUS_CONFIG,
  },
  oracle: {
    prompt: ORACLE_SYSTEM_PROMPT,
    config: ORACLE_CONFIG,
  },
  librarian: {
    prompt: LIBRARIAN_SYSTEM_PROMPT,
    config: LIBRARIAN_CONFIG,
  },
  explore: {
    prompt: EXPLORE_SYSTEM_PROMPT,
    config: EXPLORE_CONFIG,
  },
};
