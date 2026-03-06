\
/**
 * Convenience runner: runs the skill worker_once from project root.
 *
 * Usage:
 *   node scripts/tests/run_worker_once.js
 */
const { spawnSync } = require("child_process");
const path = require("path");
const { projectRoot } = require("./common");

const root = projectRoot();
const cmd = process.platform === "win32" ? "node.exe" : "node";
const args = ["skill.js", "worker_once"];

console.log(`[TEST] Running worker_once: ${cmd} ${args.join(" ")} (cwd=${root})`);
const r = spawnSync(cmd, args, { cwd: root, stdio: "inherit" });
process.exit(r.status ?? 0);
