#!/usr/bin/env node
/**
 * guard-scanner v2.1.0 — Agent Skill Security Scanner 🛡️
 *
 * @security-manifest
 *   env-read: []
 *   env-write: []
 *   network: none
 *   fs-read: [scan target directory (user-specified)]
 *   fs-write: [JSON/SARIF/HTML reports to scan directory]
 *   exec: none
 *   purpose: Static analysis of agent skill files for threat patterns
 *
 * Based on GuavaGuard v9.0.0 (OSS extraction)
 * 20 threat categories • Snyk ToxicSkills + OWASP MCP Top 10
 * Zero dependencies • CLI + JSON + SARIF + HTML output
 * Plugin API for custom detection rules
 *
 * Born from a real 3-day agent identity hijack (2026-02-12)
 *
 * License: MIT
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');

const { PATTERNS } = require('./patterns.js');
const { KNOWN_MALICIOUS } = require('./ioc-db.js');
const { generateHTML } = require('./html-template.js');

// ===== CONFIGURATION =====
const VERSION = '5.0.3';

const THRESHOLDS = {
    normal: { suspicious: 30, malicious: 80 },
    strict: { suspicious: 20, malicious: 60 },
};

// File classification
const CODE_EXTENSIONS = new Set(['.js', '.ts', '.mjs', '.cjs', '.py', '.sh', '.bash', '.ps1', '.rb', '.go', '.rs', '.php', '.pl']);
const DOC_EXTENSIONS = new Set(['.md', '.txt', '.rst', '.adoc']);
const DATA_EXTENSIONS = new Set(['.json', '.yaml', '.yml', '.toml', '.xml', '.csv']);
const BINARY_EXTENSIONS = new Set(['.png', '.jpg', '.jpeg', '.gif', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.wasm', '.wav', '.mp3', '.mp4', '.webm', '.ogg', '.pdf', '.zip', '.tar', '.gz', '.bz2', '.7z', '.exe', '.dll', '.so', '.dylib']);
const GENERATED_REPORT_FILES = new Set(['guard-scanner-report.json', 'guard-scanner-report.html', 'guard-scanner.sarif']);

// Severity weights for risk scoring
const SEVERITY_WEIGHTS = { CRITICAL: 40, HIGH: 15, MEDIUM: 5, LOW: 2 };

class GuardScanner {
    constructor(options = {}) {
        this.verbose = options.verbose || false;
        this.selfExclude = options.selfExclude || false;
        this.strict = options.strict || false;
        this.summaryOnly = options.summaryOnly || false;
        this.quiet = options.quiet || false;
        this.checkDeps = options.checkDeps || false;
        this.soulLock = options.soulLock || false;
        this.scannerDir = path.resolve(__dirname);
        this.thresholds = this.strict ? THRESHOLDS.strict : THRESHOLDS.normal;
        this.findings = [];
        this.stats = { scanned: 0, clean: 0, low: 0, suspicious: 0, malicious: 0 };
        this.ignoredSkills = new Set();
        this.ignoredPatterns = new Set();
        this.customRules = [];

        // Plugin API: load plugins
        if (options.plugins && Array.isArray(options.plugins)) {
            for (const plugin of options.plugins) {
                this.loadPlugin(plugin);
            }
        }

        // Custom rules file (legacy compat)
        if (options.rulesFile) {
            this.loadCustomRules(options.rulesFile);
        }
    }

    // Plugin API: load a plugin module
    loadPlugin(pluginPath) {
        try {
            const plugin = require(path.resolve(pluginPath));
            if (plugin.patterns && Array.isArray(plugin.patterns)) {
                for (const p of plugin.patterns) {
                    if (p.id && p.regex && p.severity && p.cat && p.desc) {
                        this.customRules.push(p);
                    }
                }
                if (!this.summaryOnly) {
                    console.log(`🔌 Plugin loaded: ${plugin.name || pluginPath} (${plugin.patterns.length} rule(s))`);
                }
            }
        } catch (e) {
            console.error(`⚠️  Failed to load plugin ${pluginPath}: ${e.message}`);
        }
    }

    // Custom rules from JSON file
    loadCustomRules(rulesFile) {
        try {
            const content = fs.readFileSync(rulesFile, 'utf-8');
            const rules = JSON.parse(content);
            if (!Array.isArray(rules)) {
                console.error(`⚠️  Custom rules file must be a JSON array`);
                return;
            }
            for (const rule of rules) {
                if (!rule.id || !rule.pattern || !rule.severity || !rule.cat || !rule.desc) {
                    console.error(`⚠️  Skipping invalid rule: ${JSON.stringify(rule).substring(0, 80)}`);
                    continue;
                }
                try {
                    const flags = rule.flags || 'gi';
                    this.customRules.push({
                        id: rule.id,
                        cat: rule.cat,
                        regex: new RegExp(rule.pattern, flags),
                        severity: rule.severity,
                        desc: rule.desc,
                        codeOnly: rule.codeOnly || false,
                        docOnly: rule.docOnly || false,
                        all: !rule.codeOnly && !rule.docOnly
                    });
                } catch (e) {
                    console.error(`⚠️  Invalid regex in rule ${rule.id}: ${e.message}`);
                }
            }
            if (!this.summaryOnly && this.customRules.length > 0) {
                console.log(`📏 Loaded ${this.customRules.length} custom rule(s) from ${rulesFile}`);
            }
        } catch (e) {
            console.error(`⚠️  Failed to load custom rules: ${e.message}`);
        }
    }

    // Load .guava-guard-ignore / .guard-scanner-ignore from scan directory
    loadIgnoreFile(scanDir) {
        const ignorePaths = [
            path.join(scanDir, '.guard-scanner-ignore'),
            path.join(scanDir, '.guava-guard-ignore'),
        ];
        for (const ignorePath of ignorePaths) {
            if (!fs.existsSync(ignorePath)) continue;
            const lines = fs.readFileSync(ignorePath, 'utf-8').split('\n');
            for (const line of lines) {
                const trimmed = line.trim();
                if (!trimmed || trimmed.startsWith('#')) continue;
                if (trimmed.startsWith('pattern:')) {
                    this.ignoredPatterns.add(trimmed.replace('pattern:', '').trim());
                } else {
                    this.ignoredSkills.add(trimmed);
                }
            }
            if (this.verbose && (this.ignoredSkills.size || this.ignoredPatterns.size)) {
                console.log(`📋 Loaded ignore file: ${this.ignoredSkills.size} skills, ${this.ignoredPatterns.size} patterns`);
            }
            break; // use first found
        }
    }

    scanDirectory(dir) {
        if (!fs.existsSync(dir)) {
            console.error(`❌ Directory not found: ${dir}`);
            process.exit(2);
        }

        this.loadIgnoreFile(dir);

        const skills = fs.readdirSync(dir).filter(f => {
            const p = path.join(dir, f);
            return fs.statSync(p).isDirectory();
        });

        if (!this.quiet) {
            console.log(`\n🛡️  guard-scanner v${VERSION}`);
            console.log(`${'═'.repeat(54)}`);
            console.log(`📂 Scanning: ${dir}`);
            console.log(`📦 Skills found: ${skills.length}`);
            if (this.strict) console.log(`⚡ Strict mode enabled`);
            console.log();
        }

        for (const skill of skills) {
            const skillPath = path.join(dir, skill);

            // Self-exclusion
            if (this.selfExclude && path.resolve(skillPath) === this.scannerDir) {
                if (!this.summaryOnly && !this.quiet) console.log(`⏭️  ${skill} — SELF (excluded)`);
                continue;
            }

            // Ignore list
            if (this.ignoredSkills.has(skill)) {
                if (!this.summaryOnly && !this.quiet) console.log(`⏭️  ${skill} — IGNORED`);
                continue;
            }

            this.scanSkill(skillPath, skill);
        }

        if (!this.quiet) this.printSummary();
        return this.findings;
    }

    scanSkill(skillPath, skillName) {
        this.stats.scanned++;
        const skillFindings = [];

        // Check 1: Known malicious skill name
        if (KNOWN_MALICIOUS.typosquats.includes(skillName.toLowerCase())) {
            skillFindings.push({
                severity: 'CRITICAL', id: 'KNOWN_TYPOSQUAT', cat: 'malicious-code',
                desc: `Known malicious/typosquat skill name`,
                file: 'SKILL NAME', line: 0
            });
        }

        // Check 2: Scan all files
        const files = this.getFiles(skillPath);
        for (const file of files) {
            const ext = path.extname(file).toLowerCase();
            const relFile = path.relative(skillPath, file);

            if (relFile.includes('node_modules/') || relFile.includes('node_modules\\')) continue;
            if (relFile.startsWith('.git/') || relFile.startsWith('.git\\')) continue;
            if (BINARY_EXTENSIONS.has(ext)) continue;
            if (this.isSelfNoisePath(skillName, relFile)) continue;

            let content;
            try { content = fs.readFileSync(file, 'utf-8'); } catch { continue; }
            if (content.length > 500000) continue;

            const fileType = this.classifyFile(ext, relFile);

            // IoC checks
            if (!this.isSelfThreatCorpus(skillName, relFile)) {
                this.checkIoCs(content, relFile, skillFindings);
            }

            // Pattern checks (context-aware)
            this.checkPatterns(content, relFile, fileType, skillFindings);

            // Custom rules / plugins
            if (this.customRules.length > 0) {
                this.checkPatterns(content, relFile, fileType, skillFindings, this.customRules);
            }

            // Hardcoded secret detection
            const baseName = path.basename(relFile).toLowerCase();
            const skipSecretCheck = baseName.endsWith('-lock.json') || baseName === 'package-lock.json' ||
                baseName === 'yarn.lock' || baseName === 'pnpm-lock.yaml' ||
                baseName === '_meta.json' || baseName === '.package-lock.json';
            if (fileType === 'code' && !skipSecretCheck) {
                this.checkHardcodedSecrets(content, relFile, skillFindings);
            }

            // Lightweight JS data flow analysis
            if ((ext === '.js' || ext === '.mjs' || ext === '.cjs' || ext === '.ts') && content.length < 200000) {
                this.checkJSDataFlow(content, relFile, skillFindings);
            }
        }

        // Check 3: Structural checks
        this.checkStructure(skillPath, skillName, skillFindings);

        // Check 4: Dependency chain scanning
        if (this.checkDeps) {
            this.checkDependencies(skillPath, skillName, skillFindings);
        }

        // Check 5: Hidden files detection
        this.checkHiddenFiles(skillPath, skillName, skillFindings);

        // Check 6: Cross-file analysis
        this.checkCrossFile(skillPath, skillName, skillFindings);

        // Check 7: Skill manifest validation (v1.1)
        this.checkSkillManifest(skillPath, skillName, skillFindings);

        // Check 8: Code complexity metrics (v1.1)
        this.checkComplexity(skillPath, skillName, skillFindings);

        // Check 9: Config impact analysis (v1.1)
        this.checkConfigImpact(skillPath, skillName, skillFindings);

        // Filter ignored patterns
        const filteredFindings = skillFindings.filter(f => !this.ignoredPatterns.has(f.id));

        // Calculate risk
        const risk = this.calculateRisk(filteredFindings);
        const verdict = this.getVerdict(risk);

        this.stats[verdict.stat]++;

        if (!this.summaryOnly && !this.quiet) {
            console.log(`${verdict.icon} ${skillName} — ${verdict.label} (risk: ${risk})`);

            if (this.verbose && filteredFindings.length > 0) {
                const byCat = {};
                for (const f of filteredFindings) {
                    (byCat[f.cat] = byCat[f.cat] || []).push(f);
                }
                for (const [cat, findings] of Object.entries(byCat)) {
                    console.log(`   📁 ${cat}`);
                    for (const f of findings) {
                        const icon = f.severity === 'CRITICAL' ? '💀' : f.severity === 'HIGH' ? '🔴' : f.severity === 'MEDIUM' ? '🟡' : '⚪';
                        const loc = f.line ? `${f.file}:${f.line}` : f.file;
                        console.log(`      ${icon} [${f.severity}] ${f.desc} — ${loc}`);
                        if (f.sample) console.log(`         └─ "${f.sample}"`);
                    }
                }
            }
        }

        if (filteredFindings.length > 0) {
            this.findings.push({ skill: skillName, risk, verdict: verdict.label, findings: filteredFindings });
        }
    }

    classifyFile(ext, relFile) {
        if (CODE_EXTENSIONS.has(ext)) return 'code';
        if (DOC_EXTENSIONS.has(ext)) return 'doc';
        if (DATA_EXTENSIONS.has(ext)) return 'data';
        const base = path.basename(relFile).toLowerCase();
        if (base === 'skill.md' || base === 'readme.md') return 'skill-doc';
        return 'other';
    }

    isSelfNoisePath(skillName, relFile) {
        if (skillName !== 'guard-scanner') return false;
        return /^test\//.test(relFile)
            || /^dist\/__tests__\//.test(relFile)
            || /^ts-src\/__tests__\//.test(relFile)
            || /^docs\//.test(relFile)
            || relFile === 'ROADMAP-RESEARCH.md'
            || relFile === 'CHANGELOG.md';
    }

    isSelfThreatCorpus(skillName, relFile) {
        if (skillName !== 'guard-scanner') return false;
        return /(^|\/)(ioc-db|patterns)\.(js|ts)$/.test(relFile);
    }

    checkIoCs(content, relFile, findings) {
        const contentLower = content.toLowerCase();

        for (const ip of KNOWN_MALICIOUS.ips) {
            if (content.includes(ip)) {
                findings.push({ severity: 'CRITICAL', id: 'IOC_IP', cat: 'malicious-code', desc: `Known malicious IP: ${ip}`, file: relFile });
            }
        }

        for (const url of KNOWN_MALICIOUS.urls) {
            if (contentLower.includes(url.toLowerCase())) {
                findings.push({ severity: 'CRITICAL', id: 'IOC_URL', cat: 'malicious-code', desc: `Known malicious URL: ${url}`, file: relFile });
            }
        }

        for (const domain of KNOWN_MALICIOUS.domains) {
            const domainRegex = new RegExp(`(?:https?://|[\\s'"\`(]|^)${domain.replace(/\./g, '\\.')}`, 'gi');
            if (domainRegex.test(content)) {
                findings.push({ severity: 'HIGH', id: 'IOC_DOMAIN', cat: 'exfiltration', desc: `Suspicious domain: ${domain}`, file: relFile });
            }
        }

        for (const fname of KNOWN_MALICIOUS.filenames) {
            if (contentLower.includes(fname.toLowerCase())) {
                findings.push({ severity: 'CRITICAL', id: 'IOC_FILE', cat: 'suspicious-download', desc: `Known malicious filename: ${fname}`, file: relFile });
            }
        }

        for (const user of KNOWN_MALICIOUS.usernames) {
            if (contentLower.includes(user.toLowerCase())) {
                findings.push({ severity: 'HIGH', id: 'IOC_USER', cat: 'malicious-code', desc: `Known malicious username: ${user}`, file: relFile });
            }
        }
    }

    checkPatterns(content, relFile, fileType, findings, patterns = PATTERNS) {
        for (const pattern of patterns) {
            // Soul Lock: skip identity-hijack/memory-poisoning patterns unless --soul-lock is enabled
            if (pattern.soulLock && !this.soulLock) continue;
            if (pattern.codeOnly && fileType !== 'code') continue;
            if (pattern.docOnly && fileType !== 'doc' && fileType !== 'skill-doc') continue;
            if (!pattern.all && !pattern.codeOnly && !pattern.docOnly) continue;

            pattern.regex.lastIndex = 0;
            const matches = content.match(pattern.regex);
            if (!matches) continue;

            pattern.regex.lastIndex = 0;
            const idx = content.search(pattern.regex);
            const lineNum = idx >= 0 ? content.substring(0, idx).split('\n').length : null;

            let adjustedSeverity = pattern.severity;
            if ((fileType === 'doc' || fileType === 'skill-doc') && pattern.all && !pattern.docOnly) {
                if (adjustedSeverity === 'HIGH') adjustedSeverity = 'MEDIUM';
                else if (adjustedSeverity === 'MEDIUM') adjustedSeverity = 'LOW';
            }

            findings.push({
                severity: adjustedSeverity,
                id: pattern.id,
                cat: pattern.cat,
                desc: pattern.desc,
                file: relFile,
                line: lineNum,
                matchCount: matches.length,
                sample: matches[0].substring(0, 80)
            });
        }
    }

    // Entropy-based secret detection
    checkHardcodedSecrets(content, relFile, findings) {
        const assignmentRegex = /(?:api[_-]?key|secret|token|password|credential|auth)\s*[:=]\s*['"]([a-zA-Z0-9_\-+/=]{16,})['"]|['"]([a-zA-Z0-9_\-+/=]{32,})['"]/gi;
        let match;
        while ((match = assignmentRegex.exec(content)) !== null) {
            const value = match[1] || match[2];
            if (!value) continue;

            if (/^[A-Z_]+$/.test(value)) continue;
            if (/^(true|false|null|undefined|none|default|example|test|placeholder|your[_-])/i.test(value)) continue;
            if (/^x{4,}|\.{4,}|_{4,}|0{8,}$/i.test(value)) continue;
            if (/^projects\/|^gs:\/\/|^https?:\/\//i.test(value)) continue;
            if (/^[a-z]+-[a-z]+-[a-z0-9]+$/i.test(value)) continue;

            const entropy = this.shannonEntropy(value);
            if (entropy > 3.5 && value.length >= 20) {
                const lineNum = content.substring(0, match.index).split('\n').length;
                findings.push({
                    severity: 'HIGH', id: 'SECRET_ENTROPY', cat: 'secret-detection',
                    desc: `High-entropy string (possible leaked secret, entropy=${entropy.toFixed(1)})`,
                    file: relFile, line: lineNum,
                    sample: value.substring(0, 8) + '...' + value.substring(value.length - 4)
                });
            }
        }
    }

    shannonEntropy(str) {
        const freq = {};
        for (const c of str) freq[c] = (freq[c] || 0) + 1;
        const len = str.length;
        let entropy = 0;
        for (const count of Object.values(freq)) {
            const p = count / len;
            if (p > 0) entropy -= p * Math.log2(p);
        }
        return entropy;
    }

    checkStructure(skillPath, skillName, findings) {
        const skillMd = path.join(skillPath, 'SKILL.md');
        if (!fs.existsSync(skillMd)) {
            findings.push({ severity: 'LOW', id: 'STRUCT_NO_SKILLMD', cat: 'structural', desc: 'No SKILL.md found', file: skillName });
            return;
        }
        const content = fs.readFileSync(skillMd, 'utf-8');
        if (content.length < 50) {
            findings.push({ severity: 'MEDIUM', id: 'STRUCT_TINY_SKILLMD', cat: 'structural', desc: 'Suspiciously short SKILL.md (< 50 chars)', file: 'SKILL.md' });
        }
        const scriptsDir = path.join(skillPath, 'scripts');
        if (fs.existsSync(scriptsDir)) {
            const scripts = fs.readdirSync(scriptsDir).filter(f => CODE_EXTENSIONS.has(path.extname(f).toLowerCase()));
            if (scripts.length > 0 && !content.includes('scripts/')) {
                findings.push({ severity: 'MEDIUM', id: 'STRUCT_UNDOCUMENTED_SCRIPTS', cat: 'structural', desc: `${scripts.length} script(s) in scripts/ not referenced in SKILL.md`, file: 'scripts/' });
            }
        }
    }

    checkDependencies(skillPath, skillName, findings) {
        const pkgPath = path.join(skillPath, 'package.json');
        if (!fs.existsSync(pkgPath)) return;

        let pkg;
        try { pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8')); } catch { return; }

        const allDeps = { ...pkg.dependencies, ...pkg.devDependencies, ...pkg.optionalDependencies };

        const RISKY_PACKAGES = new Set([
            'node-ipc', 'colors', 'faker', 'event-stream', 'ua-parser-js', 'coa', 'rc',
        ]);

        for (const [dep, version] of Object.entries(allDeps)) {
            if (RISKY_PACKAGES.has(dep)) {
                findings.push({ severity: 'HIGH', id: 'DEP_RISKY', cat: 'dependency-chain', desc: `Known risky dependency: ${dep}@${version}`, file: 'package.json' });
            }
            if (typeof version === 'string' && (version.startsWith('git+') || version.startsWith('http') || version.startsWith('github:') || version.includes('.tar.gz'))) {
                findings.push({ severity: 'HIGH', id: 'DEP_REMOTE', cat: 'dependency-chain', desc: `Remote/git dependency: ${dep}@${version}`, file: 'package.json' });
            }
            if (version === '*' || version === 'latest') {
                findings.push({ severity: 'MEDIUM', id: 'DEP_WILDCARD', cat: 'dependency-chain', desc: `Wildcard version: ${dep}@${version}`, file: 'package.json' });
            }
        }

        const RISKY_SCRIPTS = ['preinstall', 'postinstall', 'preuninstall', 'postuninstall', 'prepare'];
        if (pkg.scripts) {
            for (const scriptName of RISKY_SCRIPTS) {
                if (pkg.scripts[scriptName]) {
                    const cmd = pkg.scripts[scriptName];
                    findings.push({ severity: 'HIGH', id: 'DEP_LIFECYCLE', cat: 'dependency-chain', desc: `Lifecycle script "${scriptName}": ${cmd.substring(0, 80)}`, file: 'package.json' });
                    if (/curl|wget|node\s+-e|eval|exec|bash\s+-c/i.test(cmd)) {
                        findings.push({ severity: 'CRITICAL', id: 'DEP_LIFECYCLE_EXEC', cat: 'dependency-chain', desc: `Lifecycle script "${scriptName}" downloads/executes code`, file: 'package.json', sample: cmd.substring(0, 80) });
                    }
                }
            }
        }
    }

    // ── v1.1: Skill Manifest Validation ──
    // Checks SKILL.md frontmatter for dangerous tool declarations,
    // overly broad file scope, and sensitive env requirements
    checkSkillManifest(skillPath, skillName, findings) {
        const skillMd = path.join(skillPath, 'SKILL.md');
        if (!fs.existsSync(skillMd)) return;

        let content;
        try { content = fs.readFileSync(skillMd, 'utf-8'); } catch { return; }

        // Parse YAML frontmatter (lightweight, no dependency)
        const fmMatch = content.match(/^---\n([\s\S]*?)\n---/);
        if (!fmMatch) return;
        const fm = fmMatch[1];

        // Check 1: Dangerous binary requirements
        const DANGEROUS_BINS = new Set([
            'sudo', 'rm', 'rmdir', 'chmod', 'chown', 'kill', 'pkill',
            'curl', 'wget', 'nc', 'ncat', 'socat', 'ssh', 'scp',
            'dd', 'mkfs', 'fdisk', 'mount', 'umount',
            'iptables', 'ufw', 'firewall-cmd',
            'docker', 'kubectl', 'systemctl',
        ]);
        const binsMatch = fm.match(/bins:\s*\n((?:\s+-\s+[^\n]+\n?)*)/i);
        if (binsMatch) {
            const bins = binsMatch[1].match(/- ([^\n]+)/g) || [];
            for (const binLine of bins) {
                const bin = binLine.replace(/^-\s*/, '').trim().toLowerCase();
                if (DANGEROUS_BINS.has(bin)) {
                    findings.push({
                        severity: 'HIGH', id: 'MANIFEST_DANGEROUS_BIN',
                        cat: 'sandbox-validation',
                        desc: `SKILL.md requires dangerous binary: ${bin}`,
                        file: 'SKILL.md'
                    });
                }
            }
        }

        // Check 2: Overly broad file scope
        const filesMatch = fm.match(/files:\s*\[([^\]]+)\]/i) || fm.match(/files:\s*\n((?:\s+-\s+[^\n]+\n?)*)/i);
        if (filesMatch) {
            const filesStr = filesMatch[1];
            if (/\*\*\/\*|\*\.\*|\"\*\"/i.test(filesStr)) {
                findings.push({
                    severity: 'HIGH', id: 'MANIFEST_BROAD_FILES',
                    cat: 'sandbox-validation',
                    desc: 'SKILL.md declares overly broad file scope (e.g. **/*)',
                    file: 'SKILL.md'
                });
            }
        }

        // Check 3: Sensitive env requirements
        const SENSITIVE_ENV_PATTERNS = /(?:SECRET|PASSWORD|CREDENTIAL|PRIVATE_KEY|AWS_SECRET|GITHUB_TOKEN)/i;
        const envMatch = fm.match(/env:\s*\n((?:\s+-\s+[^\n]+\n?)*)/i);
        if (envMatch) {
            const envVars = envMatch[1].match(/- ([^\n]+)/g) || [];
            for (const envLine of envVars) {
                const envVar = envLine.replace(/^-\s*/, '').trim();
                if (SENSITIVE_ENV_PATTERNS.test(envVar)) {
                    findings.push({
                        severity: 'HIGH', id: 'MANIFEST_SENSITIVE_ENV',
                        cat: 'sandbox-validation',
                        desc: `SKILL.md requires sensitive env var: ${envVar}`,
                        file: 'SKILL.md'
                    });
                }
            }
        }

        // Check 4: exec or network declared without justification
        if (/exec:\s*(?:true|yes|enabled|'\*'|"\*")/i.test(fm)) {
            findings.push({
                severity: 'MEDIUM', id: 'MANIFEST_EXEC_DECLARED',
                cat: 'sandbox-validation',
                desc: 'SKILL.md declares exec capability',
                file: 'SKILL.md'
            });
        }
        if (/network:\s*(?:true|yes|enabled|'\*'|"\*"|all|any)/i.test(fm)) {
            findings.push({
                severity: 'MEDIUM', id: 'MANIFEST_NETWORK_DECLARED',
                cat: 'sandbox-validation',
                desc: 'SKILL.md declares unrestricted network access',
                file: 'SKILL.md'
            });
        }
    }

    // ── v1.1: Code Complexity Metrics ──
    // Detects excessive file length, deep nesting, and eval/exec density
    checkComplexity(skillPath, skillName, findings) {
        const files = this.getFiles(skillPath);
        const MAX_LINES = 1000;
        const MAX_NESTING = 5;
        const MAX_EVAL_DENSITY = 0.02; // 2% of lines

        for (const file of files) {
            const ext = path.extname(file).toLowerCase();
            if (!CODE_EXTENSIONS.has(ext)) continue;

            const relFile = path.relative(skillPath, file);
            if (relFile.includes('node_modules') || relFile.startsWith('.git')) continue;

            let content;
            try { content = fs.readFileSync(file, 'utf-8'); } catch { continue; }

            const lines = content.split('\n');

            // Check 1: Excessive file length
            if (lines.length > MAX_LINES) {
                findings.push({
                    severity: 'MEDIUM', id: 'COMPLEXITY_LONG_FILE',
                    cat: 'complexity',
                    desc: `File exceeds ${MAX_LINES} lines (${lines.length} lines)`,
                    file: relFile
                });
            }

            // Check 2: Deep nesting (brace tracking)
            let maxDepth = 0;
            let currentDepth = 0;
            let deepestLine = 0;
            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                // Count opening/closing braces outside strings (simplified)
                for (const ch of line) {
                    if (ch === '{') currentDepth++;
                    if (ch === '}') currentDepth = Math.max(0, currentDepth - 1);
                }
                if (currentDepth > maxDepth) {
                    maxDepth = currentDepth;
                    deepestLine = i + 1;
                }
            }
            if (maxDepth > MAX_NESTING) {
                findings.push({
                    severity: 'MEDIUM', id: 'COMPLEXITY_DEEP_NESTING',
                    cat: 'complexity',
                    desc: `Deep nesting detected: ${maxDepth} levels (max recommended: ${MAX_NESTING})`,
                    file: relFile, line: deepestLine
                });
            }

            // Check 3: eval/exec density
            const evalPattern = /\b(?:eval|exec|execSync|spawn|Function)\s*\(/g;
            const evalMatches = content.match(evalPattern) || [];
            const density = lines.length > 0 ? evalMatches.length / lines.length : 0;
            if (density > MAX_EVAL_DENSITY && evalMatches.length >= 3) {
                findings.push({
                    severity: 'HIGH', id: 'COMPLEXITY_EVAL_DENSITY',
                    cat: 'complexity',
                    desc: `High eval/exec density: ${evalMatches.length} calls in ${lines.length} lines (${(density * 100).toFixed(1)}%)`,
                    file: relFile
                });
            }
        }
    }

    // ── v1.1: Config Impact Analysis ──
    // Detects modifications to openclaw.json and dangerous configuration changes
    checkConfigImpact(skillPath, skillName, findings) {
        const files = this.getFiles(skillPath);

        for (const file of files) {
            const ext = path.extname(file).toLowerCase();
            if (!CODE_EXTENSIONS.has(ext) && ext !== '.json') continue;

            const relFile = path.relative(skillPath, file);
            if (relFile.includes('node_modules') || relFile.startsWith('.git')) continue;

            let content;
            try { content = fs.readFileSync(file, 'utf-8'); } catch { continue; }

            // Check 1: openclaw.json reference + write operation in same file
            // Handles both direct and variable-based patterns (e.g. writeFileSync(configPath))
            const hasConfigRef = /openclaw\.json/i.test(content);
            const hasWriteOp = /(?:writeFileSync|writeFile|fs\.write)\s*\(/i.test(content);
            if (hasConfigRef && hasWriteOp) {
                // Find the write line for location info
                const clines = content.split('\n');
                let writeLine = 0;
                for (let i = 0; i < clines.length; i++) {
                    if (/(?:writeFileSync|writeFile|fs\.write)\s*\(/i.test(clines[i])) {
                        writeLine = i + 1;
                        break;
                    }
                }
                findings.push({
                    severity: 'CRITICAL', id: 'CFG_WRITE_DETECTED',
                    cat: 'config-impact',
                    desc: 'Code writes to openclaw.json',
                    file: relFile, line: writeLine,
                    sample: writeLine > 0 ? clines[writeLine - 1].trim().substring(0, 80) : ''
                });
            }

            // Check 2: Dangerous config key modifications
            const DANGEROUS_CONFIG_KEYS = [
                { regex: /exec\.approvals?\s*[:=]\s*['"]?(off|false|disabled|none)/gi, id: 'CFG_EXEC_APPROVAL_OFF', desc: 'Disables exec approval requirement', severity: 'CRITICAL' },
                { regex: /tools\.exec\.host\s*[:=]\s*['"]gateway['"]/gi, id: 'CFG_EXEC_HOST_GATEWAY', desc: 'Sets exec host to gateway (bypasses sandbox)', severity: 'CRITICAL' },
                { regex: /hooks\s*\.\s*internal\s*\.\s*entries\s*[:=]/gi, id: 'CFG_HOOKS_INTERNAL', desc: 'Modifies internal hook entries', severity: 'HIGH' },
                { regex: /network\.allowedDomains\s*[:=]\s*\[?\s*['"]\*['"]/gi, id: 'CFG_NET_WILDCARD', desc: 'Sets network allowedDomains to wildcard', severity: 'HIGH' },
            ];

            for (const check of DANGEROUS_CONFIG_KEYS) {
                check.regex.lastIndex = 0;
                if (check.regex.test(content)) {
                    findings.push({
                        severity: check.severity, id: check.id,
                        cat: 'config-impact',
                        desc: check.desc,
                        file: relFile
                    });
                }
            }
        }
    }

    checkHiddenFiles(skillPath, skillName, findings) {
        try {
            const entries = fs.readdirSync(skillPath);
            for (const entry of entries) {
                if (entry.startsWith('.') && entry !== '.guard-scanner-ignore' && entry !== '.guava-guard-ignore' && entry !== '.gitignore' && entry !== '.git') {
                    const fullPath = path.join(skillPath, entry);
                    const stat = fs.statSync(fullPath);
                    if (stat.isFile()) {
                        const ext = path.extname(entry).toLowerCase();
                        if (CODE_EXTENSIONS.has(ext) || ext === '' || ext === '.sh') {
                            findings.push({ severity: 'MEDIUM', id: 'STRUCT_HIDDEN_EXEC', cat: 'structural', desc: `Hidden executable file: ${entry}`, file: entry });
                        }
                    } else if (stat.isDirectory() && entry !== '.git') {
                        findings.push({ severity: 'LOW', id: 'STRUCT_HIDDEN_DIR', cat: 'structural', desc: `Hidden directory: ${entry}/`, file: entry });
                    }
                }
            }
        } catch { }
    }

    checkJSDataFlow(content, relFile, findings) {
        const lines = content.split('\n');
        const imports = new Map();
        const sensitiveReads = [];
        const networkCalls = [];
        const execCalls = [];

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const lineNum = i + 1;

            const reqMatch = line.match(/(?:const|let|var)\s+(?:{[^}]+}|\w+)\s*=\s*require\s*\(\s*['"]([^'"]+)['"]\s*\)/);
            if (reqMatch) {
                const varMatch = line.match(/(?:const|let|var)\s+({[^}]+}|\w+)/);
                if (varMatch) imports.set(varMatch[1].trim(), reqMatch[1]);
            }

            if (/(?:readFileSync|readFile)\s*\([^)]*(?:\.env|\.ssh|id_rsa|\.clawdbot|\.openclaw(?!\/workspace))/i.test(line)) {
                sensitiveReads.push({ line: lineNum, text: line.trim() });
            }
            if (/process\.env\.[A-Z_]*(?:KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL)/i.test(line)) {
                sensitiveReads.push({ line: lineNum, text: line.trim() });
            }

            if (/(?:fetch|axios|request|http\.request|https\.request|got)\s*\(/i.test(line) ||
                /\.post\s*\(|\.put\s*\(|\.patch\s*\(/i.test(line)) {
                networkCalls.push({ line: lineNum, text: line.trim() });
            }

            if (/(?:exec|execSync|spawn|spawnSync|execFile)\s*\(/i.test(line)) {
                execCalls.push({ line: lineNum, text: line.trim() });
            }
        }

        if (sensitiveReads.length > 0 && networkCalls.length > 0) {
            findings.push({
                severity: 'CRITICAL', id: 'AST_CRED_TO_NET', cat: 'data-flow',
                desc: `Data flow: secret read (L${sensitiveReads[0].line}) → network call (L${networkCalls[0].line})`,
                file: relFile, line: sensitiveReads[0].line,
                sample: sensitiveReads[0].text.substring(0, 60)
            });
        }

        if (sensitiveReads.length > 0 && execCalls.length > 0) {
            findings.push({
                severity: 'HIGH', id: 'AST_CRED_TO_EXEC', cat: 'data-flow',
                desc: `Data flow: secret read (L${sensitiveReads[0].line}) → command exec (L${execCalls[0].line})`,
                file: relFile, line: sensitiveReads[0].line,
                sample: sensitiveReads[0].text.substring(0, 60)
            });
        }

        const importedModules = new Set([...imports.values()]);
        if (importedModules.has('child_process') && (importedModules.has('https') || importedModules.has('http') || importedModules.has('node-fetch'))) {
            findings.push({ severity: 'HIGH', id: 'AST_SUSPICIOUS_IMPORTS', cat: 'data-flow', desc: 'Suspicious import combination: child_process + network module', file: relFile });
        }
        if (importedModules.has('fs') && importedModules.has('child_process') && (importedModules.has('https') || importedModules.has('http'))) {
            findings.push({ severity: 'CRITICAL', id: 'AST_EXFIL_TRIFECTA', cat: 'data-flow', desc: 'Exfiltration trifecta: fs + child_process + network', file: relFile });
        }

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            if (/`[^`]*\$\{.*(?:env|key|token|secret|password).*\}[^`]*`\s*(?:\)|,)/i.test(line) &&
                /(?:fetch|request|axios|http|url)/i.test(line)) {
                findings.push({ severity: 'CRITICAL', id: 'AST_SECRET_IN_URL', cat: 'data-flow', desc: 'Secret interpolated into URL/request', file: relFile, line: i + 1, sample: line.trim().substring(0, 80) });
            }
        }
    }

    checkCrossFile(skillPath, skillName, findings) {
        const files = this.getFiles(skillPath);
        const allContent = {};

        for (const file of files) {
            const ext = path.extname(file).toLowerCase();
            if (BINARY_EXTENSIONS.has(ext)) continue;
            const relFile = path.relative(skillPath, file);
            if (relFile.includes('node_modules') || relFile.startsWith('.git')) continue;
            try {
                const content = fs.readFileSync(file, 'utf-8');
                if (content.length < 500000) allContent[relFile] = content;
            } catch { }
        }

        const skillMd = allContent['SKILL.md'] || '';
        const codeFileRefs = skillMd.match(/(?:scripts?\/|\.\/)[a-zA-Z0-9_\-./]+\.(js|py|sh|ts)/gi) || [];
        for (const ref of codeFileRefs) {
            const cleanRef = ref.replace(/^\.\//, '');
            if (!allContent[cleanRef] && !files.some(f => path.relative(skillPath, f) === cleanRef)) {
                findings.push({ severity: 'MEDIUM', id: 'XFILE_PHANTOM_REF', cat: 'structural', desc: `SKILL.md references non-existent file: ${cleanRef}`, file: 'SKILL.md' });
            }
        }

        const base64Fragments = [];
        for (const [file, content] of Object.entries(allContent)) {
            const matches = content.match(/[A-Za-z0-9+/]{20,}={0,2}/g) || [];
            for (const m of matches) {
                if (m.length > 40) base64Fragments.push({ file, fragment: m.substring(0, 30) });
            }
        }
        if (base64Fragments.length > 3 && new Set(base64Fragments.map(f => f.file)).size > 1) {
            findings.push({ severity: 'HIGH', id: 'XFILE_FRAGMENT_B64', cat: 'obfuscation', desc: `Base64 fragments across ${new Set(base64Fragments.map(f => f.file)).size} files`, file: skillName });
        }

        if (/(?:read|load|source|import)\s+(?:the\s+)?(?:script|file|code)\s+(?:from|at|in)\s+(?:scripts?\/)/gi.test(skillMd)) {
            const hasExec = Object.values(allContent).some(c => /(?:eval|exec|spawn)\s*\(/i.test(c));
            if (hasExec) {
                findings.push({ severity: 'MEDIUM', id: 'XFILE_LOAD_EXEC', cat: 'data-flow', desc: 'SKILL.md references script files that contain exec/eval', file: 'SKILL.md' });
            }
        }
    }

    calculateRisk(findings) {
        if (findings.length === 0) return 0;

        let score = 0;
        for (const f of findings) {
            score += SEVERITY_WEIGHTS[f.severity] || 0;
        }

        const ids = new Set(findings.map(f => f.id));
        const cats = new Set(findings.map(f => f.cat));

        if (cats.has('credential-handling') && cats.has('exfiltration')) score = Math.round(score * 2);
        if (cats.has('credential-handling') && findings.some(f => f.id === 'MAL_CHILD' || f.id === 'MAL_EXEC')) score = Math.round(score * 1.5);
        if (cats.has('obfuscation') && (cats.has('malicious-code') || cats.has('credential-handling'))) score = Math.round(score * 2);
        if (ids.has('DEP_LIFECYCLE_EXEC')) score = Math.round(score * 2);
        if (ids.has('PI_BIDI') && findings.length > 1) score = Math.round(score * 1.5);
        if (cats.has('leaky-skills') && (cats.has('exfiltration') || cats.has('malicious-code'))) score = Math.round(score * 2);
        if (cats.has('memory-poisoning')) score = Math.round(score * 1.5);
        if (cats.has('prompt-worm')) score = Math.round(score * 2);
        if (cats.has('cve-patterns')) score = Math.max(score, 70);
        if (cats.has('persistence') && (cats.has('malicious-code') || cats.has('credential-handling') || cats.has('memory-poisoning'))) score = Math.round(score * 1.5);
        if (cats.has('identity-hijack')) score = Math.round(score * 2);
        if (cats.has('identity-hijack') && (cats.has('persistence') || cats.has('memory-poisoning'))) score = Math.max(score, 90);
        if (ids.has('IOC_IP') || ids.has('IOC_URL') || ids.has('KNOWN_TYPOSQUAT')) score = 100;

        // v1.1 categories
        if (cats.has('config-impact')) score = Math.round(score * 2);
        if (cats.has('config-impact') && cats.has('sandbox-validation')) score = Math.max(score, 70);
        if (cats.has('complexity') && (cats.has('malicious-code') || cats.has('obfuscation'))) score = Math.round(score * 1.5);

        // v2.1 PII exposure amplifiers
        if (cats.has('pii-exposure') && cats.has('exfiltration')) score = Math.round(score * 3);
        if (cats.has('pii-exposure') && (ids.has('SHADOW_AI_OPENAI') || ids.has('SHADOW_AI_ANTHROPIC') || ids.has('SHADOW_AI_GENERIC'))) score = Math.round(score * 2.5);
        if (cats.has('pii-exposure') && cats.has('credential-handling')) score = Math.round(score * 2);

        return Math.min(100, score);
    }

    getVerdict(risk) {
        if (risk >= this.thresholds.malicious) return { icon: '🔴', label: 'MALICIOUS', stat: 'malicious' };
        if (risk >= this.thresholds.suspicious) return { icon: '🟡', label: 'SUSPICIOUS', stat: 'suspicious' };
        if (risk > 0) return { icon: '🟢', label: 'LOW RISK', stat: 'low' };
        return { icon: '🟢', label: 'CLEAN', stat: 'clean' };
    }

    getFiles(dir) {
        const results = [];
        try {
            const entries = fs.readdirSync(dir, { withFileTypes: true });
            for (const entry of entries) {
                const fullPath = path.join(dir, entry.name);
                if (entry.isDirectory()) {
                    if (entry.name === '.git' || entry.name === 'node_modules') continue;
                    results.push(...this.getFiles(fullPath));
                } else {
                    const baseName = entry.name.toLowerCase();
                    if (GENERATED_REPORT_FILES.has(baseName)) continue;
                    results.push(fullPath);
                }
            }
        } catch { }
        return results;
    }

    printSummary() {
        const total = this.stats.scanned;
        const safe = this.stats.clean + this.stats.low;
        console.log(`\n${'═'.repeat(54)}`);
        console.log(`📊 guard-scanner v${VERSION} Scan Summary`);
        console.log(`${'─'.repeat(54)}`);
        console.log(`   Scanned:      ${total}`);
        console.log(`   🟢 Clean:       ${this.stats.clean}`);
        console.log(`   🟢 Low Risk:    ${this.stats.low}`);
        console.log(`   🟡 Suspicious:  ${this.stats.suspicious}`);
        console.log(`   🔴 Malicious:   ${this.stats.malicious}`);
        console.log(`   Safety Rate:  ${total ? Math.round(safe / total * 100) : 0}%`);
        console.log(`${'═'.repeat(54)}`);

        if (this.stats.malicious > 0) {
            console.log(`\n⚠️  CRITICAL: ${this.stats.malicious} malicious skill(s) detected!`);
            console.log(`   Review findings with --verbose and remove if confirmed.`);
        } else if (this.stats.suspicious > 0) {
            console.log(`\n⚡ ${this.stats.suspicious} suspicious skill(s) found — review recommended.`);
        } else {
            console.log(`\n✅ All clear! No threats detected.`);
        }
    }

    toJSON() {
        const recommendations = [];
        for (const skillResult of this.findings) {
            const skillRecs = [];
            const cats = new Set(skillResult.findings.map(f => f.cat));

            if (cats.has('prompt-injection')) skillRecs.push('🛑 Contains prompt injection patterns.');
            if (cats.has('malicious-code')) skillRecs.push('🛑 Contains potentially malicious code.');
            if (cats.has('credential-handling') && cats.has('exfiltration')) skillRecs.push('💀 CRITICAL: Credential access + exfiltration. DO NOT INSTALL.');
            if (cats.has('dependency-chain')) skillRecs.push('📦 Suspicious dependency chain.');
            if (cats.has('obfuscation')) skillRecs.push('🔍 Code obfuscation detected.');
            if (cats.has('secret-detection')) skillRecs.push('🔑 Possible hardcoded secrets.');
            if (cats.has('leaky-skills')) skillRecs.push('💧 LEAKY SKILL: Secrets pass through LLM context.');
            if (cats.has('memory-poisoning')) skillRecs.push('🧠 MEMORY POISONING: Agent memory modification attempt.');
            if (cats.has('prompt-worm')) skillRecs.push('🪱 PROMPT WORM: Self-replicating instructions.');
            if (cats.has('data-flow')) skillRecs.push('🔀 Suspicious data flow patterns.');
            if (cats.has('persistence')) skillRecs.push('⏰ PERSISTENCE: Creates scheduled tasks.');
            if (cats.has('cve-patterns')) skillRecs.push('🚨 CVE PATTERN: Matches known exploits.');
            if (cats.has('identity-hijack')) skillRecs.push('🔒 IDENTITY HIJACK: Agent soul file tampering. DO NOT INSTALL.');
            if (cats.has('sandbox-validation')) skillRecs.push('🔒 SANDBOX: Skill requests dangerous capabilities.');
            if (cats.has('complexity')) skillRecs.push('🧩 COMPLEXITY: Excessive code complexity may hide malicious behavior.');
            if (cats.has('config-impact')) skillRecs.push('⚙️ CONFIG IMPACT: Modifies OpenClaw configuration. DO NOT INSTALL.');
            if (cats.has('pii-exposure')) skillRecs.push('🆔 PII EXPOSURE: Handles personally identifiable information. Review data handling.');

            if (skillRecs.length > 0) recommendations.push({ skill: skillResult.skill, actions: skillRecs });
        }

        return {
            timestamp: new Date().toISOString(),
            scanner: `guard-scanner v${VERSION}`,
            mode: this.strict ? 'strict' : 'normal',
            stats: this.stats,
            thresholds: this.thresholds,
            findings: this.findings,
            recommendations,
            iocVersion: '2026-02-12',
        };
    }

    toSARIF(scanDir) {
        const rules = [];
        const ruleIndex = {};
        const results = [];

        for (const skillResult of this.findings) {
            for (const f of skillResult.findings) {
                if (!ruleIndex[f.id]) {
                    ruleIndex[f.id] = rules.length;
                    rules.push({
                        id: f.id, name: f.id,
                        shortDescription: { text: f.desc },
                        defaultConfiguration: { level: f.severity === 'CRITICAL' ? 'error' : f.severity === 'HIGH' ? 'error' : f.severity === 'MEDIUM' ? 'warning' : 'note' },
                        properties: { tags: ['security', f.cat], 'security-severity': f.severity === 'CRITICAL' ? '9.0' : f.severity === 'HIGH' ? '7.0' : f.severity === 'MEDIUM' ? '4.0' : '1.0' }
                    });
                }
                const normalizedFile = String(f.file || '')
                    .replaceAll('\\', '/')
                    .replace(/^\/+/, '');
                const artifactUri = `${skillResult.skill}/${normalizedFile}`;
                const fingerprintSeed = `${f.id}|${artifactUri}|${f.line || 0}|${(f.sample || '').slice(0, 200)}`;
                const lineHash = crypto.createHash('sha256').update(fingerprintSeed).digest('hex').slice(0, 24);

                results.push({
                    ruleId: f.id, ruleIndex: ruleIndex[f.id],
                    level: f.severity === 'CRITICAL' ? 'error' : f.severity === 'HIGH' ? 'error' : f.severity === 'MEDIUM' ? 'warning' : 'note',
                    message: { text: `[${skillResult.skill}] ${f.desc}${f.sample ? ` — "${f.sample}"` : ''}` },
                    partialFingerprints: {
                        primaryLocationLineHash: lineHash
                    },
                    locations: [{ physicalLocation: { artifactLocation: { uri: artifactUri, uriBaseId: '%SRCROOT%' }, region: f.line ? { startLine: f.line } : undefined } }]
                });
            }
        }

        return {
            version: '2.1.0',
            $schema: 'https://json.schemastore.org/sarif-2.1.0.json',
            runs: [{
                tool: { driver: { name: 'guard-scanner', version: VERSION, informationUri: 'https://github.com/koatora20/guard-scanner', rules } },
                results,
                invocations: [{ executionSuccessful: true, endTimeUtc: new Date().toISOString() }]
            }]
        };
    }

    toHTML() {
        return generateHTML(VERSION, this.stats, this.findings);
    }
}

const { scanToolCall, RUNTIME_CHECKS, getCheckStats, LAYER_NAMES } = require('./runtime-guard.js');

module.exports = { GuardScanner, VERSION, THRESHOLDS, SEVERITY_WEIGHTS, scanToolCall, RUNTIME_CHECKS, getCheckStats, LAYER_NAMES };
