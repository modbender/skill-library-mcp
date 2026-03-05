import { createHash } from 'crypto';
import { readFileSync, writeFileSync, mkdirSync, readdirSync, unlinkSync, statSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const CACHE_DIR = join(__dirname, '..', '..', 'data', 'cache');

function ensureDir() {
  mkdirSync(CACHE_DIR, { recursive: true });
}

function cacheKey(input: string): string {
  return createHash('md5').update(input).digest('hex');
}

export function get(key: string, ttlMs: number = 15 * 60 * 1000): any | null {
  ensureDir();
  const file = join(CACHE_DIR, cacheKey(key) + '.json');
  if (!existsSync(file)) return null;
  try {
    const stat = statSync(file);
    if (Date.now() - stat.mtimeMs > ttlMs) {
      unlinkSync(file);
      return null;
    }
    return JSON.parse(readFileSync(file, 'utf-8'));
  } catch { return null; }
}

export function set(key: string, data: any): void {
  ensureDir();
  const file = join(CACHE_DIR, cacheKey(key) + '.json');
  writeFileSync(file, JSON.stringify(data));
}

export function clear(): number {
  ensureDir();
  const files = readdirSync(CACHE_DIR).filter(f => f.endsWith('.json'));
  for (const f of files) unlinkSync(join(CACHE_DIR, f));
  return files.length;
}
