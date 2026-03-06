/**
 * Content Router Tests
 *
 * Tests for LLM-powered content classification.
 * Run: npx ts-node src/tests/router.test.ts
 */

import { routeContent, routeWithKeywords, RoutingResult } from '../extractors/router.js';

// Test fixtures - 20 inputs with expected classifications
const TEST_CASES = [
  // Episodic (events, conversations, things that happened)
  { input: "Yesterday I met with Phillip at the coffee shop to discuss the project roadmap", expected: { episodic: true, semantic: false, procedural: false } },
  { input: "We had a meeting about the Q1 targets and decided to pivot the strategy", expected: { episodic: true, semantic: false, procedural: false } },
  { input: "Today I learned that the API is rate limiting at 100 requests per minute", expected: { episodic: true, semantic: false, procedural: false } },
  { input: "The client called and mentioned they're unhappy with the current timeline", expected: { episodic: true, semantic: false, procedural: false } },
  { input: "Last week's deployment caused a 2-hour outage due to a database migration issue", expected: { episodic: true, semantic: false, procedural: false } },

  // Semantic (facts, preferences, knowledge)
  { input: "Phillip prefers Australian English spelling and high signal-to-noise communication", expected: { episodic: false, semantic: true, procedural: false } },
  { input: "The OpenClaw gateway runs on port 18789 by default", expected: { episodic: false, semantic: true, procedural: false } },
  { input: "Elev8Advisory's revenue target is $2000 per month", expected: { episodic: false, semantic: true, procedural: false } },
  { input: "MongoDB uses BSON for document storage which supports more data types than JSON", expected: { episodic: false, semantic: true, procedural: false } },
  { input: "Phillip's timezone is Australia/Brisbane (AEST)", expected: { episodic: false, semantic: true, procedural: false } },

  // Procedural (workflows, how-tos, processes)
  { input: "To deploy the gateway, run: systemctl --user restart openclaw-gateway", expected: { episodic: false, semantic: false, procedural: true } },
  { input: "The heartbeat check protocol involves reading HEARTBEAT.md, checking the state file, and executing the appropriate window task", expected: { episodic: false, semantic: false, procedural: true } },
  { input: "First, clone the repo. Then install dependencies with npm install. Finally, run npm start.", expected: { episodic: false, semantic: false, procedural: true } },
  { input: "When the Telegram channel fails, check IPv6 connectivity and force IPv4 with IPAddressDeny=any", expected: { episodic: false, semantic: false, procedural: true } },
  { input: "The job application process: 1) Find posting, 2) Apply via form, 3) Log to JSON, 4) Track responses", expected: { episodic: false, semantic: false, procedural: true } },

  // Ambiguous cases (should report lower confidence)
  { input: "I think we should automate the testing process", expected: { episodic: false, semantic: true, procedural: true }, ambiguous: true },
  { input: "The new feature was discussed in yesterday's meeting and requires a build step", expected: { episodic: true, semantic: false, procedural: true }, ambiguous: true },
  { input: "Charlie built the memory system and it stores facts in SQLite", expected: { episodic: true, semantic: true, procedural: false }, ambiguous: true },

  // Additional edge cases
  { input: "The server crashed yesterday after we pushed the new release", expected: { episodic: true, semantic: false, procedural: false } },
  { input: "Before starting, make sure you have Node.js installed", expected: { episodic: false, semantic: false, procedural: true } },
  { input: "OpenClaw uses SQLite for storage and Ollama for embeddings", expected: { episodic: false, semantic: true, procedural: false } },
  { input: "We agreed to meet again next Tuesday to review the progress", expected: { episodic: true, semantic: false, procedural: false } },

  // ========================================
  // MESSY INPUT - Typos, informal, slang
  // ========================================

  // Typos and misspellings - Episodic
  { input: "yestrday i met with phillip at the coffe shop and we tlaked about roadmap", expected: { episodic: true, semantic: false, procedural: false }, messy: true },
  { input: "the deployemnt last nite caused a huge outgae and everything was broken lol", expected: { episodic: true, semantic: false, procedural: false }, messy: true },
  { input: "client called and sed their not happy with timline", expected: { episodic: true, semantic: false, procedural: false }, messy: true },
  { input: "we discused the Q1 targets yestrday and decided to piviot", expected: { episodic: true, semantic: false, procedural: false }, messy: true },
  { input: "today i lernt that the api rate limts at 100 req/min", expected: { episodic: true, semantic: false, procedural: false }, messy: true },

  // Typos and misspellings - Semantic
  { input: "phillip perfers australian english speling", expected: { episodic: false, semantic: true, procedural: false }, messy: true },
  { input: "the gatway runs on port 18789 by defalt", expected: { episodic: false, semantic: true, procedural: false }, messy: true },
  { input: "elev8advisory reveneu target is 2k/month", expected: { episodic: false, semantic: true, procedural: false }, messy: true },
  { input: "mongodb uses bson for storarge which is better than json", expected: { episodic: false, semantic: true, procedural: false }, messy: true },

  // Typos and misspellings - Procedural
  { input: "to deploy run: systemctl restart openclaw-gatway", expected: { episodic: false, semantic: false, procedural: true }, messy: true },
  { input: "first clone the repo then npm isntall then npm start", expected: { episodic: false, semantic: false, procedural: true }, messy: true },
  { input: "when telegram fails chck ipv6 and force ipv4", expected: { episodic: false, semantic: false, procedural: true }, messy: true },
  { input: "1) find job 2) apply 3) track respnses 4) profit", expected: { episodic: false, semantic: false, procedural: true }, messy: true },

  // Informal/slang
  { input: "bro the server literally crashed after we pushed that garbage code smh", expected: { episodic: true, semantic: false, procedural: false }, messy: true },
  { input: "ngl phillip hates corporate jargon with a passion", expected: { episodic: false, semantic: true, procedural: false }, messy: true },
  { input: "ur gonna wanna restart the service before testing just saying", expected: { episodic: false, semantic: false, procedural: true }, messy: true },
  { input: "the api is total garbage rn rate limiting every 5 seconds lol", expected: { episodic: true, semantic: true, procedural: false }, ambiguous: true },

  // Run-on sentences, no punctuation
  { input: "so yesterday we had this meeting and phillip was like we need to pivot and i was like yeah makes sense", expected: { episodic: true, semantic: false, procedural: false }, messy: true },
  { input: "gateway port is 18789 thats the default just fyi", expected: { episodic: false, semantic: true, procedural: false }, messy: true },
  { input: "first you clone then you install then you run pretty simple", expected: { episodic: false, semantic: false, procedural: true }, messy: true },

  // All lowercase
  { input: "yesterday met phillip coffee shop discuss roadmap", expected: { episodic: true, semantic: false, procedural: false }, messy: true },
  { input: "phillip prefers australian english spelling", expected: { episodic: false, semantic: true, procedural: false }, messy: true },
  { input: "clone repo install deps run start", expected: { episodic: false, semantic: false, procedural: true }, messy: true },

  // Very short fragments
  { input: "met phillip yesterday", expected: { episodic: true, semantic: false, procedural: false }, messy: true },
  { input: "gateway port 18789", expected: { episodic: false, semantic: true, procedural: false }, messy: true },
  { input: "restart service if fails", expected: { episodic: false, semantic: false, procedural: true }, messy: true },
];

