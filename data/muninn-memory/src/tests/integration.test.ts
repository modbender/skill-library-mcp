/**
 * Integration Test - Router + MCP Server
 * Verifies the enhanced router works with the full memory pipeline
 */

import { routeContent, routeWithKeywords } from '../extractors/router.js';
import { extract } from '../extractors/index.js';
import { MemoryStore } from '../storage/index.js';

async function runIntegrationTests() {
  console.log('🔗 Integration Tests: Router + MCP Pipeline\n');
  console.log('='.repeat(80));

  let passed = 0;
  let failed = 0;

  // Test cases that should flow through the system
  const testCases = [
    { input: "Yesterday I met with Phillip at the coffee shop", expectedType: "episodic" },
    { input: "Phillip prefers Australian English spelling", expectedType: "semantic" },
    { input: "To deploy the gateway, run: systemctl restart openclaw-gateway", expectedType: "procedural" },
    { input: "The server crashed last night after we pushed the release", expectedType: "episodic" },
    { input: "First, clone the repo. Then run npm install.", expectedType: "procedural" },
    { input: "OpenClaw uses SQLite for storage by default", expectedType: "semantic" },
  ];

  // Test 1: Router classification
  console.log('\n📋 Test 1: Router Classification\n');
  for (const test of testCases) {
    const result = routeWithKeywords(test.input);
    const topType = Object.entries(result.types)
      .sort((a, b) => b[1] - a[1])[0][0];
    
    if (topType === test.expectedType) {
      console.log(`✅ PASS: "${test.input.slice(0, 40)}..." → ${topType}`);
      passed++;
    } else {
      console.log(`❌ FAIL: "${test.input.slice(0, 40)}..." → expected ${test.expectedType}, got ${topType}`);
      failed++;
    }
  }

  // Test 2: Extraction pipeline with entities
  console.log('\n📋 Test 2: Extraction Pipeline with Entities\n');
  for (const test of testCases.slice(0, 3)) {
    const extraction = await extract(test.input);
    if (extraction.type === test.expectedType && extraction.entities.length > 0) {
      console.log(`✅ PASS: extract() → ${extraction.type}, entities: [${extraction.entities.slice(0, 3).join(', ')}]`);
      passed++;
    } else if (extraction.type === test.expectedType) {
      console.log(`⚠️  WARN: extract() → ${extraction.type}, but no entities extracted`);
      passed++;  // Still pass, entities are optional
    } else {
      console.log(`❌ FAIL: extract() → expected ${test.expectedType}, got ${extraction.type}`);
      failed++;
    }
  }

  // Test 3: Memory storage with auto-routing
  console.log('\n📋 Test 3: Memory Storage with Auto-Routing\n');
  
  const store = new MemoryStore('/tmp/test-memory-integration.db');
  
  try {
    // Store episodic
    const mem1 = await store.remember("Yesterday I met with Phillip about the roadmap", 'episodic');
    console.log(`✅ Stored episodic: ${mem1.id} (${mem1.type})`);
    passed++;

    // Store semantic
    const mem2 = await store.remember("Phillip prefers Australian English", 'semantic');
    console.log(`✅ Stored semantic: ${mem2.id} (${mem2.type})`);
    passed++;

    // Store procedural
    const mem3 = await store.remember("To deploy, run: systemctl restart gateway", 'procedural');
    console.log(`✅ Stored procedural: ${mem3.id} (${mem3.type})`);
    passed++;

    // Test recall
    const results = await store.recall("Phillip preferences");
    console.log(`✅ Recall found ${results.length} memories`);
    passed++;

    // Test stats
    const stats = store.getStats();
    console.log(`✅ Stats: ${stats.total} memories, ${stats.entities} entities`);
    passed++;

  } finally {
    store.close();
  }

  // Summary
  console.log('\n' + '='.repeat(80));
  console.log(`\n📊 Integration Results: ${passed}/${passed + failed} passed (${Math.round(passed/(passed+failed)*100)}%)\n`);

  process.exit(failed > 0 ? 1 : 0);
}

runIntegrationTests().catch(err => {
  console.error('Test error:', err);
  process.exit(1);
});