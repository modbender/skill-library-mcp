/**
 * Quick test: personality analysis only (no wallet, no API calls).
 * Usage: npx ts-node scripts/test-personality-only.ts
 */
import * as fs from 'fs';
import * as path from 'path';
import { EnhancedDataCollector } from '../src/analyzers/data-collector-enhanced';
import { PersonalityAnalyzer } from '../src/analyzers/personality-analyzer';

const fixtures = [
  { file: '01-visionary-crypto.txt', expected: 'The Visionary' },
  { file: '02-explorer-ai-wellness.txt', expected: 'The Explorer' },
  { file: '03-optimizer-productivity.txt', expected: 'The Optimizer' },
  { file: '04-innovator-dev-ai.txt', expected: 'The Innovator' },
  { file: '05-cultivator-education.txt', expected: 'The Cultivator' },
];

async function main() {
  const collector = new EnhancedDataCollector();
  const analyzer = new PersonalityAnalyzer();

  let pass = 0;
  let fail = 0;

  for (const { file, expected } of fixtures) {
    const text = fs.readFileSync(path.join(__dirname, '..', 'test-fixtures', file), 'utf-8');

    // Simulate collectFromConversationText (only the analyzeConversationText part)
    const userData = await collector.collectFromConversationText(`test-${file}`, text, { skipTwitter: true });

    // Convert to personality analyzer format
    const analyzerData = {
      sources: userData.sources,
      conversationMemory: userData.conversationMemory,
    };

    const result = await analyzer.analyze(analyzerData);
    const ok = result.personalityType === expected;
    const icon = ok ? '✅' : '❌';
    console.log(`${icon} ${file}: ${result.personalityType} (expected: ${expected}) — C=${result.dimensions.conviction}, I=${result.dimensions.intuition}, Cont=${result.dimensions.contribution}`);
    if (ok) pass++;
    else fail++;
  }

  console.log(`\n${pass}/${pass + fail} passed`);
}

main().catch(console.error);
