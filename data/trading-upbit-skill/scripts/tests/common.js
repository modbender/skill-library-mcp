\
const fs = require("fs");
const path = require("path");

function projectRoot() {
  // this file lives in <skillRoot>/scripts/tests/
  return path.resolve(__dirname, "..", "..");
}

function resourcesDir() {
  return path.join(projectRoot(), "resources");
}

function ensureResources() {
  const dir = resourcesDir();
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  const files = ["events.json", "positions.json"];
  for (const f of files) {
    const p = path.join(dir, f);
    if (!fs.existsSync(p)) {
      fs.writeFileSync(p, f === "events.json" ? "[]\n" : JSON.stringify({ positions: [] }, null, 2) + "\n", "utf8");
    }
  }
  return dir;
}

function readJson(filePath, fallback) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch {
    return fallback;
  }
}

function writeJson(filePath, obj) {
  fs.writeFileSync(filePath, JSON.stringify(obj, null, 2) + "\n", "utf8");
}

function nowISO() {
  return new Date().toISOString();
}

function makeId(prefix="evt") {
  return `${prefix}_${Date.now()}_${Math.random().toString(16).slice(2, 8)}`;
}

module.exports = {
  projectRoot,
  resourcesDir,
  ensureResources,
  readJson,
  writeJson,
  nowISO,
  makeId,
};
