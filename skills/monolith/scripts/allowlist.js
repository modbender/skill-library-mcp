import { daemon } from '../lib/daemon-client.js';
import { formatDaemonError } from '../lib/format.js';

/**
 * Add or remove addresses from the allowlist.
 * Usage:
 *   node scripts/allowlist.js add <address> [label]
 *   node scripts/allowlist.js remove <address>
 *
 * This is a Touch ID-protected operation; the daemon will show a
 * native confirmation dialog before applying changes.
 */
async function main() {
  const [, , action, address, label] = process.argv;

  if (!action || !address) {
    console.error('Usage: allowlist <add|remove> <address> [label]');
    process.exit(1);
  }

  if (action !== 'add' && action !== 'remove') {
    console.error('Action must be "add" or "remove".');
    process.exit(1);
  }

  const changes = { action, address };
  if (label && action === 'add') {
    changes.label = label;
  }

  try {
    const response = await daemon.allowlistUpdate(changes);

    if (response.status === 200) {
      if (action === 'add') {
        console.log(`Address ${address} added to allowlist.`);
      } else {
        console.log(`Address ${address} removed from allowlist.`);
      }
      if (response.data) {
        console.log(JSON.stringify(response.data, null, 2));
      }
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
