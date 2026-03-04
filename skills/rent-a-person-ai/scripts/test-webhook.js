#!/usr/bin/env node
/**
 * Test script to verify RentAPerson webhook setup
 * Usage: node test-webhook.js <ngrok-url>
 * Example: node test-webhook.js https://abc123.ngrok.io
 */

const webhookUrl = process.argv[2];

if (!webhookUrl) {
  console.error('Usage: node test-webhook.js <ngrok-url>');
  console.error('Example: node test-webhook.js https://abc123.ngrok.io');
  process.exit(1);
}

async function testWebhook() {
  console.log('🧪 Testing RentAPerson webhook setup...\n');
  console.log(`Target URL: ${webhookUrl}\n`);

  // Test payload similar to what RentAPerson sends
  const testPayload = {
    event: 'message.received',
    agentId: 'test_agent',
    conversationId: 'test_conv_123',
    messageId: 'test_msg_456',
    humanId: 'test_human_789',
    humanName: 'Test User',
    contentPreview: 'This is a test message from the webhook test script',
    createdAt: new Date().toISOString(),
  };

  console.log('📤 Sending test webhook...');
  console.log('Payload:', JSON.stringify(testPayload, null, 2));
  console.log('');

  try {
    // ngrok-free.dev requires browser verification - add bypass header
    const headers = {
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true', // Skip ngrok browser warning
    };
    
    const response = await fetch(webhookUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(testPayload),
    });

    const responseText = await response.text();
    
    console.log(`📥 Response Status: ${response.status} ${response.statusText}`);
    console.log(`📥 Response Headers:`, Object.fromEntries(response.headers.entries()));
    console.log(`📥 Response Body:`, responseText);
    console.log('');

    if (response.ok || response.status === 202) {
      console.log('✅ Webhook accepted successfully!');
      console.log('');
      console.log('Next steps:');
      console.log('1. Check your OpenClaw session (agent:main:rentaperson or your configured session)');
      console.log('2. Look for the test message in the session');
      console.log('3. Verify the message contains: [RENTAPERSON] Use for all API calls: X-API-Key: ...');
      console.log('4. The agent should be able to see the API key and respond');
    } else {
      console.log('❌ Webhook was rejected');
      console.log('');
      if (response.status === 401) {
        console.log('⚠️  401 Unauthorized: Check your OpenClaw hooks token');
        console.log('   Make sure webhookBearerToken is set correctly in RentAPerson');
      } else if (response.status === 404) {
        console.log('⚠️  404 Not Found: Check the webhook URL path');
        console.log('   Bridge: Should be root /');
        console.log('   Transform: Should be /hooks/rentaperson');
      } else {
        console.log(`⚠️  Error ${response.status}: ${responseText}`);
      }
    }
  } catch (error) {
    console.error('❌ Error sending webhook:', error.message);
    console.error('');
    console.error('Troubleshooting:');
    console.error('1. Visit the ngrok URL in browser first (ngrok-free.dev requires browser verification)');
    console.error('   https://velia-regardable-reed.ngrok-free.dev');
    console.error('2. Is the bridge service running on port 3001?');
    console.error('   Check: ps aux | grep "bridge/server.js"');
    console.error('3. Check bridge logs for incoming requests');
    console.error('4. Check ngrok web interface: http://127.0.0.1:4040');
    console.error('5. Try manual curl test:');
    console.error(`   curl -X POST ${webhookUrl} \\`);
    console.error('     -H "Content-Type: application/json" \\');
    console.error('     -H "ngrok-skip-browser-warning: true" \\');
    console.error('     -d \'{"event":"message.received","conversationId":"test"}\'');
  }
}

testWebhook();
