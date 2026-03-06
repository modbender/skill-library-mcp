#!/usr/bin/env node
/**
 * Test credential loading from openclaw.json
 */

import { getCredentials } from '../lib/lark-api.mjs';

console.log('\n🔍 Testing credential loading...\n');

try {
  const creds = getCredentials();

  console.log('✅ Credentials loaded successfully!\n');
  console.log('Source:', creds.source);
  console.log('App ID:', creds.appId);
  console.log('App Secret:', creds.appSecret ? '***' + creds.appSecret.slice(-4) : 'not set');

  console.log('\n✨ The skill will use these credentials for all API calls!\n');

} catch (error) {
  console.error('❌ Failed to load credentials:', error.message);
  console.error('\nPlease check your ~/.openclaw/openclaw.json configuration.\n');
  process.exit(1);
}
