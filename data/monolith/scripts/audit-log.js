import { daemon } from '../lib/daemon-client.js';
import { formatDaemonError } from '../lib/format.js';

/**
 * Fetch and display the daemon audit log.
 * Usage: node scripts/audit-log.js
 */
async function main() {
  try {
    const response = await daemon.auditLog();

    if (response.status === 200) {
      const entries = response.data?.entries || response.data;

      if (Array.isArray(entries) && entries.length > 0) {
        for (const entry of entries) {
          const time = entry.timestamp || 'unknown';
          const action = entry.action || 'unknown';
          const detail = entry.detail || entry.summary || '';
          const status = entry.status || '';
          console.log(`[${time}] ${action}: ${detail}${status ? ` (${status})` : ''}`);
        }
      } else {
        console.log('No audit log entries.');
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
