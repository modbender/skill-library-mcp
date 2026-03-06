const fs = require('fs');
const path = require('path');

const statePath = path.resolve(
  process.env.HOME,
  '.openclaw/workspace/benos/runtime/state.json'
);

const lastPath = path.resolve(
  process.env.HOME,
  '.openclaw/workspace/benos/runtime/last-session.md'
);

module.exports = {
  name: "benos-memory-core",
  description: "BenOS runtime memory module",

  async run(ctx) {
    return {
      ok: true,
      message: "BenOS core memory module is active."
    };
  },

  async hydrate(ctx) {
    try {
      const state = fs.existsSync(statePath)
        ? JSON.parse(fs.readFileSync(statePath, 'utf8'))
        : {};

      const last = fs.existsSync(lastPath)
        ? fs.readFileSync(lastPath, 'utf8')
        : "";

      return {
        ok: true,
        hydration: {
          lastSession: last,
          state
        }
      };
    } catch (err) {
      return {
        ok: false,
        error: err.message
      };
    }
  }
};
