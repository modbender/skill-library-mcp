#!/usr/bin/env node

/**
 * Test script for SQ Memory skill
 * 
 * Tests both local and cloud endpoints
 * 
 * Usage:
 *   node test.js                          # Test with default config
 *   node test.js http://localhost:1337    # Test specific endpoint
 */

const SQMemory = require('./index.js');

// Test configuration
const config = {
  endpoint: process.argv[2] || process.env.SQ_ENDPOINT || 'http://localhost:1337',
  api_key: process.env.SQ_API_KEY || '',
  namespace: 'test-agent'
};

console.log(`\n🔱 Testing SQ Memory Skill`);
console.log(`📍 Endpoint: ${config.endpoint}`);
console.log(`🏷️  Namespace: ${config.namespace}\n`);

async function runTests() {
  try {
    // Initialize skill
    console.log('1️⃣  Initializing skill...');
    const { tools } = await SQMemory.init(config);
    const { remember, recall, forget, list_memories } = tools;
    console.log('✅ Skill initialized\n');
    
    // Test 1: Basic remember/recall
    console.log('2️⃣  Test: Basic remember/recall');
    const testKey = 'test/basic';
    const testValue = 'Hello from SQ!';
    
    await remember(testKey, testValue);
    console.log(`   📝 Stored: "${testValue}" at ${testKey}`);
    
    const recalled = await recall(testKey);
    if (recalled === testValue) {
      console.log(`   ✅ Recalled correctly: "${recalled}"`);
    } else {
      throw new Error(`Recall mismatch: expected "${testValue}", got "${recalled}"`);
    }
    console.log('');
    
    // Test 2: Update (overwrite)
    console.log('3️⃣  Test: Update existing memory');
    const updatedValue = 'Updated value!';
    await remember(testKey, updatedValue);
    console.log(`   📝 Updated: "${updatedValue}" at ${testKey}`);
    
    const recalledUpdated = await recall(testKey);
    if (recalledUpdated === updatedValue) {
      console.log(`   ✅ Update successful: "${recalledUpdated}"`);
    } else {
      throw new Error(`Update failed: expected "${updatedValue}", got "${recalledUpdated}"`);
    }
    console.log('');
    
    // Test 3: Multiple memories
    console.log('4️⃣  Test: Multiple memories');
    await remember('test/multi/item1', 'First item');
    await remember('test/multi/item2', 'Second item');
    await remember('test/multi/item3', 'Third item');
    console.log(`   📝 Stored 3 items under test/multi/`);
    
    const item1 = await recall('test/multi/item1');
    const item2 = await recall('test/multi/item2');
    const item3 = await recall('test/multi/item3');
    
    if (item1 === 'First item' && item2 === 'Second item' && item3 === 'Third item') {
      console.log(`   ✅ All items recalled correctly`);
    } else {
      throw new Error('Multi-item recall failed');
    }
    console.log('');
    
    // Test 4: List memories
    console.log('5️⃣  Test: List memories');
    const listed = await list_memories('test/multi/');
    console.log(`   📋 Found ${listed.length} memories under test/multi/`);
    
    if (listed.length >= 3) {
      console.log(`   ✅ List working: ${listed.join(', ')}`);
    } else {
      throw new Error(`List failed: expected 3+, got ${listed.length}`);
    }
    console.log('');
    
    // Test 5: Forget (delete)
    console.log('6️⃣  Test: Forget (delete)');
    await forget('test/multi/item2');
    console.log(`   🗑️  Deleted test/multi/item2`);
    
    const deletedRecall = await recall('test/multi/item2');
    if (deletedRecall === null) {
      console.log(`   ✅ Delete successful (recall returned null)`);
    } else {
      throw new Error(`Delete failed: item still exists`);
    }
    console.log('');
    
    // Test 6: JSON storage
    console.log('7️⃣  Test: JSON storage');
    const jsonData = {
      name: 'Alice',
      preferences: {
        theme: 'dark',
        language: 'en'
      },
      timestamp: Date.now()
    };
    
    await remember('test/json/data', JSON.stringify(jsonData));
    console.log(`   📝 Stored JSON object`);
    
    const jsonRecalled = await recall('test/json/data');
    const parsed = JSON.parse(jsonRecalled);
    
    if (parsed.name === 'Alice' && parsed.preferences.theme === 'dark') {
      console.log(`   ✅ JSON round-trip successful`);
    } else {
      throw new Error('JSON parsing failed');
    }
    console.log('');
    
    // Test 7: Large text
    console.log('8️⃣  Test: Large text storage');
    const largeText = 'A'.repeat(10000); // 10KB
    await remember('test/large', largeText);
    console.log(`   📝 Stored 10KB of text`);
    
    const largeRecalled = await recall('test/large');
    if (largeRecalled.length === 10000) {
      console.log(`   ✅ Large text stored/recalled successfully`);
    } else {
      throw new Error(`Large text size mismatch: ${largeRecalled.length}`);
    }
    console.log('');
    
    // Test 8: Non-existent key
    console.log('9️⃣  Test: Recall non-existent key');
    const missing = await recall('test/does-not-exist');
    if (missing === null) {
      console.log(`   ✅ Returns null for missing key`);
    } else {
      throw new Error(`Expected null, got "${missing}"`);
    }
    console.log('');
    
    // Cleanup
    console.log('🧹 Cleaning up test data...');
    await forget('test/basic');
    await forget('test/multi/item1');
    await forget('test/multi/item3');
    await forget('test/json/data');
    await forget('test/large');
    console.log('   ✅ Cleanup complete\n');
    
    console.log('✅ ALL TESTS PASSED! 🎉\n');
    console.log('The SQ Memory skill is working correctly.');
    console.log('You can now use it in your OpenClaw agents.\n');
    
  } catch (err) {
    console.error(`\n❌ TEST FAILED: ${err.message}`);
    console.error(err.stack);
    process.exit(1);
  }
}

// Run tests
runTests().catch(err => {
  console.error(`Fatal error: ${err.message}`);
  process.exit(1);
});
