/**
 * USER.md Parser
 *
 * Parses ~/.config/claude/USER.md (or custom path) into structured signals
 * that can be blended with conversation-derived identity data.
 *
 * Gracefully returns null if the file doesn't exist.
 */

import { readFileSync, existsSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

export interface UserMdSignals {
  role?: string;               // "BD Lead", "Senior Engineer"
  currentFocus?: string[];     // ["DeFi protocols", "AI agent ecosystem"]
  techStack?: string[];        // ["claude-code", "typescript", "solidity"]
  interests?: string[];        // ["music production", "generative art"]
  workingStyle?: string;       // "explorer" | "deep-focus" | "multitasker"
  raw?: Record<string, string>; // Unparsed sections for future use
}

const DEFAULT_USER_MD_PATH = join(homedir(), '.config', 'claude', 'USER.md');

/**
 * Parse a USER.md file into structured signals.
 * Returns null if the file doesn't exist (graceful degradation).
 */
export function parseUserMd(filePath?: string): UserMdSignals | null {
  const resolvedPath = filePath || DEFAULT_USER_MD_PATH;

  if (!existsSync(resolvedPath)) {
    return null;
  }

  let content: string;
  try {
    content = readFileSync(resolvedPath, 'utf-8');
  } catch {
    return null;
  }

  if (!content.trim()) {
    return null;
  }

  const sections = parseSections(content);
  const signals: UserMdSignals = {};

  // Extract structured fields from known sections
  for (const [header, body] of Object.entries(sections)) {
    const normalized = header.toLowerCase().trim();

    if (matchesHeader(normalized, ['role', 'title', 'position', 'job'])) {
      signals.role = extractSingleValue(body);
    } else if (matchesHeader(normalized, ['focus', 'current focus', 'working on', 'projects'])) {
      signals.currentFocus = extractListValues(body);
    } else if (matchesHeader(normalized, ['tech stack', 'stack', 'tools', 'technologies'])) {
      signals.techStack = extractListValues(body);
    } else if (matchesHeader(normalized, ['interests', 'hobbies', 'passions', 'likes'])) {
      signals.interests = extractListValues(body);
    } else if (matchesHeader(normalized, ['working style', 'style', 'work style', 'approach'])) {
      signals.workingStyle = inferWorkingStyle(body);
    }
  }

  // Store raw sections for future extensibility
  signals.raw = sections;

  // Only return if we extracted at least one meaningful signal
  const hasSignals = signals.role || signals.currentFocus?.length ||
    signals.techStack?.length || signals.interests?.length || signals.workingStyle;

  return hasSignals ? signals : null;
}

// ─── Internal helpers ────────────────────────────────────────────────────

/**
 * Split markdown content into sections keyed by ## headers.
 * Content before the first header is stored under key "".
 */
function parseSections(content: string): Record<string, string> {
  const sections: Record<string, string> = {};
  const lines = content.split('\n');
  let currentHeader = '';
  let currentBody: string[] = [];

  for (const line of lines) {
    // Match ## headers (level 2 or 3)
    const headerMatch = line.match(/^#{1,3}\s+(.+)/);
    if (headerMatch) {
      // Save previous section
      if (currentHeader || currentBody.length > 0) {
        sections[currentHeader] = currentBody.join('\n').trim();
      }
      currentHeader = headerMatch[1].trim();
      currentBody = [];
    } else {
      currentBody.push(line);
    }
  }

  // Save last section
  if (currentHeader || currentBody.length > 0) {
    sections[currentHeader] = currentBody.join('\n').trim();
  }

  return sections;
}

function matchesHeader(normalized: string, candidates: string[]): boolean {
  return candidates.some(c => normalized.includes(c));
}

/**
 * Extract a single value from a section body.
 * Handles: "BD Lead", "- BD Lead", "Role: BD Lead"
 */
function extractSingleValue(body: string): string {
  const trimmed = body.trim();

  // Try bullet point first
  const bulletMatch = trimmed.match(/^[-*]\s+(.+)/m);
  if (bulletMatch) return bulletMatch[1].trim();

  // Try "Key: Value" format
  const kvMatch = trimmed.match(/^[^:]+:\s*(.+)/m);
  if (kvMatch) return kvMatch[1].trim();

  // Just return the first non-empty line
  const firstLine = trimmed.split('\n').find(l => l.trim().length > 0);
  return firstLine?.trim() || trimmed;
}

/**
 * Extract a list of values from a section body.
 * Handles bullet lists, comma-separated values, and mixed formats.
 */
function extractListValues(body: string): string[] {
  const values: string[] = [];

  // Extract bullet points
  const bulletRegex = /^[-*]\s+(.+)/gm;
  let match;
  while ((match = bulletRegex.exec(body)) !== null) {
    const item = match[1].trim();
    // Split comma-separated items within a bullet
    if (item.includes(',')) {
      values.push(...item.split(',').map(v => v.trim()).filter(Boolean));
    } else {
      values.push(item);
    }
  }

  // If no bullets found, try comma-separated on a single line
  if (values.length === 0) {
    const lines = body.trim().split('\n').filter(l => l.trim().length > 0);
    for (const line of lines) {
      if (line.includes(',')) {
        values.push(...line.split(',').map(v => v.trim()).filter(Boolean));
      } else {
        values.push(line.trim());
      }
    }
  }

  return values.filter(Boolean);
}

/**
 * Infer working style from free-text description.
 * Maps to: "deep-focus" | "explorer" | "multitasker"
 */
function inferWorkingStyle(body: string): string {
  const lower = body.toLowerCase();

  const deepFocusKeywords = ['deep focus', 'deep-focus', 'focused', 'single task', 'deep dive',
    'concentrated', 'immersive', 'flow state', 'specialist'];
  const explorerKeywords = ['explorer', 'exploring', 'curious', 'breadth', 'diverse',
    'variety', 'experiment', 'try new', 'discover'];
  const multitaskerKeywords = ['multitask', 'multi-task', 'juggle', 'parallel', 'many projects',
    'context switch', 'wear many hats', 'generalist'];

  const deepScore = deepFocusKeywords.filter(k => lower.includes(k)).length;
  const explorerScore = explorerKeywords.filter(k => lower.includes(k)).length;
  const multiScore = multitaskerKeywords.filter(k => lower.includes(k)).length;

  if (deepScore >= explorerScore && deepScore >= multiScore && deepScore > 0) return 'deep-focus';
  if (explorerScore >= multiScore && explorerScore > 0) return 'explorer';
  if (multiScore > 0) return 'multitasker';

  // Default based on content length — short, decisive = deep-focus
  return 'deep-focus';
}
