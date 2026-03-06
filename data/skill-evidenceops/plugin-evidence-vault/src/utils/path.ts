import * as path from 'path';
import * as fs from 'fs/promises';
import filenamify from 'filenamify';

const DANGEROUS_PATTERNS = [
  /\.\./,
  /~\//,
  /\0/,
  /\.\./,
];

const ALLOWED_FILENAME_CHARS = /^[a-zA-Z0-9._-]+$/;

export function sanitizeFilename(filename: string): string {
  if (!filename || typeof filename !== 'string') {
    return 'unnamed';
  }

  let sanitized = filenamify(filename, { replacement: '_' });
  
  sanitized = sanitized.replace(/\s+/g, '_');
  
  if (sanitized.length > 200) {
    const ext = path.extname(sanitized);
    const base = path.basename(sanitized, ext).substring(0, 200 - ext.length);
    sanitized = base + ext;
  }
  
  if (!sanitized || sanitized === '.') {
    return 'unnamed';
  }
  
  return sanitized;
}

export function sanitizePath(inputPath: string, basePath: string): string | null {
  if (!inputPath || typeof inputPath !== 'string') {
    return null;
  }

  for (const pattern of DANGEROUS_PATTERNS) {
    if (pattern.test(inputPath)) {
      return null;
    }
  }

  const resolved = path.resolve(basePath, inputPath);
  const normalizedBase = path.resolve(basePath);
  
  if (!resolved.startsWith(normalizedBase)) {
    return null;
  }
  
  return resolved;
}

export function sanitizeCaseId(caseId: string): string | null {
  if (!caseId || typeof caseId !== 'string') {
    return null;
  }

  if (!/^case-[a-zA-Z0-9_-]+$/.test(caseId)) {
    return null;
  }
  
  return caseId;
}

export function sanitizeEvidenceId(evidenceId: string): string | null {
  if (!evidenceId || typeof evidenceId !== 'string') {
    return null;
  }

  if (!/^ev-[a-zA-Z0-9-]+$/.test(evidenceId)) {
    return null;
  }
  
  return evidenceId;
}

export async function ensureDirectory(dirPath: string): Promise<void> {
  try {
    await fs.mkdir(dirPath, { recursive: true });
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== 'EEXIST') {
      throw error;
    }
  }
}

export function isPathWithinBase(filePath: string, basePath: string): boolean {
  const resolved = path.resolve(filePath);
  const normalizedBase = path.resolve(basePath);
  return resolved.startsWith(normalizedBase);
}
