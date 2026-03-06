#!/usr/bin/env node
/**
 * 🔒 Skulk Skill Scanner
 * Analyzes OpenClaw skill folders for security red flags.
 *
 * Usage: node scanner.js <path-to-skill-folder> [--json] [--summary] [--verbose]
 */

const fs = require('fs');
const path = require('path');

// =========================================
// Pattern Definitions
// =========================================

const SAFE_DOMAINS = [
  'github.com', 'raw.githubusercontent.com',
  'npmjs.com', 'registry.npmjs.org',
  'clawhub.com', 'clawhub.ai',
  'moltbook.com',
  'skulk.ai',
  'api.openai.com', 'api.anthropic.com',
  'googleapis.com',
];

const DEFAULT_IGNORE_PREFIXES = [
  '.clawhub/',
  'node_modules/',
  '.git/',
];

const DEFAULT_IGNORE_EXACT = new Set([
  '_meta.json',
]);

function isSafeDomain(hostname = '') {
  const h = hostname.toLowerCase();
  return SAFE_DOMAINS.some((d) => h === d || h.endsWith(`.${d}`));
}

function extractHostnames(text) {
  const out = [];
  const re = /https?:\/\/([^\s/:'"`]+)(?::\d+)?/gi;
  let m;
  while ((m = re.exec(text)) !== null) {
    out.push((m[1] || '').toLowerCase());
  }
  return out;
}

function hasUnsafeHostname(text) {
  const hosts = extractHostnames(text);
  if (hosts.length === 0) return false;
  return hosts.some((h) => !isSafeDomain(h));
}

const PATTERNS = {
  critical: [
    {
      id: 'exfil-webhook',
      name: 'Outbound data to external URL',
      patterns: [
        /(?:curl|wget|fetch|http\.request|axios|got)\s+[^\n]*(?:POST|PUT|PATCH)/gi,
        /webhook[s]?\s*[=:]\s*["'`]https?:\/\//gi,
        /(?:send|post|upload|exfil|forward)\s+(?:to|data|content|file|secret|key|token)\s+(?:to\s+)?(?:https?:\/\/|external|remote)/gi,
      ],
      description: 'Skill attempts to send data to external URLs',
      networkRule: true,
    },
    {
      id: 'credential-access',
      name: 'Credential/secret access',
      patterns: [
        /(?:cat|read|access|steal|copy|send|forward|exfil).*(?:\.ssh|authorized_keys|id_rsa|id_ed25519|\.env|credentials|secrets?\.|api[_-]?key|token|password)/gi,
        /(?:private[_-]?key|secret[_-]?key|access[_-]?token)\s*(?:=|:|\s+is\s+)/gi,
      ],
      description: 'Skill attempts to access credentials or secret files',
    },
    {
      id: 'ignore-safety',
      name: 'Override safety/system instructions',
      patterns: [
        /(?:ignore|override|bypass|disregard|forget)\s+(?:your|all|any|previous|system|safety)\s+(?:instructions|rules|guidelines|prompt|constraints|guardrails)/gi,
        /you\s+(?:are|must)\s+(?:now|no longer)\s+(?:a|an|my)\s+/gi,
        /(?:jailbreak|DAN|do anything now|roleplay as)/gi,
      ],
      description: 'Skill attempts to override agent safety guidelines',
    },
    {
      id: 'destructive-commands',
      name: 'Destructive system commands',
      patterns: [
        /(?:rm\s+-rf\s+[\/~]|mkfs|dd\s+if=|:\(\)\s*\{|fork\s*bomb)/gi,
        /(?:chmod\s+777|chmod\s+-R\s+777)\s+\//gi,
        /(?:DROP\s+TABLE|DROP\s+DATABASE|TRUNCATE|DELETE\s+FROM)\s+/gi,
      ],
      description: 'Skill contains destructive system commands',
    },
  ],

  high: [
    {
      id: 'obfuscation',
      name: 'Obfuscated content',
      patterns: [
        /(?:base64|atob|btoa)\s*[\(]/gi,
        /\\x[0-9a-f]{2}(?:\\x[0-9a-f]{2}){3,}/gi,
        /\\u[0-9a-f]{4}(?:\\u[0-9a-f]{4}){3,}/gi,
        /eval\s*\(/gi,
      ],
      description: 'Skill contains obfuscated or encoded content',
    },
    {
      id: 'network-access',
      name: 'Unrestricted network access',
      patterns: [
        /(?:curl|wget|fetch|http\.request|axios|got)\s+[^\n]*https?:\/\//gi,
        /(?:nc|netcat|ncat)\s+/gi,
        /(?:reverse\s+shell|bind\s+shell)/gi,
      ],
      description: 'Skill makes network requests to unknown domains',
      networkRule: true,
    },
    {
      id: 'env-scanning',
      name: 'Environment variable scanning',
      patterns: [
        /(?:^|\s)(?:printenv|env\s*\|\s*grep|set\s*\|\s*grep)\b/gim,
        /process\.env(?:\[|\.)/gi,
        /\$\{?\w*(?:KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)\w*\}?/gi,
        /os\.environ/gi,
      ],
      description: 'Skill scans environment variables for secrets',
    },
    {
      id: 'privilege-escalation',
      name: 'Privilege escalation',
      patterns: [
        /(?:sudo|su\s+-|doas)\s+/gi,
        /(?:chmod\s+[+u]s|setuid|setgid)/gi,
        /(?:\/etc\/passwd|\/etc\/shadow)/gi,
      ],
      description: 'Skill attempts privilege escalation',
    },
    {
      id: 'hidden-instructions',
      name: 'Hidden/invisible instructions',
      patterns: [
        /<!--.*(?:ignore|override|execute|send|forward).*-->/gis,
        /\u200b|\u200c|\u200d|\ufeff/g,
      ],
      description: 'Skill contains hidden instructions in comments or invisible characters',
    },
  ],

  medium: [
    {
      id: 'file-system-write',
      name: 'File system writes outside workspace',
      patterns: [
        /(?:write|create|save|copy|mv|cp)\s+.*(?:\/etc\/|\/usr\/|\/var\/|\/tmp\/|\/root\/(?!\.openclaw))/gi,
        /(?:>>?\s*(?:\/etc\/|\/usr\/|\/var\/))/gi,
      ],
      description: 'Skill writes files outside the workspace',
    },
    {
      id: 'external-skill-install',
      name: 'Installs other skills/packages',
      patterns: [
        /(?:clawhub|npm|pip|apt|brew)\s+install\s+/gi,
        /npx\s+/gi,
      ],
      description: 'Skill installs additional packages or skills (supply chain risk)',
    },
    {
      id: 'messaging-actions',
      name: 'Sends messages on behalf of user',
      patterns: [
        /(?:send\s+(?:a\s+)?(?:message|email|dm|notification)|post\s+(?:to|on)\s+(?:twitter|x\.com|discord|slack|moltbook))/gi,
        /action.*[=:].*["']send["']/gi,
      ],
      description: 'Skill sends messages or posts on external platforms',
    },
    {
      id: 'cron-scheduling',
      name: 'Creates scheduled tasks',
      patterns: [
        /(?:cron|schedule|setInterval|setTimeout|at\s+\d)/gi,
        /systemd.*service|systemctl.*enable/gi,
      ],
      description: 'Skill creates persistent scheduled tasks',
    },
  ],

  info: [
    {
      id: 'api-key-reference',
      name: 'References API keys',
      patterns: [
        /api[_-]?key/gi,
        /bearer\s+/gi,
        /authorization:\s+/gi,
      ],
      description: 'Skill references API keys (verify they are user-provided, not hardcoded)',
    },
    {
      id: 'skill-scope',
      name: 'Broad tool access',
      patterns: [
        /allowed-tools:\s*\[.*(?:exec|browser|message|gateway).*\]/gi,
        /tools?:\s*["']?(?:full|all)["']?/gi,
      ],
      description: 'Skill requests broad tool access',
    },
  ],
};

function shouldIgnore(relPath, options) {
  const normalized = relPath.replace(/\\/g, '/');

  if (!options.includeSelf && normalized === 'scripts/scanner.js') return true;
  if (DEFAULT_IGNORE_EXACT.has(normalized)) return true;
  if (DEFAULT_IGNORE_PREFIXES.some((p) => normalized.startsWith(p))) return true;

  for (const raw of options.ignore || []) {
    const rule = (raw || '').trim();
    if (!rule) continue;
    if (rule.endsWith('/')) {
      if (normalized.startsWith(rule)) return true;
    } else {
      if (normalized === rule || normalized.includes(rule)) return true;
    }
  }

  return false;
}

function scanFile(filePath, content) {
  const findings = [];
  const lines = content.split('\n');

  for (const [severity, rules] of Object.entries(PATTERNS)) {
    for (const rule of rules) {
      for (const pattern of rule.patterns) {
        pattern.lastIndex = 0;
        let match;

        while ((match = pattern.exec(content)) !== null) {
          const beforeMatch = content.slice(0, match.index);
          const lineNum = beforeMatch.split('\n').length;
          const lineContent = lines[lineNum - 1]?.trim() || '';

          if (rule.networkRule) {
            const candidate = `${match[0]} ${lineContent}`;
            if (!hasUnsafeHostname(candidate)) {
              continue;
            }
          }

          findings.push({
            severity,
            ruleId: rule.id,
            ruleName: rule.name,
            description: rule.description,
            file: filePath,
            line: lineNum,
            lineContent: lineContent.slice(0, 120),
            match: match[0].slice(0, 80),
          });
        }
      }
    }
  }

  return findings;
}

function scanSkill(skillPath, options = {}) {
  const results = {
    path: skillPath,
    name: path.basename(skillPath),
    scannedAt: new Date().toISOString(),
    files: [],
    findings: [],
    score: 100,
    verdict: 'PASS',
  };

  function walk(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      const relPath = path.relative(skillPath, fullPath).replace(/\\/g, '/');

      if (entry.isDirectory()) {
        if (!shouldIgnore(`${relPath}/`, options)) walk(fullPath);
      } else {
        if (shouldIgnore(relPath, options)) continue;
        const ext = path.extname(entry.name).toLowerCase();
        if (
          ['.md', '.txt', '.sh', '.py', '.js', '.ts', '.json', '.yaml', '.yml', '.toml', '.html'].includes(ext) ||
          entry.name === 'SKILL.md'
        ) {
          results.files.push(fullPath);
        }
      }
    }
  }

  if (!fs.existsSync(skillPath)) {
    console.error(`❌ Path not found: ${skillPath}`);
    process.exit(1);
  }

  walk(skillPath);

  const skillMd = path.join(skillPath, 'SKILL.md');
  if (!fs.existsSync(skillMd)) {
    results.findings.push({
      severity: 'high',
      ruleId: 'missing-skill-md',
      ruleName: 'Missing SKILL.md',
      description: 'No SKILL.md found — this is required for a valid skill',
      file: skillPath,
      line: 0,
      lineContent: '',
      match: '',
    });
  }

  for (const file of results.files) {
    try {
      const content = fs.readFileSync(file, 'utf-8');
      const relPath = path.relative(skillPath, file).replace(/\\/g, '/');
      const fileFindings = scanFile(relPath, content);
      results.findings.push(...fileFindings);
    } catch {
      // skip unreadable/binary files
    }
  }

  const weights = { critical: 30, high: 15, medium: 5, info: 0 };
  const deductions = {};
  for (const f of results.findings) {
    if (!deductions[f.ruleId]) deductions[f.ruleId] = weights[f.severity] || 0;
  }
  const totalDeduction = Object.values(deductions).reduce((a, b) => a + b, 0);
  results.score = Math.max(0, 100 - totalDeduction);

  if (results.findings.some((f) => f.severity === 'critical')) {
    results.verdict = 'FAIL';
  } else if (results.score < 50) {
    results.verdict = 'FAIL';
  } else if (results.score < 75) {
    results.verdict = 'WARN';
  } else {
    results.verdict = 'PASS';
  }

  return results;
}

function printResults(results, verbose = false) {
  const icons = { critical: '🔴', high: '🟠', medium: '🟡', info: '🔵' };

  console.log(`\n🔒 Skulk Skill Scanner`);
  console.log(`${'─'.repeat(50)}`);
  console.log(`Skill:    ${results.name}`);
  console.log(`Path:     ${results.path}`);
  console.log(`Files:    ${results.files.length} scanned`);
  console.log(`Scanned:  ${results.scannedAt}`);
  console.log(`${'─'.repeat(50)}`);

  const grouped = { critical: [], high: [], medium: [], info: [] };
  for (const f of results.findings) grouped[f.severity].push(f);

  for (const severity of ['critical', 'high', 'medium', 'info']) {
    const findings = grouped[severity];
    if (findings.length === 0) continue;

    console.log(`\n${icons[severity]} ${severity.toUpperCase()} (${findings.length})`);

    const byRule = {};
    for (const f of findings) {
      if (!byRule[f.ruleId]) byRule[f.ruleId] = [];
      byRule[f.ruleId].push(f);
    }

    for (const ruleFindings of Object.values(byRule)) {
      const first = ruleFindings[0];
      console.log(`   ${first.ruleName} (${ruleFindings.length}x)`);
      console.log(`   ${first.description}`);
      if (verbose) {
        for (const f of ruleFindings.slice(0, 5)) {
          console.log(`     → ${f.file}:${f.line}  ${f.lineContent}`);
        }
        if (ruleFindings.length > 5) {
          console.log(`     ... and ${ruleFindings.length - 5} more`);
        }
      }
    }
  }

  console.log(`\n${'─'.repeat(50)}`);
  const verdictColors = { PASS: '✅', WARN: '⚠️', FAIL: '❌' };
  console.log(`Score:    ${results.score}/100`);
  console.log(`Verdict:  ${verdictColors[results.verdict]} ${results.verdict}`);
  console.log(`${'─'.repeat(50)}\n`);
}

function printSummary(results) {
  const counts = { critical: 0, high: 0, medium: 0, info: 0 };
  for (const f of results.findings) counts[f.severity]++;
  console.log(`${results.verdict} score=${results.score} files=${results.files.length} critical=${counts.critical} high=${counts.high} medium=${counts.medium} info=${counts.info}`);
}

// =========================================
// Main
// =========================================

const args = process.argv.slice(2);
const skillPath = args.find((a) => !a.startsWith('--'));
const jsonOutput = args.includes('--json');
const summary = args.includes('--summary');
const verbose = args.includes('--verbose') || args.includes('-v');
const includeSelf = args.includes('--include-self');
const ignore = [];

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--ignore' && args[i + 1]) {
    ignore.push(args[i + 1]);
    i++;
  }
}

if (!skillPath) {
  console.log(`🔒 Skulk Skill Scanner

Usage: node scanner.js <path-to-skill> [--json] [--summary] [--verbose] [--include-self] [--ignore <path>]

Scans an OpenClaw skill folder for security red flags.
Checks for: data exfiltration, credential access, prompt injection,
destructive commands, obfuscation, privilege escalation, and more.

Examples:
  node scanner.js ./skills/my-skill
  node scanner.js ./skills/my-skill --verbose
  node scanner.js ./skills/my-skill --json
  node scanner.js ./skills/my-skill --summary
  node scanner.js ./skills/my-skill --ignore scripts/
  node scanner.js ./skills/skulk-skill-scanner --include-self
`);
  process.exit(0);
}

const results = scanSkill(path.resolve(skillPath), { includeSelf, ignore });

if (jsonOutput) {
  console.log(JSON.stringify(results, null, 2));
} else if (summary) {
  printSummary(results);
} else {
  printResults(results, verbose);
}

process.exit(results.verdict === 'FAIL' ? 1 : 0);
