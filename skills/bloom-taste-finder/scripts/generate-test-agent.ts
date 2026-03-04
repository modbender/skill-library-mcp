/**
 * Generate a test agent for testing purposes
 */

import 'dotenv/config';
import { BloomIdentitySkillV2, ExecutionMode } from '../src/bloom-identity-skill-v2';

async function main() {
  console.log('🧪 Generating test agent identity...\n');

  const skill = new BloomIdentitySkillV2();

  // Provide manual answers simulating an AI/Crypto enthusiast (The Innovator personality)
  const manualAnswers = [
    {
      question: "What's been taking most of your attention lately?",
      answer: "Exploring or building new AI tools",
    },
    {
      question: "What kind of content naturally pulls you in?",
      answer: "Fresh AI/tool demos",
    },
    {
      question: "When you support an early-stage project, which role feels most like you?",
      answer: "The first to try new tech",
    },
    {
      question: "If you had to pick one theme to go deep on first, what would it be?",
      answer: "AI Tools / New Tech",
    },
  ];

  const result = await skill.execute('test-user-bloom-protocol', {
    mode: ExecutionMode.MANUAL,
    skipShare: true,
    manualAnswers,
  });

  if (result.success) {
    console.log('\n✅ Test Agent Generated Successfully!\n');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    console.log(`🎴 Personality: ${result.identityData?.personalityType}`);
    console.log(`💬 Tagline: "${result.identityData?.customTagline}"\n`);
    console.log(`📊 Categories: ${result.identityData?.mainCategories.join(', ')}`);
    console.log(`🔢 Agent Wallet: ${result.agentWallet?.address || 'N/A'}\n`);

    if (result.dashboardUrl) {
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
      console.log('🔗 Public Dashboard URL:\n');
      console.log(`   ${result.dashboardUrl}\n`);
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
      console.log('✨ Use this URL to test:');
      console.log('   - Save card functionality');
      console.log('   - OG image generation');
      console.log('   - Twitter/X sharing\n');

      // Extract agent user ID from URL
      const match = result.dashboardUrl.match(/\/agents\/(\d+)/);
      if (match) {
        const agentUserId = match[1];
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
        console.log('🖼️  OG Image URL:\n');
        console.log(`   ${result.dashboardUrl.replace(/\/agents\/\d+/, '')}/api/og/agent/${agentUserId}\n`);
      }
    }

    if (result.recommendations && result.recommendations.length > 0) {
      console.log(`🎯 Recommendations: ${result.recommendations.length} skills found\n`);
    }
  } else {
    console.error('\n❌ Failed to generate test agent:');
    console.error(result.error || 'Unknown error');
    process.exit(1);
  }
}

main().catch(console.error);
