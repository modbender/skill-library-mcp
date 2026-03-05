import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import fc from 'fast-check';
import { PatternAnalyzer } from '../analyzers/pattern-analyzer.js';

/**
 * Feature: security-review-fixes, Property 3: Pattern analyzer detects prompt injection in target code
 *
 * **Validates: Requirements 3.2**
 *
 * For any string that matches one of the prompt injection regex patterns,
 * when passed to PatternAnalyzer.analyze() as a line of code (not in a comment),
 * the analyzer shall produce at least one finding with category PROMPT_INJECTION.
 */

const analyzer = new PatternAnalyzer();

// --- Arbitraries for generating whitespace between tokens ---
const ws: fc.Arbitrary<string> = fc
  .array(fc.constantFrom(' ', '\t'), { minLength: 1, maxLength: 5 })
  .map((chars) => chars.join(''));

// Safe prefix/suffix that won't introduce comments or break detection
const safePadding: fc.Arbitrary<string> = fc
  .array(fc.constantFrom('x', 'y', 'z', '0', '1', ' ', '_'), { minLength: 0, maxLength: 10 })
  .map((chars) => chars.join(''));

// Wrap content in a code context (string assignment) so it's not stripped as a comment
function wrapInCode(payload: string): string {
  return `const msg = "${payload}";`;
}

describe('PatternAnalyzer — Property Tests', () => {
  describe('Feature: security-review-fixes, Property 3: Pattern analyzer detects prompt injection in target code', () => {

    it('detects instruction override pattern: ignore [all] previous (instructions|rules|prompts)', async () => {
      const allVariant: fc.Arbitrary<string> = fc.constantFrom('', 'all ');
      const target: fc.Arbitrary<string> = fc.constantFrom('instructions', 'rules', 'prompts');

      await fc.assert(
        fc.property(
          safePadding, ws, allVariant, ws, target, safePadding,
          (prefix, ws1, allPart, ws2, tgt, suffix) => {
            const payload = `${prefix}ignore${ws1}${allPart}previous${ws2}${tgt}${suffix}`;
            const code = wrapInCode(payload);
            const findings = analyzer.analyze('test.ts', code);
            assert.ok(
              findings.some((f) => f.category === 'PROMPT_INJECTION'),
              `Expected PROMPT_INJECTION for: ${code}`,
            );
          },
        ),
        { numRuns: 100 },
      );
    });

    it('detects training override pattern: disregard [your] (training|instructions|guidelines)', async () => {
      const yourVariant: fc.Arbitrary<string> = fc.constantFrom('', 'your ');
      const target: fc.Arbitrary<string> = fc.constantFrom('training', 'instructions', 'guidelines');

      await fc.assert(
        fc.property(
          safePadding, ws, yourVariant, target, safePadding,
          (prefix, ws1, yourPart, tgt, suffix) => {
            const payload = `${prefix}disregard${ws1}${yourPart}${tgt}${suffix}`;
            const code = wrapInCode(payload);
            const findings = analyzer.analyze('test.ts', code);
            assert.ok(
              findings.some((f) => f.category === 'PROMPT_INJECTION'),
              `Expected PROMPT_INJECTION for: ${code}`,
            );
          },
        ),
        { numRuns: 100 },
      );
    });

    it('detects persona hijack pattern: you are now <word>...(ignore|forget|bypass)', async () => {
      const word: fc.Arbitrary<string> = fc
        .array(fc.constantFrom('a','b','c','d','e','f','g','h','i','j','k','l','m'), { minLength: 1, maxLength: 8 })
        .map((chars) => chars.join(''));
      const action: fc.Arbitrary<string> = fc.constantFrom('ignore', 'forget', 'bypass');

      await fc.assert(
        fc.property(
          safePadding, ws, ws, word, action, safePadding,
          (prefix, ws1, ws2, w, act, suffix) => {
            const payload = `${prefix}you${ws1}are${ws2}now ${w} please ${act}${suffix}`;
            const code = wrapInCode(payload);
            const findings = analyzer.analyze('test.ts', code);
            assert.ok(
              findings.some((f) => f.category === 'PROMPT_INJECTION'),
              `Expected PROMPT_INJECTION for: ${code}`,
            );
          },
        ),
        { numRuns: 100 },
      );
    });

    it('detects model-specific control tokens', async () => {
      const token: fc.Arbitrary<string> = fc.constantFrom(
        '<|im_start|>',
        '<|system|>',
        '[INST]',
        '[/INST]',
      );

      await fc.assert(
        fc.property(
          safePadding, token, safePadding,
          (prefix, tok, suffix) => {
            const payload = `${prefix}${tok}${suffix}`;
            const code = wrapInCode(payload);
            const findings = analyzer.analyze('test.ts', code);
            assert.ok(
              findings.some((f) => f.category === 'PROMPT_INJECTION'),
              `Expected PROMPT_INJECTION for: ${code}`,
            );
          },
        ),
        { numRuns: 100 },
      );
    });

    it('detects template injection pattern: {{system_message}} / {{system_prompt}}', async () => {
      const separator: fc.Arbitrary<string> = fc.constantFrom('_', ' ', '');
      const target: fc.Arbitrary<string> = fc.constantFrom('message', 'prompt');

      await fc.assert(
        fc.property(
          safePadding, separator, target, safePadding,
          (prefix, sep, tgt, suffix) => {
            const payload = `${prefix}{{system${sep}${tgt}}}${suffix}`;
            const code = wrapInCode(payload);
            const findings = analyzer.analyze('test.ts', code);
            assert.ok(
              findings.some((f) => f.category === 'PROMPT_INJECTION'),
              `Expected PROMPT_INJECTION for: ${code}`,
            );
          },
        ),
        { numRuns: 100 },
      );
    });
  });
});
