import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

function fail(message) {
  console.error(`Error: ${message}`);
  process.exit(1);
}

const args = process.argv.slice(2);
const versionIdx = args.indexOf("--version");
if (versionIdx === -1 || !args[versionIdx + 1]) {
  fail("Usage: node scripts/release.mjs --version <x.y.z>");
}
const version = args[versionIdx + 1];
if (!/^\d+\.\d+\.\d+$/.test(version)) {
  fail(`Invalid version '${version}'. Use semantic version x.y.z`);
}

const root = process.cwd();
const packageJsonPath = path.join(root, "package.json");
const metaPath = path.join(root, "_meta.json");

const pkg = JSON.parse(fs.readFileSync(packageJsonPath, "utf8"));
pkg.version = version;
fs.writeFileSync(packageJsonPath, `${JSON.stringify(pkg, null, 2)}\n`, "utf8");

const meta = JSON.parse(fs.readFileSync(metaPath, "utf8"));
meta.version = version;
fs.writeFileSync(metaPath, `${JSON.stringify(meta, null, 2)}\n`, "utf8");

const run = (cmd, cmdArgs) => {
  const result = spawnSync(cmd, cmdArgs, { stdio: "inherit" });
  if (result.error || result.status !== 0) {
    fail(`Failed command: ${cmd} ${cmdArgs.join(" ")}`);
  }
};

run("npm", ["test"]);
run("npm", ["run", "pack"]);

console.log("");
console.log(`Release prep complete for v${version}`);
console.log("Next steps:");
console.log(`1) Update CHANGELOG.md entry for v${version}`);
console.log("2) Commit and tag release");
console.log("3) Upload dist/jk-archivist-tiktok-skill.zip");
