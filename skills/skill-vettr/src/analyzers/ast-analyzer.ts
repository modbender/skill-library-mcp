import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Parser, Language, Query } from 'web-tree-sitter';
import { Finding, FindingCategory } from '../types.js';
import { generateFindingId, truncateEvidence } from '../utils/sanitise.js';

interface RuleDef {
  query: string;
  category: FindingCategory;
  severity: Finding['severity'];
  message: string;
  cwe?: string;
  /** Name of the capture whose text to use as evidence. Defaults to first capture. */
  evidenceCapture?: string;
}

/**
 * AST-based code analyser using tree-sitter.
 *
 * Parses JS/TS source into a concrete syntax tree, then runs S-expression
 * queries to detect dangerous patterns structurally rather than with regex.
 * This eliminates false positives from comments, strings, and partial matches.
 */
export class AstAnalyzer {
  private parser!: Parser;
  private jsLang!: Language;
  private tsLang!: Language;
  private jsQueries: CompiledRule[] = [];
  private tsQueries: CompiledRule[] = [];
  private initialised = false;

  /** WASM artifacts required at runtime, relative to node_modules. */
  static readonly REQUIRED_WASM_PATHS = [
    path.join('tree-sitter-javascript', 'tree-sitter-javascript.wasm'),
    path.join('tree-sitter-typescript', 'tree-sitter-typescript.wasm'),
    path.join('web-tree-sitter', 'web-tree-sitter.wasm'),
  ];

  async init(): Promise<void> {
    if (this.initialised) return;

    // Resolve .wasm paths relative to this module, not cwd.
    const thisDir = path.dirname(fileURLToPath(import.meta.url));
    const nodeModules = path.resolve(thisDir, '..', '..', 'node_modules');

    // Verify WASM artifacts exist before attempting to load
    const missing: string[] = [];
    for (const wasmRelPath of AstAnalyzer.REQUIRED_WASM_PATHS) {
      const fullPath = path.join(nodeModules, wasmRelPath);
      try {
        await fs.access(fullPath);
      } catch {
        missing.push(wasmRelPath);
      }
    }
    if (missing.length > 0) {
      throw new Error(
        `Missing required WASM artifacts (run "npm install" to fix):\n${missing.map((p) => `  - ${p}`).join('\n')}`,
      );
    }

    await Parser.init();
    this.parser = new Parser();

    this.jsLang = await Language.load(
      path.join(nodeModules, 'tree-sitter-javascript', 'tree-sitter-javascript.wasm'),
    );
    this.tsLang = await Language.load(
      path.join(nodeModules, 'tree-sitter-typescript', 'tree-sitter-typescript.wasm'),
    );

    this.jsQueries = this.compileRules(this.jsLang, JS_RULES);
    this.tsQueries = this.compileRules(this.tsLang, JS_RULES);

    this.initialised = true;
  }

  analyze(filePath: string, content: string, ext: string): Finding[] {
    const isTs = ext === '.ts' || ext === '.mts' || ext === '.cts';
    const lang = isTs ? this.tsLang : this.jsLang;
    const rules = isTs ? this.tsQueries : this.jsQueries;

    this.parser.setLanguage(lang);
    const tree = this.parser.parse(content);
    if (!tree) return [];

    const findings: Finding[] = [];

    try {
      for (const { query, rule } of rules) {
        const matches = query.matches(tree.rootNode);
        for (const match of matches) {
          const evidenceCapture = rule.evidenceCapture
            ? match.captures.find((c) => c.name === rule.evidenceCapture)
            : match.captures[0];

          const node = evidenceCapture?.node ?? match.captures[0]?.node;
          if (!node) continue;

          findings.push({
            id: generateFindingId(),
            severity: rule.severity,
            category: rule.category,
            message: rule.message,
            file: filePath,
            line: node.startPosition.row + 1,
            evidence: truncateEvidence(node.text),
            cwe: rule.cwe,
          });
        }
      }
    } finally {
      tree.delete();
    }

    return findings;
  }

