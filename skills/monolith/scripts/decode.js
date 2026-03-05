import { daemon } from '../lib/daemon-client.js';
import { formatDaemonError } from '../lib/format.js';

/**
 * Decode a transaction intent into a human-readable summary.
 * Usage: node scripts/decode.js <target> <calldata> <value>
 */
async function main() {
  const [, , target, calldata = '0x', value = '0'] = process.argv;

  if (!target) {
    console.error('Usage: decode <target> <calldata> <value>');
    process.exit(1);
  }

  try {
    const response = await daemon.decode({ target, calldata, value });

    if (response.status === 200) {
      const d = response.data;
      console.log(`Action: ${d.action}`);
      console.log(`Summary: ${d.summary}`);
      console.log(`Selector: ${d.selector}`);
      console.log(`Known: ${d.isKnown ? 'Yes' : 'No'}`);
      console.log(`Chain: ${d.chainId}`);
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
