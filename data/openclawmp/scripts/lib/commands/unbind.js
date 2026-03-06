// ============================================================================
// commands/unbind.js — Unbind a device from your account
// ============================================================================

'use strict';

const api = require('../api.js');
const config = require('../config.js');
const { fish, ok, err, warn, c, detail } = require('../ui.js');

async function run(args, flags) {
  const deviceId = args[0] || config.getDeviceId();

  if (!deviceId) {
    err('No device ID specified and none found locally.');
    console.log('');
    console.log(`  Usage: openclawmp unbind [deviceId]`);
    console.log(`  Without arguments, unbinds the current device.`);
    process.exit(1);
  }

  fish(`Unbinding device ${c('dim', deviceId.slice(0, 12) + '...')} ...`);

  const { status, data } = await api.del('/api/auth/device', { deviceId });

  if (status >= 200 && status < 300 && data?.success) {
    console.log('');
    ok('设备已解绑');
    detail('Device', deviceId.slice(0, 16) + '...');
    console.log('');
  } else {
    err(data?.message || data?.error || `Unbind failed (HTTP ${status})`);
    process.exit(1);
  }
}

module.exports = { run };
