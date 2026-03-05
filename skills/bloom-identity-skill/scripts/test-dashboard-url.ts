#!/usr/bin/env tsx
/**
 * Test Dashboard URL Generation
 *
 * Tests that the new /dashboard?token=xxx URL is correctly generated
 */

import 'dotenv/config';
import { BloomIdentitySkillV2 } from '../src/bloom-identity-skill-v2';

async function testDashboardUrl() {
  console.log('🧪 Testing Dashboard URL Generation\n');
  console.log('━'.repeat(60));
  console.log('📋 STEP 1: Initialize Skill');
  console.log('━'.repeat(60));

  const skill = new BloomIdentitySkillV2();
  console.log('✅ Skill initialized\n');

  console.log('━'.repeat(60));
  console.log('🎴 STEP 2: Generate Identity with Manual Mode');
  console.log('━'.repeat(60));

  const testUserId = `test-dashboard-${Date.now()}`;
  console.log(`User ID: ${testUserId}\n`);

  try {
    // Step 2a: First call - get questions
    console.log('📝 Step 2a: Getting manual questions...\n');
    const firstResult = await skill.execute({
      userId: testUserId,
      mode: 'manual',
      skipShare: true,
    });

    if (!firstResult.needsManualInput) {
      console.error('❌ Expected manual input request');
      return;
    }

    console.log('✅ Manual questions received\n');

    // Step 2b: Second call - provide answers
    console.log('📝 Step 2b: Providing answers...\n');
    const manualAnswers = {
      '1': '1', // AI Tools focus
      '2': '1', // AI/tool demos
      '3': '1', // First to try new tech
      '4': '1', // AI Tools / New Tech
    };

    const result = await skill.execute({
      userId: testUserId,
      mode: 'manual',
      manualAnswers,
      skipShare: true,
    });

    if (!result.success) {
      console.error('❌ Identity generation failed:', result);
      return;
    }

    console.log('\n' + '━'.repeat(60));
    console.log('📊 RESULTS');
    console.log('━'.repeat(60));
    console.log('\n✅ SUCCESS!\n');

    console.log('🎴 Identity Data:');
    console.log(`   Personality: ${result.identityData?.personalityType}`);
    console.log(`   Tagline: ${result.identityData?.customTagline}`);
    console.log(`   Categories: ${result.identityData?.mainCategories.join(', ')}`);

    console.log('\n🔗 Dashboard URL:');
    console.log(`   ${result.dashboardUrl}\n`);

    // Check if URL has token
    if (result.dashboardUrl?.includes('/dashboard?token=')) {
      console.log('✅ URL Format: Correct (/dashboard?token=xxx)');

      // Extract token
      const url = new URL(result.dashboardUrl);
      const token = url.searchParams.get('token');
      if (token) {
        console.log(`✅ Token Found: ${token.substring(0, 20)}...`);
        console.log(`✅ Token Length: ${token.length} characters`);
      }
    } else if (result.dashboardUrl?.includes('/agents/')) {
      console.log('❌ URL Format: OLD format (/agents/xxx)');
      console.log('   Expected: /dashboard?token=xxx');
    } else {
      console.log('⚠️  Unexpected URL format');
    }

    console.log('\n🧪 Test: Visit this URL to verify authentication:');
    console.log(`   ${result.dashboardUrl}`);
    console.log('   Expected: Should see your card in dashboard carousel\n');

  } catch (error) {
    console.error('\n❌ FAILED\n');
    console.error('Error:', error instanceof Error ? error.message : error);
    if (error instanceof Error && error.stack) {
      console.error('\nStack trace:', error.stack);
    }
  }

  console.log('\n' + '━'.repeat(60));
  console.log('✨ Test Complete');
  console.log('━'.repeat(60));
}

testDashboardUrl().catch(console.error);
