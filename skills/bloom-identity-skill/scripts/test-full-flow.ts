/**
 * Complete Flow Test
 *
 * Tests the full identity generation flow:
 * 1. Data collection (conversation + Twitter)
 * 2. Personality analysis
 * 3. ClawHub skill recommendations
 * 4. Wallet creation
 * 5. Backend registration
 * 6. Dashboard URL generation
 */

import * as dotenv from 'dotenv';
import { BloomIdentitySkillV2 } from '../src/bloom-identity-skill-v2';

// Load environment variables
dotenv.config();

async function testFullFlow() {
  console.log('🧪 Testing Complete Bloom Identity Flow\n');
  console.log('━'.repeat(60));
  console.log('📋 STEP 1: Initialize Skill');
  console.log('━'.repeat(60));

  const skill = new BloomIdentitySkillV2();
  console.log('✅ Skill initialized\n');

  console.log('━'.repeat(60));
  console.log('🎴 STEP 2: Generate Identity');
  console.log('━'.repeat(60));

  // Test with a mock user ID
  const testUserId = `test-user-${Date.now()}`;
  console.log(`User ID: ${testUserId}\n`);

  // First attempt — will likely need manual Q&A for test users with no history
  let result = await skill.execute(testUserId, {
    skipShare: true,
  });

  // If manual input required, provide test answers and retry
  if (!result.success && result.needsManualInput) {
    console.log('📝 No conversation history — providing Q&A answers...\n');
    result = await skill.execute(testUserId, {
      skipShare: true,
      manualAnswers: [
        { questionIndex: 0, answerIndex: 0 }, // Exploring or building new AI tools
        { questionIndex: 1, answerIndex: 0 }, // Fresh AI/tool demos
        { questionIndex: 2, answerIndex: 0 }, // The first to try new tech
        { questionIndex: 3, answerIndex: 0 }, // AI Tools / New Tech
      ],
    });
  }

  console.log('━'.repeat(60));
  console.log('📊 RESULTS');
  console.log('━'.repeat(60));

  if (result.success) {
    console.log('\n✅ SUCCESS!\n');

    console.log('🎭 Identity Data:');
    console.log(`   Type: ${result.identityData?.personalityType}`);
    console.log(`   Tagline: ${result.identityData?.customTagline}`);
    console.log(`   Description: ${result.identityData?.customDescription}`);
    console.log(`   Main Categories: ${result.identityData?.mainCategories.join(', ')}`);
    console.log(`   Sub Categories: ${result.identityData?.subCategories.join(', ')}`);

    if (result.dimensions) {
      console.log('\n📊 2x2 Metrics:');
      console.log(`   Conviction: ${result.dimensions.conviction}/100`);
      console.log(`   Intuition: ${result.dimensions.intuition}/100`);
      console.log(`   Contribution: ${result.dimensions.contribution}/100`);
    }

    console.log('\n💰 Wallet:');
    console.log(`   Address: ${result.agentWallet?.address}`);
    console.log(`   Network: ${result.agentWallet?.network}`);
    console.log(`   X402 Endpoint: ${result.agentWallet?.x402Endpoint}`);

    console.log('\n🎯 Skill Recommendations:');
    if (result.recommendations && result.recommendations.length > 0) {
      result.recommendations.slice(0, 5).forEach((skill, i) => {
        console.log(`   ${i + 1}. ${skill.skillName} (${skill.matchScore}% match)`);
        console.log(`      ${skill.description}`);
        console.log(`      URL: ${skill.url}`);
        console.log(`      Creator: ${skill.creator || 'Unknown'}`);
        console.log('');
      });
    } else {
      console.log('   ⚠️  No recommendations found');
    }

    console.log('🔗 Dashboard:');
    console.log(`   URL: ${result.dashboardUrl || 'Not generated'}`);

    if (result.actions?.save) {
      console.log('\n💾 Save Actions:');
      console.log(`   Register: ${result.actions.save.registerUrl}`);
      console.log(`   Login: ${result.actions.save.loginUrl}`);
    }

    console.log('\n📈 Quality:');
    console.log(`   Mode: ${result.mode}`);
    console.log(`   Data Quality: ${result.dataQuality}%`);

  } else {
    console.log('\n❌ FAILED\n');
    console.log(`Error: ${result.error}`);

    if (result.needsManualInput) {
      console.log('\nℹ️  Manual input required:');
      console.log(result.manualQuestions);
    }
  }

  console.log('\n' + '━'.repeat(60));
  console.log('✨ Test Complete');
  console.log('━'.repeat(60));
}

// Run test
testFullFlow().catch(error => {
  console.error('\n❌ Test failed:', error);
  process.exit(1);
});
