// Test credit score with simulated activity
const AgentGuard = require('./src/index');

async function testCreditScore() {
  const guard = new AgentGuard({
    masterPassword: 'nano-test-password'
  });

  await guard.init();

  console.log('\n🧪 Testing Credit Score System\n');

  // Simulate some activity
  console.log('1. Simulating agent activity...');

  // Log some successful operations
  for (let i = 0; i < 5; i++) {
    await guard.audit.log('nano', 'operation_executed', { success: true, operation: 'api_call' });
  }

  // Log some credential accesses
  for (let i = 0; i < 3; i++) {
    await guard.audit.log('nano', 'credential_accessed', { key: 'OPENAI_API_KEY' });
  }

  // Log some dangerous operations
  for (let i = 0; i < 2; i++) {
    await guard.audit.log('nano', 'permission_check', {
      operation: 'send_email',
      result: { requiresApproval: true }
    });
  }

  // Log an approval
  await guard.audit.log('nano', 'approval_result', {
    operation: 'send_email',
    approved: true
  });

  console.log('   ✓ 5 successful operations');
  console.log('   ✓ 3 credential accesses');
  console.log('   ✓ 2 dangerous operation checks');
  console.log('   ✓ 1 approval granted');

  // Calculate score
  console.log('\n2. Calculating credit score...');
  const score = await guard.getCreditScore('nano', 1);

  console.log(`\n${score.tier.emoji} Credit Score: ${score.score}/100`);
  console.log(`Tier: ${score.tier.name} (${score.tier.level})`);

  console.log('\n3. Score breakdown:');
  for (const factor of score.factors) {
    const sign = factor.impact >= 0 ? '+' : '';
    console.log(`   ${factor.factor}: ${sign}${factor.impact} (${factor.count}x)`);
  }

  // Generate report
  console.log('\n4. Generating credit report...');
  const report = await guard.getCreditReport('nano', 1);

  console.log('\nRecommendation:');
  console.log(`   Level: ${report.recommendation.level}`);
  console.log(`   Message: ${report.recommendation.message}`);
  console.log(`   Can Automate: ${report.recommendation.canAutomate}`);
  console.log(`   Suggested Permissions: ${report.recommendation.suggestedPermissions.join(', ')}`);

  // Test ranking
  console.log('\n5. Testing agent rankings...');

  // Create another agent for comparison
  try {
    await guard.registerAgent('test-agent-2', { owner: 'test@example.com', level: 'read' });
  } catch (e) {
    // Already exists
  }

  const ranking = await guard.getAgentRankings(1);
  console.log('\nAgent Rankings:');
  for (const agent of ranking.ranking) {
    const tier = guard.creditScore.getTier(agent.score);
    console.log(`  ${tier.emoji} #${agent.rank} ${agent.agentId}: ${agent.score}/100 (${tier.level})`);
  }

  console.log('\n✅ Credit Score System Test Complete!\n');
}

testCreditScore().catch(console.error);
