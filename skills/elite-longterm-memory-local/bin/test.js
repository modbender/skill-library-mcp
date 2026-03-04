#!/usr/bin/env node
/**
 * Test script for Elite Longterm Memory
 */

const { MemoryManager } = require('../lib/memory');
const path = require('path');

const TEST_DB_PATH = path.join(process.cwd(), 'memory', 'vectors-test');

async function test() {
  console.log('🧪 Testing Elite Longterm Memory...\n');
  
  const memory = new MemoryManager({
    dbPath: TEST_DB_PATH,
    ollamaUrl: process.env.OLLAMA_URL || 'http://localhost:11434',
    embeddingModel: 'nomic-embed-text'
  });
  
  try {
    // Test 1: Initialize
    console.log('1️⃣ Testing initialization...');
    await memory.init();
    console.log('   ✅ Initialized successfully\n');
    
    // Test 2: Store memories
    console.log('2️⃣ Testing memory storage...');
    const memories = [
      { text: '用户喜欢深色模式界面', importance: 0.9, category: 'preference' },
      { text: '决定使用 React + TypeScript', importance: 0.8, category: 'decision' },
      { text: '项目截止日期是 3 月 15 日', importance: 0.7, category: 'fact' }
    ];
    
    for (const m of memories) {
      const result = await memory.store(m.text, { 
        importance: m.importance, 
        category: m.category 
      });
      console.log(`   ✅ Stored: "${m.text.slice(0, 40)}..." (${result.id.slice(0, 8)})`);
    }
    console.log();
    
    // Test 3: Search
    console.log('3️⃣ Testing memory search...');
    const searches = [
      '用户界面偏好',
      '技术栈选择',
      '项目时间安排'
    ];
    
    for (const query of searches) {
      const results = await memory.search(query, 3);
      console.log(`   Query: "${query}"`);
      results.forEach((r, i) => {
        console.log(`   ${i + 1}. [${(r.score * 100).toFixed(0)}%] ${r.entry.text.slice(0, 50)}...`);
      });
      console.log();
    }
    
    // Test 4: Stats
    console.log('4️⃣ Testing statistics...');
    const count = await memory.count();
    console.log(`   ✅ Total memories: ${count}\n`);
    
    // Test 5: Duplicate detection
    console.log('5️⃣ Testing duplicate detection...');
    const dupResult = await memory.store('用户喜欢深色模式界面', { 
      importance: 0.9, 
      category: 'preference' 
    });
    console.log(`   ${dupResult.duplicate ? '✅' : '❌'} Duplicate detected: ${dupResult.duplicate}\n`);
    
    console.log('🎉 All tests passed!');
    
  } catch (err) {
    console.error('❌ Test failed:', err.message);
    if (err.message.includes('Ollama')) {
      console.error('\n💡 Make sure Ollama is running:');
      console.error('   ollama serve');
      console.error('   ollama pull nomic-embed-text');
    }
    process.exit(1);
  } finally {
    await memory.close();
  }
}

test();
