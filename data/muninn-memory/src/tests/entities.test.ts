/**
 * Entity Extraction Tests
 *
 * Tests for NER-style entity extraction with types.
 * Run: npx ts-node src/tests/entities.test.ts
 */

import { extractEntities, Entity, EntityType } from '../extractors/entities.js';

// Test fixtures - inputs with expected entities
const TEST_CASES: { input: string; expected: { text: string; type: EntityType }[] }[] = [
  // People
  {
    input: "Yesterday I met with Phillip at the coffee shop to discuss the roadmap",
    expected: [
      { text: "Phillip", type: "person" }
    ]
  },
  {
    input: "Sammy Clemens wrote the content for BrandForge",
    expected: [
      { text: "Sammy Clemens", type: "person" },
      { text: "BrandForge", type: "project" }
    ]
  },
  {
    input: "Charlie Babbage and Donna Paulsen are part of the agent team",
    expected: [
      { text: "Charlie Babbage", type: "person" },
      { text: "Donna Paulsen", type: "person" }
    ]
  },

  // Organizations
  {
    input: "We need to follow up with Elev8Advisory about the partnership",
    expected: [
      { text: "Elev8Advisory", type: "organization" }
    ]
  },
  {
    input: "OpenClaw uses SQLite for storage and Ollama for embeddings",
    expected: [
      { text: "OpenClaw", type: "organization" },
      { text: "SQLite", type: "technology" },
      { text: "Ollama", type: "technology" }
    ]
  },

  // Projects
  {
    input: "Mission Control dashboard now shows NRL Fantasy tracking",
    expected: [
      { text: "Mission Control", type: "project" },
      { text: "NRL Fantasy", type: "project" }
    ]
  },
  {
    input: "GigHunter is scraping remote jobs from multiple platforms",
    expected: [
      { text: "GigHunter", type: "project" }
    ]
  },

  // Technologies
  {
    input: "The router is built with TypeScript and uses better-sqlite3",
    expected: [
      { text: "TypeScript", type: "technology" },
      { text: "better-sqlite3", type: "technology" }
    ]
  },
  {
    input: "We're using React for the frontend and Node.js for the backend",
    expected: [
      { text: "React", type: "technology" },
      { text: "Node.js", type: "technology" }
    ]
  },

  // Locations
  {
    input: "Phillip is based in Brisbane, Australia",
    expected: [
      { text: "Phillip", type: "person" },
      { text: "Brisbane", type: "location" },
      { text: "Australia", type: "location" }
    ]
  },
  {
    input: "The team met at the Sydney office last week",
    expected: [
      { text: "Sydney", type: "location" }
    ]
  },

  // Events
  {
    input: "We discussed the Q1 planning session and the product launch",
    expected: [
      { text: "Q1 planning session", type: "event" },
      { text: "product launch", type: "event" }
    ]
  },

  // Concepts
  {
    input: "The memory system uses embeddings for semantic search",
    expected: [
      { text: "memory system", type: "project" },  // Could be concept or project
      { text: "embeddings", type: "technology" },   // Could be concept or technology
      { text: "semantic search", type: "technology" }  // Could be concept or technology
    ]
  },

  // Mixed - complex cases
  {
    input: "Yesterday Charlie deployed Muninn to the homelab server using Docker",
    expected: [
      { text: "Charlie", type: "person" },
      { text: "Muninn", type: "project" },
      { text: "homelab", type: "location" },
      { text: "Docker", type: "technology" }
    ]
  },
  {
    input: "Phillip prefers Australian English and uses VS Code for development",
    expected: [
      { text: "Phillip", type: "person" },
      { text: "Australian English", type: "concept" },
      { text: "VS Code", type: "technology" }
    ]
  },

  // Edge cases - should NOT extract
  {
    input: "The system should handle this automatically",
    expected: []  // No named entities
  },
  {
    input: "We need to think about how to approach this problem",
    expected: []  // No named entities
  },

  // Typos and variations
  {
    input: "phillip and sammy discussed the project yesterday",
    expected: [
      { text: "phillip", type: "person" },
      { text: "sammy", type: "person" }
    ]
  },
];

interface TestResult {
  passed: number;
  failed: number;
  results: {
    input: string;
    expected: Entity[];
    actual: Entity[];
    correct: boolean;
    precision: number;
    recall: number;
  }[];
}

async function runEntityTests(): Promise<TestResult> {
  const results: TestResult['results'] = [];
  let passed = 0;
  let failed = 0;

  console.log('🧪 Entity Extraction Tests\n');
  console.log('='.repeat(80));

  for (const test of TEST_CASES) {
    const entities = extractEntities(test.input);

    // Check if all expected entities were found
    let matched = 0;
    for (const expected of test.expected) {
      const found = entities.find(e =>
        e.text.toLowerCase() === expected.text.toLowerCase() &&
        e.type === expected.type
      );
      if (found) matched++;
    }

    const precision = entities.length > 0 ? matched / entities.length : (test.expected.length === 0 ? 1 : 0);
    const recall = test.expected.length > 0 ? matched / test.expected.length : 1;
    
    // Pass if recall is 100% (all expected found) and precision >= 50% (not too much noise)
    const correct = recall >= 1.0 && precision >= 0.5;

    if (correct) {
      passed++;
      console.log(`✅ PASS: "${test.input.slice(0, 50)}..."`);
      console.log(`   Found: ${entities.map(e => `${e.text}(${e.type})`).join(', ') || 'none'}`);
    } else {
      failed++;
      console.log(`❌ FAIL: "${test.input.slice(0, 50)}..."`);
      console.log(`   Expected: ${test.expected.map(e => `${e.text}(${e.type})`).join(', ') || 'none'}`);
      console.log(`   Got: ${entities.map(e => `${e.text}(${e.type})`).join(', ') || 'none'}`);
      console.log(`   Precision: ${(precision * 100).toFixed(0)}%, Recall: ${(recall * 100).toFixed(0)}%`);
    }

    results.push({
      input: test.input,
      expected: test.expected.map(e => ({ text: e.text, type: e.type, confidence: 1, context: '' })),
      actual: entities,
      correct,
      precision,
      recall
    });
  }

  console.log('\n' + '='.repeat(80));
  console.log(`\n📊 Results: ${passed}/${TEST_CASES.length} passed (${Math.round(passed/TEST_CASES.length*100)}%)`);

  const avgPrecision = results.reduce((sum, r) => sum + r.precision, 0) / results.length;
  const avgRecall = results.reduce((sum, r) => sum + r.recall, 0) / results.length;
  console.log(`📊 Average Precision: ${(avgPrecision * 100).toFixed(0)}%`);
  console.log(`📊 Average Recall: ${(avgRecall * 100).toFixed(0)}%`);

  return { passed, failed, results };
}

// Run tests
runEntityTests()
  .then(({ passed, failed }) => {
    process.exit(failed > 0 ? 1 : 0);
  })
  .catch(err => {
    console.error('Test error:', err);
    process.exit(1);
  });