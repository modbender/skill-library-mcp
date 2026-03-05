import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const shouldClean = process.argv.includes("--clean");
const disallowedMatchers = [
  (p) => p.endsWith(".pyc"),
  (p) => p.includes(`${path.sep}__pycache__${path.sep}`),
  (p) => p.includes(`${path.sep}outbox${path.sep}`),
  (p) => path.basename(p) === ".DS_Store",
];

function walk(dir, files = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(full, files);
      continue;
    }
    files.push(full);
  }
  return files;
}

const allFiles = walk(root);
const flagged = allFiles.filter((file) => disallowedMatchers.some((m) => m(file)));

if (shouldClean && flagged.length > 0) {
  for (const file of flagged) {
    fs.rmSync(file, { force: true });
  }
  // Remove empty __pycache__ and outbox dirs if they became empty.
  for (const dirName of ["__pycache__", "outbox"]) {
    for (const candidate of walk(root)
      .map((f) => path.dirname(f))
      .filter((d) => d.endsWith(`${path.sep}${dirName}`))) {
      try {
        fs.rmdirSync(candidate);
      } catch {
        // ignore non-empty dirs
      }
    }
  }
}

const refreshedFiles = walk(root);
const refreshedFlagged = refreshedFiles.filter((file) =>
  disallowedMatchers.some((m) => m(file))
);

if (refreshedFlagged.length > 0) {
  console.error("Bundle validation failed. Remove these files:");
  for (const file of refreshedFlagged) {
    console.error(`- ${path.relative(root, file)}`);
  }
  process.exit(1);
}

console.log("Bundle validation passed.");
