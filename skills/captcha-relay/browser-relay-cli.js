#!/usr/bin/env node
/**
 * Browser Relay CLI — start a relay server for a headless Chrome tab
 * Usage: node browser-relay-cli.js [--port 8787] [--cdp-port 18800] [--target-id <id>]
 */
const { createBrowserRelay } = require('./lib/browser-relay');

const args = process.argv.slice(2);
function getArg(name, def) {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : def;
}

(async () => {
  try {
    const relay = await createBrowserRelay({
      cdpPort: parseInt(getArg('--cdp-port', '18800')),
      targetId: getArg('--target-id', undefined),
      port: parseInt(getArg('--port', '8787')),
      timeout: parseInt(getArg('--timeout', '300')) * 1000,
    });
    console.log(`\n🖥️  Browser Relay running!`);
    console.log(`   Local:     http://localhost:${relay.port}`);
    console.log(`   Tailscale: http://100.117.26.44:${relay.port}\n`);
  } catch (e) {
    console.error('Failed to start:', e.message);
    process.exit(1);
  }
})();
