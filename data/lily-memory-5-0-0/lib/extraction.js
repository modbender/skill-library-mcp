// ============================================================================
// Fact extraction (regex-based, with entity validation)
// ============================================================================

import { isValidEntity } from './entities.js';

// Exported constants
export const MIN_VALUE_LENGTH = 15;
export const MAX_VALUE_LENGTH = 200;

// Values that are conversational noise, not facts
export const NOISE_VALUES = /^(there|here|that|this|it|they|we|built|done|ready|fine|good|bad|actually|really|just|also|now|then|still|already|not|very|much|more|less|what|how|why|where|when|who)[\s:,.]|[:*#\n?()]|^\w+ing\b/i;

// Only match "the X is Y" when X looks like a config/technical term
export const TECHNICAL_NOUN = /^(primary|default|main|current|preferred|configured|target|active|selected|base|core|max|min|api|db|model|port|host|url|path|dir|file|key|token|version|timeout|limit|rate|mode|level|format|encoding|provider|backend|frontend|server|client|endpoint|schema|table|queue|cache|buffer|pool|worker|thread|process|service|plugin|module|package|library|framework|runtime|environment|config|setting|option|param)/i;

export const FACT_PATTERNS = [
  // "Alice prefers X" / "Alice likes X" — only from user messages
  { re: /(\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s+(?:prefers?|likes?|loves?|hates?|wants?)\s+(.+?)(?:\.|$)/gm,
    extract: (m) => ({ entity: m[1], key: "preference", value: m[2].trim() }) },

  // "X is set to Y" / "X is configured as Y" — explicit configuration statements
  { re: /(\b[A-Za-z_]+(?:\s[A-Za-z_]+)?)\s+is\s+(?:set to|configured as|configured to|equal to)\s+(.+?)(?:\.|$)/gm,
    extract: (m) => ({ entity: "config", key: m[1].trim().replace(/\s+/g, "_").toLowerCase(), value: m[2].trim() }) },

  // "The primary model is gemini-2.5-pro" — only when the noun is technical
  { re: /the\s+((?:[\w-]+\s+){0,2}[\w-]+)\s+is\s+([A-Za-z0-9][\w./:@_-]+(?:\s[\w./:@_-]+){0,3})(?:\.|,|$)/gim,
    extract: (m) => {
      const key = m[1].trim().replace(/\s+/g, "_").toLowerCase();
      const value = m[2].trim();
      if (key.length < 4 || key.length > 40) return null;
      if (!TECHNICAL_NOUN.test(key)) return null;
      if (NOISE_VALUES.test(value)) return null;
      return { entity: "config", key, value };
    }
  },

  // "Remember: X" / "Note: X" / "Important: X" — explicit user annotations
  { re: /(?:remember|note|important):\s*(.+?)(?:\.|$)/gim,
    extract: (m) => ({ entity: "note", key: "user_note", value: m[1].trim() }) },

  // "Alice's favorite language is TypeScript" — possessive facts
  { re: /(\b[A-Z][a-z]+)'s\s+([\w\s]+?)\s+is\s+([A-Z][\w./:@_-]+(?:\s[\w./:@_-]+){0,3})(?:\.|,|$)/gm,
    extract: (m) => {
      const value = m[3].trim();
      if (NOISE_VALUES.test(value)) return null;
      return { entity: m[1], key: m[2].trim().replace(/\s+/g, "_").toLowerCase(), value };
    }
  },
];

/**
 * Extract facts from text using FACT_PATTERNS.
 * @param {string} text - The text to extract facts from
 * @param {Set<string>} runtimeEntities - Set of known entities (lowercase)
 * @returns {Array<{entity: string, key: string, value: string}>}
 */
export function extractFacts(text, runtimeEntities) {
  const facts = [];
  const seen = new Set();

  for (const pattern of FACT_PATTERNS) {
    let match;
    pattern.re.lastIndex = 0;
    while ((match = pattern.re.exec(text)) !== null) {
      const fact = pattern.extract(match);
      if (!fact) continue;

      // === ENTITY VALIDATION (new in v3) ===
      if (!isValidEntity(fact.entity, runtimeEntities)) continue;

      // === VALUE VALIDATION (tightened in v3) ===
      // Min length bumped from 2 to 15
      if (fact.value.length < MIN_VALUE_LENGTH || fact.value.length > MAX_VALUE_LENGTH) continue;
      // Noise filter
      if (NOISE_VALUES.test(fact.value)) continue;
      // Markdown artifacts
      if (/[*#`\[\]{}]/.test(fact.value)) continue;
      // Sentence fragments (ends with colon, dash, question mark, open paren)
      if (/[:—?(\)]$/.test(fact.value)) continue;
      // Values starting with quotes or angle brackets
      if (/^["'<]/.test(fact.value)) continue;

      // Dedupe
      const key = `${fact.entity}:${fact.key}:${fact.value}`.toLowerCase();
      if (seen.has(key)) continue;
      seen.add(key);
      facts.push(fact);
    }
  }

  return facts;
}
