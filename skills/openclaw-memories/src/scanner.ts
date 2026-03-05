/**
 * Unicode Smuggling Scanner — detects invisible prompt injection in skill files.
 * Based on wunderwuzzi23's research: https://embracethered.com/blog/posts/2026/scary-agent-skills/
 *
 * Detects: Unicode Tags (U+E0000-E007F), Zero-Width chars, Bidi marks, Variation Selectors.
 * Unicode Tags are the primary attack vector — they encode hidden ASCII instructions
 * that models like Claude, Gemini, Grok interpret but humans can't see.
 */

export type Severity = 'info' | 'medium' | 'high' | 'critical';

export interface ScanHit {
  line: number;
  column: number;
  char: string;
  codePoint: number;
  category: string;
  severity: Severity;
}

export interface ScanResult {
  file: string;
  clean: boolean;
  severity: Severity;
  hits: ScanHit[];
  decodedTags?: string; // Hidden ASCII message decoded from Unicode Tags
  summary: string;
}

// Unicode Tag codepoints decode to ASCII by subtracting 0xE0000
function decodeUnicodeTags(text: string): string {
  let decoded = '';
  for (let i = 0; i < text.length; i++) {
    const cp = text.codePointAt(i)!;
    if (cp >= 0xE0000 && cp <= 0xE007F) {
      decoded += String.fromCharCode(cp - 0xE0000);
    }
    if (cp > 0xFFFF) i++; // skip surrogate pair
  }
  return decoded;
}

function categorize(cp: number): string | null {
  if (cp >= 0xE0000 && cp <= 0xE007F) return 'unicode-tag';
  if (cp >= 0x200B && cp <= 0x200F) return 'zero-width';
  if (cp >= 0x202A && cp <= 0x202E) return 'bidi-format';  // LRE, RLE, PDF, LRO, RLO
  if (cp >= 0x2060 && cp <= 0x206F) return 'bidi-format';  // WJ, invisible operators, deprecated
  if (cp >= 0x2066 && cp <= 0x2069) return 'bidi-format';  // LRI, RLI, FSI, PDI
  if (cp === 0x061C) return 'bidi-format';                  // Arabic Letter Mark
  if (cp === 0xFEFF) return 'bom/zwnbsp';
  if (cp >= 0xFE00 && cp <= 0xFE0F) return 'variation-selector';
  if (cp >= 0xE0100 && cp <= 0xE01EF) return 'variation-selector-ext';
  if (cp >= 0x00AD && cp <= 0x00AD) return 'soft-hyphen';
  return null;
}

/** Scan a string for hidden Unicode characters. */
export function scanText(text: string, file = '<input>'): ScanResult {
  const hits: ScanHit[] = [];
  let tagRun = 0;
  let line = 1;
  let column = 1;

  for (let i = 0; i < text.length; i++) {
    const cp = text.codePointAt(i)!;
    const cat = categorize(cp);

    if (cp === 0x0A) { line++; column = 1; continue; }

    if (cat) {
      hits.push({
        line, column,
        char: `U+${cp.toString(16).toUpperCase().padStart(4, '0')}`,
        codePoint: cp,
        category: cat,
        severity: cat === 'unicode-tag' ? 'critical' : 'info',
      });
      if (cat === 'unicode-tag') tagRun++;
    }

    column++;
    if (cp > 0xFFFF) { i++; column++; } // surrogate pair
  }

  // Determine overall severity
  let severity: Severity = 'info';
  const tagCount = hits.filter(h => h.category === 'unicode-tag').length;
  const totalCount = hits.length;

  if (tagCount > 10) severity = 'critical';
  else if (totalCount > 100) severity = 'high';
  else if (totalCount > 10) severity = 'medium';
  else if (totalCount > 0) severity = 'info';

  // Decode hidden message from Unicode Tags
  const decoded = decodeUnicodeTags(text);

  const clean = hits.length === 0;
  const summary = clean
    ? 'Clean — no suspicious Unicode found'
    : `${hits.length} suspicious chars (${tagCount} tags, severity: ${severity})${decoded ? ` — decoded: "${decoded}"` : ''}`;

  return { file, clean, severity, hits, decodedTags: decoded || undefined, summary };
}

/** Scan a SKILL.md file content. */
export function scanSkill(content: string, path = 'SKILL.md'): ScanResult {
  return scanText(content, path);
}
