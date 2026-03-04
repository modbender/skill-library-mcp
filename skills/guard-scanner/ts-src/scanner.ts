/**
 * guard-scanner v3.0.0 — Core Scanner (TypeScript)
 *
 * Full TypeScript rewrite of guard-scanner v2.1.0 + hbg-scan features.
 * Adds: Compaction Persistence check, Signature hash matching, typed interfaces.
 *
 * Zero dependencies. MIT License.
 */

import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';

import type {
    Severity, Finding, SkillResult, PatternRule, CustomRuleInput,
    ScannerOptions, ScanStats, Thresholds, Verdict, VerdictLabel, FileType,
    JSONReport, Recommendation, SARIFReport, SARIFRule, SARIFResult,
    ThreatSignature,
} from './types.js';

import { KNOWN_MALICIOUS, SIGNATURES_DB } from './ioc-db.js';
import { PATTERNS } from './patterns.js';

// ── Constants ───────────────────────────────────────────────────────────────

export const VERSION = '4.0.1';

const THRESHOLDS_MAP: Record<string, Thresholds> = {
    normal: { suspicious: 30, malicious: 80 },
    strict: { suspicious: 20, malicious: 60 },
};

const SEVERITY_WEIGHTS: Record<Severity, number> = {
    CRITICAL: 40, HIGH: 15, MEDIUM: 5, LOW: 2,
};

const CODE_EXTENSIONS = new Set([
    '.js', '.ts', '.mjs', '.cjs', '.py', '.sh', '.bash', '.ps1',
    '.rb', '.go', '.rs', '.php', '.pl',
]);
const DOC_EXTENSIONS = new Set(['.md', '.txt', '.rst', '.adoc']);
const DATA_EXTENSIONS = new Set(['.json', '.yaml', '.yml', '.toml', '.xml', '.csv']);
const BINARY_EXTENSIONS = new Set([
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.woff', '.woff2', '.ttf',
    '.eot', '.wasm', '.wav', '.mp3', '.mp4', '.webm', '.ogg', '.pdf',
    '.zip', '.tar', '.gz', '.bz2', '.7z', '.exe', '.dll', '.so', '.dylib',
]);
const GENERATED_REPORT_FILES = new Set([
    'guard-scanner-report.json', 'guard-scanner-report.html', 'guard-scanner.sarif',
]);

// ── GuardScanner ────────────────────────────────────────────────────────────

export class GuardScanner {
    readonly verbose: boolean;
    readonly selfExclude: boolean;
    readonly strict: boolean;
    readonly summaryOnly: boolean;
    /** Suppress all console.log output (v3.2.0: for --format stdout piping) */
    readonly quiet: boolean;
    readonly checkDeps: boolean;
    readonly thresholds: Thresholds;

    findings: SkillResult[] = [];
    stats: ScanStats = { scanned: 0, clean: 0, low: 0, suspicious: 0, malicious: 0 };

    private scannerDir: string;
    private ignoredSkills = new Set<string>();
    private ignoredPatterns = new Set<string>();
    private customRules: PatternRule[] = [];

    constructor(options: ScannerOptions = {}) {
        this.verbose = options.verbose ?? false;
        this.selfExclude = options.selfExclude ?? false;
        this.strict = options.strict ?? false;
        this.summaryOnly = options.summaryOnly ?? false;
        this.quiet = options.quiet ?? false;
        this.checkDeps = options.checkDeps ?? false;
        this.scannerDir = path.resolve(__dirname);
        this.thresholds = this.strict ? THRESHOLDS_MAP.strict : THRESHOLDS_MAP.normal;

        if (options.plugins) {
            for (const plugin of options.plugins) {
                this.loadPlugin(plugin);
            }
        }
        if (options.rulesFile) {
            this.loadCustomRules(options.rulesFile);
        }
    }

    // ── Plugin System ───────────────────────────────────────────────────────

    loadPlugin(pluginPath: string): void {
        try {
            // eslint-disable-next-line @typescript-eslint/no-var-requires
            const plugin = require(path.resolve(pluginPath));
            if (plugin.patterns && Array.isArray(plugin.patterns)) {
                for (const p of plugin.patterns) {
                    if (p.id && p.regex && p.severity && p.cat && p.desc) {
                        this.customRules.push(p as PatternRule);
                    }
                }
                if (!this.summaryOnly) {
                    console.log(`🔌 Plugin loaded: ${plugin.name || pluginPath} (${plugin.patterns.length} rule(s))`);
                }
            }
        } catch (e) {
            console.error(`⚠️  Failed to load plugin ${pluginPath}: ${(e as Error).message}`);
        }
    }

