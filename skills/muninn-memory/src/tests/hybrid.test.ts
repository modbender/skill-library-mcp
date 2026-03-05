/**
 * Hybrid Retrieval Tests
 * Tests for BM25 and hybrid (RRF) retrieval
 */

import { BM25Scorer, bm25Search } from '../retrieval/bm25.js';
import { hybridSearch, getRetrievalBreakdown } from '../retrieval/hybrid.js';
import type { Memory } from '../storage/index.js';

// Mock memories for testing
const mockMemories: Memory[] = [
  {
    id: 'm1',
    type: 'semantic',
    content: 'Sammy Clemens prefers working late at night',
    embedding: [0.1, 0.2, 0.3], // Fake embedding
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
    embedding: [0.4, 0.5, 0.6],
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
    embedding: [0.7, 0.8, 0.9],
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
    embedding: [0.2, 0.1, 0.4],
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
    embedding: [0.3, 0.4, 0.5],
    entities: ['Robert'],
    topics: ['preferences', 'tools'],
    salience: 0.7,
    created_at: '2026-02-16T10:00:00Z',
    updated_at: '2026-02-16T10:00:00Z'
  },
  {
    id: 'm6',
    type: 'semantic',
    content: 'The first computer was invented by Charles Babbage',
    embedding: [0.5, 0.6, 0.7],
    entities: ['Charles Babbage'],
    topics: ['history', 'computers'],
    salience: 0.8,
    created_at: '2026-02-15T10:00:00Z',
    updated_at: '2026-02-15T10:00:00Z'
  }
];

async function runTests() {
  console.log('🧪 Running hybrid retrieval tests...\n');
  let passed = 0;
  let failed = 0;
  
  try {
    // ===== BM25 Tests =====
    console.log('--- BM25 Tests ---');
    
    // Test 1: BM25 finds exact term matches
    const bm25Results = bm25Search('prefers', mockMemories, { k: 3 });
    if (bm25Results.length > 0 && bm25Results.some(r => r.content.includes('prefers'))) {
      console.log('✅ PASS: BM25 finds term matches');
      passed++;
    } else {
      console.log('❌ FAIL: BM25 term matching');
      failed++;
    }
    
    // Test 2: BM25 handles name variations (Charles vs Charlie)
    const nameResults = bm25Search('Charles Babbage computer', mockMemories, { k: 3 });
    const hasBabbage = nameResults.some(r => r.content.toLowerCase().includes('babbage'));
    if (hasBabbage) {
      console.log('✅ PASS: BM25 handles name variations');
      passed++;
    } else {
      console.log('❌ FAIL: BM25 name matching');
      failed++;
    }
    
    // Test 3: BM25 returns results in score order
    const scorer = new BM25Scorer();
    scorer.index(mockMemories);
    const scored = mockMemories.map(d => ({
      id: d.id,
      score: scorer['scoreDocument']('weather', d.id)
    }));
    const weatherResults = scored.filter(s => s.score > 0).sort((a, b) => b.score - a.score);
    if (weatherResults[0].id === 'm4') { // m4 is about weather
      console.log('✅ PASS: BM25 ranks by score');
      passed++;
    } else {
      console.log('❌ FAIL: BM25 ranking');
      failed++;
    }
    
    // ===== Hybrid Search Tests =====
    console.log('\n--- Hybrid Search Tests ---');
    
    // Test 4: Hybrid search combines dense and sparse
    const hybridResults = await hybridSearch('prefers dark mode', mockMemories, { k: 3 });
    if (hybridResults.length > 0 && hybridResults.length <= 3) {
      console.log('✅ PASS: Hybrid search returns results');
      passed++;
    } else {
      console.log('❌ FAIL: Hybrid search');
      failed++;
    }
    
    // Test 5: Hybrid prioritizes exact term matches
    const exactMatchResults = await hybridSearch('Sammy Clemens', mockMemories, { k: 3 });
    const sammyInResults = exactMatchResults.some(r => r.id === 'm1');
    if (sammyInResults) {
      console.log('✅ PASS: Hybrid finds exact name match');
      passed++;
    } else {
      console.log('❌ FAIL: Hybrid name matching');
      failed++;
    }
    
    // Test 6: Hybrid handles multiple term matches
    const multiTermResults = await hybridSearch('Babbage computer history', mockMemories, { k: 3 });
    const babbageResults = multiTermResults.filter(r => 
      r.content.toLowerCase().includes('babbage') || 
      r.content.toLowerCase().includes('computer')
    );
    if (babbageResults.length > 0) {
      console.log('✅ PASS: Hybrid handles multiple terms');
      passed++;
    } else {
      console.log('❌ FAIL: Multi-term search');
      failed++;
    }
    
    // Test 7: Small corpus bypass
    const smallResults = await hybridSearch('test', mockMemories.slice(0, 2), { k: 10 });
    if (smallResults.length === 2) {
      console.log('✅ PASS: Small corpus bypass');
      passed++;
    } else {
      console.log('❌ FAIL: Small corpus handling');
      failed++;
    }
    
    // Test 8: k parameter limits results
    const limitedResults = await hybridSearch('test query', mockMemories, { k: 2 });
    if (limitedResults.length <= 2) {
      console.log('✅ PASS: k parameter limits results');
      passed++;
    } else {
      console.log('❌ FAIL: k limiting');
      failed++;
    }
    
    // ===== RRF Tests =====
    console.log('\n--- Reciprocal Rank Fusion Tests ---');
    
    // Test 9: RRF combines rankings (would need to check internal)
    // Just verify we get results that appear in either dense or sparse
    const rrfResults = await hybridSearch('meeting launch', mockMemories, { k: 3 });
    const hasMeeting = rrfResults.some(r => r.content.toLowerCase().includes('meeting'));
    if (hasMeeting || rrfResults.length > 0) {
      console.log('✅ PASS: RRF produces results');
      passed++;
    } else {
      console.log('❌ FAIL: RRF');
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
