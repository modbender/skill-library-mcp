import { daemon } from '../lib/daemon-client.js';
import { formatDaemonError } from '../lib/format.js';

/**
 * View or update the spending policy.
 * Usage:
 *   node scripts/policy.js                     — show current policy
 *   node scripts/policy.js update '<json>'      — update policy (requires Touch ID)
 *
 * The update JSON should match the daemon's expected policy format.
 * This is a Touch ID-protected operation; the daemon will show a
 * native confirmation dialog before applying changes.
 */
async function main() {
  const [, , action, changesJson] = process.argv;

  if (!action || action === 'show') {
    // Show current policy
    try {
      const response = await daemon.policy();

      if (response.status === 200) {
        console.log(JSON.stringify(response.data, null, 2));
      } else {
        console.error(formatDaemonError(response));
        process.exit(1);
      }
    } catch (err) {
      console.error(err.message);
      process.exit(1);
    }
  } else if (action === 'update') {
    if (!changesJson) {
      console.error('Usage: policy update \'{"perTxEthCap": "0.1", ...}\'');
      process.exit(1);
    }

    let changes;
    try {
      changes = JSON.parse(changesJson);
    } catch {
      console.error('Invalid JSON for policy changes.');
      process.exit(1);
    }

    try {
      const response = await daemon.policyUpdate(changes);

      if (response.status === 200) {
        console.log('Policy updated successfully.');
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
  } else {
    console.error('Usage: policy [show|update \'<json>\']');
    process.exit(1);
  }
}

main();