    loadCustomRules(rulesFile: string): void {
        try {
            const content = fs.readFileSync(rulesFile, 'utf-8');
            const rules: CustomRuleInput[] = JSON.parse(content);
            if (!Array.isArray(rules)) {
                console.error('⚠️  Custom rules file must be a JSON array');
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
                        codeOnly: rule.codeOnly ?? false,
                        docOnly: rule.docOnly ?? false,
                        all: !rule.codeOnly && !rule.docOnly,
                    });
                } catch (e) {
                    console.error(`⚠️  Invalid regex in rule ${rule.id}: ${(e as Error).message}`);
                }
            }
            if (!this.summaryOnly && this.customRules.length > 0) {
                console.log(`📏 Loaded ${this.customRules.length} custom rule(s) from ${rulesFile}`);
            }
        } catch (e) {
            console.error(`⚠️  Failed to load custom rules: ${(e as Error).message}`);
        }
    }

    // ── Ignore System ───────────────────────────────────────────────────────

    private loadIgnoreFile(scanDir: string): void {
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
            break;
        }
    }

    // ── Main Scan ─────────────────────────────────────────────────────────

    scanDirectory(dir: string): SkillResult[] {
        if (!fs.existsSync(dir)) {
            console.error(`❌ Directory not found: ${dir}`);
            process.exit(2);
        }

        this.loadIgnoreFile(dir);

        const skills = fs.readdirSync(dir).filter((f: string) => {
            const p = path.join(dir, f);
            return fs.statSync(p).isDirectory();
        });

        if (!this.quiet) {
            console.log(`\n🛡️  guard-scanner v${VERSION}`);
            console.log(`${'═'.repeat(54)}`);
            console.log(`📂 Scanning: ${dir}`);
            console.log(`📦 Skills found: ${skills.length}`);
            if (this.strict) console.log('⚡ Strict mode enabled');
            console.log();
        }

        for (const skill of skills) {
            const skillPath = path.join(dir, skill);

            if (this.selfExclude && path.resolve(skillPath) === this.scannerDir) {
                if (!this.summaryOnly && !this.quiet) console.log(`⏭️  ${skill} — SELF (excluded)`);
                continue;
            }
            if (this.ignoredSkills.has(skill)) {
                if (!this.summaryOnly && !this.quiet) console.log(`⏭️  ${skill} — IGNORED`);
                continue;
            }

            this.scanSkill(skillPath, skill);
        }

        if (!this.quiet) this.printSummary();
        return this.findings;
    }

    // ── Skill Scanner ─────────────────────────────────────────────────────

    scanSkill(skillPath: string, skillName: string): void {
        this.stats.scanned++;
        const skillFindings: Finding[] = [];

        // Check: Known typosquat
        if (KNOWN_MALICIOUS.typosquats.includes(skillName.toLowerCase())) {
            skillFindings.push({
                severity: 'CRITICAL', id: 'KNOWN_TYPOSQUAT', cat: 'malicious-code',
                desc: 'Known malicious/typosquat skill name', file: 'SKILL NAME',
            });
        }

        // Scan all files
        const files = this.getFiles(skillPath);
        for (const file of files) {
            const ext = path.extname(file).toLowerCase();
            const relFile = path.relative(skillPath, file);

            if (relFile.includes('node_modules') || relFile.startsWith('.git')) continue;
            if (BINARY_EXTENSIONS.has(ext)) continue;

            let content: string;
            try { content = fs.readFileSync(file, 'utf-8'); } catch { continue; }
            if (content.length > 500_000) continue;

            const fileType = this.classifyFile(ext, relFile);

            this.checkIoCs(content, relFile, skillFindings);
            this.checkPatterns(content, relFile, fileType, skillFindings);
            this.checkSignatures(content, file, skillFindings); // NEW: hbg-scan compatible

            if (this.customRules.length > 0) {
                this.checkPatterns(content, relFile, fileType, skillFindings, this.customRules);
            }

            // Secret detection (skip lock files)
            const baseName = path.basename(relFile).toLowerCase();
            const skipSecret = baseName.endsWith('-lock.json') || baseName === 'package-lock.json' ||
                baseName === 'yarn.lock' || baseName === 'pnpm-lock.yaml' ||
                baseName === '_meta.json' || baseName === '.package-lock.json';
            if (fileType === 'code' && !skipSecret) {
                this.checkHardcodedSecrets(content, relFile, skillFindings);
            }

            // JS data flow
            if (['.js', '.mjs', '.cjs', '.ts'].includes(ext) && content.length < 200_000) {
                this.checkJSDataFlow(content, relFile, skillFindings);
            }
        }

        // Structural checks
        this.checkStructure(skillPath, skillName, skillFindings);
        if (this.checkDeps) this.checkDependencies(skillPath, skillName, skillFindings);
        this.checkHiddenFiles(skillPath, skillName, skillFindings);
        this.checkCrossFile(skillPath, skillName, skillFindings);
        this.checkSkillManifest(skillPath, skillName, skillFindings);
        this.checkComplexity(skillPath, skillName, skillFindings);
        this.checkConfigImpact(skillPath, skillName, skillFindings);
        this.checkCompactionPersistence(skillPath, skillName, skillFindings); // NEW

        // Filter & score
        const filtered = skillFindings.filter(f => !this.ignoredPatterns.has(f.id));
        const risk = this.calculateRisk(filtered);
        const verdict = this.getVerdict(risk);

        this.stats[verdict.stat]++;

        if (!this.summaryOnly && !this.quiet) {
            console.log(`${verdict.icon} ${skillName} — ${verdict.label} (risk: ${risk})`);
            if (this.verbose && filtered.length > 0) {
                const byCat: Record<string, Finding[]> = {};
                for (const f of filtered) (byCat[f.cat] = byCat[f.cat] || []).push(f);
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

        if (filtered.length > 0) {
            this.findings.push({ skill: skillName, risk, verdict: verdict.label, findings: filtered });
        }
    }

    // ── Check Methods ─────────────────────────────────────────────────────

    private classifyFile(ext: string, relFile: string): FileType {
        if (CODE_EXTENSIONS.has(ext)) return 'code';
        if (DOC_EXTENSIONS.has(ext)) return 'doc';
        if (DATA_EXTENSIONS.has(ext)) return 'data';
        const base = path.basename(relFile).toLowerCase();
        if (base === 'skill.md' || base === 'readme.md') return 'skill-doc';
        return 'other';
    }

    private checkIoCs(content: string, relFile: string, findings: Finding[]): void {
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

    private checkPatterns(
        content: string, relFile: string, fileType: FileType,
        findings: Finding[], patterns: PatternRule[] = PATTERNS,
    ): void {
        for (const pattern of patterns) {
            if (pattern.codeOnly && fileType !== 'code') continue;
            if (pattern.docOnly && fileType !== 'doc' && fileType !== 'skill-doc') continue;
            if (!pattern.all && !pattern.codeOnly && !pattern.docOnly) continue;

            pattern.regex.lastIndex = 0;
            const matches = content.match(pattern.regex);
            if (!matches) continue;

            pattern.regex.lastIndex = 0;
            const idx = content.search(pattern.regex);
            const lineNum = idx >= 0 ? content.substring(0, idx).split('\n').length : undefined;

            let adjustedSeverity: Severity = pattern.severity;
            if ((fileType === 'doc' || fileType === 'skill-doc') && pattern.all && !pattern.docOnly) {
                if (adjustedSeverity === 'HIGH') adjustedSeverity = 'MEDIUM';
                else if (adjustedSeverity === 'MEDIUM') adjustedSeverity = 'LOW';
            }

            findings.push({
                severity: adjustedSeverity, id: pattern.id, cat: pattern.cat,
                desc: pattern.desc, file: relFile, line: lineNum,
                matchCount: matches.length, sample: matches[0].substring(0, 80),
            });
        }
    }

    /** NEW: hbg-scan compatible signature matching (hash + pattern + domain) */
    private checkSignatures(content: string, filePath: string, findings: Finding[]): void {
        const contentHash = crypto.createHash('sha256').update(content).digest('hex');
        const relFile = path.basename(filePath);

        for (const sig of SIGNATURES_DB.signatures) {
            // Hash match
            if (sig.hash && sig.hash === contentHash) {
                findings.push({
                    severity: sig.severity, id: `SIG_${sig.id}`, cat: 'signature-match',
                    desc: `[${sig.id}] ${sig.name} — exact hash match`, file: relFile,
                });
                continue;
            }

            // Pattern match
            if (sig.patterns) {
                for (const pat of sig.patterns) {
                    if (content.includes(pat)) {
                        const idx = content.indexOf(pat);
                        const lineNum = content.substring(0, idx).split('\n').length;
                        findings.push({
                            severity: sig.severity, id: `SIG_${sig.id}`, cat: 'signature-match',
                            desc: `[${sig.id}] ${sig.name}`, file: relFile, line: lineNum,
                            sample: content.split('\n')[lineNum - 1]?.trim().substring(0, 120),
                        });
                        break; // One finding per sig per file
                    }
                }
            }

            // Domain match
            if (sig.domains) {
                for (const domain of sig.domains) {
                    if (content.includes(domain)) {
                        const idx = content.indexOf(domain);
                        const lineNum = content.substring(0, idx).split('\n').length;
                        findings.push({
                            severity: sig.severity, id: `SIG_${sig.id}`, cat: 'signature-match',
                            desc: `[${sig.id}] Suspicious domain: ${domain}`, file: relFile, line: lineNum,
                        });
                    }
                }
            }
        }
    }

    /** NEW: Compaction Layer Persistence check (hbg-scan Check 5) */
    private checkCompactionPersistence(
        skillPath: string, skillName: string, findings: Finding[],
    ): void {
        const files = this.getFiles(skillPath);
        for (const file of files) {
            const ext = path.extname(file).toLowerCase();
            if (BINARY_EXTENSIONS.has(ext)) continue;
            const relFile = path.relative(skillPath, file);
            if (relFile.includes('node_modules') || relFile.startsWith('.git')) continue;

            let content: string;
            try { content = fs.readFileSync(file, 'utf-8'); } catch { continue; }
            if (content.length > 500_000) continue;

            // Post-compaction audit patterns
            const compactionPatterns: Array<{ regex: RegExp; label: string; severity: Severity }> = [
                { regex: /post-?compaction\s+audit/gi, label: 'Post-compaction audit trigger', severity: 'CRITICAL' },
                { regex: /WORKFLOW_AUTO/g, label: 'WORKFLOW_AUTO marker', severity: 'CRITICAL' },
                { regex: /⚠️\s*post-?compaction/gi, label: 'Post-compaction emoji warning', severity: 'CRITICAL' },
                { regex: /after\s+compaction/gi, label: 'After-compaction trigger', severity: 'HIGH' },
                { regex: /survive\s+compaction/gi, label: 'Compaction survival pattern', severity: 'HIGH' },
                { regex: /HEARTBEAT\.md/g, label: 'HEARTBEAT.md reference', severity: 'HIGH' },
                { regex: /BOOTSTRAP\.md/g, label: 'BOOTSTRAP.md reference', severity: 'HIGH' },
                { regex: /persistent\s+instructions/gi, label: 'Persistent instructions pattern', severity: 'HIGH' },
                { regex: /setTimeout\s*\([^)]*(?:86400|604800|2592000)/g, label: 'Very long timer delay (persistence)', severity: 'MEDIUM' },
            ];

            for (const pat of compactionPatterns) {
                pat.regex.lastIndex = 0;
                const match = pat.regex.exec(content);
                if (match) {
                    const lineNum = content.substring(0, match.index).split('\n').length;
                    findings.push({
                        severity: pat.severity,
                        id: 'COMPACTION_PERSISTENCE',
                        cat: 'compaction-persistence',
                        desc: pat.label,
                        file: relFile,
                        line: lineNum,
                        sample: content.split('\n')[lineNum - 1]?.trim().substring(0, 80),
                    });
                }
            }
        }
    }

    private checkHardcodedSecrets(content: string, relFile: string, findings: Finding[]): void {
        const assignmentRegex = /(?:api[_-]?key|secret|token|password|credential|auth)\s*[:=]\s*['"]([a-zA-Z0-9_\-+/=]{16,})['"]|['"]([a-zA-Z0-9_\-+/=]{32,})['"]/gi;
        let match: RegExpExecArray | null;
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
                    sample: value.substring(0, 8) + '...' + value.substring(value.length - 4),
                });
            }
        }
    }

    private shannonEntropy(str: string): number {
        const freq: Record<string, number> = {};
        for (const c of str) freq[c] = (freq[c] || 0) + 1;
        const len = str.length;
        let entropy = 0;
        for (const count of Object.values(freq)) {
            const p = count / len;
            if (p > 0) entropy -= p * Math.log2(p);
        }
        return entropy;
    }

    private checkStructure(skillPath: string, skillName: string, findings: Finding[]): void {
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
            const scripts = fs.readdirSync(scriptsDir).filter((f: string) => CODE_EXTENSIONS.has(path.extname(f).toLowerCase()));
            if (scripts.length > 0 && !content.includes('scripts/')) {
                findings.push({ severity: 'MEDIUM', id: 'STRUCT_UNDOCUMENTED_SCRIPTS', cat: 'structural', desc: `${scripts.length} script(s) in scripts/ not referenced in SKILL.md`, file: 'scripts/' });
            }
        }
    }

    private checkDependencies(skillPath: string, skillName: string, findings: Finding[]): void {
        const pkgPath = path.join(skillPath, 'package.json');
        if (!fs.existsSync(pkgPath)) return;

        let pkg: { dependencies?: Record<string, string>; devDependencies?: Record<string, string>; optionalDependencies?: Record<string, string>; scripts?: Record<string, string> };
        try { pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8')); } catch { return; }

        const allDeps: Record<string, string> = { ...pkg.dependencies, ...pkg.devDependencies, ...pkg.optionalDependencies };

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
                const cmd = pkg.scripts[scriptName];
                if (cmd) {
                    findings.push({ severity: 'HIGH', id: 'DEP_LIFECYCLE', cat: 'dependency-chain', desc: `Lifecycle script "${scriptName}": ${cmd.substring(0, 80)}`, file: 'package.json' });
                    if (/curl|wget|node\s+-e|eval|exec|bash\s+-c/i.test(cmd)) {
                        findings.push({ severity: 'CRITICAL', id: 'DEP_LIFECYCLE_EXEC', cat: 'dependency-chain', desc: `Lifecycle script "${scriptName}" downloads/executes code`, file: 'package.json', sample: cmd.substring(0, 80) });
                    }
                }
            }
        }
    }

    private checkSkillManifest(skillPath: string, skillName: string, findings: Finding[]): void {
        const skillMd = path.join(skillPath, 'SKILL.md');
        if (!fs.existsSync(skillMd)) return;
        let content: string;
        try { content = fs.readFileSync(skillMd, 'utf-8'); } catch { return; }

        const fmMatch = content.match(/^---\n([\s\S]*?)\n---/);
        if (!fmMatch) return;
        const fm = fmMatch[1];

        const DANGEROUS_BINS = new Set([
            'sudo', 'rm', 'rmdir', 'chmod', 'chown', 'kill', 'pkill',
            'curl', 'wget', 'nc', 'ncat', 'socat', 'ssh', 'scp',
            'dd', 'mkfs', 'fdisk', 'mount', 'umount',
            'iptables', 'ufw', 'firewall-cmd', 'docker', 'kubectl', 'systemctl',
        ]);

        const binsMatch = fm.match(/bins:\s*\n((?:\s+-\s+[^\n]+\n?)*)/i);
        if (binsMatch) {
            const bins = binsMatch[1].match(/- ([^\n]+)/g) || [];
            for (const binLine of bins) {
                const bin = binLine.replace(/^-\s*/, '').trim().toLowerCase();
                if (DANGEROUS_BINS.has(bin)) {
                    findings.push({ severity: 'HIGH', id: 'MANIFEST_DANGEROUS_BIN', cat: 'sandbox-validation', desc: `SKILL.md requires dangerous binary: ${bin}`, file: 'SKILL.md' });
                }
            }
        }

        const filesMatch = fm.match(/files:\s*\[([^\]]+)\]/i) || fm.match(/files:\s*\n((?:\s+-\s+[^\n]+\n?)*)/i);
        if (filesMatch && /\*\*\/\*|\*\.\*|"\*"/i.test(filesMatch[1])) {
            findings.push({ severity: 'HIGH', id: 'MANIFEST_BROAD_FILES', cat: 'sandbox-validation', desc: 'SKILL.md declares overly broad file scope (e.g. **/*)', file: 'SKILL.md' });
        }

        const SENSITIVE_ENV = /(?:SECRET|PASSWORD|CREDENTIAL|PRIVATE_KEY|AWS_SECRET|GITHUB_TOKEN)/i;
        const envMatch = fm.match(/env:\s*\n((?:\s+-\s+[^\n]+\n?)*)/i);
        if (envMatch) {
            const envVars = envMatch[1].match(/- ([^\n]+)/g) || [];
            for (const envLine of envVars) {
                const envVar = envLine.replace(/^-\s*/, '').trim();
                if (SENSITIVE_ENV.test(envVar)) {
                    findings.push({ severity: 'HIGH', id: 'MANIFEST_SENSITIVE_ENV', cat: 'sandbox-validation', desc: `SKILL.md requires sensitive env var: ${envVar}`, file: 'SKILL.md' });
                }
            }
        }

        if (/exec:\s*(?:true|yes|enabled|'\*'|"\*")/i.test(fm)) {
            findings.push({ severity: 'MEDIUM', id: 'MANIFEST_EXEC_DECLARED', cat: 'sandbox-validation', desc: 'SKILL.md declares exec capability', file: 'SKILL.md' });
        }
        if (/network:\s*(?:true|yes|enabled|'\*'|"\*"|all|any)/i.test(fm)) {
            findings.push({ severity: 'MEDIUM', id: 'MANIFEST_NETWORK_DECLARED', cat: 'sandbox-validation', desc: 'SKILL.md declares unrestricted network access', file: 'SKILL.md' });
        }
    }

    private checkComplexity(skillPath: string, skillName: string, findings: Finding[]): void {
        const files = this.getFiles(skillPath);
        const MAX_LINES = 1000;
        const MAX_NESTING = 5;
        const MAX_EVAL_DENSITY = 0.02;

        for (const file of files) {
            const ext = path.extname(file).toLowerCase();
            if (!CODE_EXTENSIONS.has(ext)) continue;
            const relFile = path.relative(skillPath, file);
            if (relFile.includes('node_modules') || relFile.startsWith('.git')) continue;

            let content: string;
            try { content = fs.readFileSync(file, 'utf-8'); } catch { continue; }
            const lines = content.split('\n');

            if (lines.length > MAX_LINES) {
                findings.push({ severity: 'MEDIUM', id: 'COMPLEXITY_LONG_FILE', cat: 'complexity', desc: `File exceeds ${MAX_LINES} lines (${lines.length} lines)`, file: relFile });
            }

            let maxDepth = 0, currentDepth = 0, deepestLine = 0;
            for (let i = 0; i < lines.length; i++) {
                for (const ch of lines[i]) {
                    if (ch === '{') currentDepth++;
                    if (ch === '}') currentDepth = Math.max(0, currentDepth - 1);
                }
                if (currentDepth > maxDepth) { maxDepth = currentDepth; deepestLine = i + 1; }
            }
            if (maxDepth > MAX_NESTING) {
                findings.push({ severity: 'MEDIUM', id: 'COMPLEXITY_DEEP_NESTING', cat: 'complexity', desc: `Deep nesting: ${maxDepth} levels (max: ${MAX_NESTING})`, file: relFile, line: deepestLine });
            }

            const evalMatches = content.match(/\b(?:eval|exec|execSync|spawn|Function)\s*\(/g) || [];
            const density = lines.length > 0 ? evalMatches.length / lines.length : 0;
            if (density > MAX_EVAL_DENSITY && evalMatches.length >= 3) {
                findings.push({ severity: 'HIGH', id: 'COMPLEXITY_EVAL_DENSITY', cat: 'complexity', desc: `High eval/exec density: ${evalMatches.length} calls in ${lines.length} lines (${(density * 100).toFixed(1)}%)`, file: relFile });
            }
        }
    }

    private checkConfigImpact(skillPath: string, skillName: string, findings: Finding[]): void {
        const files = this.getFiles(skillPath);
        for (const file of files) {
            const ext = path.extname(file).toLowerCase();
            if (!CODE_EXTENSIONS.has(ext) && ext !== '.json') continue;
            const relFile = path.relative(skillPath, file);
            if (relFile.includes('node_modules') || relFile.startsWith('.git')) continue;

            let content: string;
            try { content = fs.readFileSync(file, 'utf-8'); } catch { continue; }

            const hasConfigRef = /openclaw\.json/i.test(content);
            const hasWriteOp = /(?:writeFileSync|writeFile|fs\.write)\s*\(/i.test(content);
            if (hasConfigRef && hasWriteOp) {
                const clines = content.split('\n');
                let writeLine = 0;
                for (let i = 0; i < clines.length; i++) {
                    if (/(?:writeFileSync|writeFile|fs\.write)\s*\(/i.test(clines[i])) { writeLine = i + 1; break; }
                }
                findings.push({ severity: 'CRITICAL', id: 'CFG_WRITE_DETECTED', cat: 'config-impact', desc: 'Code writes to openclaw.json', file: relFile, line: writeLine });
            }

            const DANGEROUS_CFG = [
                { regex: /exec\.approvals?\s*[:=]\s*['"]?(off|false|disabled|none)/gi, id: 'CFG_EXEC_APPROVAL_OFF', desc: 'Disables exec approval', severity: 'CRITICAL' as Severity },
                { regex: /tools\.exec\.host\s*[:=]\s*['"]gateway['"]/gi, id: 'CFG_EXEC_HOST_GATEWAY', desc: 'Sets exec host to gateway', severity: 'CRITICAL' as Severity },
                { regex: /hooks\s*\.\s*internal\s*\.\s*entries\s*[:=]/gi, id: 'CFG_HOOKS_INTERNAL', desc: 'Modifies internal hooks', severity: 'HIGH' as Severity },
                { regex: /network\.allowedDomains\s*[:=]\s*\[?\s*['"]\*['"]/gi, id: 'CFG_NET_WILDCARD', desc: 'Sets network domains to wildcard', severity: 'HIGH' as Severity },
            ];
            for (const check of DANGEROUS_CFG) {
                check.regex.lastIndex = 0;
                if (check.regex.test(content)) {
                    findings.push({ severity: check.severity, id: check.id, cat: 'config-impact', desc: check.desc, file: relFile });
                }
            }
        }
    }

    private checkHiddenFiles(skillPath: string, skillName: string, findings: Finding[]): void {
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
        } catch { /* empty */ }
    }

    private checkJSDataFlow(content: string, relFile: string, findings: Finding[]): void {
        const lines = content.split('\n');
        const imports = new Map<string, string>();
        const sensitiveReads: Array<{ line: number; text: string }> = [];
        const networkCalls: Array<{ line: number; text: string }> = [];
        const execCalls: Array<{ line: number; text: string }> = [];

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const lineNum = i + 1;

            const reqMatch = line.match(/(?:const|let|var)\s+(?:\{[^}]+\}|\w+)\s*=\s*require\s*\(\s*['"]([^'"]+)['"]\s*\)/);
            if (reqMatch) {
                const varMatch = line.match(/(?:const|let|var)\s+(\{[^}]+\}|\w+)/);
                if (varMatch) imports.set(varMatch[1].trim(), reqMatch[1]);
            }

            if (/(?:readFileSync|readFile)\s*\([^)]*(?:\.env|\.ssh|id_rsa|\.clawdbot|\.openclaw(?!\/workspace))/i.test(line)) {
                sensitiveReads.push({ line: lineNum, text: line.trim() });
            }
            if (/process\.env\.[A-Z_]*(?:KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL)/i.test(line)) {
                sensitiveReads.push({ line: lineNum, text: line.trim() });
            }
            if (/(?:fetch|axios|request|http\.request|https\.request|got)\s*\(/i.test(line) || /\.post\s*\(|\.put\s*\(|\.patch\s*\(/i.test(line)) {
                networkCalls.push({ line: lineNum, text: line.trim() });
            }
            if (/(?:exec|execSync|spawn|spawnSync|execFile)\s*\(/i.test(line)) {
                execCalls.push({ line: lineNum, text: line.trim() });
            }
        }

        if (sensitiveReads.length > 0 && networkCalls.length > 0) {
            findings.push({ severity: 'CRITICAL', id: 'AST_CRED_TO_NET', cat: 'data-flow', desc: `Data flow: secret read (L${sensitiveReads[0].line}) → network call (L${networkCalls[0].line})`, file: relFile, line: sensitiveReads[0].line, sample: sensitiveReads[0].text.substring(0, 60) });
        }
        if (sensitiveReads.length > 0 && execCalls.length > 0) {
            findings.push({ severity: 'HIGH', id: 'AST_CRED_TO_EXEC', cat: 'data-flow', desc: `Data flow: secret read (L${sensitiveReads[0].line}) → command exec (L${execCalls[0].line})`, file: relFile, line: sensitiveReads[0].line, sample: sensitiveReads[0].text.substring(0, 60) });
        }

        const importedModules = new Set([...imports.values()]);
        if (importedModules.has('child_process') && (importedModules.has('https') || importedModules.has('http') || importedModules.has('node-fetch'))) {
            findings.push({ severity: 'HIGH', id: 'AST_SUSPICIOUS_IMPORTS', cat: 'data-flow', desc: 'Suspicious: child_process + network module', file: relFile });
        }
        if (importedModules.has('fs') && importedModules.has('child_process') && (importedModules.has('https') || importedModules.has('http'))) {
            findings.push({ severity: 'CRITICAL', id: 'AST_EXFIL_TRIFECTA', cat: 'data-flow', desc: 'Exfiltration trifecta: fs + child_process + network', file: relFile });
        }

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            if (/`[^`]*\$\{.*(?:env|key|token|secret|password).*\}[^`]*`\s*(?:\)|,)/i.test(line) && /(?:fetch|request|axios|http|url)/i.test(line)) {
                findings.push({ severity: 'CRITICAL', id: 'AST_SECRET_IN_URL', cat: 'data-flow', desc: 'Secret interpolated into URL', file: relFile, line: i + 1, sample: line.trim().substring(0, 80) });
            }
        }
    }

    private checkCrossFile(skillPath: string, skillName: string, findings: Finding[]): void {
        const files = this.getFiles(skillPath);
        const allContent: Record<string, string> = {};

        for (const file of files) {
            const ext = path.extname(file).toLowerCase();
            if (BINARY_EXTENSIONS.has(ext)) continue;
            const relFile = path.relative(skillPath, file);
            if (relFile.includes('node_modules') || relFile.startsWith('.git')) continue;
            try {
                const content = fs.readFileSync(file, 'utf-8');
                if (content.length < 500_000) allContent[relFile] = content;
            } catch { /* empty */ }
        }

        const skillMd = allContent['SKILL.md'] || '';
        const codeFileRefs = skillMd.match(/(?:scripts?\/|\.\/)[a-zA-Z0-9_\-.\/]+\.(js|py|sh|ts)/gi) || [];
        for (const ref of codeFileRefs) {
            const cleanRef = ref.replace(/^\.\//, '');
            if (!allContent[cleanRef] && !files.some(f => path.relative(skillPath, f) === cleanRef)) {
                findings.push({ severity: 'MEDIUM', id: 'XFILE_PHANTOM_REF', cat: 'structural', desc: `SKILL.md references non-existent: ${cleanRef}`, file: 'SKILL.md' });
            }
        }

        const b64Fragments: Array<{ file: string; fragment: string }> = [];
        for (const [file, content] of Object.entries(allContent)) {
            const matches = content.match(/[A-Za-z0-9+/]{20,}={0,2}/g) || [];
            for (const m of matches) {
                if (m.length > 40) b64Fragments.push({ file, fragment: m.substring(0, 30) });
            }
        }
        if (b64Fragments.length > 3 && new Set(b64Fragments.map(f => f.file)).size > 1) {
            findings.push({ severity: 'HIGH', id: 'XFILE_FRAGMENT_B64', cat: 'obfuscation', desc: `Base64 fragments across ${new Set(b64Fragments.map(f => f.file)).size} files`, file: skillName });
        }

        if (/(?:read|load|source|import)\s+(?:the\s+)?(?:script|file|code)\s+(?:from|at|in)\s+(?:scripts?\/)/gi.test(skillMd)) {
            const hasExec = Object.values(allContent).some(c => /(?:eval|exec|spawn)\s*\(/i.test(c));
            if (hasExec) {
                findings.push({ severity: 'MEDIUM', id: 'XFILE_LOAD_EXEC', cat: 'data-flow', desc: 'SKILL.md references scripts with exec/eval', file: 'SKILL.md' });
            }
        }
    }

    // ── Risk Scoring ──────────────────────────────────────────────────────

    private calculateRisk(findings: Finding[]): number {
        if (findings.length === 0) return 0;

        let score = 0;
        for (const f of findings) {
            score += SEVERITY_WEIGHTS[f.severity] || 0;
        }

        const ids = new Set(findings.map(f => f.id));
        const cats = new Set(findings.map(f => f.cat));

        // Amplifiers
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

        // v1.1
        if (cats.has('config-impact')) score = Math.round(score * 2);
        if (cats.has('config-impact') && cats.has('sandbox-validation')) score = Math.max(score, 70);
        if (cats.has('complexity') && (cats.has('malicious-code') || cats.has('obfuscation'))) score = Math.round(score * 1.5);

        // v2.1 PII
        if (cats.has('pii-exposure') && cats.has('exfiltration')) score = Math.round(score * 3);
        if (cats.has('pii-exposure') && (ids.has('SHADOW_AI_OPENAI') || ids.has('SHADOW_AI_ANTHROPIC') || ids.has('SHADOW_AI_GENERIC'))) score = Math.round(score * 2.5);
        if (cats.has('pii-exposure') && cats.has('credential-handling')) score = Math.round(score * 2);

        // v3.0 Compaction persistence
        if (cats.has('compaction-persistence')) score = Math.round(score * 2);
        if (cats.has('compaction-persistence') && cats.has('prompt-injection')) score = Math.max(score, 90);
        if (cats.has('signature-match')) score = Math.max(score, 70);

        return Math.min(100, score);
    }

    private getVerdict(risk: number): Verdict {
        if (risk >= this.thresholds.malicious) return { icon: '🔴', label: 'MALICIOUS', stat: 'malicious' };
        if (risk >= this.thresholds.suspicious) return { icon: '🟡', label: 'SUSPICIOUS', stat: 'suspicious' };
        if (risk > 0) return { icon: '🟢', label: 'LOW RISK', stat: 'low' };
        return { icon: '🟢', label: 'CLEAN', stat: 'clean' };
    }

    // ── File Discovery ────────────────────────────────────────────────────

    private getFiles(dir: string): string[] {
        const results: string[] = [];
        try {
            const entries = fs.readdirSync(dir, { withFileTypes: true });
            for (const entry of entries) {
                const fullPath = path.join(dir, entry.name);
                if (entry.isDirectory()) {
                    if (entry.name === '.git' || entry.name === 'node_modules') continue;
                    results.push(...this.getFiles(fullPath));
                } else {
                    if (GENERATED_REPORT_FILES.has(entry.name.toLowerCase())) continue;
                    results.push(fullPath);
                }
            }
        } catch { /* empty */ }
        return results;
    }

    // ── Output ────────────────────────────────────────────────────────────

    printSummary(): void {
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
        } else if (this.stats.suspicious > 0) {
            console.log(`\n⚡ ${this.stats.suspicious} suspicious skill(s) found — review recommended.`);
        } else {
            console.log('\n✅ All clear! No threats detected.');
        }
    }

    toJSON(): JSONReport {
        const recommendations: Recommendation[] = [];
        for (const sr of this.findings) {
            const actions: string[] = [];
            const cats = new Set(sr.findings.map(f => f.cat));

            if (cats.has('prompt-injection')) actions.push('🛑 Contains prompt injection patterns.');
            if (cats.has('malicious-code')) actions.push('🛑 Contains potentially malicious code.');
            if (cats.has('credential-handling') && cats.has('exfiltration')) actions.push('💀 CRITICAL: Credential + exfiltration. DO NOT INSTALL.');
            if (cats.has('dependency-chain')) actions.push('📦 Suspicious dependency chain.');
            if (cats.has('obfuscation')) actions.push('🔍 Code obfuscation detected.');
            if (cats.has('secret-detection')) actions.push('🔑 Possible hardcoded secrets.');
            if (cats.has('memory-poisoning')) actions.push('🧠 MEMORY POISONING: Agent memory modification.');
            if (cats.has('prompt-worm')) actions.push('🪱 PROMPT WORM: Self-replicating instructions.');
            if (cats.has('data-flow')) actions.push('🔀 Suspicious data flow patterns.');
            if (cats.has('identity-hijack')) actions.push('🔒 IDENTITY HIJACK: Agent soul file tampering.');
            if (cats.has('compaction-persistence')) actions.push('⏰ COMPACTION PERSISTENCE: Survives context compaction.');
            if (cats.has('signature-match')) actions.push('🎯 SIGNATURE MATCH: Known threat signature detected.');
            if (cats.has('config-impact')) actions.push('⚙️ CONFIG IMPACT: Modifies OpenClaw configuration.');
            if (cats.has('pii-exposure')) actions.push('🆔 PII EXPOSURE: Handles personal information.');

            if (actions.length > 0) recommendations.push({ skill: sr.skill, actions });
        }

        return {
            timestamp: new Date().toISOString(),
            scanner: `guard-scanner v${VERSION}`,
            mode: this.strict ? 'strict' : 'normal',
            stats: this.stats,
            thresholds: this.thresholds,
            findings: this.findings,
            recommendations,
            iocVersion: '2026-02-21',
            signaturesVersion: SIGNATURES_DB.version,
        };
    }

    toSARIF(scanDir: string): SARIFReport {
        const rules: SARIFRule[] = [];
        const ruleIndex: Record<string, number> = {};
        const results: SARIFResult[] = [];

        for (const sr of this.findings) {
            for (const f of sr.findings) {
                if (!ruleIndex[f.id] && ruleIndex[f.id] !== 0) {
                    ruleIndex[f.id] = rules.length;
                    // Look up OWASP mapping from PATTERNS
                    const patternDef = PATTERNS.find((p) => p.id === f.id);
                    const owaspTag = patternDef?.owasp;
                    const tags = ['security', f.cat];
                    if (owaspTag) tags.push(`OWASP/${owaspTag}`);

                    rules.push({
                        id: f.id, name: f.id,
                        shortDescription: { text: f.desc },
                        defaultConfiguration: { level: f.severity === 'CRITICAL' || f.severity === 'HIGH' ? 'error' : f.severity === 'MEDIUM' ? 'warning' : 'note' },
                        properties: {
                            tags,
                            'security-severity': f.severity === 'CRITICAL' ? '9.0' : f.severity === 'HIGH' ? '7.0' : f.severity === 'MEDIUM' ? '4.0' : '1.0',
                        },
                    });
                }

                const normalizedFile = String(f.file || '').replaceAll('\\', '/').replace(/^\/+/, '');
                const artifactUri = `${sr.skill}/${normalizedFile}`;
                const seed = `${f.id}|${artifactUri}|${f.line || 0}|${(f.sample || '').slice(0, 200)}`;
                const lineHash = crypto.createHash('sha256').update(seed).digest('hex').slice(0, 24);

                results.push({
                    ruleId: f.id, ruleIndex: ruleIndex[f.id],
                    level: f.severity === 'CRITICAL' || f.severity === 'HIGH' ? 'error' : f.severity === 'MEDIUM' ? 'warning' : 'note',
                    message: { text: `[${sr.skill}] ${f.desc}${f.sample ? ` — "${f.sample}"` : ''}` },
                    partialFingerprints: { primaryLocationLineHash: lineHash },
                    locations: [{
                        physicalLocation: {
                            artifactLocation: { uri: artifactUri, uriBaseId: '%SRCROOT%' },
                            region: f.line ? { startLine: f.line } : undefined,
                        },
                    }],
                });
            }
        }

        return {
            version: '2.1.0',
            $schema: 'https://json.schemastore.org/sarif-2.1.0.json',
            runs: [{
                tool: { driver: { name: 'guard-scanner', version: VERSION, informationUri: 'https://github.com/koatora20/guard-scanner', rules } },
                results,
                invocations: [{ executionSuccessful: true, endTimeUtc: new Date().toISOString() }],
            }],
        };
    }
    toHTML(): string {
        const report = this.toJSON();
        const ts = new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC';
        const severityColor: Record<string, string> = {
            CRITICAL: '#ff4444', HIGH: '#ff8800', MEDIUM: '#ffcc00', LOW: '#aaaaaa',
        };
        const verdictColor: Record<string, string> = {
            MALICIOUS: '#ff4444', SUSPICIOUS: '#ffcc00', 'LOW RISK': '#44cc88', CLEAN: '#44cc88',
        };

        const rows = report.findings.map(sr => {
            const color = verdictColor[sr.verdict] || '#aaaaaa';
            const findingRows = sr.findings.map(f => {
                const c = severityColor[f.severity] || '#aaaaaa';
                const loc = f.file ? `${f.file}${f.line ? ':' + f.line : ''}` : '—';
                const sample = f.sample ? `<code>${f.sample.replace(/</g, '&lt;')}</code>` : '—';
                return `<tr><td style="color:${c};font-weight:bold">${f.severity}</td><td>${f.id}</td><td>${f.desc}</td><td>${loc}</td><td>${sample}</td></tr>`;
            }).join('');
            const badge = `<span style="background:${color};color:#000;padding:2px 8px;border-radius:4px;font-weight:bold;font-size:0.85em">${sr.verdict}</span>`;
            return `<tr><td colspan="5" style="background:#1a1a2e;padding:8px 12px;font-weight:bold">
                🛡️ ${sr.skill} — ${badge} (risk: ${sr.risk})</td></tr>${findingRows}`;
        }).join('');

        const total = report.stats.scanned;
        const safe = report.stats.clean + report.stats.low;
        const safeRate = total ? Math.round(safe / total * 100) : 0;

        return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>guard-scanner v${VERSION} Report</title>
<style>
  body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0d0d1a; color: #e0e0e0; margin: 0; padding: 24px; }
  h1 { color: #7ec8e3; margin: 0 0 4px; }
  .meta { color: #888; font-size: 0.85em; margin-bottom: 24px; }
  .stats { display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
  .stat { background: #1a1a2e; border: 1px solid #333; border-radius: 8px; padding: 12px 20px; text-align: center; min-width: 80px; }
  .stat-label { font-size: 0.75em; color: #888; margin-bottom: 4px; }
  .stat-val { font-size: 1.8em; font-weight: bold; }
  table { width: 100%; border-collapse: collapse; margin-top: 8px; }
  th { background: #1a1a2e; padding: 8px 12px; text-align: left; font-size: 0.85em; color: #888; border-bottom: 1px solid #333; }
  td { padding: 6px 12px; border-bottom: 1px solid #222; font-size: 0.85em; vertical-align: top; }
  tr:hover td { background: #13132a; }
  code { background: #1e1e3a; padding: 1px 4px; border-radius: 3px; font-family: monospace; font-size: 0.9em; word-break: break-all; }
  .clean { color: #44cc88; font-weight: bold; }
  .footer { margin-top: 32px; color: #555; font-size: 0.8em; }
</style>
</head>
<body>
<h1>🛡️ guard-scanner v${VERSION}</h1>
<div class="meta">Generated: ${ts} | Mode: ${report.mode} | Thresholds: suspicious≥${report.thresholds.suspicious}, malicious≥${report.thresholds.malicious}</div>
<div class="stats">
  <div class="stat"><div class="stat-label">Scanned</div><div class="stat-val">${report.stats.scanned}</div></div>
  <div class="stat"><div class="stat-label">Clean</div><div class="stat-val" style="color:#44cc88">${report.stats.clean}</div></div>
  <div class="stat"><div class="stat-label">Low Risk</div><div class="stat-val" style="color:#44cc88">${report.stats.low}</div></div>
  <div class="stat"><div class="stat-label">Suspicious</div><div class="stat-val" style="color:#ffcc00">${report.stats.suspicious}</div></div>
  <div class="stat"><div class="stat-label">Malicious</div><div class="stat-val" style="color:#ff4444">${report.stats.malicious}</div></div>
  <div class="stat"><div class="stat-label">Safety Rate</div><div class="stat-val" style="color:${safeRate >= 80 ? '#44cc88' : '#ff8800'}">${safeRate}%</div></div>
</div>
${report.findings.length === 0 ? '<p class="clean">✅ All clear — no threats detected.</p>' : `
<table>
<thead><tr><th>Severity</th><th>Pattern ID</th><th>Description</th><th>Location</th><th>Sample</th></tr></thead>
<tbody>${rows}</tbody>
</table>`}
<div class="footer">guard-scanner v${VERSION} | IoC DB: ${report.iocVersion} | Signatures: ${report.signaturesVersion} | <a href="https://github.com/koatora20/guard-scanner" style="color:#7ec8e3">GitHub</a></div>
</body></html>`;
    }
}
