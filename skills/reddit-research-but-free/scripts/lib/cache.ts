/**
 * Simple file-based cache with configurable TTL.
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync, readdirSync, unlinkSync, statSync } from "fs";
import { join, dirname } from "path";
import { createHash } from "crypto";
import { fileURLToPath } from "url";

const __dirname = import.meta.dirname ?? dirname(fileURLToPath(import.meta.url));
const CACHE_DIR = join(__dirname, "..", "..", "data", "cache");

function ensureDir() {
  if (!existsSync(CACHE_DIR)) mkdirSync(CACHE_DIR, { recursive: true });
}

function keyHash(key: string): string {
  return createHash("md5").update(key).digest("hex");
}

export function get<T>(key: string, ttlMs: number): T | null {
  ensureDir();
  const file = join(CACHE_DIR, `${keyHash(key)}.json`);
  if (!existsSync(file)) return null;

  try {
    const data = JSON.parse(readFileSync(file, "utf-8"));
    if (Date.now() - data.ts > ttlMs) return null;
    return data.value as T;
  } catch {
    return null;
  }
}

export function set(key: string, value: any): void {
  ensureDir();
  const file = join(CACHE_DIR, `${keyHash(key)}.json`);
  writeFileSync(file, JSON.stringify({ ts: Date.now(), key, value }));
}

export function clear(): number {
  ensureDir();
  const files = readdirSync(CACHE_DIR).filter((f) => f.endsWith(".json"));
  for (const f of files) unlinkSync(join(CACHE_DIR, f));
  return files.length;
}

export function stats(): { count: number; sizeKb: number } {
  ensureDir();
  const files = readdirSync(CACHE_DIR).filter((f) => f.endsWith(".json"));
  let size = 0;
  for (const f of files) size += statSync(join(CACHE_DIR, f)).size;
  return { count: files.length, sizeKb: Math.round(size / 1024) };
}
