#!/usr/bin/env node
/**
 * Skill Auditor v2.0 — Enhanced security scanner for OpenClaw skills
 * Usage: node scan-skill.js <skill-directory> [options]
 * 
 * Options:
 *   --json <file>         Output results in JSON format
 *   --format sarif        Output in SARIF format for GitHub Code Scanning
 *   --mode <mode>         Detection mode: strict|balanced|permissive (default: balanced)
 *   --use-virustotal     Enable VirusTotal binary scanning (requires VIRUSTOTAL_API_KEY)
 *   --use-llm           Enable LLM semantic analysis (requires OpenClaw gateway)
 *   --custom-rules <dir> Additional YARA rules directory
 *   --fail-on-findings  Exit with code 1 if HIGH/CRITICAL findings found
 *   --help              Show this help message
 * 
 * Exit codes: 0 = clean/low findings, 1 = significant findings, 2 = error
 */

const fs = require('fs');
const path = require('path');

// ─── Import Analyzers (with graceful fallback) ─────────────────────

const staticAnalyzer = require('./analyzers/static.js');

let astAnalyzer, vtAnalyzer, llmAnalyzer, sarifUtils;
let yaraSupport = false;

try {
  astAnalyzer = require('./analyzers/ast-python.js');
} catch (e) {
  astAnalyzer = null;
}

try {
  vtAnalyzer = require('./analyzers/virustotal.js');
} catch (e) {
  vtAnalyzer = null;
}

try {
  llmAnalyzer = require('./analyzers/llm-semantic.js');
} catch (e) {
  llmAnalyzer = null;
}

try {
  sarifUtils = require('./utils/sarif.js');
} catch (e) {
  sarifUtils = null;
}

// Check for YARA support
try {
  require('yara');
  yaraSupport = true;
} catch (e) {
  yaraSupport = false;
}

// ─── File Discovery ────────────────────────────────────────────────

function discoverFiles(dir) {
  const files = [];
  function walk(d) {
    let entries;
    try { entries = fs.readdirSync(d, { withFileTypes: true }); } catch { return; }
    for (const entry of entries) {
      const full = path.join(d, entry.name);
      if (entry.isDirectory()) {
        if (entry.name === 'node_modules' || entry.name === '.git') continue;
        walk(full);
      } else {
        files.push(full);
      }
    }
  }
  walk(dir);
  return files;
}

// ─── Skill Metadata Parsing ───────────────────────────────────────

