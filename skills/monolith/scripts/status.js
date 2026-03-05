import { daemon } from '../lib/daemon-client.js';
import { formatDaemonError } from '../lib/format.js';

/**
 * Check daemon health and wallet status.
 * Usage: node scripts/status.js
 */
async function main() {
  try {
    // Health check
    const health = await daemon.health();
    if (health.status === 200) {
      console.log(`Daemon: ${health.data.status} (v${health.data.version})`);
    } else {
      console.error('Daemon: unreachable');
      process.exit(1);
    }

    // Address
    const addr = await daemon.address();
    if (addr.status === 200) {
      console.log(`Wallet: ${addr.data.walletAddress}`);
      console.log(`Chain: ${addr.data.homeChainId}`);
    }

    // Capabilities
    const caps = await daemon.capabilities();
    if (caps.status === 200) {
      console.log(`Profile: ${caps.data.profile}`);
      console.log(`Frozen: ${caps.data.frozen}`);
      console.log(`Gas: ${caps.data.gasStatus}`);
    }
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }
}

main();
