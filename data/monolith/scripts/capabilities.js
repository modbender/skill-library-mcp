import { daemon } from '../lib/daemon-client.js';
import { formatCapabilities, formatDaemonError } from '../lib/format.js';

/**
 * Query daemon /capabilities.
 * Usage: node scripts/capabilities.js
 */
async function main() {
  try {
    const response = await daemon.capabilities();

    if (response.status === 200) {
      console.log(formatCapabilities(response.data));
    } else {
      console.error(formatDaemonError(response));
      process.exit(1);
    }
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }
}

main();
