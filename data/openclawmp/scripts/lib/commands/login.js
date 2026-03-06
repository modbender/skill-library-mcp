// ============================================================================
// commands/login.js — Device authorization (login / authorize)
// ============================================================================

'use strict';

const config = require('../config.js');
const { fish, err, c, detail } = require('../ui.js');

async function run() {
  const deviceId = config.getDeviceId();

  console.log('');
  fish('Device Authorization');
  console.log('');

  if (!deviceId) {
    err(`No OpenClaw device identity found at ${config.DEVICE_JSON}`);
    console.log('');
    console.log('  Make sure OpenClaw is installed and has been started at least once.');
    process.exit(1);
  }

  console.log(`  Device ID: ${deviceId.slice(0, 16)}...`);
  console.log('');
  console.log('  To authorize this device, you need:');
  console.log(`    1. An account on ${c('bold', config.getApiBase())} (GitHub/Google login)`);
  console.log('    2. An activated invite code');
  console.log('');
  console.log('  Then authorize via the web UI, or ask your Agent to call:');
  console.log(`    POST /api/auth/device  { "deviceId": "${deviceId}" }`);
  console.log('');
  console.log(`  Once authorized, you can publish with: ${c('bold', 'openclawmp publish ./')}`);
  console.log('');
}

module.exports = { run };
