"use strict";

const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const libDir = path.join(root, "lib", "clawd_migrate");

const pyFiles = [
  "__init__.py",
  "__main__.py",
  "config.py",
  "discover.py",
  "migrate.py",
  "backup.py",
  "tui.py",
  "openclaw_setup.py",
  "verify.py",
];

if (!fs.existsSync(libDir)) {
  fs.mkdirSync(libDir, { recursive: true });
}

for (const f of pyFiles) {
  const src = path.join(root, f);
  if (fs.existsSync(src)) {
    fs.copyFileSync(src, path.join(libDir, f));
  }
}

const docSrc = path.join(root, "Documentation");
const docDest = path.join(libDir, "Documentation");
if (fs.existsSync(docSrc)) {
  if (!fs.existsSync(docDest)) fs.mkdirSync(docDest, { recursive: true });
  for (const name of fs.readdirSync(docSrc)) {
    const p = path.join(docSrc, name);
    if (fs.statSync(p).isFile()) {
      fs.copyFileSync(p, path.join(docDest, name));
    }
  }
}

console.log("Prepublish: copied Python package to lib/clawd_migrate/");
