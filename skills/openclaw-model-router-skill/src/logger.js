const fs = require('node:fs');
const path = require('node:path');

function rotateIfNeeded(logPath, maxBytes = 2 * 1024 * 1024, maxBackups = 5) {
  try {
    if (!fs.existsSync(logPath)) return;
    const stat = fs.statSync(logPath);
    if (stat.size < maxBytes) return;

    for (let i = maxBackups - 1; i >= 1; i -= 1) {
      const src = `${logPath}.${i}`;
      const dst = `${logPath}.${i + 1}`;
      if (fs.existsSync(src)) fs.renameSync(src, dst);
    }
    fs.renameSync(logPath, `${logPath}.1`);
  } catch {
    // do not crash caller on rotation failure
  }
}

function createLogger(logPath = path.join(process.cwd(), 'router.log.jsonl'), options = {}) {
  const maxBytes = options.maxBytes || 2 * 1024 * 1024;
  const maxBackups = options.maxBackups || 5;

  return {
    log(event) {
      const record = {
        ts: new Date().toISOString(),
        ...event,
      };
      try {
        rotateIfNeeded(logPath, maxBytes, maxBackups);
        fs.appendFileSync(logPath, JSON.stringify(record) + '\n', 'utf8');
      } catch {
        // Avoid crashing the router on logging failures.
      }
      return record;
    },
  };
}

module.exports = { createLogger, rotateIfNeeded };
