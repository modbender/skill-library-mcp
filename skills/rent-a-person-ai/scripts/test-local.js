#!/usr/bin/env node
/**
 * Test bridge locally (bypasses ngrok)
 * Usage: node test-local.js
 */

async function testLocal() {
  console.log('🧪 Testing bridge locally...\n');
  
  const bridgeUrl = 'http://127.0.0.1:3001';
  const testPayload = {
    event: 'message.received',
    agentId: 'test_agent',
    conversationId: 'test_conv_123',
    messageId: 'test_msg_456',
    humanId: 'test_human_789',
    humanName: 'Test User',
    contentPreview: 'This is a test message from local test script',
    createdAt: new Date().toISOString(),
  };

  console.log(`📤 Sending to: ${bridgeUrl}`);
  console.log('Payload:', JSON.stringify(testPayload, null, 2));
  console.log('');

  try {
    const response = await fetch(bridgeUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testPayload),
    });

    const responseText = await response.text();
    
    console.log(`📥 Response Status: ${response.status} ${response.statusText}`);
    console.log(`📥 Response Body:`, responseText);
    console.log('');

    if (response.ok || response.status === 202) {
      console.log('✅ Bridge received webhook successfully!');
      console.log('');
      console.log('Check:');
      console.log('1. Bridge logs should show the request');
      console.log('2. Bridge should forward to OpenClaw at http://127.0.0.1:18789/hooks/agent');
      console.log('3. Check your OpenClaw session for the message');
    } else {
      console.log(`⚠️  Bridge returned ${response.status}: ${responseText}`);
    }
  } catch (error) {
    console.error('❌ Error:', error.message);
    console.error('');
    console.error('Make sure bridge is running:');
    console.error('  cd openclaw-skill/bridge');
    console.error('  node server.js');
  }
}

testLocal();
