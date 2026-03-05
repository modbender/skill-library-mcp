#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const { processLogsWithOptions } = require('../process_logs');

// ─── Security Helpers ───

/**
 * Validate that a path stays within the expected base directory.
 * Throws if path escapes the base.
 */
function safePath(basePath, userPath) {
  const base = path.resolve(basePath);
  const resolved = path.resolve(base, userPath);

  if (!resolved.startsWith(base + path.sep) && resolved !== base) {
    throw new Error(`Path traversal attempt blocked: ${userPath}`);
  }

  return resolved;
}

const SKILL_ROOT = path.resolve(__dirname, '../..');

function parseArgs(argv) {
  const args = {
    logsDir: null,
    outputDir: null,
    intervalMs: 1500
  };

  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--logs' && argv[i + 1]) {
      const userPath = argv[++i];
      try {
        args.logsDir = safePath(SKILL_ROOT, userPath);
      } catch (e) {
        console.warn(`--logs path validation failed (${userPath}), ignoring:`, e.message);
      }
    } else if (a === '--out' && argv[i + 1]) {
      const userPath = argv[++i];
      try {
        args.outputDir = safePath(SKILL_ROOT, userPath);
      } catch (e) {
        console.warn(`--out path validation failed (${userPath}), ignoring:`, e.message);
      }
    } else if (a === '--interval-ms' && argv[i + 1]) {
      args.intervalMs = Number(argv[++i]);
    } else if (a === '-h' || a === '--help') {
      args.help = true;
    }
  }

  return args;
}

function listRelevantFiles(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  return entries
    .filter(e => e.isFile())
    .map(e => e.name)
    .filter(n => /^incoming_.*\.json$/.test(n) || /^rtc_.*\.txt$/.test(n) || /^rtc_.*\.summary\.json$/.test(n))
    .map(n => path.join(dir, n));
}

function computeSignature(files) {
  let maxMtime = 0;
  let totalSize = 0;
  for (const f of files) {
    try {
      const st = fs.statSync(f);
      if (st.mtimeMs > maxMtime) maxMtime = st.mtimeMs;
      totalSize += st.size;
    } catch {
      // ignore
    }
  }
  return `${files.length}:${maxMtime}:${totalSize}`;
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help) {
    console.log('Usage: node scripts/watch.js [--logs <dir>] [--out <dir>] [--interval-ms <n>]');
    console.log('');
    console.log('If --logs is not specified, uses LOGS_DIR env var or default from process_logs.js');
    process.exit(0);
  }

  // Get default logs dir from env or process_logs.js defaults
  if (!args.logsDir) {
    const envLogsDir = process.env.LOGS_DIR;
    const defaultLogsDir = path.join(__dirname, '../../runtime/logs');
    if (envLogsDir) {
      try {
        args.logsDir = safePath(SKILL_ROOT, envLogsDir);
      } catch (e) {
        console.warn(`LOGS_DIR env validation failed (${envLogsDir}), using default:`, e.message);
        args.logsDir = defaultLogsDir;
      }
    } else {
      args.logsDir = defaultLogsDir;
    }
  }

  let lastSig = null;
  let running = false;

  console.log(`Watching: ${args.logsDir}`);
  console.log(`Interval: ${args.intervalMs}ms`);

  const tick = async () => {
    if (running) return;
    let files = [];
    try {
      files = listRelevantFiles(args.logsDir);
    } catch (e) {
      console.error('Watch error (readdir):', e);
      return;
    }
    const sig = computeSignature(files);
    if (sig === lastSig) return;
    lastSig = sig;

    running = true;
    try {
      console.log(`[${new Date().toISOString()}] change detected → aggregating…`);
      await processLogsWithOptions({
        logsDir: args.logsDir,
        outputDir: args.outputDir || undefined,
        writeSample: true
      });
    } catch (e) {
      console.error('Aggregation failed:', e);
    } finally {
      running = false;
    }
  };

  // Run once immediately, then poll.
  await tick();
  setInterval(tick, args.intervalMs);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
