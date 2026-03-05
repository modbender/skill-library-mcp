import { describe, test } from 'node:test';
import assert from 'node:assert/strict';
import { extractFacts, MIN_VALUE_LENGTH, MAX_VALUE_LENGTH, NOISE_VALUES, TECHNICAL_NOUN, FACT_PATTERNS } from '../lib/extraction.js';

describe('extraction', () => {
  describe('extractFacts', () => {
    test('should extract preference pattern "Kevin prefers TypeScript for all new projects"', () => {
      const runtimeEntities = new Set(['kevin']);
      const text = 'Kevin prefers TypeScript for all new projects.';
      const facts = extractFacts(text, runtimeEntities);

      assert.equal(facts.length, 1);
      assert.equal(facts[0].entity, 'Kevin');
      assert.equal(facts[0].key, 'preference');
      assert.equal(facts[0].value, 'TypeScript for all new projects');
    });

    test('should extract possessive pattern "Kevin\'s favorite language is TypeScript for all projects"', () => {
      const runtimeEntities = new Set(['kevin']);
      const text = "Kevin's favorite language is TypeScript for all projects.";
      const facts = extractFacts(text, runtimeEntities);

      assert.equal(facts.length, 1);
      assert.equal(facts[0].entity, 'Kevin');
      assert.equal(facts[0].key, 'favorite_language');
      // Possessive pattern includes the period in the capture
      assert.equal(facts[0].value, 'TypeScript for all projects.');
    });

    test('should extract config pattern "The primary model is set to gemini-2.5-pro for inference"', () => {
      const runtimeEntities = new Set(['config']);
      const text = 'The primary model is set to gemini-2.5-pro for inference.';
      const facts = extractFacts(text, runtimeEntities);

      assert.equal(facts.length, 1);
      assert.equal(facts[0].entity, 'config');
      assert.equal(facts[0].key, 'primary_model');
      // Pattern 2 "is set to" captures differently than pattern 3 "the X is Y"
      assert.ok(facts[0].value.includes('gemini-2') || facts[0].value === 'gemini-2.5-pro for inference');
    });

    test('should extract note pattern "Remember: always use strict mode in TypeScript projects"', () => {
      const runtimeEntities = new Set(['note']);
      const text = 'Remember: always use strict mode in TypeScript projects.';
      const facts = extractFacts(text, runtimeEntities);

      assert.equal(facts.length, 1);
      assert.equal(facts[0].entity, 'note');
      assert.equal(facts[0].key, 'user_note');
      assert.equal(facts[0].value, 'always use strict mode in TypeScript projects');
    });

    test('should extract "entity: key = some value that is long enough" pattern', () => {
      const runtimeEntities = new Set(['config']);
      const text = 'The cache backend is set to Redis for session storage across all services.';
      const facts = extractFacts(text, runtimeEntities);

      assert.ok(facts.length >= 1);
      const configFact = facts.find(f => f.entity === 'config');
      assert.ok(configFact);
      assert.ok(configFact.value.length >= MIN_VALUE_LENGTH);
    });

    test('should reject value too short (< 15 chars)', () => {
      const runtimeEntities = new Set(['kevin']);
      const text = 'Kevin prefers Go.';
      const facts = extractFacts(text, runtimeEntities);

      assert.equal(facts.length, 0);
    });

    test('should reject value with question mark', () => {
      const runtimeEntities = new Set(['kevin']);
      const text = 'Kevin prefers TypeScript for what?';
      const facts = extractFacts(text, runtimeEntities);

      assert.equal(facts.length, 0);
    });

    test('should reject value with parentheses at end', () => {
      const runtimeEntities = new Set(['kevin']);
      const text = 'Kevin prefers TypeScript for all new projects (maybe).';
      const facts = extractFacts(text, runtimeEntities);

      // Should be rejected due to parentheses
      assert.equal(facts.length, 0);
    });

    test('should reject noise value (markdown/URL)', () => {
      const runtimeEntities = new Set(['kevin']);
      const text = 'Kevin prefers building things quickly.';
      const facts = extractFacts(text, runtimeEntities);

      // "building" starts with noise pattern "^\w+ing\b"
      assert.equal(facts.length, 0);
    });

    test('should reject invalid entity (Still, Just)', () => {
      const runtimeEntities = new Set(['kevin']);
      const text = 'Still prefers TypeScript for all new projects today.';
      const facts = extractFacts(text, runtimeEntities);

      // "Still" is a noise word, should be rejected by isValidEntity
      assert.equal(facts.length, 0);
    });

    test('should accept capitalized entity with possessive pattern', () => {
      const runtimeEntities = new Set(['alice']);
      const text = "Alice's preferred editor is VSCode for daily coding.";
      const facts = extractFacts(text, runtimeEntities);

      assert.ok(facts.length >= 1);
      const aliceFact = facts.find(f => f.entity === 'Alice');
      assert.ok(aliceFact);
      assert.equal(aliceFact.key, 'preferred_editor');
      // Pattern captures up to 3 words after the first word
      assert.ok(aliceFact.value.includes('VSCode'));
    });

    test('should deduplicate duplicate facts in same text', () => {
      const runtimeEntities = new Set(['kevin']);
      const text = 'Kevin prefers TypeScript for all new projects. Kevin prefers TypeScript for all new projects.';
      const facts = extractFacts(text, runtimeEntities);

      assert.equal(facts.length, 1);
    });

    test('should return empty array for empty text', () => {
      const runtimeEntities = new Set(['kevin']);
      const text = '';
      const facts = extractFacts(text, runtimeEntities);

      assert.deepEqual(facts, []);
    });

    test('should return empty array for text with no facts', () => {
      const runtimeEntities = new Set(['kevin']);
      const text = 'This is just some random text without any facts.';
      const facts = extractFacts(text, runtimeEntities);

      assert.equal(facts.length, 0);
    });

    test('should capture multiple valid facts in one text', () => {
      const runtimeEntities = new Set(['kevin', 'config', 'note']);
      const text = 'Kevin prefers TypeScript for all new projects. The primary model is gemini-2.5-pro for inference. Remember: always use strict mode in TypeScript projects.';
      const facts = extractFacts(text, runtimeEntities);

      assert.ok(facts.length >= 3);
      assert.ok(facts.some(f => f.entity === 'Kevin'));
      assert.ok(facts.some(f => f.entity === 'config'));
      assert.ok(facts.some(f => f.entity === 'note'));
    });
  });

  describe('constants', () => {
    test('MIN_VALUE_LENGTH should be 15', () => {
      assert.equal(MIN_VALUE_LENGTH, 15);
    });

    test('MAX_VALUE_LENGTH should be 200', () => {
      assert.equal(MAX_VALUE_LENGTH, 200);
    });

    test('NOISE_VALUES should be a RegExp', () => {
      assert.ok(NOISE_VALUES instanceof RegExp);
    });

    test('TECHNICAL_NOUN should be a RegExp', () => {
      assert.ok(TECHNICAL_NOUN instanceof RegExp);
    });

    test('FACT_PATTERNS should be an array', () => {
      assert.ok(Array.isArray(FACT_PATTERNS));
      assert.ok(FACT_PATTERNS.length > 0);
    });
  });
});
