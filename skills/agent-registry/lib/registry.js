"use strict";

const fs = require("fs");
const path = require("path");

/**
 * Path utilities and registry I/O for Agent Registry.
 *
 * Centralizes the path resolution and JSON read/write logic that was
 * previously duplicated across every Python script.
 */

function getSkillDir() {
  return path.resolve(__dirname, "..");
}

function getRegistryPath() {
  return path.join(getSkillDir(), "references", "registry.json");
}

function getAgentsDir() {
  return path.join(getSkillDir(), "agents");
}

function isPathInsideDir(parentDir, targetPath) {
  const rel = path.relative(parentDir, targetPath);
  return rel === "" || (rel !== ".." && !rel.startsWith(".." + path.sep) && !path.isAbsolute(rel));
}

function resolveRegistryAgentPath(agentPath) {
  if (typeof agentPath !== "string" || agentPath.trim() === "") {
    return { ok: false, error: "Invalid agent path in registry entry." };
  }

  const skillDir = getSkillDir();
  const agentsDir = getAgentsDir();
  const raw = agentPath.trim();

  let resolved;
  if (path.isAbsolute(raw)) {
    resolved = path.resolve(raw);
  } else if (raw.startsWith("agents/") || raw.startsWith("agents" + path.sep)) {
    resolved = path.resolve(skillDir, raw);
  } else {
    resolved = path.resolve(agentsDir, raw);
  }

  if (!isPathInsideDir(agentsDir, resolved)) {
    return {
      ok: false,
      error: `Refusing to load agent outside '${agentsDir}': ${agentPath}`,
    };
  }

  return { ok: true, path: resolved };
}

function loadRegistry() {
  const registryPath = getRegistryPath();

  try {
    const raw = fs.readFileSync(registryPath, "utf8");
    return JSON.parse(raw);
  } catch (err) {
    if (err.code === "ENOENT") {
      process.stderr.write(
        "Error: Registry not found. Run 'bun bin/init.js' first.\n"
      );
    } else {
      process.stderr.write("Error loading registry: " + err.message + "\n");
    }
    return null;
  }
}

function saveRegistry(registry) {
  const registryPath = getRegistryPath();
  const dir = path.dirname(registryPath);

  try {
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(registryPath, JSON.stringify(registry), "utf8");
  } catch (err) {
    process.stderr.write("Error saving registry: " + err.message + "\n");
    return false;
  }
  return true;
}

module.exports = {
  getSkillDir,
  getRegistryPath,
  getAgentsDir,
  resolveRegistryAgentPath,
  loadRegistry,
  saveRegistry,
};
