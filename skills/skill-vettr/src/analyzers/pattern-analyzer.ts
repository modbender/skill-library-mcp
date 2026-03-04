import { Finding, FindingCategory } from '../types.js';
import { generateFindingId, truncateEvidence } from '../utils/sanitise.js';

interface PatternDef {
  pattern: RegExp;
  category: FindingCategory;
  severity: Finding['severity'];
  message: string;
  cwe?: string;
}

/**
 * Regex-based analyser for threats that AST parsing can't detect:
 * - Prompt injection (natural language in strings/comments)
 * - Encoded escape sequences (unicode/hex obfuscation)
 * - Homoglyph attacks (Cyrillic lookalike characters)
 *
 * Code-structural patterns (eval, exec, spawn, etc.) are handled
 * by AstAnalyzer — they are NOT duplicated here.
 */
export class PatternAnalyzer {
  private patterns: PatternDef[] = [
    // -- Prompt injection --
    {
      pattern: /ignore\s+(all\s+)?previous\s+(instructions|rules|prompts)/i,
      category: 'PROMPT_INJECTION',
      severity: 'CRITICAL',
      message: 'Prompt injection: instruction override attempt',
      cwe: 'CWE-74',
    },
    {
      pattern: /disregard\s+(your\s+)?(training|instructions|guidelines)/i,
      category: 'PROMPT_INJECTION',
      severity: 'CRITICAL',
      message: 'Prompt injection: training override attempt',
      cwe: 'CWE-74',
    },
    {
      pattern: /you\s+are\s+now\s+[a-z]+.*?(ignore|forget|bypass)/i,
      category: 'PROMPT_INJECTION',
      severity: 'CRITICAL',
      message: 'Prompt injection: persona hijack attempt',
      cwe: 'CWE-74',
    },
    {
      pattern: /<\|im_start\|>|<\|system\|>|\[INST\]|\[\/INST\]/i,
      category: 'PROMPT_INJECTION',
      severity: 'CRITICAL',
      message: 'Prompt injection: model-specific control token',
      cwe: 'CWE-74',
    },
    {
      pattern: /\{\{system[_\s]?(message|prompt)\}\}/i,
      category: 'PROMPT_INJECTION',
      severity: 'CRITICAL',
      message: 'Prompt injection: template injection attempt',
      cwe: 'CWE-74',
    },

    // -- Encoded dangerous function names --
    {
      pattern: /\\u0065\\u0076\\u0061\\u006c/i, // 'eval' in unicode
      category: 'CODE_OBFUSCATION',
      severity: 'CRITICAL',
      message: 'Unicode-escaped dangerous function name (eval)',
      cwe: 'CWE-95',
    },
    {
      pattern: /\\x65\\x76\\x61\\x6c/i, // 'eval' in hex
      category: 'CODE_OBFUSCATION',
      severity: 'CRITICAL',
      message: 'Hex-escaped dangerous function name (eval)',
      cwe: 'CWE-95',
    },

    // -- Credential path access (as string literals in non-code contexts) --
    {
      pattern: /\.ssh[/\\]/i,
      category: 'PERMISSION_RISK',
      severity: 'CRITICAL',
      message: 'SSH directory path reference',
      cwe: 'CWE-522',
    },
    {
      pattern: /\.aws[/\\]|\.azure[/\\]|\.gcp[/\\]/i,
      category: 'PERMISSION_RISK',
      severity: 'CRITICAL',
      message: 'Cloud credentials directory path reference',
      cwe: 'CWE-522',
    },
    {
      pattern: /keychain|credential\s*manager|secret\s*store/i,
      category: 'PERMISSION_RISK',
      severity: 'CRITICAL',
      message: 'System credential store access',
      cwe: 'CWE-522',
    },
  ];

  // Cyrillic characters that look identical to ASCII
  private homoglyphs: Record<string, string> = {
    '\u0430': 'a', // Cyrillic а
    '\u0435': 'e', // Cyrillic е
    '\u043e': 'o', // Cyrillic о
    '\u0440': 'p', // Cyrillic р
    '\u0441': 'c', // Cyrillic с
    '\u0445': 'x', // Cyrillic х
    '\u0455': 's', // Cyrillic ѕ
    '\u0456': 'i', // Cyrillic і
  };

  private homoglyphChars: Set<string>;

  constructor() {
    this.homoglyphChars = new Set(Object.keys(this.homoglyphs));
  }

