/**
 * AgentGuard Tests
 */

const assert = require('assert');
const path = require('path');
const fs = require('fs');
const AgentGuard = require('../src/index');

const TEST_DIR = path.join(__dirname, '.test-data');

// Clean up test directory
function cleanup() {
  if (fs.existsSync(TEST_DIR)) {
    fs.rmSync(TEST_DIR, { recursive: true });
  }
}

// Test suite
async function runTests() {
  console.log('🧪 Running AgentGuard Tests\n');

  cleanup();

  const guard = new AgentGuard({
    basePath: TEST_DIR,
    masterPassword: 'test-password-123',
    timeout: 60
  });

  await guard.init();

  let passed = 0;
  let failed = 0;

  async function test(name, fn) {
    try {
      await fn();
      console.log(`✅ ${name}`);
      passed++;
    } catch (e) {
      console.log(`❌ ${name}`);
      console.log(`   Error: ${e.message}`);
      failed++;
    }
  }

  // ============ Registry Tests ============
  console.log('\n📋 Registry Tests\n');

  await test('Register agent', async () => {
    const agent = await guard.registerAgent('test-agent', {
      owner: 'test@example.com',
      level: 'write'
    });
    assert.strictEqual(agent.id, 'test-agent');
    assert.strictEqual(agent.owner, 'test@example.com');
    assert.strictEqual(agent.permissions.level, 'write');
  });

  await test('Get agent', async () => {
    const agent = await guard.getAgent('test-agent');
    assert.strictEqual(agent.id, 'test-agent');
  });

  await test('List agents', async () => {
    const agents = await guard.listAgents();
    assert(agents.length >= 1);
  });

  // ============ Vault Tests ============
  console.log('\n🔐 Vault Tests\n');

  await test('Store credential', async () => {
    await guard.storeCredential('test-agent', 'API_KEY', 'secret-key-123');
    const value = await guard.getCredential('test-agent', 'API_KEY');
    assert.strictEqual(value, 'secret-key-123');
  });

  await test('List credential keys', async () => {
    const keys = await guard.vault.listKeys('test-agent');
    assert(keys.some(k => k.key === 'API_KEY'));
  });

  // ============ Scope Tests ============
  console.log('\n🎯 Scope Tests\n');

  await test('Check read operation (auto-approved)', async () => {
    const result = await guard.scope.check('test-agent', 'read_file');
    assert.strictEqual(result.allowed, true);
    assert.strictEqual(result.requiresApproval, false);
  });

  await test('Check dangerous operation (requires approval)', async () => {
    const result = await guard.scope.check('test-agent', 'send_email');
    assert.strictEqual(result.allowed, true);
    assert.strictEqual(result.requiresApproval, true);
  });

  await test('Set permission level', async () => {
    await guard.setPermissionLevel('test-agent', 'admin');
    const info = await guard.scope.getInfo('test-agent');
    assert.strictEqual(info.level, 'admin');
  });

  // ============ Audit Tests ============
  console.log('\n📝 Audit Tests\n');

  await test('Log operation', async () => {
    const entry = await guard.audit.log('test-agent', 'test_operation', { foo: 'bar' });
    assert(entry.hash);
    assert(entry.timestamp);
  });

  await test('Get logs', async () => {
    const logs = await guard.getAuditLogs('test-agent', { last: 10 });
    assert(logs.length >= 1);
  });

  await test('Verify audit integrity', async () => {
    const today = new Date().toISOString().split('T')[0];
    const result = await guard.verifyAudit('test-agent', today);
    assert.strictEqual(result.valid, true);
  });

  // ============ Human Gate Tests ============
  console.log('\n🚪 Human Gate Tests\n');

  await test('Create approval request', async () => {
    const request = await guard.humanGate.request('test-agent', 'send_email', { to: 'user@test.com' });
    assert(request.id);
    assert.strictEqual(request.status, 'pending');
  });

  await test('List pending requests', async () => {
    const pending = await guard.listPendingRequests('test-agent');
    assert(pending.length >= 1);
  });

  await test('Approve request', async () => {
    const pending = await guard.listPendingRequests('test-agent');
    const requestId = pending[0].id;
    const request = await guard.approveRequest(requestId, 'test-user');
    assert.strictEqual(request.status, 'approved');
  });

  // ============ Cleanup ============
  cleanup();

  // ============ Results ============
  console.log('\n' + '='.repeat(40));
  console.log(`✅ Passed: ${passed}`);
  console.log(`❌ Failed: ${failed}`);
  console.log('='.repeat(40) + '\n');

  if (failed > 0) {
    process.exit(1);
  }
}

runTests().catch(console.error);
