import { ContextStorage } from './src/storage.js';
import { join } from 'path';
import { homedir } from 'os';

/**
 * Test script to verify ContextStorage functionality
 */

async function testStorage() {
  console.log('\n🧪 Testing ContextStorage class...\n');

  const dataDir = join(homedir(), '.openclaw', 'openclaw-context-optimizer');
  const dbPath = join(dataDir, 'context-optimizer.db');

  const storage = new ContextStorage(dbPath);

  try {
    // Test 1: Record a compression session
    console.log('1️⃣ Testing recordCompressionSession...');
    const sessionData = {
      session_id: 'test-session-001',
      agent_wallet: '0x1234567890abcdef',
      original_tokens: 5000,
      compressed_tokens: 2000,
      compression_ratio: 0.4,
      tokens_saved: 3000,
      cost_saved_usd: 0.015,
      strategy_used: 'hybrid',
      quality_score: 0.95,
      original_context: 'Original long context...',
      compressed_context: 'Compressed context...'
    };

    storage.recordCompressionSession(sessionData);
    console.log('   ✅ Session recorded');

    // Test 2: Get compression stats
    console.log('\n2️⃣ Testing getCompressionStats...');
    const stats = storage.getCompressionStats('0x1234567890abcdef', '30 days');
    console.log('   Stats:', JSON.stringify(stats, null, 2));
    console.log('   ✅ Stats retrieved');

    // Test 3: Update token statistics
    console.log('\n3️⃣ Testing updateTokenStats...');
    storage.updateTokenStats('0x1234567890abcdef', 5000, 2000, 0.015);
    console.log('   ✅ Token stats updated');

    // Test 4: Record a pattern
    console.log('\n4️⃣ Testing recordPattern...');
    storage.recordPattern({
      pattern_id: 'pattern-001',
      agent_wallet: '0x1234567890abcdef',
      pattern_type: 'redundant',
      pattern_text: 'Repeated boilerplate text',
      frequency: 1,
      token_impact: -50,
      importance_score: 0.3
    });
    console.log('   ✅ Pattern recorded');

    // Test 5: Get patterns
    console.log('\n5️⃣ Testing getPatterns...');
    const patterns = storage.getPatterns('0x1234567890abcdef');
    console.log('   Patterns count:', patterns.length);
    console.log('   ✅ Patterns retrieved');

    // Test 6: Check quota
    console.log('\n6️⃣ Testing checkQuotaAvailable...');
    const quotaCheck = storage.checkQuotaAvailable('0x1234567890abcdef');
    console.log('   Quota:', JSON.stringify(quotaCheck, null, 2));
    console.log('   ✅ Quota checked');

    // Test 7: Increment compression count
    console.log('\n7️⃣ Testing incrementCompressionCount...');
    storage.incrementCompressionCount('0x1234567890abcdef');
    const updatedQuota = storage.checkQuotaAvailable('0x1234567890abcdef');
    console.log('   Updated quota:', JSON.stringify(updatedQuota, null, 2));
    console.log('   ✅ Compression count incremented');

    // Test 8: Record payment request
    console.log('\n8️⃣ Testing recordPaymentRequest...');
    storage.recordPaymentRequest('req-001', '0x1234567890abcdef', 0.5, 'USDT');
    console.log('   ✅ Payment request recorded');

    // Test 9: Get payment request
    console.log('\n9️⃣ Testing getPaymentRequest...');
    const paymentReq = storage.getPaymentRequest('req-001');
    console.log('   Payment request:', JSON.stringify(paymentReq, null, 2));
    console.log('   ✅ Payment request retrieved');

    // Test 10: Record feedback
    console.log('\n🔟 Testing recordFeedback...');
    storage.recordFeedback('test-session-001', 'success', 0.95, 'Excellent compression quality');
    console.log('   ✅ Feedback recorded');

    // Test 11: Get feedback
    console.log('\n1️⃣1️⃣ Testing getFeedback...');
    const feedback = storage.getFeedback('test-session-001');
    console.log('   Feedback count:', feedback.length);
    console.log('   ✅ Feedback retrieved');

    // Test 12: Get strategy stats
    console.log('\n1️⃣2️⃣ Testing getStrategyStats...');
    const strategyStats = storage.getStrategyStats('0x1234567890abcdef', '30 days');
    console.log('   Strategy stats:', JSON.stringify(strategyStats, null, 2));
    console.log('   ✅ Strategy stats retrieved');

    console.log('\n✅ All tests passed!\n');

  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  } finally {
    storage.close();
  }
}

// Run tests
testStorage().catch(error => {
  console.error('Test error:', error);
  process.exit(1);
});
