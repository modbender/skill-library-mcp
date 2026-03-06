import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

const cwd = process.cwd();
const repoRoot = path.resolve(cwd, "..", "..");
const skillPath = "skills/jk-archivist-tiktok-skill";
const distDir = path.join(cwd, "dist");
const outZip = path.join(distDir, "jk-archivist-tiktok-skill.zip");

fs.mkdirSync(distDir, { recursive: true });

const result = spawnSync(
  "git",
  ["archive", "--format=zip", "--output", outZip, `HEAD:${skillPath}`],
  { cwd: repoRoot, stdio: "inherit" }
);

if (result.error) {
  console.error(`Failed to pack skill: ${result.error.message}`);
  process.exit(1);
}
if (result.status !== 0) {
  console.error(`git archive failed with status ${result.status ?? "unknown"}`);
  process.exit(1);
}

console.log(`Wrote ${outZip}`);
