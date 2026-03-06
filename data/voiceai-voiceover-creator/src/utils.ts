/**
 * Shared utilities: slugify, hashing, formatting, file helpers.
 */
import { createHash } from 'node:crypto';
import { mkdir, writeFile, readFile, stat } from 'node:fs/promises';
import { dirname } from 'node:path';

/* ------------------------------------------------------------------ */
/*  String helpers                                                     */
/* ------------------------------------------------------------------ */

/** Slugify a string for safe filenames and directory names. */
export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/['']/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 60);
}

/** Zero-pad a number (e.g. 3 → "003"). */
export function zeroPad(n: number, width = 3): string {
  return String(n).padStart(width, '0');
}

/* ------------------------------------------------------------------ */
/*  Hashing                                                            */
/* ------------------------------------------------------------------ */

/** SHA-256 content hash (first 16 hex chars). */
export function contentHash(...parts: string[]): string {
  const h = createHash('sha256');
  for (const p of parts) h.update(p);
  return h.digest('hex').slice(0, 16);
}

/* ------------------------------------------------------------------ */
/*  Duration / timestamp formatting                                    */
/* ------------------------------------------------------------------ */

/** Format seconds → "M:SS" or "H:MM:SS". */
export function formatDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  return `${m}:${String(s).padStart(2, '0')}`;
}

/** Format seconds → "HH:MM:SS" (YouTube chapter format). */
export function formatTimestamp(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

/** Format seconds → YouTube-friendly "M:SS" or "H:MM:SS" (no leading zero on hours). */
export function youtubeTimestamp(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  return `${m}:${String(s).padStart(2, '0')}`;
}

/** Format seconds → SRT timestamp "HH:MM:SS,mmm". */
export function srtTimestamp(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  const ms = Math.round((seconds % 1) * 1000);
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')},${String(ms).padStart(3, '0')}`;
}

/* ------------------------------------------------------------------ */
/*  File system helpers                                                */
/* ------------------------------------------------------------------ */

/** Create directory (recursive). */
export async function ensureDir(dirPath: string): Promise<void> {
  await mkdir(dirPath, { recursive: true });
}

/** Write file, creating parent directories as needed. */
export async function writeOutputFile(filePath: string, content: string | Buffer): Promise<void> {
  await ensureDir(dirname(filePath));
  await writeFile(filePath, content);
}

/** Check if a path exists. */
export async function fileExists(filePath: string): Promise<boolean> {
  try {
    await stat(filePath);
    return true;
  } catch {
    return false;
  }
}

/** Read a text file to string. */
export async function readTextFile(filePath: string): Promise<string> {
  return readFile(filePath, 'utf-8');
}
