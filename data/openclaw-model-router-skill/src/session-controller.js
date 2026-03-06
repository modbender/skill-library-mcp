const { execFile } = require('node:child_process');
const { promisify } = require('node:util');
const { RouterError } = require('./errors');

const execFileAsync = promisify(execFile);

function pickModelFromStatus(payload) {
  if (!payload || typeof payload !== 'object') return null;
  return payload.activeModel || payload.model || payload.defaultModel || null;
}

function ensureAuth(authConfig = {}) {
  const requiredEnv = Array.isArray(authConfig.requiredEnv) ? authConfig.requiredEnv : [];
  const missing = requiredEnv.filter((k) => !process.env[k]);
  if (missing.length > 0) {
    throw new RouterError(`Missing auth env: ${missing.join(', ')}`, {
      code: 'AUTH_MISSING',
      retryable: false,
      details: { missing },
    });
  }
}

async function runCommand(command, args, opts = {}) {
  try {
    const { stdout, stderr } = await execFileAsync(command, args, {
      timeout: opts.timeoutMs || 15000,
      maxBuffer: 2 * 1024 * 1024,
      env: process.env,
    });
    return {
      ok: true,
      stdout: String(stdout || ''),
      stderr: String(stderr || ''),
      code: 0,
    };
  } catch (err) {
    return {
      ok: false,
      stdout: String(err.stdout || ''),
      stderr: String(err.stderr || err.message || ''),
      code: Number.isInteger(err.code) ? err.code : 1,
    };
  }
}

function createOpenClawSessionController(config = {}) {
  const auth = config.auth || {};
  const setArgsPrefix = Array.isArray(config.setArgsPrefix) && config.setArgsPrefix.length
    ? config.setArgsPrefix
    : ['models', 'set'];
  const statusArgs = Array.isArray(config.statusArgs) && config.statusArgs.length
    ? config.statusArgs
    : ['models', 'status', '--json'];
  const binary = config.binary || 'openclaw';

  return {
    async getCurrentModel() {
      ensureAuth(auth);
      const res = await runCommand(binary, statusArgs, { timeoutMs: config.timeoutMs || 15000 });
      if (!res.ok) {
        throw new RouterError(`getCurrentModel failed: ${res.stderr || res.stdout}`, {
          code: 'MODEL_QUERY_FAILED',
          retryable: true,
        });
      }
      let parsed;
      try {
        parsed = JSON.parse(res.stdout);
      } catch {
        throw new RouterError('getCurrentModel returned invalid JSON', {
          code: 'MODEL_QUERY_PARSE_FAILED',
          retryable: true,
        });
      }
      const current = pickModelFromStatus(parsed);
      if (!current) {
        throw new RouterError('current model not found in status output', {
          code: 'MODEL_QUERY_EMPTY',
          retryable: true,
        });
      }
      return current;
    },

    async setModel(targetModel) {
      ensureAuth(auth);
      const args = [...setArgsPrefix, targetModel];
      const res = await runCommand(binary, args, { timeoutMs: config.timeoutMs || 20000 });
      if (!res.ok) {
        return false;
      }
      return true;
    },
  };
}

module.exports = {
  createOpenClawSessionController,
  pickModelFromStatus,
  ensureAuth,
};
