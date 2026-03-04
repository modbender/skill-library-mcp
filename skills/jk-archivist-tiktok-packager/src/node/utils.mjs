import fs from "node:fs";
import path from "node:path";

export function todayISO() {
  const now = new Date();
  const year = String(now.getFullYear());
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

export function writeText(filePath, text) {
  fs.writeFileSync(filePath, text, "utf8");
}

export function writeJson(filePath, obj) {
  fs.writeFileSync(filePath, `${JSON.stringify(obj, null, 2)}\n`, "utf8");
}

export function exists(targetPath) {
  return fs.existsSync(targetPath);
}

export function optionalEnv(name) {
  const raw = process.env[name];
  if (typeof raw !== "string") {
    return undefined;
  }
  const trimmed = raw.trim();
  return trimmed.length > 0 ? trimmed : undefined;
}

export function requireEnv(name) {
  const value = optionalEnv(name);
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

export function repoRoot() {
  const cwd = process.cwd();
  const scriptsDir = path.join(cwd, "scripts");
  if (!fs.existsSync(scriptsDir) || !fs.statSync(scriptsDir).isDirectory()) {
    throw new Error(
      `Run this command from the skill directory root. Could not find scripts/ under: ${cwd}`
    );
  }
  return cwd;
}

export function join(...parts) {
  return path.join(...parts);
}