  analyze(filePath: string, content: string): Finding[] {
    const findings: Finding[] = [];

    // Homoglyph detection (whole-file scan)
    findings.push(...this.detectHomoglyphs(filePath, content));

    const lines = content.split('\n');
    let inBlockComment = false;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (line === undefined) continue;

      // Track block comments
      const { code, stillInBlock } = this.stripComments(line, inBlockComment);
      inBlockComment = stillInBlock;

      // Skip lines that are entirely comments
      if (code.trim() === '') continue;

      for (const def of this.patterns) {
        if (def.pattern.test(code)) {
          findings.push({
            id: generateFindingId(),
            severity: def.severity,
            category: def.category,
            message: def.message,
            file: filePath,
            line: i + 1,
            evidence: truncateEvidence(code),
            cwe: def.cwe,
          });
        }
      }
    }

    return findings;
  }

  /**
   * Strip comments from a line, tracking block comment state.
   * Returns the code portion and whether we're still inside a block comment.
   */
  private stripComments(line: string, inBlock: boolean): { code: string; stillInBlock: boolean } {
    let result = '';
    let i = 0;
    let insideBlock = inBlock;

    while (i < line.length) {
      if (insideBlock) {
        // Look for end of block comment
        const endIdx = line.indexOf('*/', i);
        if (endIdx === -1) {
          // Entire rest of line is comment
          return { code: result, stillInBlock: true };
        }
        i = endIdx + 2;
        insideBlock = false;
      } else {
        // Check for string literals — skip over them to avoid stripping // inside strings
        const ch = line[i];
        if (ch === '"' || ch === "'" || ch === '`') {
          const closeIdx = this.findStringEnd(line, i, ch);
          result += line.substring(i, closeIdx + 1);
          i = closeIdx + 1;
        } else if (line[i] === '/' && line[i + 1] === '/') {
          // Line comment — rest of line is comment
          return { code: result, stillInBlock: false };
        } else if (line[i] === '/' && line[i + 1] === '*') {
          // Block comment start
          insideBlock = true;
          i += 2;
        } else {
          result += ch;
          i++;
        }
      }
    }

    return { code: result, stillInBlock: insideBlock };
  }

  /** Find the closing quote, handling backslash escapes. */
  private findStringEnd(line: string, start: number, quote: string): number {
    for (let i = start + 1; i < line.length; i++) {
      if (line[i] === '\\') {
        i++; // skip escaped character
      } else if (line[i] === quote) {
        return i;
      }
    }
    return line.length - 1; // unterminated string
  }

  /**
   * Detect homoglyph attacks by finding identifiers that contain
   * Cyrillic lookalike characters. When normalised to ASCII, if
   * the resulting word matches a dangerous function name, flag it.
   */
  private detectHomoglyphs(filePath: string, content: string): Finding[] {
    const findings: Finding[] = [];
    const dangerousFunctions = new Set(['eval', 'exec', 'Function', 'spawn', 'fetch', 'require']);

    // Find all word-like tokens that contain at least one homoglyph character
    const wordPattern = /[\w\u0400-\u04FF]+/g;
    let match;

    const lines = content.split('\n');

    for (let lineIdx = 0; lineIdx < lines.length; lineIdx++) {
      const line = lines[lineIdx];
      if (line === undefined) continue;

      wordPattern.lastIndex = 0;
      while ((match = wordPattern.exec(line)) !== null) {
        const word = match[0];

        // Check if word contains any homoglyph characters
        let hasHomoglyph = false;
        for (const ch of word) {
          if (this.homoglyphChars.has(ch)) {
            hasHomoglyph = true;
            break;
          }
        }
        if (!hasHomoglyph) continue;

        // Normalise: replace each homoglyph with its ASCII equivalent
        let normalised = '';
        for (const ch of word) {
          normalised += this.homoglyphs[ch] ?? ch;
        }

        // Check if the normalised word is a dangerous function name
        if (dangerousFunctions.has(normalised)) {
          findings.push({
            id: generateFindingId(),
            severity: 'CRITICAL',
            category: 'CODE_OBFUSCATION',
            message: `Homoglyph attack: "${word}" looks like "${normalised}"`,
            file: filePath,
            line: lineIdx + 1,
            evidence: truncateEvidence(word),
            cwe: 'CWE-176',
          });
        }
      }
    }

    return findings;
  }
}
