// Generate an OpenClaw config snippet for integrating outsideclaw (installed by outsideclaw_setup.sh)
// Usage: node generate_openclaw_snippet.js

const os = require("node:os");
const path = require("node:path");

const OUTSIDECLAW_HOME = process.env.OUTSIDECLAW_HOME || path.join(os.homedir(), ".outsideclaw");
const OUTSIDECLAW_APP_DIR = process.env.OUTSIDECLAW_APP_DIR || path.join(OUTSIDECLAW_HOME, "app", "outsideclaw");

const snippet = {
  notes: "Add this to your OpenClaw skills list (paths are local).",
  skills: [
    {
      name: "trail-nav-telegram",
      path: path.join(OUTSIDECLAW_APP_DIR, "skills", "trail-nav-telegram"),
    },
  ],
};

process.stdout.write(JSON.stringify(snippet, null, 2) + "\n");