  /** Extract network call URLs from AST. Only detects fetch() with literal URL strings. */
  extractNetworkCalls(filePath: string, content: string, ext: string): { url: string; line: number }[] {
    const isTs = ext === '.ts' || ext === '.mts' || ext === '.cts';
    const lang = isTs ? this.tsLang : this.jsLang;

    this.parser.setLanguage(lang);
    const tree = this.parser.parse(content);
    if (!tree) return [];

    const calls: { url: string; line: number }[] = [];

    // Match fetch('url') with literal string argument only
    // Note: axios, http module, and dynamic URLs are NOT detected
    const query = new Query(lang, NETWORK_CALL_QUERY);
    try {
      const matches = query.matches(tree.rootNode);
      for (const match of matches) {
        const urlCapture = match.captures.find((c) => c.name === 'url');
        if (!urlCapture) continue;

        // Strip surrounding quotes from string literal
        const raw = urlCapture.node.text;
        const url = raw.replace(/^['"`]|['"`]$/g, '');
        if (url.startsWith('http://') || url.startsWith('https://')) {
          calls.push({ url, line: urlCapture.node.startPosition.row + 1 });
        }
      }
    } finally {
      query.delete();
      tree.delete();
    }

    return calls;
  }

  private compileRules(lang: Language, rules: RuleDef[]): CompiledRule[] {
    const compiled: CompiledRule[] = [];
    for (const rule of rules) {
      try {
        const query = new Query(lang, rule.query);
        compiled.push({ query, rule });
      } catch {
        // Query may use JS-specific nodes that don't exist in TS grammar or vice versa.
        // Skip silently — this is expected.
      }
    }
    return compiled;
  }
}

interface CompiledRule {
  query: Query;
  rule: RuleDef;
}

// ---------------------------------------------------------------------------
// Detection rules as tree-sitter S-expression queries
// ---------------------------------------------------------------------------

const JS_RULES: RuleDef[] = [
  // -- Arbitrary code execution --
  {
    query: `(call_expression function: (identifier) @fn (#eq? @fn "eval"))`,
    category: 'CODE_OBFUSCATION',
    severity: 'CRITICAL',
    message: 'eval() call — arbitrary code execution',
    cwe: 'CWE-95',
  },
  {
    query: `(new_expression constructor: (identifier) @fn (#eq? @fn "Function"))`,
    category: 'CODE_OBFUSCATION',
    severity: 'CRITICAL',
    message: 'new Function() — arbitrary code execution',
    cwe: 'CWE-95',
  },
  // Bracket-notation evasion: obj['eval'](...)
  {
    query: `(subscript_expression index: (string) @str (#match? @str "^['\\"](eval|Function|exec|execSync)['\\"]\$"))`,
    category: 'CODE_OBFUSCATION',
    severity: 'CRITICAL',
    message: 'Bracket-notation access to dangerous function — evasion technique',
    cwe: 'CWE-95',
  },

  // -- VM module (code execution without eval keyword) --
  {
    query: `(call_expression
      function: (member_expression
        property: (property_identifier) @method
        (#any-of? @method "runInThisContext" "runInNewContext" "compileFunction")))`,
    category: 'CODE_OBFUSCATION',
    severity: 'CRITICAL',
    message: 'vm module code execution',
    cwe: 'CWE-95',
    evidenceCapture: 'method',
  },

  // -- Shell injection --
  {
    query: `(call_expression
      function: (identifier) @fn
      arguments: (arguments (string) @arg)
      (#eq? @fn "exec"))`,
    category: 'SHELL_INJECTION',
    severity: 'CRITICAL',
    message: 'exec() with string argument — shell injection risk',
    cwe: 'CWE-78',
  },
  {
    query: `(call_expression
      function: (member_expression
        property: (property_identifier) @method)
      arguments: (arguments (string) @arg)
      (#eq? @method "exec"))`,
    category: 'SHELL_INJECTION',
    severity: 'CRITICAL',
    message: 'exec() with string argument — shell injection risk',
    cwe: 'CWE-78',
    evidenceCapture: 'arg',
  },
  {
    query: `(call_expression function: (identifier) @fn (#eq? @fn "execSync"))`,
    category: 'SHELL_INJECTION',
    severity: 'WARNING',
    message: 'execSync() — synchronous shell execution',
    cwe: 'CWE-78',
  },
  {
    query: `(call_expression
      function: (member_expression
        property: (property_identifier) @method)
      (#eq? @method "execSync"))`,
    category: 'SHELL_INJECTION',
    severity: 'WARNING',
    message: 'execSync() — synchronous shell execution',
    cwe: 'CWE-78',
  },

  // -- child_process imports --
  {
    query: `(import_statement
      source: (string) @mod
      (#match? @mod "child_process"))`,
    category: 'SHELL_INJECTION',
    severity: 'WARNING',
    message: 'child_process module import',
    cwe: 'CWE-78',
  },
  {
    query: `(call_expression
      function: (identifier) @fn
      arguments: (arguments (string) @mod (#match? @mod "child_process"))
      (#eq? @fn "require"))`,
    category: 'SHELL_INJECTION',
    severity: 'WARNING',
    message: 'child_process module require',
    cwe: 'CWE-78',
    evidenceCapture: 'mod',
  },

  // -- Spawn with shell --
  {
    query: `(call_expression
      function: (identifier) @fn
      arguments: (arguments
        (string) @shell
        (#match? @shell "(bash|sh|cmd|cmd\\\\.exe|powershell|powershell\\\\.exe)"))
      (#eq? @fn "spawn"))`,
    category: 'SHELL_INJECTION',
    severity: 'WARNING',
    message: 'spawn() with shell process',
    cwe: 'CWE-78',
    evidenceCapture: 'shell',
  },

  // -- Dynamic require (non-literal argument) --
  {
    query: `(call_expression
      function: (identifier) @fn
      arguments: (arguments (identifier) @arg)
      (#eq? @fn "require"))`,
    category: 'CODE_OBFUSCATION',
    severity: 'WARNING',
    message: 'Dynamic require() with variable argument — cannot statically verify module',
    cwe: 'CWE-829',
    evidenceCapture: 'arg',
  },
  {
    query: `(call_expression
      function: (identifier) @fn
      arguments: (arguments (template_string) @arg)
      (#eq? @fn "require"))`,
    category: 'CODE_OBFUSCATION',
    severity: 'WARNING',
    message: 'Dynamic require() with template string — cannot statically verify module',
    cwe: 'CWE-829',
    evidenceCapture: 'arg',
  },

  // -- Credential access --
  {
    query: `(member_expression
      object: (member_expression
        object: (identifier) @obj
        property: (property_identifier) @prop
        (#eq? @obj "process")
        (#eq? @prop "env"))
      property: (property_identifier) @key)`,
    category: 'PERMISSION_RISK',
    severity: 'INFO',
    message: 'process.env access — check if accessing sensitive keys',
    cwe: 'CWE-522',
    evidenceCapture: 'key',
  },

  // -- System persistence --
  {
    query: `(call_expression
      function: (identifier) @fn
      arguments: (arguments (string) @arg)
      (#eq? @fn "exec")
      (#match? @arg "crontab|launchctl|systemctl\\\\s+enable|chkconfig"))`,
    category: 'PERMISSION_RISK',
    severity: 'CRITICAL',
    message: 'System persistence mechanism via shell command',
    cwe: 'CWE-912',
    evidenceCapture: 'arg',
  },

  // -- Prototype pollution --
  {
    query: `(assignment_expression
      left: (member_expression
        property: (property_identifier) @prop
        (#any-of? @prop "__proto__")))`,
    category: 'CODE_OBFUSCATION',
    severity: 'WARNING',
    message: '__proto__ assignment — prototype pollution risk',
    cwe: 'CWE-1321',
  },
];

const NETWORK_CALL_QUERY = `
  (call_expression
    function: (identifier) @fn
    arguments: (arguments (string) @url)
    (#eq? @fn "fetch"))
`;
