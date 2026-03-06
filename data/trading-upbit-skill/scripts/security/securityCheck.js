const fs = require('fs');
const path = require('path');

/**
 * securityCheck
 *
 * Lightweight static scan to help users verify:
 * - No unexpected remote endpoints are embedded in the codebase
 * - Upbit API host is allowlisted (api.upbit.com)
 *
 * Notes:
 * - This is NOT a formal security audit.
 * - It only scans for obvious URL strings.
 */
function securityCheck() {
  const projectRoot = path.resolve(__dirname, '..', '..');
  const allowHosts = new Set(['api.upbit.com']);

  const findings = [];

  function walk(dir) {
    for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, ent.name);
      if (ent.isDirectory()) {
        // skip node_modules and .git if present
        if (ent.name === 'node_modules' || ent.name === '.git') continue;
        walk(full);
      } else if (ent.isFile()) {
        if (!/\.(js|md|json)$/.test(ent.name)) continue;
        const txt = fs.readFileSync(full, 'utf8');
        const urls = txt.match(/https?:\/\/[^\s'"\)\]]+/g) || [];
        for (const url of urls) {
          try {
            const u = new URL(url);
            if (!allowHosts.has(u.host)) {
              findings.push({ file: path.relative(projectRoot, full), url });
            }
          } catch {
            // ignore
          }
        }
      }
    }
  }

  walk(projectRoot);

  return { ok: findings.length === 0, allowHosts: Array.from(allowHosts), findings };
}

module.exports = { securityCheck };
