#!/usr/bin/env node
/**
 * Send message to OpenClaw session via CLI
 * 
 * Usage:
 *   node send-to-session.js "agent:main:rentaperson" "Your message here"
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const sessionKey = process.argv[2] || 'agent:main:rentaperson';
const message = process.argv[3] || 'Test message';

// Load API key from credentials
const credPath = path.join(__dirname, '..', 'rentaperson-agent.json');
let apiKey = '';
if (fs.existsSync(credPath)) {
  const creds = JSON.parse(fs.readFileSync(credPath, 'utf8'));
  apiKey = creds.apiKey || '';
}

// Build the full message with API key
const fullMessage = `${message}

🔑 API KEY: ${apiKey}
Use this header: X-API-Key: ${apiKey}`;

try {
  // Use OpenClaw CLI to send message to session
  // Format: openclaw send <sessionKey> <message>
  const cmd = `openclaw send "${sessionKey}" "${fullMessage.replace(/"/g, '\\"')}"`;
  console.log(`Sending to session: ${sessionKey}`);
  console.log(`Message: ${message.substring(0, 50)}...`);
  
  const output = execSync(cmd, { encoding: 'utf-8', stdio: 'inherit' });
  console.log('✓ Message sent');
} catch (err) {
  console.error('Error:', err.message);
  console.error('\nMake sure OpenClaw CLI is installed and the session exists.');
  process.exit(1);
}
