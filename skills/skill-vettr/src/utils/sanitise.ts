import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import type { AllowedRootsConfig } from '../types.js';

const SLUG_PATTERN = /^[a-z0-9][a-z0-9-]{0,62}[a-z0-9]$/i;
const URL_PATTERN = /^https:\/\/[a-z0-9][a-z0-9.-]*[a-z0-9]\.[a-z]{2,}(\/[\w./-]*)?$/i;

export function sanitiseSlug(input: string): string {
  const trimmed = input.trim().toLowerCase();

  if (!SLUG_PATTERN.test(trimmed)) {
    throw new Error(
      `Invalid slug format: must be alphanumeric with hyphens, 2-64 chars. Got: "${trimmed.substring(0, 20)}"`,
    );
  }

  return trimmed;
}

export function sanitiseUrl(input: string): string {
  const trimmed = input.trim();

  if (!URL_PATTERN.test(trimmed)) {
    throw new Error(
      `Invalid URL format: must be HTTPS with valid domain. Got: "${trimmed.substring(0, 50)}"`,
    );
  }

  const parsed = new URL(trimmed);

  if (parsed.username || parsed.password) {
    throw new Error('URLs with embedded credentials are not permitted');
  }

  if (parsed.pathname.includes('..')) {
    throw new Error('URL path traversal detected');
  }

  return trimmed;
}

export function sanitisePath(input: string, allowedRoots: string[]): string {
  const resolved = path.resolve(input);

  if (input.includes('..') || input.includes('\0')) {
    throw new Error('Path traversal detected');
  }

  const isAllowed = allowedRoots.some((root) => {
    const resolvedRoot = path.resolve(root);
    return resolved.startsWith(resolvedRoot + path.sep) || resolved === resolvedRoot;
  });

  if (!isAllowed) {
    throw new Error(
      `Path "${resolved}" is outside allowed directories: ${allowedRoots.join(', ')}`,
    );
  }

  return resolved;
}

export function getAllowedRoots(config?: AllowedRootsConfig): string[] {
  const roots = [
    os.tmpdir(),
    path.join(os.homedir(), '.openclaw'),
    path.join(os.homedir(), 'Downloads'),
  ];

  if (config?.allowCwd === true) {
    roots.push(process.cwd());
  }

  if (config?.additionalRoots) {
    roots.push(...config.additionalRoots);
  }

  return roots;
}

export function generateSecureTempName(): string {
  return `skill-vettr-${crypto.randomBytes(16).toString('hex')}`;
}

export function truncateEvidence(evidence: string, maxLen = 80): string {
  const sanitised = evidence
    .replace(/[\n\r\t]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  if (sanitised.length <= maxLen) {
    return sanitised;
  }

  return sanitised.substring(0, maxLen - 3) + '...';
}

export function generateFindingId(): string {
  return crypto.randomBytes(8).toString('hex');
}