function parseSkillMd(skillDir) {
  const skillMdPath = path.join(skillDir, 'SKILL.md');
  if (!fs.existsSync(skillMdPath)) {
    return { name: 'unknown', description: 'No SKILL.md found', hasSkillMd: false, fullContent: '' };
  }

  const content = fs.readFileSync(skillMdPath, 'utf-8');
  const fmMatch = content.match(/^---\s*\n([\s\S]*?)\n---/);
  if (!fmMatch) {
    return { name: 'unknown', description: 'No frontmatter', hasSkillMd: true, fullContent: content };
  }

  const fm = fmMatch[1];
  const nameMatch = fm.match(/^name:\s*(.+)$/m);
  const descMatch = fm.match(/^description:\s*(.+)$/m);

  return {
    name: nameMatch ? nameMatch[1].trim() : 'unknown',
    description: descMatch ? descMatch[1].trim().replace(/^["']|["']$/g, '') : 'No description',
    hasSkillMd: true,
    fullContent: content
  };
}

// ─── Intent-Aware Finding Analysis ─────────────────────────────────

function applyIntentMatching(findings, skillMeta) {
  if (!skillMeta.hasSkillMd || !skillMeta.fullContent) return findings;

  const desc = (skillMeta.description + '\n' + skillMeta.fullContent).toLowerCase();

  // Build intent patterns: what files/behaviors does the skill say it touches?
  const INTENT_PATTERNS = [
    { fileRef: /SOUL\.md/i, descMatch: /soul\.md/i },
    { fileRef: /AGENTS\.md/i, descMatch: /agents\.md/i },
    { fileRef: /TOOLS\.md/i, descMatch: /tools\.md/i },
    { fileRef: /MEMORY\.md/i, descMatch: /memory\.md/i },
    { fileRef: /HEARTBEAT\.md/i, descMatch: /heartbeat\.md/i },
    { fileRef: /USER\.md/i, descMatch: /user\.md/i },
    { fileRef: /memory\//i, descMatch: /memory\//i },
    { fileRef: /\.learnings/i, descMatch: /\.learnings/i },
    { fileRef: /sessions_send|sessions_spawn/i, descMatch: /sessions?_(?:send|spawn|list|history)/i },
    { fileRef: /cron|schedul/i, descMatch: /cron|schedul|hook/i },
    { fileRef: /CLAUDE\.md/i, descMatch: /claude\.md/i },
    { fileRef: /copilot-instructions/i, descMatch: /copilot-instructions/i },
  ];

  // Purpose-keyword patterns
  const PURPOSE_PATTERNS = [
    {
      purposeMatch: /\b(?:compress|optimi[zs]e|reduce\s*tokens?|token\s*sav|minif|compact|shrink|ai.?efficient)\b/i,
      expectedCategories: ['File Access', 'Sensitive File Access', 'Persistence'],
      expectedIds: ['memory-file-access', 'memory-write', 'path-traversal', 'homedir-access']
    },
    {
      purposeMatch: /\b(?:modif(?:y|ies)\s*(?:ai\s*)?behavio[ur]|persistent\s*mode|ai.?writing|notation|instruction)\b/i,
      expectedCategories: ['Persistence', 'Sensitive File Access', 'Prompt Injection'],
      expectedIds: ['memory-write', 'prompt-injection-system', 'prompt-injection-new-instructions']
    },
    {
      purposeMatch: /\b(?:audit\s*model|detect\s*model|model\s*(?:audit|detect|cost|compar)|cost\s*(?:analy|calculat|compar))\b/i,
      expectedCategories: ['File Access', 'Sensitive File Access'],
      expectedIds: ['memory-file-access', 'homedir-access', 'config-modification']
    },
    {
      purposeMatch: /\b(?:workspace|organiz|clean\s*up|restructur|format\s*files?)\b/i,
      expectedCategories: ['File Access', 'Sensitive File Access'],
      expectedIds: ['memory-file-access', 'path-traversal', 'homedir-access']
    }
  ];

  const matchedPurposes = PURPOSE_PATTERNS.filter(pp => pp.purposeMatch.test(desc));
  const purposeExpectedCategories = new Set();
  const purposeExpectedIds = new Set();
  for (const pp of matchedPurposes) {
    pp.expectedCategories.forEach(c => purposeExpectedCategories.add(c));
    pp.expectedIds.forEach(id => purposeExpectedIds.add(id));
  }

  const severityDowngrade = { critical: 'medium', high: 'low', medium: 'low', low: 'low' };

  return findings.map(f => {
    let matched = false;

    // Method 1: Direct file-reference matching
    for (const ip of INTENT_PATTERNS) {
      if (ip.fileRef.test(f.snippet) || ip.fileRef.test(f.explanation)) {
        if (ip.descMatch.test(desc)) {
          matched = true;
          break;
        }
      }
    }

    // Method 2: Purpose-keyword matching
    if (!matched && (purposeExpectedCategories.has(f.category) || purposeExpectedIds.has(f.id))) {
      matched = true;
    }

    if (matched) {
      return {
        ...f,
        intentMatch: true,
        originalSeverity: f.originalSeverity || f.severity,
        severity: severityDowngrade[f.severity] || f.severity,
        explanation: f.explanation + ' ⚡ Expected behavior — matches skill\'s stated purpose'
      };
    } else {
      const sensitiveCategories = ['Sensitive File Access', 'Persistence', 'Data Exfiltration', 'Privilege Escalation'];
      const note = sensitiveCategories.includes(f.category)
        ? ' ⚠️ Undisclosed — not mentioned in skill description'
        : '';
      return {
        ...f,
        intentMatch: false,
        explanation: f.explanation + note
      };
    }
  });
}

// ─── Risk Scoring ──────────────────────────────────────────────────

function calculateRisk(findings) {
  const unmatched = findings.filter(f => !f.intentMatch);
  const counts = { critical: 0, high: 0, medium: 0, low: 0 };
  const categories = new Set();

  for (const f of unmatched) {
    counts[f.severity] = (counts[f.severity] || 0) + 1;
    categories.add(f.category);
  }

  const hasObfuscation = categories.has('Obfuscation');
  const hasDataAccess = categories.has('Sensitive File Access') || categories.has('Data Exfiltration');
  const hasPromptInjection = categories.has('Prompt Injection');

  if (hasPromptInjection || (hasObfuscation && hasDataAccess)) {
    return 'CRITICAL';
  }
  if (counts.critical > 0) return 'CRITICAL';
  if (counts.high > 0) return 'HIGH';
  if (counts.medium >= 3 || (counts.medium >= 1 && counts.low >= 2)) return 'MEDIUM';
  if (counts.medium > 0 || counts.low > 2) return 'LOW';
  return 'CLEAN';
}

// ─── Capability Summary ────────────────────────────────────────────

function summarizeCapabilities(findings) {
  const caps = new Set();
  for (const f of findings) {
    if (f.category === 'Network' || f.id === 'fetch-call' || f.id === 'curl-wget') caps.add('Makes network requests');
    if (f.category === 'File Access' || f.category === 'Sensitive File Access') caps.add('Accesses files outside skill directory');
    if (f.category === 'Shell Execution') caps.add('Executes shell commands');
    if (f.category === 'Obfuscation') caps.add('Uses obfuscation techniques');
    if (f.category === 'Prompt Injection') caps.add('Contains prompt injection attempts');
    if (f.category === 'Data Exfiltration') caps.add('Potential data exfiltration');
    if (f.category === 'Persistence') caps.add('Attempts persistence mechanisms');
    if (f.category === 'Privilege Escalation') caps.add('Attempts privilege escalation');
  }
  return Array.from(caps);
}

// ─── Accuracy Score Calculation ───────────────────────────────────

function calculateAccuracyScore(description, actualCapabilities, findings = [], fullContent = '') {
  if (!description || description === 'No SKILL.md found' || description === 'No frontmatter' || description === 'No description') {
    return { score: 1, disclosed: [], undisclosed: actualCapabilities, reason: 'No description provided — impossible to verify intent' };
  }

  if (actualCapabilities.length === 0) {
    return { score: 10, disclosed: [], undisclosed: [], reason: 'Skill does what it says and nothing more' };
  }

  const fullText = (description + '\n' + (fullContent || '')).toLowerCase();
  const disclosed = [];
  const undisclosed = [];

  const DESC_CAPABILITY_KEYWORDS = {
    'Makes network requests': [
      /\b(?:fetch|download|upload|sync|cloud|api|web|url|http|online|remote|server|connect|request|send|receive|internet)\b/i
    ],
    'Accesses files outside skill directory': [
      /\b(?:system\s*files?|user\s*files?|documents?|config|settings?|memory|workspace|home\s*dir|browse\s*files?)\b/i
    ],
    'Executes shell commands': [
      /\b(?:shell|command|terminal|exec|run\s*(?:program|process|command)|cli|system\s*command|script)\b/i
    ],
    'Uses obfuscation techniques': [],
    'Contains prompt injection attempts': [],
    'Potential data exfiltration': [],
    'Attempts persistence mechanisms': [
      /\b(?:schedul|cron|autostart|background|persist|always.?on|daemon|service)\b/i
    ],
    'Attempts privilege escalation': [
      /\b(?:browser|device|camera|screen|node|control|automat)/i
    ]
  };

  const ALWAYS_SUSPICIOUS = new Set([
    'Uses obfuscation techniques',
    'Contains prompt injection attempts',
    'Potential data exfiltration'
  ]);

  for (const cap of actualCapabilities) {
    if (ALWAYS_SUSPICIOUS.has(cap)) {
      const capCategories = {
        'Contains prompt injection attempts': 'Prompt Injection',
        'Uses obfuscation techniques': 'Obfuscation',
        'Potential data exfiltration': 'Data Exfiltration'
      };
      const cat = capCategories[cap];
      const catFindings = findings.filter(f => f.category === cat);
      const allIntentMatched = catFindings.length > 0 && catFindings.every(f => f.intentMatch);
      if (allIntentMatched) {
        disclosed.push(cap + ' (disclosed)');
        continue;
      }
      undisclosed.push(cap);
      continue;
    }

    const keywords = DESC_CAPABILITY_KEYWORDS[cap] || [];
    const mentioned = keywords.some(regex => regex.test(fullText));
    if (mentioned) {
      disclosed.push(cap);
    } else {
      undisclosed.push(cap);
    }
  }

  const intentMatchedCategories = new Set();
  for (const f of findings) {
    if (f.intentMatch) intentMatchedCategories.add(f.category);
  }

  const DEDUCTIONS = {
    'Uses obfuscation techniques': 4,
    'Contains prompt injection attempts': 5,
    'Potential data exfiltration': 5,
    'Makes network requests': 1.5,
    'Accesses files outside skill directory': 2,
    'Executes shell commands': 2,
    'Attempts persistence mechanisms': 3,
    'Attempts privilege escalation': 2
  };

  const CAP_TO_CATEGORIES = {
    'Accesses files outside skill directory': ['File Access', 'Sensitive File Access'],
    'Attempts persistence mechanisms': ['Persistence'],
    'Makes network requests': ['Network'],
    'Executes shell commands': ['Shell Execution'],
    'Attempts privilege escalation': ['Privilege Escalation'],
  };

  let score = 10;
  for (const cap of undisclosed) {
    const relatedCats = CAP_TO_CATEGORIES[cap] || [];
    const hasIntentMatch = relatedCats.some(c => intentMatchedCategories.has(c));
    if (hasIntentMatch) {
      score -= (DEDUCTIONS[cap] || 1) * 0.25;
    } else {
      score -= (DEDUCTIONS[cap] || 1);
    }
  }

  score += disclosed.length * 0.25;
  score = Math.max(1, Math.min(10, Math.round(score)));

  let reason;
  if (score >= 8) {
    reason = 'Description accurately reflects what the skill does';
  } else if (score >= 5) {
    reason = 'Some capabilities are not mentioned in the description';
  } else if (score >= 3) {
    reason = 'Significant undisclosed capabilities — description is misleading';
  } else {
    reason = 'Description does not match actual behavior — skill is deceptive';
  }

  return { score, disclosed, undisclosed, reason };
}

// ─── Deduplication ─────────────────────────────────────────────────

function deduplicateFindings(findings) {
  const seen = new Set();
  return findings.filter(f => {
    const key = `${f.id}:${f.file}:${f.line}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

// ─── Multi-Analyzer Scanner ───────────────────────────────────────

async function scanFileWithAnalyzers(filePath, skillDir, options) {
  let allFindings = [];

  // 1. Static analysis (always available)
  try {
    const staticFindings = staticAnalyzer.scanFile(filePath, skillDir, options);
    allFindings.push(...staticFindings);
  } catch (e) {
    allFindings.push({
      id: 'static-analyzer-error',
      category: 'Error',
      severity: 'medium',
      file: path.relative(skillDir, filePath),
      line: 0,
      snippet: '',
      explanation: `Static analysis failed: ${e.message}`,
      analyzer: 'static'
    });
  }

  // 2. Python AST analysis (optional)
  if (astAnalyzer && path.extname(filePath).toLowerCase() === '.py') {
    try {
      const astFindings = astAnalyzer.scanFile(filePath, skillDir, options);
      allFindings.push(...astFindings);
    } catch (e) {
      allFindings.push({
        id: 'ast-analyzer-error',
        category: 'Error',
        severity: 'low',
        file: path.relative(skillDir, filePath),
        line: 0,
        snippet: '',
        explanation: `AST analysis failed: ${e.message}`,
        analyzer: 'ast-python'
      });
    }
  }

  // 3. VirusTotal scanning (optional)
  if (vtAnalyzer && options.useVirusTotal) {
    try {
      const vtFindings = await vtAnalyzer.scanFile(filePath, skillDir, options);
      allFindings.push(...vtFindings);
    } catch (e) {
      allFindings.push({
        id: 'virustotal-error',
        category: 'Error',
        severity: 'low',
        file: path.relative(skillDir, filePath),
        line: 0,
        snippet: '',
        explanation: `VirusTotal scan failed: ${e.message}`,
        analyzer: 'virustotal'
      });
    }
  }

  return allFindings;
}

// ─── Command Line Parsing ──────────────────────────────────────────

function parseArgs(args) {
  const options = {
    skillDir: null,
    jsonOutput: null,
    jsonStdout: false,
    format: 'json',
    mode: 'balanced',
    useVirusTotal: false,
    useLLM: false,
    customRules: null,
    failOnFindings: false,
    help: false
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    switch (arg) {
      case '--json':
        options.jsonOutput = args[++i];
        break;
      case '--json-stdout':
        options.jsonStdout = true;
        break;
      case '--format':
        options.format = args[++i];
        break;
      case '--mode':
        options.mode = args[++i];
        break;
      case '--use-virustotal':
        options.useVirusTotal = true;
        break;
      case '--use-llm':
        options.useLLM = true;
        break;
      case '--custom-rules':
        options.customRules = args[++i];
        break;
      case '--fail-on-findings':
        options.failOnFindings = true;
        break;
      case '--help':
      case '-h':
        options.help = true;
        break;
      default:
        if (!options.skillDir && !arg.startsWith('--')) {
          options.skillDir = arg;
        }
        break;
    }
  }

  return options;
}

function showHelp() {
  console.log(`
Skill Auditor v2.0 — Enhanced security scanner for OpenClaw skills

Usage: node scan-skill.js <skill-directory> [options]

Options:
  --json <file>         Output results in JSON format
  --format sarif        Output in SARIF format for GitHub Code Scanning
  --mode <mode>         Detection mode: strict|balanced|permissive (default: balanced)
  --use-virustotal     Enable VirusTotal binary scanning (requires VIRUSTOTAL_API_KEY)
  --use-llm           Enable LLM semantic analysis (requires OpenClaw gateway)
  --custom-rules <dir> Additional YARA rules directory
  --fail-on-findings  Exit with code 1 if HIGH/CRITICAL findings found
  --help              Show this help message

Detection Modes:
  strict      - All patterns, higher false positive rate
  balanced    - Default mode with optimized accuracy
  permissive  - Only critical patterns, lower false positive rate

Optional Features (require npm install):
  Python AST Analysis: npm install tree-sitter tree-sitter-python
  YARA Rules Support: npm install yara
  VirusTotal Scanning: Set VIRUSTOTAL_API_KEY environment variable
  LLM Semantic Analysis: Requires OpenClaw gateway running

Exit codes: 0 = clean/low findings, 1 = significant findings, 2 = error
`);
}

// ─── Main Function ─────────────────────────────────────────────────

async function main() {
  const options = parseArgs(process.argv.slice(2));

  if (options.help) {
    showHelp();
    process.exit(0);
  }

  if (!options.skillDir) {
    console.error('Error: Skill directory required');
    showHelp();
    process.exit(2);
  }

  const skillDir = path.resolve(options.skillDir);

  if (!fs.existsSync(skillDir)) {
    console.error(`Error: Directory not found: ${skillDir}`);
    process.exit(2);
  }

  try {
    // Parse skill metadata
    const skillMeta = parseSkillMd(skillDir);

    // Discover and scan files
    const files = discoverFiles(skillDir);
    let allFindings = [];

    for (const file of files) {
      const findings = await scanFileWithAnalyzers(file, skillDir, options);
      allFindings.push(...findings);
    }

    allFindings = deduplicateFindings(allFindings);

    // Apply intent matching BEFORE LLM analysis and risk calculation
    allFindings = applyIntentMatching(allFindings, skillMeta);

    // Apply LLM semantic analysis if enabled
    if (llmAnalyzer && options.useLLM) {
      try {
        const llmFindings = await llmAnalyzer.analyzeFindings(skillMeta, allFindings.filter(f => !f.analyzer || f.analyzer !== 'llm-semantic'), options);
        // Replace original findings with LLM-analyzed versions
        const llmFindingIds = new Set(llmFindings.map(f => `${f.id}:${f.file}:${f.line}`));
        allFindings = allFindings.filter(f => !llmFindingIds.has(`${f.id}:${f.file}:${f.line}`));
        allFindings.push(...llmFindings);
      } catch (e) {
        allFindings.push({
          id: 'llm-analysis-error',
          category: 'Error',
          severity: 'low',
          file: '',
          line: 0,
          snippet: '',
          explanation: `LLM semantic analysis failed: ${e.message}`,
          analyzer: 'llm-semantic'
        });
      }
    }

    // Calculate risk and capabilities
    const riskLevel = calculateRisk(allFindings);
    const capabilities = summarizeCapabilities(allFindings);

    // Extract URLs
    const urls = allFindings
      .filter(f => f.id === 'http-url' && f.match)
      .map(f => f.match);
    const uniqueUrls = [...new Set(urls)];

    // Build report
    const report = {
      skill: {
        name: skillMeta.name,
        description: skillMeta.description,
        hasSkillMd: skillMeta.hasSkillMd,
        directory: skillDir
      },
      scan: {
        timestamp: new Date().toISOString(),
        filesScanned: files.map(f => path.relative(skillDir, f)),
        fileCount: files.length,
        version: '2.0.0',
        mode: options.mode,
        analyzers: ['static']
      },
      riskLevel,
      reputation: { 
        publisher: 'Local install', 
        tier: 'local', 
        note: 'Installed from local source', 
        warning: 'No publisher info available — verify source yourself.' 
      },
      accuracyScore: calculateAccuracyScore(skillMeta.description, capabilities, allFindings, skillMeta.fullContent),
      findings: allFindings,
      findingCount: allFindings.length,
      summary: {
        declaredPurpose: skillMeta.description,
        actualCapabilities: capabilities,
        externalUrls: uniqueUrls,
        severityCounts: {
          critical: allFindings.filter(f => f.severity === 'critical').length,
          high: allFindings.filter(f => f.severity === 'high').length,
          medium: allFindings.filter(f => f.severity === 'medium').length,
          low: allFindings.filter(f => f.severity === 'low').length
        },
        analyzersUsed: getAllUsedAnalyzers(allFindings, options)
      }
    };

    // Add analyzer info to scan metadata
    if (astAnalyzer?.isAvailable) report.scan.analyzers.push('ast-python');
    if (options.useVirusTotal) report.scan.analyzers.push('virustotal');
    if (options.useLLM) report.scan.analyzers.push('llm-semantic');
    if (yaraSupport) report.scan.analyzers.push('yara');

    // Output report
    if (options.format === 'sarif' && sarifUtils) {
      const sarif = sarifUtils.generateSarif(report);
      const output = sarifUtils.formatSarif(sarif);
      
      if (options.jsonOutput) {
        fs.writeFileSync(options.jsonOutput, output);
        console.log(`SARIF report saved to: ${options.jsonOutput}`);
      } else {
        console.log(output);
      }

      // Exit with appropriate code
      const exitCode = sarifUtils.calculateExitCode(report, options);
      process.exit(exitCode);
    } else {
      const json = JSON.stringify(report, null, 2);

      if (options.jsonStdout) {
        // Clean JSON output only - for programmatic parsing
        process.stdout.write(json);
      } else if (options.jsonOutput) {
        fs.writeFileSync(options.jsonOutput, json);
        console.log(`Report saved to: ${options.jsonOutput}`);
      } else {
        console.log(json);
      }

      // Exit code based on findings
      if (options.failOnFindings) {
        const significantFindings = allFindings.filter(f => 
          f.severity && ['critical', 'high'].includes(f.severity)
        );
        process.exit(significantFindings.length > 0 ? 1 : 0);
      } else {
        process.exit(allFindings.length > 0 ? 1 : 0);
      }
    }

  } catch (e) {
    console.error(`Scan failed: ${e.message}`);
    if (process.env.DEBUG) {
      console.error(e.stack);
    }
    process.exit(2);
  }
}

function getAllUsedAnalyzers(findings, options) {
  const analyzers = new Set();
  for (const finding of findings) {
    if (finding.analyzer) analyzers.add(finding.analyzer);
  }
  return Array.from(analyzers);
}

// ─── Run Main ──────────────────────────────────────────────────────

main().catch(e => {
  console.error(`Fatal error: ${e.message}`);
  process.exit(2);
});