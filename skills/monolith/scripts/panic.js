import { daemon } from '../lib/daemon-client.js';
import { formatDaemonError } from '../lib/format.js';

/**
 * Emergency freeze — instant, no Touch ID.
 * Usage: node scripts/panic.js
 */
async function main() {
  try {
    const response = await daemon.panic();

    if (response.status === 200) {
      console.log('WALLET FROZEN');
      console.log(response.data.message);
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
