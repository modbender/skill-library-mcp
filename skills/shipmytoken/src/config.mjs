import { readFile, mkdir, rename, chmod, stat, open } from "fs/promises";
import { constants } from "fs";
import { join } from "path";
import { homedir } from "os";
import { randomBytes } from "crypto";

const SMT_DIR = join(homedir(), ".shipmytoken");
const SMT_CONFIG = join(SMT_DIR, "config.json");
const SMT_TOKENS = join(SMT_DIR, "tokens.json");

const DIR_MODE = 0o700;
const FILE_MODE = 0o600;

async function ensureSecureDir() {
  await mkdir(SMT_DIR, { recursive: true, mode: DIR_MODE });
  // Force correct permissions even if directory already existed
  await chmod(SMT_DIR, DIR_MODE);
}

async function writeFileSecure(filePath, content) {
  await ensureSecureDir();

  // Random suffix prevents predictable temp filenames
  const tmp = `${filePath}.${randomBytes(8).toString("hex")}.tmp`;

  // O_EXCL fails if file exists (prevents symlink attacks)
  const fd = await open(tmp, constants.O_CREAT | constants.O_EXCL | constants.O_WRONLY, FILE_MODE);
  try {
    await fd.writeFile(content);
  } finally {
    await fd.close();
  }

  await rename(tmp, filePath);
}

function warnInsecurePermissions(filePath, mode) {
  if ((mode & 0o077) !== 0) {
    console.error(
      `WARNING: ${filePath} has insecure permissions (${(mode & 0o777).toString(8)}). Fixing to ${FILE_MODE.toString(8)}.`
    );
    return true;
  }
  return false;
}

export async function readConfig() {
  try {
    // Check and fix permissions on every read
    const stats = await stat(SMT_CONFIG);
    if (warnInsecurePermissions(SMT_CONFIG, stats.mode)) {
      await chmod(SMT_CONFIG, FILE_MODE);
    }

    const raw = await readFile(SMT_CONFIG, "utf-8");
    return JSON.parse(raw);
  } catch {
    return {};
  }
}

export async function writeConfig(key, value) {
  const config = await readConfig();
  config[key] = value;
  await writeFileSecure(SMT_CONFIG, JSON.stringify(config, null, 2) + "\n");
}

export async function getKey(name) {
  if (process.env[name]) return process.env[name];
  const config = await readConfig();
  return config[name] || null;
}

export async function readTokenHistory() {
  try {
    const stats = await stat(SMT_TOKENS);
    if (warnInsecurePermissions(SMT_TOKENS, stats.mode)) {
      await chmod(SMT_TOKENS, FILE_MODE);
    }

    const raw = await readFile(SMT_TOKENS, "utf-8");
    return JSON.parse(raw);
  } catch {
    return { tokens: [] };
  }
}

export async function writeTokenHistory(data) {
  await writeFileSecure(SMT_TOKENS, JSON.stringify(data, null, 2) + "\n");
}
