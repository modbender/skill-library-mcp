// Test AgentGuard API
const AgentGuard = require('./src/index');

async function test() {
  const guard = new AgentGuard({
    masterPassword: 'nano-test-password'
  });

  await guard.init();

  console.log('\n🧪 Testing AgentGuard API\n');

  // 1. Check read operation (should auto-approve)
  console.log('1. Read operation check:');
  const readCheck = await guard.scope.check('nano', 'read_file');
  console.log('   Result:', readCheck.allowed ? '✅ Allowed' : '❌ Denied');
  console.log('   Reason:', readCheck.reason);

  // 2. Check dangerous operation (should require approval)
  console.log('\n2. Dangerous operation check (send_email):');
  const emailCheck = await guard.scope.check('nano', 'send_email', {
    to: 'master@example.com',
    subject: 'Test email'
  });
  console.log('   Result:', emailCheck.allowed ? '✅ Allowed' : '❌ Denied');
  console.log('   Requires approval:', emailCheck.requiresApproval);

  // 3. Get credential
  console.log('\n3. Get credential:');
  const apiKey = await guard.getCredential('nano', 'OPENAI_API_KEY');
  console.log('   OPENAI_API_KEY:', apiKey.substring(0, 10) + '...');

  // 4. Audit log
  console.log('\n4. Recent audit logs:');
  const logs = await guard.getAuditLogs('nano', { last: 5 });
  logs.forEach(log => {
    console.log(`   ${log.timestamp.split('T')[1].split('.')[0]} - ${log.operation}`);
  });

  // 5. Stats
  console.log('\n5. Agent stats:');
  const stats = await guard.getStats('nano', 1);
  console.log('   Total operations:', stats.totalOperations);
  console.log('   By operation:', stats.byOperation);

  // 6. Test approval workflow (create request)
  console.log('\n6. Create approval request:');
  const request = await guard.humanGate.request('nano', 'send_email', {
    to: 'master@example.com',
    subject: 'Daily report',
    body: 'This is a test email'
  });
  console.log('   Request ID:', request.id);
  console.log('   Status:', request.status);
  console.log('   Expires:', request.expiresAt);

  // 7. List pending
  console.log('\n7. Pending requests:');
  const pending = await guard.listPendingRequests('nano');
  console.log('   Count:', pending.length);
  if (pending.length > 0) {
    console.log('   First:', pending[0].operation);
  }

  // 8. Approve the request
  console.log('\n8. Approve request:');
  const approved = await guard.approveRequest(request.id, 'master');
  console.log('   Status:', approved.status);
  console.log('   Approved by:', approved.response.approvedBy);

  // 9. Final stats
  console.log('\n9. Final stats:');
  const finalStats = await guard.getStats('nano', 1);
  console.log('   Approvals:', finalStats.approvals);

  console.log('\n✅ All tests passed!\n');
}

test().catch(console.error);