interface TestResult {
  passed: number;
  failed: number;
  results: {
    input: string;
    expected: any;
    actual: any;
    correct: boolean;
    confidence?: number;
  }[];
}

async function runRouterTests(): Promise<TestResult> {
  const results: TestResult['results'] = [];
  let passed = 0;
  let failed = 0;

  console.log('🧪 Content Router Tests\n');
  console.log('=' .repeat(80));

  for (const test of TEST_CASES) {
    const result = routeWithKeywords(test.input);

    // Check if the primary type matches
    const expectedTypes = test.expected as { [key: string]: boolean };
    const expectedPrimaries = Object.entries(expectedTypes)
      .filter(([_, v]) => v)
      .map(([k]) => k);

    const primaryActual = Object.entries(result.types)
      .sort((a, b) => b[1] - a[1])[0][0];

    // For ambiguous cases, accept any of the expected types as valid
    const correct = test.ambiguous
      ? expectedPrimaries.includes(primaryActual)
      : primaryActual === expectedPrimaries[0];

    if (correct) {
      passed++;
      console.log(`✅ PASS: "${test.input.slice(0, 50)}..."`);
    } else {
      failed++;
      console.log(`❌ FAIL: "${test.input.slice(0, 50)}..."`);
      console.log(`   Expected: ${expectedPrimaries.join(' or ')}, Got: ${primaryActual}`);
    }

    results.push({
      input: test.input,
      expected: test.expected,
      actual: result.types,
      correct,
      confidence: result.confidence,
    });
  }

  console.log('\n' + '='.repeat(80));
  console.log(`\n📊 Results: ${passed}/${TEST_CASES.length} passed (${Math.round(passed/TEST_CASES.length*100)}%)`);

  return { passed, failed, results };
}

// Run tests
runRouterTests()
  .then(({ passed, failed }) => {
    process.exit(failed > 0 ? 1 : 0);
  })
  .catch(err => {
    console.error('Test error:', err);
    process.exit(1);
  });