// ============================================================================
// commands/whoami.js — Show current user / device info
// ============================================================================

'use strict';

const config = require('../config.js');
const { fish, info, warn, c, detail } = require('../ui.js');

async function run() {
  console.log('');
  fish('Who Am I');
  console.log('');

  // Device identity
  const deviceId = config.getDeviceId();
  if (deviceId) {
    detail('Device ID', deviceId);
  } else {
    warn(`No device identity found (expected: ${config.DEVICE_JSON})`);
  }

  // Auth token
  const token = config.getAuthToken();
  if (token) {
    detail('Auth Token', `${token.slice(0, 8)}...${token.slice(-4)} (configured)`);
  } else {
    detail('Auth Token', c('dim', 'not configured'));
  }

  // API base
  detail('API Base', config.getApiBase());

  // Config dir
  detail('Config Dir', config.CONFIG_DIR);

  // Install base
  detail('Install Base', config.OPENCLAW_STATE_DIR);

  // Lockfile stats
  const lock = config.readLockfile();
  const count = Object.keys(lock.installed || {}).length;
  detail('Installed', `${count} asset(s)`);

  console.log('');
}

module.exports = { run };
