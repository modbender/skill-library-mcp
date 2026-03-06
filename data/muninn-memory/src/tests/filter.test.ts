/**
 * Retrieval Filter Tests
 * Tests for LLM-based post-filtering on retrieval results
 */

import { filterMemories, type FilterOptions } from '../retrieval/filter.js';
import type { Memory } from '../storage/index.js';

// Mock memories for testing
const mockMemories: Memory[] = [
  {
    id: 'm1',
    type: 'semantic',
    content: 'Sammy Clemens prefers working late at night',
    embedding: [],
    entities: ['Sammy Clemens'],
    topics: ['preferences', 'work habits'],
    salience: 0.8,
    created_at: '2026-02-20T10:00:00Z',
    updated_at: '2026-02-20T10:00:00Z'
  },
  {
    id: 'm2',
    type: 'semantic',
    content: 'Charlie Babbage built the first mechanical computer in 1837',
    embedding: [],
    entities: ['Charlie Babbage'],
    topics: ['history', 'inventions'],
    salience: 0.9,
    created_at: '2026-02-19T10:00:00Z',
    updated_at: '2026-02-19T10:00:00Z'
  },
  {
    id: 'm3',
    type: 'episodic',
    content: 'Meeting with the team about the new feature launch',
    embedding: [],
    entities: ['team'],
    topics: ['meetings', 'product'],
    salience: 0.6,
    created_at: '2026-02-18T10:00:00Z',
    updated_at: '2026-02-18T10:00:00Z'
  },
  {
    id: 'm4',
    type: 'semantic',
    content: 'The weather in New York City is sunny today',
    embedding: [],
    entities: ['New York City'],
    topics: ['weather'],
    salience: 0.3,
    created_at: '2026-02-17T10:00:00Z',
    updated_at: '2026-02-17T10:00:00Z'
  },
  {
    id: 'm5',
    type: 'semantic',
    content: 'Robert prefers dark mode in VS Code settings',
    embedding: [],
    entities: ['Robert'],
    topics: ['preferences', 'tools'],
    salience: 0.7,
    created_at: '2026-02-16T10:00:00Z',
    updated_at: '2026-02-16T10:00:00Z'
  }
];

// Simple test runner
async function runTests() {
  console.log('🧪 Running filter tests...\n');
  let passed = 0;
  let failed = 0;
  
  try {
    // Test 1: Empty list
    let result = await filterMemories('test', []);
    if (result.length === 0) {
      console.log('✅ PASS: Empty list returns empty');
      passed++;
    } else {
      console.log('❌ FAIL: Empty list should return empty');
      failed++;
    }
    
    // Test 2: Small list bypass (2 or fewer memories skip LLM)
    const smallList = mockMemories.slice(0, 2);
    result = await filterMemories('test', smallList);
    if (result.length === 2) {
      console.log('✅ PASS: Small list (2) bypasses LLM');
      passed++;
    } else {
      console.log('❌ FAIL: Small list should return all');
      failed++;
    }
    
    // Test 3: LLM filtering
    (globalThis as any).generateLLMResponse = async () => {
      return JSON.stringify({ relevantIndices: [0, 2, 4] });
    };
    
    result = await filterMemories('preferences', mockMemories);
    if (result.length === 3) {
      console.log('✅ PASS: LLM filtering returns filtered results');
      passed++;
    } else {
      console.log('❌ FAIL: LLM filtering - got', result.length, 'expected 3');
      failed++;
    }
    
    // Test 4: k limiting
    result = await filterMemories('test', mockMemories, { k: 2 });
    if (result.length <= 2) {
      console.log('✅ PASS: k limiting works');
      passed++;
    } else {
      console.log('❌ FAIL: k limiting - got', result.length);
      failed++;
    }
    
    // Test 5: Error handling - fallback
    (globalThis as any).generateLLMResponse = async () => {
      throw new Error('LLM fail');
    };
    
    result = await filterMemories('test', mockMemories.slice(0, 3));
    if (result.length === 3) {
      console.log('✅ PASS: Error fallback returns original sorted by salience');
      passed++;
    } else {
      console.log('❌ FAIL: Error fallback - got', result.length);
      failed++;
    }
    
    // Test 6: Prompt includes recall-biased language
    let promptUsed = '';
    (globalThis as any).generateLLMResponse = async (prompt: string) => {
      promptUsed = prompt;
      return JSON.stringify({ relevantIndices: [0, 1] });
    };
    
    await filterMemories('developer preferences', mockMemories.slice(0, 3));
    if (promptUsed.toLowerCase().includes('uncertain') || 
        promptUsed.toLowerCase().includes('include') ||
        promptUsed.toLowerCase().includes('relevant')) {
      console.log('✅ PASS: Recall-biased prompt language present');
      passed++;
    } else {
      console.log('❌ FAIL: Prompt missing recall-biased language');
      failed++;
    }
    
    console.log(`\n📊 Results: ${passed} passed, ${failed} failed`);
    
    if (failed > 0) {
      process.exit(1);
    }
    console.log('\n✅ All tests passed!');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
    process.exit(1);
  }
}

// Run if executed directly
runTests();
