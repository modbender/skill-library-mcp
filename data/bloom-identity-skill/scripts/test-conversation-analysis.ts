/**
 * Test Script: Conversation Analysis
 *
 * Tests the complete flow:
 * 1. Read OpenClaw session history
 * 2. Analyze personality using 2x2 metrics
 * 3. Detect actual interests from conversation
 * 4. Generate recommendations based on personality + interests
 */

import dotenv from 'dotenv';
import path from 'path';

// Explicitly load .env from project root (works with ts-node)
dotenv.config({ path: path.join(__dirname, '..', '.env') });

import { OpenClawSessionReader } from '../src/integrations/openclaw-session-reader';
import { EnhancedDataCollector } from '../src/analyzers/data-collector-enhanced';
import { PersonalityAnalyzer } from '../src/analyzers/personality-analyzer';

async function testConversationAnalysis() {
  console.log('🧪 Testing Conversation Analysis Flow\n');
  console.log('━'.repeat(60));

  // Test with a user ID (replace with actual user ID)
  const testUserId = 'test-user-123';

  try {
    // Step 1: Read session history
    console.log('\n📖 STEP 1: Reading Session History');
    console.log('━'.repeat(60));

    const sessionReader = new OpenClawSessionReader();
    const conversationAnalysis = await sessionReader.readSessionHistory(testUserId);

    console.log(`\n✅ Session Analysis Complete:`);
    console.log(`   Messages: ${conversationAnalysis.messageCount}`);
    console.log(`   Topics: ${conversationAnalysis.topics.join(', ') || '(none)'}`);
    console.log(`   Interests: ${conversationAnalysis.interests.slice(0, 5).join(', ') || '(none)'}`);
    console.log(`   Preferences: ${conversationAnalysis.preferences.join(', ') || '(none)'}`);
    console.log(`\n   Recent History:`);
    conversationAnalysis.history.slice(0, 3).forEach(h => {
      console.log(`   - ${h.slice(0, 100)}...`);
    });

    // Step 2: Collect all user data (including conversation)
    console.log('\n\n📊 STEP 2: Collecting User Data');
    console.log('━'.repeat(60));

    const dataCollector = new EnhancedDataCollector();
    const userData = await dataCollector.collect(testUserId, {
      skipTwitter: true,   // Skip for testing
      skipWallet: true,    // Skip for testing
      skipFarcaster: true, // Skip for testing
    });

    console.log(`\n✅ Data Collection Complete:`);
    console.log(`   Sources: ${userData.sources.join(', ')}`);
    console.log(`   Data Quality: ${dataCollector.getDataQualityScore(userData)}%`);

    if (userData.conversationMemory) {
      console.log(`\n   Conversation Memory:`);
      console.log(`   - Topics: ${userData.conversationMemory.topics.join(', ') || '(none)'}`);
      console.log(`   - Interests: ${userData.conversationMemory.interests.slice(0, 5).join(', ') || '(none)'}`);
      console.log(`   - Preferences: ${userData.conversationMemory.preferences.join(', ') || '(none)'}`);
    }

    // Step 3: Analyze personality using 2x2 metrics
    console.log('\n\n🤖 STEP 3: Analyzing Personality');
    console.log('━'.repeat(60));

    const personalityAnalyzer = new PersonalityAnalyzer();
    const analysis = await personalityAnalyzer.analyze(userData);

    console.log(`\n✅ Personality Analysis Complete:`);
    console.log(`\n   Type: ${analysis.personalityType}`);
    console.log(`   Tagline: "${analysis.tagline}"`);
    console.log(`\n   2x2 Dimensions:`);
    console.log(`   - Conviction: ${analysis.dimensions.conviction}/100`);
    console.log(`   - Intuition: ${analysis.dimensions.intuition}/100`);
    console.log(`   - Contribution: ${analysis.dimensions.contribution}/100`);
    console.log(`\n   Detected Categories (from conversation):`);
    console.log(`   - Main: ${analysis.detectedCategories.join(', ')}`);
    console.log(`   - Interests: ${analysis.detectedInterests.slice(0, 5).join(', ')}`);
    console.log(`\n   Description:`);
    console.log(`   ${analysis.description}`);
    console.log(`\n   Confidence: ${analysis.confidence}%`);

    // Step 4: Show recommendation logic
    console.log('\n\n🎯 STEP 4: Recommendation Logic');
    console.log('━'.repeat(60));

    console.log(`\n   Recommendation will be based on:`);
    console.log(`   1. Main Categories (what they like): ${analysis.detectedCategories.join(', ')}`);
    console.log(`   2. Personality Type (how they approach): ${analysis.personalityType}`);
    console.log(`   3. Sub-interests: ${analysis.detectedInterests.slice(0, 5).join(', ')}`);

    console.log('\n\n✅ Test Complete!');
    console.log('━'.repeat(60));
    console.log('\n✨ Summary:');
    console.log('   - Session reading: ✅ Working');
    console.log('   - Conversation analysis: ✅ Working');
    console.log('   - Personality detection: ✅ Working');
    console.log('   - Interest detection: ✅ Working');
    console.log('   - Recommendation data: ✅ Ready\n');

  } catch (error) {
    console.error('\n❌ Test Failed:', error);
    if (error instanceof Error) {
      console.error('\nStack trace:', error.stack);
    }
    process.exit(1);
  }
}

// Run test
testConversationAnalysis();
