/**
 * Basic tests for claude-code-control
 * 
 * Run with: npm test
 */

const cc = require('./index');
const assert = require('assert');
const path = require('path');

async function testBasics() {
  console.log('🧪 Testing claude-code-control\n');

  // Test 1: Check if Claude Code is installed
  console.log('Test 1: Checking Claude Code installation...');
  try {
    require('child_process').execSync('which claude', { stdio: 'pipe' });
    console.log('✅ Claude Code is installed\n');
  } catch {
    console.error('❌ Claude Code not found. Install with: brew install anthropic-cli');
    process.exit(1);
  }

  // Test 2: Launch session
  console.log('Test 2: Launching Claude Code session...');
  const projectPath = process.env.TEST_PROJECT || process.cwd();
  
  let sessionId;
  try {
    sessionId = await cc.launch(projectPath);
    assert(sessionId, 'Session ID should be truthy');
    console.log(`✅ Session launched (ID: ${sessionId})\n`);
  } catch (err) {
    console.error('❌ Failed to launch:', err.message);
    process.exit(1);
  }

  // Test 3: Check status
  console.log('Test 3: Checking session status...');
  const status = cc.getStatus(sessionId);
  assert(status, 'Status should not be null');
  assert(status.running, 'Session should be running');
  assert(status.uptime_ms > 0, 'Uptime should be positive');
  console.log(`✅ Status OK (uptime: ${status.uptime_ms}ms)\n`);

  // Test 4: Send a simple command
  console.log('Test 4: Sending a test command...');
  try {
    const result = await cc.send(sessionId, 'echo "Hello from Claude Code"');
    assert(result.sessionId === sessionId, 'Session ID should match');
    assert(result.status === 'success', `Status should be 'success', got '${result.status}'`);
    assert(result.output, 'Output should be present');
    assert(result.duration_ms > 0, 'Duration should be positive');
    console.log(`✅ Command executed (duration: ${result.duration_ms}ms)\n`);
  } catch (err) {
    console.error('❌ Command failed:', err.message);
    process.exit(1);
  }

  // Test 5: Close session
  console.log('Test 5: Closing session...');
  try {
    await cc.close(sessionId);
    const closedStatus = cc.getStatus(sessionId);
    assert(!closedStatus, 'Status should be null after close');
    console.log('✅ Session closed\n');
  } catch (err) {
    console.error('❌ Close failed:', err.message);
    process.exit(1);
  }

  console.log('🎉 All tests passed!\n');
  process.exit(0);
}

testBasics().catch((err) => {
  console.error('Test error:', err);
  process.exit(1);
});
